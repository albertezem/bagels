# Repository Summary

_Last updated: initial baseline summary._

## Purpose
This repository implements a **Pico/Fermi/Bagels** game environment with multiple guesser strategies and tooling for experiments around information theory, minimax, reinforcement learning, and precomputed optimal policies.

## Core Gameplay Model
- `Game` in `game.py` runs turn-by-turn interaction between a guesser and responder until a win response (`"You win!"`) or guess limit.
- Answers are 3-digit values with no repeated digits.
- Responses are encoded as Bagels/Pico/Fermi strings.

## Main User Entry Point
- `app.py` provides an interactive CLI menu for:
  - human guessing mode,
  - human responder mode vs bots,
  - training mode,
  - bot battle mode,
  - human and bot performance evaluation.

## Guesser Implementations
- `HumanGuesser`: manual guesses with input validation.
- `IntelligentGuesser`: entropy / expected information strategy.
- `MinimaxGuesser`: minimizes largest remaining candidate partition.
- `SimpleGuesser`: picks first remaining candidate.
- `HelpfulGuesser` (`guesserBots/`): coaching mode that estimates information lost/luck.
- `PerfectGuesser` (`guesserBots/`): follows precomputed policy trees.
- `MCGuesser` (`rl/`): Monte Carlo-style RL guesser with epsilon-greedy exploration.

## Responder Implementations
- `ComputerResponder`: random valid answer.
- `DeterministicResponder`: fixed provided answer.

## Policy/Research Assets
- `optimalValueFunc.py` contains dynamic-programming style logic for computing optimal policies.
- `policies/` contains serialized trees (`.json`, `.pkl`) for different search depths/sizes.
- `context/` includes Wordle-related papers/text likely used as conceptual references.

## Notes / Observations
- `readme.md` references `interface.py`, while the observable runnable menu entrypoint in this repo is `app.py`.
- Some files show duplicated/reused logic patterns for response encoding/decoding and candidate filtering.

## Ongoing Update Log
- Initialized `agents/repo_summary.md` with baseline architecture summary.

## Runtime Validation Findings (app.py modes)
- Attempting to run `python app.py` in this environment fails immediately due to missing `numpy` import in `rl/MCGuesser.py` (imported transitively by `game.py`), before any menu interaction.
- For runtime exploration, a temporary in-memory `numpy` shim (`zeros`, `argmin`, `std`) was injected in a one-off harness so app modes could be exercised without editing source files.

### Mode-by-mode observations
- **Mode 1 (Play as guesser):** Works interactively; game continues indefinitely until guessed, so scripted finite input exhausts.
- **Mode 2 (Play as responder vs bot):** Works; with deterministic answer `012`, Entropy bot guessed `012` immediately.
- **Mode 3 (Training mode):** HelpfulGuesser prints per-guess information-loss and luck diagnostics as expected.
- **Mode 4 (Battle vs AI):** Works; alternates bot and human rounds, and can run long if user input is exhausted mid-match.
- **Mode 5 (Evaluate human skill):** Requires substantial ongoing human input (10 games), so scripted short input exhausts quickly.
- **Mode 6 (Evaluate bot skill):** Works; for Simple bot over all 720 answers, summary showed mean `5.2667`, max `9`, min `1`, std `1.2207`.
- **Mode 7 (Quit):** Clean exit.

### Additional interesting notes
- The menu prompt string has a typo: `Wh3at do you want to do?`.
- Mode 6 prints a very large full dictionary of per-answer results before summary stats (high verbosity in normal runs).

## Ongoing Update Log
- Added runtime validation notes after exercising all app menu modes using a non-invasive runtime harness.
- Added `agents/optimal_policy.md` with a crosswalk between Wordle optimality references and `optimalValueFunc.py`, including potential correctness risks (cache key dependence, determinism, solver scope/config).

- Updated `agents.md` with an additional objective to refactor solver code for outsider readability while preserving repository coding style.

- Updated planning docs to reflect new solver direction: do not add `possible_guesses` to cache keys; remove `remove_guess` and rely on bounded-depth recursion plus repeat-guess pruning for runtime control.

- Updated planning docs with the new execution plan: constant action set, bitset states, canonicalized cache states, response-table precompute, and explicit self-loop pruning.

- Moved detailed execution plan out of `agents.md` into `plan.md`; `agents.md` now remains high-level/invariant guidance.

- Added `skill.md` with coding-skill workflows and added `agents/policy_verification.md` documenting independent policy verification status (exact for n=3/4, structural consistency for n=3..6, tree10 empty).

- Added a mandatory regression gate: after every solver change, regenerate `tree3..tree6` and enforce value-equivalence; if guess differs under ties, run extra diagnostics before accepting.

- Continued solver phases with parity-gated optimizations: added deterministic state bitset/canonicalization helpers and precomputed response table usage in partitioning; regression checks on n=3..5 preserved root values (n=5 tie-case root guess changed but equal value and equal root child values).

- Continued optimization work: reduced repeated work in `find_best_guess` by moving `remove_guess` outside response loop and replacing repeated `sum(lower_bounds)` with incremental running bound accumulation; parity checks on n=3..5 preserved root values and root child diagnostics.

- Implemented major optimization pass in `optimalValueFunc.py`: bitmask state transitions + canonicalized cache reuse + precomputed response masks. Re-tested n=6 with a 10-minute timeout and it still timed out in this environment (status 124, wall ~601s), indicating more optimization is still needed.

- Added `agents/solver_regression_postmortem.md` documenting why current solver values diverged from `tree3..tree6` (objective drift + horizon/semantics change + parity-gate violation).

- Expanded solver postmortem with an n=3 derivation showing why legacy artifacts produce 2.5 while current terminal-cost semantics produce a higher value; documented this as objective mismatch rather than arithmetic error.

- Documented singleton-terminal subtlety in `agents/solver_regression_postmortem.md` (guessed-correct singleton => 0 vs elimination singleton => 1) and proposed a win-aware branch fix that treats `(0,0,3)` as an absorbed zero-cost transition while keeping constant action-set caching.
