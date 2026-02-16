# Coding Skills Reference

This file lists practical skills/workflows to apply while coding in this repo.

## 1) DP correctness verification
- Re-derive recurrence independently before trusting implementation output.
- Validate Bellman equations by recomputing expected child-value aggregation at each policy node.
- Cross-check small-`n` cases with exhaustive search.

## 2) State-space optimization
- Prefer compact state representation (bitsets) over set-of-strings in hot paths.
- Use deterministic canonicalization to collapse symmetry-equivalent states.
- Keep cache keys minimal but semantically complete for the chosen recurrence.

## 3) Performance engineering
- Precompute stable tables used repeatedly in inner loops (e.g., guess/answer responses).
- Add pruning for non-progress branches and terminate weak candidates early.
- Measure both micro-benchmarks (operation-level) and end-to-end runtime.

## 4) Reproducibility and determinism
- Ensure deterministic ordering for tie handling and artifact generation.
- Keep policy serialization structure stable (`best_guess`, `value`, `response`).

## 5) Refactor readability discipline
- Keep helpers small and name data by role (`state_mask`, `response_masks`, `best_guess_obj`).
- Keep control flow explicit and comment correctness assumptions near cache/pruning logic.
- Preserve the repository’s coding voice and simple module structure.

## 6) Validation workflow before merge
- Run structural policy checks (reachable edges, value consistency, terminal behavior).
- Compare reported policy value vs independently computed baseline on tractable `n`.
- Record limitations clearly when full exhaustive verification is not yet computationally feasible.


## 7) Tree-regeneration regression workflow (mandatory)
- After each solver change, regenerate policies for `n=3..6`.
- Compare against known-correct `tree3..tree6` artifacts.
- If generated guess order differs, treat as possible tie-case and run diagnostics rather than failing immediately.
- Tie-case diagnostics:
  - verify equal node value,
  - verify Bellman consistency,
  - verify no root-value regression.
- Fail only when value-equivalence or consistency fails.
