from pprint import pprint
import pickle
import json
from decimal import Decimal, getcontext
from stringify import stringify_keys


# This is the file containing the necessary logic to find the
# optimal policy for a game of Pico Fermi Bagels

getcontext().prec = 10


def initializePossibleAnswers(n=10):
    possible = set()

    for i in range(0, n):
        for j in range(0, n):
            for k in range(0, n):
                if i != j and j != k and i != k:
                    possible.add(str(i) + str(j) + str(k))

    return possible


class OptimalGame:
    def __init__(self, possible_guesses=initializePossibleAnswers()) -> None:
        self.possible_guesses = tuple(sorted(possible_guesses))
        self.possible_answers = tuple(sorted(possible_guesses))

        self.answer_index = self.possible_answers
        self.answer_to_idx = {
            answer: idx for idx, answer in enumerate(self.answer_index)
        }

        self.digits = sorted({digit for answer in self.answer_index for digit in answer})

        self.responses = [
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 1),
            (0, 2, 0),
            (0, 1, 1),
            (0, 0, 2),
            (0, 3, 0),
            (0, 2, 1),
            (0, 0, 3),
        ]
        self.win_response = (0, 0, 3)

        self.response_to_idx = {response: idx for idx, response in enumerate(self.responses)}

        self.value_cache = {}
        self.best_action_cache = {}
        self.canonical_cache = {}

        self.response_masks = [
            [0 for _ in self.responses] for _ in range(len(self.possible_guesses))
        ]

        for answer_idx, answer in enumerate(self.answer_index):
            bit = 1 << answer_idx
            for guess_idx, guess in enumerate(self.possible_guesses):
                response = self.computeResponse(guess, answer)
                response_idx = self.response_to_idx[response]
                self.response_masks[guess_idx][response_idx] |= bit

        self.full_state_mask = (1 << len(self.answer_index)) - 1

    def computeResponse(self, guess, answer):
        clues = [0, 0, 0]

        for i in range(3):
            if guess[i] == answer[i]:
                clues[2] += 1
            elif guess[i] in answer:
                clues[1] += 1

        if clues == [0, 0, 0]:
            clues[0] += 1

        return tuple(clues)

    def mask_to_state(self, state_mask):
        state = []
        mask = state_mask
        while mask:
            bit = mask & -mask
            idx = bit.bit_length() - 1
            state.append(self.answer_index[idx])
            mask ^= bit

        return tuple(state)

    def canonicalize_mask(self, state_mask):
        cached = self.canonical_cache.get(state_mask)
        if cached is not None:
            return cached

        old_to_new = {}
        new_to_old = {}
        next_digit = 0

        canonical_state = []
        mask = state_mask

        while mask:
            bit = mask & -mask
            idx = bit.bit_length() - 1
            answer = self.answer_index[idx]

            canonical_answer = []
            for digit in answer:
                if digit not in old_to_new:
                    mapped = str(next_digit)
                    old_to_new[digit] = mapped
                    new_to_old[mapped] = digit
                    next_digit += 1
                canonical_answer.append(old_to_new[digit])

            canonical_state.append("".join(canonical_answer))
            mask ^= bit

        for digit in self.digits:
            if digit not in old_to_new:
                mapped = str(next_digit)
                old_to_new[digit] = mapped
                new_to_old[mapped] = digit
                next_digit += 1

        result = (tuple(canonical_state), old_to_new, new_to_old)
        self.canonical_cache[state_mask] = result
        return result

    def remap_guess(self, guess, mapping):
        return "".join(mapping[digit] for digit in guess)

    def ordered_guess_indices(self, state_mask):
        in_state = []
        mask = state_mask
        while mask:
            bit = mask & -mask
            in_state.append(bit.bit_length() - 1)
            mask ^= bit

        in_state_set = set(in_state)
        out_state = [idx for idx in range(len(self.possible_guesses)) if idx not in in_state_set]

        return in_state + out_state

    # t = guesses remaining
    def value_of(self, t, state_mask=None, max_val=Decimal("Infinity")):
        if state_mask is None:
            state_mask = self.full_state_mask

        state_size = state_mask.bit_count()

        if t == 0:
            return Decimal("Infinity")

        if t == 1 and state_size > 1:
            return Decimal("Infinity")

        if state_size == 1:
            return Decimal("1")

        canonical_state, old_to_new, _ = self.canonicalize_mask(state_mask)
        cache_key = (canonical_state, t)

        cached_value = self.value_cache.get(cache_key)
        if cached_value is not None:
            return cached_value

        best_value = max_val
        best_guess = None
        state_size_decimal = Decimal(state_size)

        for guess_idx in self.ordered_guess_indices(state_mask):
            guess_masks = self.response_masks[guess_idx]

            # prune non-informative guesses that can only self-loop
            informative = False
            for response_idx in range(len(self.responses)):
                future_state_mask = state_mask & guess_masks[response_idx]
                if future_state_mask != 0 and future_state_mask != state_mask:
                    informative = True
                    break
            if not informative:
                continue

            expected_value = Decimal("1")
            pruned = False

            for response_idx in range(len(self.responses)):
                response = self.responses[response_idx]
                future_state_mask = state_mask & guess_masks[response_idx]
                if future_state_mask == 0:
                    continue

                count = future_state_mask.bit_count()
                probability = Decimal(count) / state_size_decimal

                if response == self.win_response:
                    future_val = Decimal("0")
                else:
                    future_val = self.value_of(t - 1, future_state_mask, best_value)
                expected_value += probability * future_val

                if expected_value >= best_value:
                    pruned = True
                    break

            if pruned:
                continue

            if expected_value < best_value:
                best_value = expected_value
                best_guess = self.possible_guesses[guess_idx]

        if best_guess is None:
            best_guess = self.answer_index[0]

        self.value_cache[cache_key] = best_value
        self.best_action_cache[cache_key] = self.remap_guess(best_guess, old_to_new)

        return best_value

    def build_policy(self, t, state_mask=None):
        if state_mask is None:
            state_mask = self.full_state_mask

        state_size = state_mask.bit_count()

        if t == 0:
            return {
                "best_guess": self.answer_index[0],
                "value": Decimal("Infinity"),
                "response": {},
            }

        if t == 1 and state_size > 1:
            state = self.mask_to_state(state_mask)
            return {
                "best_guess": state[0],
                "value": Decimal("Infinity"),
                "response": {},
            }

        if state_size == 1:
            state = self.mask_to_state(state_mask)
            answer = state[0]

            return {
                "best_guess": answer,
                "value": Decimal("1"),
                "response": {
                    (0, 0, 3): {
                        "best_guess": answer,
                        "value": Decimal("0"),
                        "response": {},
                    }
                },
            }

        canonical_state, _, new_to_old = self.canonicalize_mask(state_mask)
        cache_key = (canonical_state, t)

        value = self.value_cache.get(cache_key)
        if value is None:
            value = self.value_of(t, state_mask)

        canonical_guess = self.best_action_cache[cache_key]
        best_guess = self.remap_guess(canonical_guess, new_to_old)
        guess_idx = self.answer_to_idx[best_guess]

        node = {
            "best_guess": best_guess,
            "value": value,
            "response": {},
        }

        for response_idx, response in enumerate(self.responses):
            future_state_mask = state_mask & self.response_masks[guess_idx][response_idx]
            if future_state_mask == 0:
                continue

            if response == self.win_response:
                node["response"][response] = {
                    "best_guess": best_guess,
                    "value": Decimal("0"),
                    "response": {},
                }
                continue

            node["response"][response] = self.build_policy(t - 1, future_state_mask)

        return node


def write_policy(cur_solve=4, t=10, max_val=Decimal("5.1")):
    g = OptimalGame(possible_guesses=initializePossibleAnswers(cur_solve))

    with open("policies/tree" + str(cur_solve) + ".json", "w") as t_file:
        with open("policies/tree" + str(cur_solve) + ".pkl", "wb") as p_file:
            g.value_of(t, max_val=max_val)
            tree = g.build_policy(t)

            records = stringify_keys(tree)

            pickle.dump(tree, p_file)
            json.dump(records, t_file, indent=4)

    return records


def main():
    records = write_policy(cur_solve=4, t=10, max_val=Decimal("5.1"))
    pprint(records)


if __name__ == "__main__":
    main()
