# Project Objectives and Working Context

## Current understanding of this repository

This repo implements a Pico/Fermi/Bagels (PFB) environment with interactive gameplay and multiple guesser strategies:

- Core game loop and utilities live in `game.py`.
- CLI menu entrypoint is `app.py`.
- Baseline guessers (`HumanGuesser`, `IntelligentGuesser`, `MinimaxGuesser`, `SimpleGuesser`) are in `guesser.py`.
- Additional guessers and training helpers are in `guesserBots/`.
- Reinforcement-learning experiments are in `rl/`.
- Exact-policy generation attempts are in `optimalValueFunc.py`.
- Previously generated policy artifacts are in `policies/`.
- Research context material is in `context/`.

At a high level, this codebase explores multiple paradigms for solving PFB:
- heuristic/information-theoretic guessing,
- minimax-style guessing,
- RL experiments,
- dynamic-programming based exact policy search.

## Project objective for upcoming implementation work

Primary goal:
- Write an **algorithmically correct and optimized** version of `optimalValueFunc.py` that can compute the **optimal policy** for PFB at `n = 10` (digits `0` through `9`, no repeats).

Key technical direction (updated):
- Do **not** add `possible_guesses` to cache keys.
- Remove `remove_guess` so action availability remains constant across recursion.
- Keep cache keyed by state/horizon, and add pruning that avoids non-informative repeat guesses (self-loop branches) to protect runtime.

Secondary goals:
- Preserve the current conceptual paradigm (exact DP over belief states / feasible-answer sets).
- Improve runtime through principled optimization (memoization strategy, pruning, state canonicalization, and efficient transition handling).
- Refactor solver code so it is easier for outsiders to read and reason about while preserving the repo's general coding style.
- Keep output policy artifacts compatible with existing usage (`.json` / `.pkl` pipeline where appropriate).

## Style and implementation constraint

When implementing the revised solver:
- Match the coding style used in this repository.
- Prioritize readability for new/outsider contributors: clear structure, low-ambiguity naming, and understandable control flow.
- Even with wide internal improvements/refactors, final code should feel like it was authored in the same style and conventions as the existing codebase.


## Style and conventions to replicate from this repo

When refactoring `optimalValueFunc.py`, mirror the repo's existing style:

- Keep files as script-friendly modules with simple top-to-bottom flow.
- Prefer explicit loops and straightforward control flow over dense abstractions.
- Use small helper functions and class methods for major logical blocks.
- Keep naming plain and descriptive (e.g., `possible_answers`, `best_guess_obj`, `future_states`).
- Preserve light inline comments that explain intent and section purpose.
- Favor built-in Python containers (`dict`, `list`, `set`, `tuple`) and direct transformations.
- Keep type hints minimal (the repo mostly does not use strict typing across all files).
- Preserve current data-shape conventions for policy trees (`best_guess`, `value`, `response`).
- Keep serialization behavior compatible with current `.json` / `.pkl` outputs.
- Avoid introducing architectural patterns that feel foreign to the repo (heavy frameworks, deeply layered abstractions, or over-generalized utility stacks).

Readability conventions for outsider contributors:

- Make each decision step easy to follow (state -> actions -> transitions -> value aggregation).
- Prefer deterministic iteration where practical for reproducibility in generated artifacts.
- Keep optimization logic (memoization/pruning) explicit and local to solver flow.
- Add concise comments where correctness assumptions matter (cache keys, bounds, termination).
