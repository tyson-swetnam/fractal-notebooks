#!/usr/bin/env python3
"""Make the optimum/ONNX imports in the t2v-transformers app lazy.

optimum 1.27 imports a symbol that PyTorch 2.9 removed (torch.onnx.symbolic_opset14._attention_scale),
so importing it at module level crashes download.py and the server. The ONNX runtime path is unused in
this build (ONNX_RUNTIME=false), so the imports move inside the only functions that need them.
Idempotent; exits non-zero if the expected code is not found.
"""
import pathlib, re, sys

MARK = "LAZY_ONNX_PATCHED"

def sub1(s, pattern, repl, flags=0):
    new, n = re.subn(pattern, repl, s, flags=flags)
    if n != 1:
        raise SystemExit(f"expected exactly one match, found {n}: {pattern!r}")
    return new

def patch(path):
    p = pathlib.Path(path); s = p.read_text(encoding="utf-8")
    if MARK in s:
        print("already patched", path); return
    if p.name == "download.py":
        s = sub1(s, r"from optimum\.onnxruntime import ORTModelForFeatureExtraction\nfrom optimum\.onnxruntime\.configuration import AutoQuantizationConfig\nfrom optimum\.onnxruntime import ORTQuantizer\n",
                 f"# {MARK}: optimum is imported inside download_onnx_model\n")
        s = sub1(s, r"(def download_onnx_model\([^)]*\):\n)",
                 r"\1    from optimum.onnxruntime import ORTModelForFeatureExtraction, ORTQuantizer\n    from optimum.onnxruntime.configuration import AutoQuantizationConfig\n\n")
    elif p.name == "vectorizer.py":
        s = sub1(s, r"from optimum\.onnxruntime import ORTModelForFeatureExtraction\n",
                 f"# {MARK}: optimum is imported inside ONNXVectorizer.__init__\n")
        s = sub1(s, r"class ONNXVectorizer:\n    model: ORTModelForFeatureExtraction\n",
                 'class ONNXVectorizer:\n    model: "ORTModelForFeatureExtraction"\n')
        s = sub1(s, r"(    def __init__\(self, model_path, trust_remote_code: bool\) -> None:\n)(        onnx_path = Path\(model_path\)\n)",
                 r"\1        from optimum.onnxruntime import ORTModelForFeatureExtraction\n\n\2")
    else:
        raise SystemExit(f"unknown file {path}")
    p.write_text(s, encoding="utf-8"); print("patched", path)

for f in sys.argv[1:]:
    patch(f)
