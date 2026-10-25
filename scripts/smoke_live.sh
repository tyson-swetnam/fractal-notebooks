#!/usr/bin/env bash
# Post-deploy smoke test for https://tyson-swetnam.github.io/fractal-notebooks (~25 requests).
# Run by the `verify` job after `deploy-pages`, or by hand:  bash scripts/smoke_live.sh [BASE_URL]
# Exit 1 on the first group of failures; prints one line per check.
set -uo pipefail

BASE="${1:-${BASE:-https://tyson-swetnam.github.io/fractal-notebooks}}"
BASE="${BASE%/}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# --retry-all-errors also retries HTTP 404/5xx, which Pages serves for a short while right after a deploy.
CURL=(curl -sS -L --max-time 30 --retry 3 --retry-delay 5 --retry-all-errors)
fail=0
pass=0

status() {  # status URL -> http code
  "${CURL[@]}" -o /dev/null -w '%{http_code}' "$1" 2>/dev/null || echo 000
}
header() {  # header URL name -> lowercase value
  "${CURL[@]}" -I "$1" 2>/dev/null | tr -d '\r' | awk -v k="$2" 'BEGIN{IGNORECASE=1} tolower($1)==tolower(k)":" {sub(/^[^:]*: */,""); print tolower($0)}' | tail -1
}
check() {  # check description condition...
  local desc="$1"; shift
  if "$@"; then echo "ok   $desc"; pass=$((pass+1)); else echo "FAIL $desc"; fail=$((fail+1)); fi
}
is200() { [ "$(status "$1")" = "200" ]; }
body_has() {  # read the whole body first: `grep -q` exiting early makes curl fail with SIGPIPE under pipefail
  local body; body="$("${CURL[@]}" "$1" 2>/dev/null)" || return 1
  grep -q -- "$2" <<<"$body"
}
body_count_ge() { [ "$("${CURL[@]}" "$1" 2>/dev/null | grep -c -- "$2")" -ge "$3" ]; }
ctype_is() { case "$(header "$1" content-type)" in *"$2"*) return 0;; *) return 1;; esac; }
is200_ctype() { is200 "$1" && ctype_is "$1" "$2"; }

echo "smoke_live: $BASE"

# Bounded wait (max ~2 min) for the deploy to propagate: poll llms.txt (no curl retries here) until it answers 200.
for attempt in $(seq 1 12); do
  code="$(curl -sS -L --max-time 20 -o /dev/null -w '%{http_code}' "$BASE/llms.txt" 2>/dev/null || echo 000)"
  [ "$code" = "200" ] && break
  echo "wait $BASE/llms.txt -> $code (attempt $attempt/12)"; sleep 10
done

# Home and one page per tab
for p in "" "foundations/" "foundations/history/" "metabolic-scaling/" "spectral-geometry/abstract/" \
         "notebooks/" "applications/" "okf/" "fractal-rag/" "agents/" "log/"; do
  check "GET /$p -> 200" is200 "$BASE/$p"
done

# Three notebook pages + a twin
for p in "notebooks/foundations/1_history/" "notebooks/metabolic-scaling/methods/1_mst_allometry/" "fractal-rag/notebooks/01_quickstart/"; do
  check "GET /$p -> 200" is200 "$BASE/$p"
done
check "notebook twin /notebooks/foundations/1_history.md -> 200" is200 "$BASE/notebooks/foundations/1_history.md"
# First figure of the committed Chapter 1 notebook page (render_notebooks.py names them <stem>_<cell>_<n>.png);
# read it from the page so a re-render cannot leave this check pointing at a stale name.
IMG="$(grep -o -m1 '1_history_files/[A-Za-z0-9_.-]*\.png' "$ROOT/docs/notebooks/foundations/1_history.md" 2>/dev/null || true)"
IMG="${IMG:-1_history_files/1_history_3_1.png}"
check "notebook image published ($IMG)" is200 "$BASE/notebooks/foundations/$IMG"

# Agent surface
check "llms.txt -> 200 text/plain" is200_ctype "$BASE/llms.txt" text/plain
check "llms.txt has entries" body_count_ge "$BASE/llms.txt" '^- \[' 60
check "llms-full.txt -> 200" is200 "$BASE/llms-full.txt"
check "robots.txt -> 200" is200 "$BASE/robots.txt"
check "sitemap.xml lists >= 100 URLs" body_count_ge "$BASE/sitemap.xml" '<loc>' 100
check "okf/concepts/index.md twin is text/markdown" ctype_is "$BASE/okf/concepts/index.md" markdown
check "okf/concepts/index.md starts with okf_version 0.2" body_has "$BASE/okf/concepts/index.md" 'okf_version: "0.2"'
check "proof twin -> 200 text/markdown" is200_ctype "$BASE/okf/proofs/cantor-set-dimension.md" markdown
check "landing twin /metabolic-scaling/index.md -> 200" is200 "$BASE/metabolic-scaling/index.md"
check "home twin /index.md -> 200" is200 "$BASE/index.md"
check "page head declares text/markdown alternate" body_has "$BASE/foundations/history/" 'rel="alternate" type="text/markdown"'

# React app and a redirect stub
check "GET /react/ -> 200" is200 "$BASE/react/"
check "/introduction/ stub -> metabolic-scaling/introduction" body_has "$BASE/introduction/" 'metabolic-scaling/introduction/'
# Stubs use relative destinations (../../../../../research/#3dep-canopy-height-models)
check "/notebooks/3dep/modified/sites/harvard_forest/chm_harvard_forest/ stub -> research" body_has "$BASE/notebooks/3dep/modified/sites/harvard_forest/chm_harvard_forest/" 'research/#3dep-canopy-height-models'

echo "smoke_live: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
