# Solver Refactor Plan

## Goal
Implement an algorithmically correct, optimized, and outsider-readable `optimalValueFunc.py` that can practically target PFB with `n=10`.

## Phase 1: Correctness-preserving refactor
- Establish a **parity-first refactor path**: no semantic drift from currently verified `tree3..tree6` outputs.
- Refactor structure/readability first (helper extraction, clearer method boundaries, comments), while preserving recurrence behavior.
- Add explicit regression harness for `n=3..6` after each edit to catch any value drift immediately.
- Centralize response handling helpers only when it does not alter transition semantics.
- Keep tie behavior unchanged in this phase unless diagnostics prove equivalence at all affected nodes.
- Defer objective-shifting changes (e.g., constant-action objective semantics) until parity-preserving phase is complete and explicitly approved.

## Phase 2: State representation and symmetry reduction
- Represent states as bitsets over indexed candidate answers for faster set algebra and lower memory overhead.
- Introduce deterministic state canonicalization under digit relabeling symmetry.
- Cache by `(canonical_state, t)` to collapse equivalent states.
- Store/return guess selections with canonical-to-local remapping so external policy remains in caller digit labels.

## Phase 3: Transition speed and pruning
- Precompute guess/answer response table once and reuse across all DP calls.
- Build response partitions with bitset intersections instead of Python set-of-string filtering.
- Add explicit pruning for non-progress/self-loop repeat guesses.
- Tighten lower-bound pruning so weak branches terminate earlier.

## Phase 4: Validation and benchmarking
- Verify small-n outputs against previous solver behavior where appropriate.
- Add invariants: probability mass checks, terminal-state behavior, deterministic output checks.
- Benchmark at n=4/5/6 after each phase; project n=10 runtime after each optimization layer.
- Keep output format compatible with existing policy tree schema and `.json`/`.pkl` artifacts.


## Regression gate (required after every solver change)
- Re-run `optimalValueFunc.py` to regenerate policies for `n=3,4,5,6`.
- Confirm regenerated trees remain equivalent to existing known-correct outputs for `tree3`-`tree6`.
- Primary acceptance criterion is value/policy-equivalence; exact guess string may differ when ties exist.
- If a guess differs but value is equal, run extra diagnostics:
  - compare expected value at the differing node,
  - compare child-response partition values,
  - confirm no degradation in root value and downstream Bellman consistency.
- Any non-tie value regression is a blocker.
