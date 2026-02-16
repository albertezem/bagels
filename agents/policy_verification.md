# Independent Policy Verification Notes

## Scope
Policies found in `policies/`:
- `tree3.json`
- `tree4.json`
- `tree5.json`
- `tree6.json`
- `tree10.json` (currently empty)

## Verification method A (independent exhaustive solve on tractable sizes)
I implemented an independent bitmask-based finite-horizon DP verifier (horizon = 10, guess-removal semantics) and solved root states for:
- `n=3` -> value `2.5`
- `n=4` -> value `3.0`

These exactly match policy roots in repository artifacts:
- `tree3.json` root value `2.50000`
- `tree4.json` root value `3.00000`

## Verification method B (policy-structure Bellman consistency)
For `tree3.json`, `tree4.json`, `tree5.json`, and `tree6.json`:
- Parsed policy trees and reconstructed reachable states from path constraints.
- Recomputed expected value at each visited node as:
  - `1 + sum_r P(r | state, best_guess) * child_value(r)`
- Checked edge reachability for response transitions.

Result:
- No consistency issues found in `tree3`, `tree4`, `tree5`, `tree6` under this check.

## Findings
- `tree3` and `tree4` are independently verified optimal at root under the verified recurrence.
- `tree5` and `tree6` are internally Bellman-consistent with no unreachable edge issues in the stored policy tree.
- Full independent exhaustive optimality proof for `n=5` and `n=6` root (under guess-removal horizon-10 recurrence) was started but is computationally heavy in this environment; not yet completed end-to-end.
- `tree10.json` is empty (0 bytes), so there is no policy there to verify.

## Next step to complete full proof for n=5/6
- Run canonicalized/optimized independent verifier to completion for `n=5` and `n=6` root values and compare against `tree5`/`tree6` roots.
