# Solver Regression Postmortem

## What happened
The latest solver rewrite changed more than Decimal precision. It also changed the DP problem definition and cache/search semantics, so current outputs no longer match the previously verified policy artifacts.

## Observable symptom
Running current `optimalValueFunc.py` for `t=10` produces root values that diverge from the stored policy files:

- `n=3`: stored `2.50000`, computed `3.166666667`
- `n=4`: stored `3.00000`, computed `3.416666667`
- `n=5`: stored `3.26667`, computed `3.583333334`
- `n=6`: stored `3.63335`, computed `3.900000000`

## Root causes
1. **Objective/semantics drift**
   - The code no longer removes used guesses across recursion (legacy behavior relied on `possible_guesses` dynamics).
   - The current base cases enforce explicit final-guess cost (`state_size == 1 -> 1`), so expected values increase under the new recurrence.

2. **Finite-horizon approximation became behaviorally significant**
   - Current value recursion is solved with horizon guard (`t == 0` and `t == 1` failure cases), which interacts with self-loop-prone branches and changes value compared with prior artifacts.

3. **Regression gate intent was violated by semantic changes**
   - `plan.md` requires parity-first changes for phase 1, but the solver changed recurrence semantics before parity was maintained.

## Why this looked like a “precision-only” PR
Although the PR title mentioned Decimal precision, the commit included substantial rewrites to `optimalValueFunc.py` plus planning/docs changes, so behavior changed materially.

## Immediate corrective action
- Treat current solver outputs as solving a different model than `policies/tree3..tree6`.
- Before further optimization, decide and freeze one objective definition, then enforce regression checks against that definition.


## Research note: why hand math gives 2.5 for n=3
For `n=3`, the answer space has 6 permutations of `012`. If first guess is `012`, partitions are:

- `(0,0,3)`: 1 answer (immediate win)
- `(0,2,1)`: 3 answers
- `(0,3,0)`: 2 answers

Under the **legacy artifact semantics** (the one used by stored `tree3.json`), the branch values are:

- `V({single}) = 0` when the secret is already identified by elimination and no explicit confirmation guess is charged.
- `V(size 2) = 1`
- `V(size 3) = 2`

So the root value is:

`1 + (1/6)*0 + (3/6)*2 + (2/6)*1 = 2.5`.

This exactly matches `policies/tree3.json`.

Under the **new semantics implemented in current solver**, singleton is charged as `1` (`state_size == 1 -> 1`), meaning an explicit final confirmation guess is always counted. The same branch structure therefore shifts upward, and root value becomes `3.166666667` in current code.

So the discrepancy is not your math error; it is a **model-definition mismatch**:

- Stored policies are from one terminal-cost convention.
- Current solver is using another terminal-cost convention.

Once the terminal objective is fixed and applied consistently, both hand derivation and code align.

## Subtlety to preserve (singleton is not one case)
When the candidate state shrinks to size 1, there are two semantically different situations that must not be conflated:

1. **Guessed-correct singleton (win already happened):**
   - The current step's guess produced `(0,0,3)` and the game is already won.
   - Continuation cost must be `0` from that branch.

2. **Elimination singleton (one candidate left but not yet typed):**
   - The state collapsed to one candidate via information elimination.
   - One additional explicit guess is still required, so continuation cost is `1`.

The legacy solver captured this distinction indirectly through action-history (`remove_guess` / guessed-availability context). The refactor removed that history dimension and then applied a single singleton rule (`state_size==1 -> 1`), which erased the distinction and inflated values.

## Suggested fix
Use a **win-aware transition model** that keeps a constant action set (for better caching) while preserving terminal semantics:

- Keep state key as `(canonical_state, t)` (or bitmask equivalent).
- In the Bellman loop, handle each response branch as:
  - if `response == (0,0,3)`: add probability * `0` directly (do not recurse);
  - else recurse on child state.
- Base case for `|S|==1` should represent the elimination case (`1`) because guessed-correct case is already absorbed at transition time.

This preserves your intended objective (“count actual guesses typed to win”), avoids reintroducing full `possible_guesses` into cache keys, and recovers the `n=3` style accounting subtlety.
