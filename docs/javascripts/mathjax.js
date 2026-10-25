// MathJax 3 configuration for Zensical (Material theme) with pymdownx.arithmatex
// (generic mode). Only elements with class "arithmatex" are typeset; `$...$`
// delimiters work because arithmatex converts them to \( ... \) at build time.
window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"]],
    displayMath: [["\\[", "\\]"]],
    processEscapes: true,
    processEnvironments: true
  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex"
  }
};

// Re-typeset after every page load, including instant navigation (document$ is
// the theme's page observable), so math survives client-side page swaps.
document$.subscribe(() => {
  MathJax.startup.output.clearCache()
  MathJax.typesetClear()
  MathJax.texReset()
  MathJax.typesetPromise()
})

// Code annotations are mounted lazily into tooltips, so math inside them is
// typeset when the annotation component appears (Zensical math recipe).
component$.subscribe(({ ref }) => {
  if (ref.classList.contains("md-annotation"))
    MathJax.typesetPromise([ref])
})
