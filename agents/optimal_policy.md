# Optimal Policy Notes: Wordle Papers vs. `optimalValueFunc.py`

## 1) What the context papers say about optimality in Wordle

### Paper 1: `context/wordle_paper.txt` (Bertsimas & Paskov)
- The paper explicitly frames Wordle as a finite-state MDP and claims a **certifiably optimal** policy via **Exact Dynamic Programming** with a Bellman equation (not a heuristic search).【F:context/wordle_paper.txt†L7-L8】【F:context/wordle_paper.txt†L31-L34】
- Their optimality claim is tied to *no approximation* in the core solve, and they discuss tractability improvements as optimizations layered on top of exact DP logic.【F:context/wordle_paper.txt†L20-L24】
- They report concrete optimal-policy outcomes: SALET as best first word, max 5 guesses to solve all hidden words, and 3.421 average guesses from SALET.【F:context/wordle_paper.txt†L7-L7】【F:context/wordle_paper.txt†L36-L37】
- They also emphasize interpretability by turning policy structure into readable trees (OCT with hyperplanes), but the optimality itself is anchored in DP over the exact game model.【F:context/wordle_paper.txt†L7-L7】【F:context/wordle_paper.txt†L37-L38】

### Paper 2: `context/sonorous_paper.txt` (Alex Selby post)
- This write-up reports **exhaustive-search** evaluations and states these are proved optimal for average number of guesses over the hidden-word set.【F:context/sonorous_paper.txt†L63-L65】
- It compares easy vs hard mode first-word rankings and averages (e.g., SALET/TARSE era-dependent results), again based on exhaustive optimization objective rather than one-step heuristics.【F:context/sonorous_paper.txt†L56-L63】
- It distinguishes strict optimal play from human-friendly approximations/rules-of-thumb, indicating the optimal engine can also support post-hoc skill/luck analysis.【F:context/sonorous_paper.txt†L70-L76】【F:context/sonorous_paper.txt†L101-L101】

## 2) How your PFB code tries to find optimality

Your `optimalValueFunc.py` follows the same broad DP structure as those Wordle approaches:

- **State representation:** remaining feasible answers (`state`), initialized as all non-repeating 3-digit strings over a chosen digit range `n`.【F:optimalValueFunc.py†L13-L23】【F:optimalValueFunc.py†L25-L29】
- **Transition model:** for each guess, partition current state by response pattern via `possible_future_states` using exact response logic (`computeResponse`).【F:optimalValueFunc.py†L33-L45】【F:optimalValueFunc.py†L73-L99】
- **Objective style:** expected future cost is computed as probability-weighted child values plus 1 for the current guess, and the minimizing guess is selected in `find_best_guess`.【F:optimalValueFunc.py†L244-L271】
- **DP + memoization:** `value_of` caches solved subproblems keyed by state and remaining horizon `t`.【F:optimalValueFunc.py†L204-L216】
- **Branch-and-bound flavor:** it computes lower bounds per response branch and can early-break a guess evaluation if current lower-bound sum already exceeds best known value.【F:optimalValueFunc.py†L113-L117】【F:optimalValueFunc.py†L237-L263】
- **Policy artifact export:** it serializes a computed policy tree to pickle/json under `policies/` after key-stringification for JSON compatibility.【F:optimalValueFunc.py†L307-L315】

So conceptually: yes, this is an exact-belief-state DP skeleton for PFB, very much in the spirit of “optimal average guesses” methods used in Wordle.

## 3) Potential correctness issues in `optimalValueFunc.py`

### A. **Memoization key likely incomplete (high risk)**
- Cache key is only `(frozenset(state), t)`.【F:optimalValueFunc.py†L205-L206】
- But recurrence also depends on `possible_guesses` because:
  - you explicitly remove used guesses (`remove_guess`) before recursing,【F:optimalValueFunc.py†L118-L123】【F:optimalValueFunc.py†L248-L252】
  - base-case value for `len(state)==1` depends on whether solution is in `possible_guesses`.【F:optimalValueFunc.py†L187-L200】
- Therefore, same `(state, t)` reached with different remaining-guess sets can have different optimal value/policy, but cache would conflate them.

**Impact:** can return wrong values/policies in deeper tree regions.

### B. **Nondeterministic tie behavior from set-to-list conversion (medium risk)**
- Multiple places choose `list(state)[0]` for fallback/base returns.【F:optimalValueFunc.py†L148-L151】【F:optimalValueFunc.py†L186-L187】
- `state` is often a set/frozenset; iteration order is not stable across runs.

**Impact:** policy artifacts can vary run-to-run for ties, making reproducibility and diffing harder; in some branches this can alter chosen fallback action.

### C. **Solver currently runs only reduced game at module import (scope correctness risk)**
- Bottom-of-file execution sets `cur_solve = 4` and immediately writes `policies/tree4.*`.【F:optimalValueFunc.py†L302-L315】
- That means this script, as written, solves only digits `{0,1,2,3}` space by default, not full 0–9 PFB.

**Impact:** if interpreted as “the full optimal policy generator,” outputs are only for a reduced variant unless manually changed.

### D. **Hardcoded pruning cap may bias results if reused broadly (medium risk)**
- Top-level call uses `g.value_of(10, max_val=Decimal("5.1"))`.【F:optimalValueFunc.py†L309-L309】
- `max_val` seeds incumbent best value for pruning in `find_best_guess`.【F:optimalValueFunc.py†L219-L222】【F:optimalValueFunc.py†L261-L269】

**Impact:** if true optimum exceeds this seed in a different configuration, pruning assumptions/behavior may become unsafe or distort search effort. (Could be fine for known bounded subproblem, but fragile as a general default.)

### E. **No explicit terminal guard for empty state (low-to-medium risk)**
- There is no dedicated `len(state)==0` handling in `value_of`.【F:optimalValueFunc.py†L125-L217】
- Logic likely avoids this under consistent response partitions, but defensive handling would improve robustness against inconsistent input/policy corruption.

**Impact:** potential crash or undefined behavior in edge/integrity-failure scenarios.

## 4) Bottom line

- Your approach is structurally aligned with the “exact DP over belief states” idea behind optimal Wordle solvers.
- With the updated design decision (remove `remove_guess`, keep action set constant), cache-key incompleteness from `possible_guesses` no longer applies.
- Next most important for reliability are deterministic tie-handling, strong pruning for non-informative repeats, and making solver configuration/entrypoint explicit (reduced-vs-full game and pruning assumptions).


## 5) Update to implementation direction

Project direction has changed:
- We will **not** include `possible_guesses` in the cache key.
- Instead, we will remove `remove_guess` so available actions remain constant over the solve.
- In that formulation, recursion depth is still bounded by `t -> t-1`, so recursion cannot be infinite by itself.
- Practical risk is not infinite recursion but wasted compute from self-loop / low-information repeat guesses, so explicit pruning for non-progress branches should be added.


## 6) Updated implementation plan with bitset + canonicalization

- Keep constant action availability (no `remove_guess`) and cache by horizon + state.
- Move state representation from set-of-strings to indexed bitsets.
- Add deterministic canonicalization (digit relabeling symmetry) and cache by canonical state.
- On cache reuse, remap canonical guesses back to caller-local digit labels.
- Keep response tuples unchanged across relabeling, so response-edge semantics remain stable.
- Combine with response-table precompute + non-progress pruning for practical n=10 runtime.
