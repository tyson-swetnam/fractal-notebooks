/**
 * Minimal stochastic L-system (Lindenmayer system) rewriter.
 *
 * L-systems are the canonical formalism for modelling plant development
 * (Lindenmayer 1968; Prusinkiewicz & Lindenmayer, "The Algorithmic Beauty of
 * Plants", 1990). A string of module symbols is rewritten in parallel by a set
 * of production rules; a turtle then interprets the final string as geometry.
 *
 * Symbols with no production rule (turtle commands such as F + - & ^ / \ [ ] !
 * > <) pass through unchanged. Rules may be deterministic (one successor) or
 * stochastic (a list of successors with probabilities that should sum to ~1).
 */

export type Production = string | { successor: string; probability: number }[];

export interface LSystemSpec {
  axiom: string;
  rules: Record<string, Production>;
  iterations: number;
}

/** Deterministic, seedable RNG (mulberry32) so a seed reproduces a plant. */
export function makeRng(seed: number): () => number {
  let a = seed >>> 0;
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Pick a stochastic successor using the supplied RNG. */
function chooseSuccessor(options: { successor: string; probability: number }[], rng: () => number): string {
  const r = rng();
  let cumulative = 0;
  for (const opt of options) {
    cumulative += opt.probability;
    if (r <= cumulative) return opt.successor;
  }
  return options[options.length - 1].successor;
}

/**
 * Rewrite the axiom for `iterations` generations. `maxLength` guards against
 * exponential blow-up; expansion stops early once the string exceeds it.
 */
export function rewrite(spec: LSystemSpec, rng: () => number, maxLength = 2_000_000): string {
  let current = spec.axiom;

  for (let gen = 0; gen < spec.iterations; gen++) {
    let next = '';
    for (const symbol of current) {
      const rule = spec.rules[symbol];
      if (rule === undefined) {
        next += symbol;
      } else if (typeof rule === 'string') {
        next += rule;
      } else {
        next += chooseSuccessor(rule, rng);
      }
    }
    current = next;
    if (current.length > maxLength) break;
  }

  return current;
}
