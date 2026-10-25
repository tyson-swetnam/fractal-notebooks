
import stage_okf as so


def test_stage_copies_and_removes_only_inside_bundle_dirs(fx):
    docs_okf = fx.docs / "okf"
    (docs_okf / "concepts" / "old-group").mkdir(parents=True)
    stale = docs_okf / "concepts" / "old-group" / "stale.md"
    stale.write_text("stale\n", encoding="utf-8")
    hand = docs_okf / "index.md"
    before = hand.read_bytes()

    copied, unchanged, removed, problems = so.stage(fx.okf, fx.docs)
    assert problems == []
    assert copied == 7 and unchanged == 0 and removed == 1
    assert not stale.exists() and not stale.parent.exists()
    assert hand.read_bytes() == before  # the hand-written docs/okf/index.md is never touched
    assert (docs_okf / "concepts" / "geometry" / "fractal.md").read_bytes() == (fx.okf / "concepts" / "geometry" / "fractal.md").read_bytes()
    assert (docs_okf / "proofs" / "log.md").is_file()

    # second run is a no-op
    assert so.stage(fx.okf, fx.docs) == (0, 7, 0, [])

    # --check reports drift without writing
    (fx.okf / "proofs" / "p1.md").write_text("changed\n", encoding="utf-8")
    copied, unchanged, removed, problems = so.stage(fx.okf, fx.docs, check=True)
    assert copied == 1 and any("okf/proofs/p1.md: differs" in p for p in problems)
    assert (docs_okf / "proofs" / "p1.md").read_text(encoding="utf-8") != "changed\n"


def test_cli(fx, capsys):
    assert so.main(["--okf", str(fx.okf), "--docs", str(fx.docs)]) == 0
    assert "copied 7" in capsys.readouterr().out
    assert so.main(["--okf", str(fx.okf), "--docs", str(fx.docs), "--check"]) == 0
    assert so.main(["--okf", str(fx.root / "nowhere"), "--docs", str(fx.docs)]) == 1
