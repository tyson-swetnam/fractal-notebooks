#!/usr/bin/env bash
# Build the Fractal Notebooks site (local and CI). Steps, in order:
#   1 fractal_rag.okf_export --check     the committed okf/concepts bundle matches seed.yaml
#   2 stage_okf.py                       copy okf/{concepts,proofs} -> docs/okf/
#   3 render_notebooks.py --check        the committed notebook pages match the .ipynb files
#   4 validate_okf.py x3                 docs/ (minus the staged okf/concepts/**, okf/proofs/**), okf/concepts, okf/proofs
#   5 zensical build --clean --strict    (always strict; zensical.toml also sets strict = true)
#   6 publish_sources.py --verify        Markdown twins + alternate-link check
#   7 generate_llms_txt.py --strict      llms.txt + llms-full.txt
#   8 (--with-react) npm ci, type-check, lint, build; copy react/build/. -> site/react/
#   9 check_site.py                      coverage, links, leaks, redirects, llms, robots, okf, icons, size
#                                        (links into react/ are only checked after step 8)
#
# Flags:  --with-react   build and merge the React SPA (CI deploy; needs Node 20)
#         --serve        after a successful build, exec `zensical serve`
#         --ci           non-interactive: no colours, print tool versions
# Usage:  bash scripts/build_site.sh [--with-react] [--serve] [--ci]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

WITH_REACT=0; SERVE=0; CI_MODE=0
for arg in "$@"; do
  case "$arg" in
    --with-react) WITH_REACT=1 ;;
    --serve) SERVE=1 ;;
    --ci) CI_MODE=1 ;;
    -h|--help) sed -n '2,/^set -euo/p' "$0" | sed '$d'; exit 0 ;;
    *) echo "build_site.sh: unknown flag $arg" >&2; exit 2 ;;
  esac
done

# Python: prefer the project venv, else whatever `python` is on PATH (CI installs requirements-docs.txt there).
if [ -n "${PYTHON:-}" ]; then :; elif [ -x "$ROOT/.venv/bin/python" ]; then PYTHON="$ROOT/.venv/bin/python"; else PYTHON="$(command -v python3 || command -v python)"; fi
ZENSICAL="${ZENSICAL:-}"
if [ -z "$ZENSICAL" ]; then
  if [ -x "$(dirname "$PYTHON")/zensical" ]; then ZENSICAL="$(dirname "$PYTHON")/zensical"; else ZENSICAL="$(command -v zensical || true)"; fi
fi
if [ -z "$ZENSICAL" ] || [ ! -x "$ZENSICAL" ]; then
  echo "build_site.sh: zensical not found (looked next to $PYTHON and on PATH). Install the docs toolchain first:" >&2
  echo "  $PYTHON -m pip install -r requirements-docs.txt" >&2
  exit 2
fi
CONFIG="$ROOT/zensical.toml"
SITE="$ROOT/site"

step() { printf '\n==> [%s] %s\n' "$1" "$2"; }

if [ ! -f "$CONFIG" ]; then
  echo "build_site.sh: $CONFIG not found" >&2; exit 2
fi
if [ "$CI_MODE" = 1 ]; then
  "$PYTHON" --version; "$ZENSICAL" --version || true; export NO_COLOR=1 TERM=dumb
fi

step 1/9 "fractal_rag.okf_export --check (okf/concepts matches seed.yaml)"
PYTHONPATH="$ROOT/fractal_rag/src${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON" -m fractal_rag.okf_export --check --out "$ROOT/okf/concepts"

step 2/9 "stage_okf.py (okf/{concepts,proofs} -> docs/okf/)"
"$PYTHON" scripts/stage_okf.py

step 3/9 "render_notebooks.py --check (committed notebook pages are fresh)"
"$PYTHON" scripts/render_notebooks.py --check --strict --config "$CONFIG"

step 4/9 "validate_okf.py (docs, okf/concepts, okf/proofs)"
"$PYTHON" scripts/validate_okf.py docs --exclude 'okf/concepts/**' --exclude 'okf/proofs/**' --config "$CONFIG"
"$PYTHON" scripts/validate_okf.py okf/concepts --profile concept --config "$CONFIG"
"$PYTHON" scripts/validate_okf.py okf/proofs --profile proof --config "$CONFIG"

step 5/9 "zensical build --strict"
rm -rf "$SITE"
"$ZENSICAL" build -f "$CONFIG" --clean --strict

step 6/9 "publish_sources.py --verify (Markdown twins)"
"$PYTHON" scripts/publish_sources.py --config "$CONFIG" --verify

step 7/9 "generate_llms_txt.py --strict"
"$PYTHON" scripts/generate_llms_txt.py --config "$CONFIG" --strict

if [ "$WITH_REACT" = 1 ]; then
  step 8/9 "React: npm ci && type-check && lint && build -> site/react/"
  ( cd "$ROOT/react" && npm ci && npm run type-check && npm run lint && npm run build )
  mkdir -p "$SITE/react"
  cp -R "$ROOT/react/build/." "$SITE/react/"
else
  step 8/9 "React build skipped (pass --with-react)"
fi

step 9/9 "check_site.py"
"$PYTHON" scripts/check_site.py --config "$CONFIG" --site "$SITE"

echo
echo "build_site.sh: site ready in $SITE ($(du -sh "$SITE" | cut -f1))"

if [ "$SERVE" = 1 ]; then
  exec "$ZENSICAL" serve -f "$CONFIG"
fi
