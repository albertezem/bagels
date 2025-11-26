from pprint import pprint
import pickle
import json
from stringify import stringify_keys
from decimal import *

getcontext().prec = 6
getcontext().traps[FloatOperation] = True

# This is the file containing the necessary logic to find the 
# optimal policy for a game of Pico Fermi Bagels 

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
        self.possible_guesses = possible_guesses
        self.possible_answers = possible_guesses
        # self.table = self.generate_answer_table()

        self.cache = {}

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

    is_possible_answer = {}
    """
    def possible_future_states2(self, state, guess):  # O(len(state))

        possible_future_states = {}

        for possible_answer in state:

            response = self.computeResponse(guess, possible_answer)  # O(3)

            s_temp = set()

            for temp_solution in state:
                if self.table[guess][response][temp_solution]:
                    s_temp.add(temp_solution)

            s_temp = frozenset(s_temp)

            if s_temp not in possible_future_states:
                possible_future_states[s_temp] = 0

            possible_future_states[s_temp] += 1 / len(state)

        return possible_future_states
        """

    def possible_future_states(self, state, guess):  # O(len(state))
        # for possible_guess in self.possible_answers:

        possible_future_states = {}

        for possible_answer in state:
            # Determine the response of guess/answer pair
            # Add answer to respective pattern in pattern_proportions

            response = self.computeResponse(guess, possible_answer)  # O(3)

            if response not in possible_future_states:
                possible_future_states[response] = [set(), 0]

            possible_future_states[response][0].add(possible_answer)
            possible_future_states[response][1] += 1

        total = str(len(state))
        total = Decimal(total)
        for response in possible_future_states:
            count = str(possible_future_states[response][1])
            count = Decimal(count)

            possible_future_states[response][1] = count / total

        return possible_future_states

    # Returns the decision tree associated with the best guess + score
    def sorted_guesses(self, guesses, state):
        guesses_sorted = sorted(guesses, key=lambda x: (x not in state, x))

        return guesses_sorted

    def sorted_states(self, states, i=1):
        sorted_states = dict(
            sorted(states.items(), key=lambda x: x[1][i], reverse=True)
        )

        return sorted_states

    def lower_bound(self, state):
        l = len(state)
        l = Decimal(l)
        return (Decimal(2 * l) - 1) / l

    def remove_guess(self, possible_guesses, guess):
        new_possible_guesses = list(possible_guesses)
        new_possible_guesses.remove(guess)
        new_possible_guesses = tuple(new_possible_guesses)

        return new_possible_guesses

    # t = guesses used so far, max 7
    def value_of(
        self, t, f_str=None, possible_guesses=None, state=None, max_val=Decimal("Inf")
    ):
        # Used this to make sure my cache works
        if f_str:
            with open(f_str, "w") as f:
                records = [{"key": str(k), "value": str(v)} for k, v in g.cache.items()]

                json.dump(records, f, indent=2)

        # If state = None, then solve from beginning of tree with state = all possible answers
        if state == None:
            state = self.possible_answers

        # If guesses = None, then consider all available guesses
        if possible_guesses == None:
            possible_guesses = self.possible_guesses

        # If we have 1 guess left and more than 1 possible answer, we cannot solve in time
        if t == 1 and len(state) > 1:

            return {
                "best_guess": list(state)[0],
                "value": Decimal("Inf"),
                "response": {},
            }

        # If we only have 2 possible answers left
        elif t > 1 and len(state) == 2:
            state_list = list(state)
            alt_response = self.computeResponse(state_list[0], state_list[1])
            best_guess_obj = {
                "best_guess": state_list[0],
                "value": Decimal("1.5"),
                "response": {
                    (0, 0, 3): {
                        "best_guess": state_list[0],
                        "value": Decimal("0"),
                        "response": {},
                    },
                    alt_response: {
                        "best_guess": state_list[1],
                        "value": Decimal("1"),
                        "response": {
                            (0, 0, 3): {
                                "best_guess": state_list[1],
                                "value": Decimal("0"),
                                "response": {},
                            }
                        },
                    },
                },
            }

            return best_guess_obj

        # If there is only 1 answer left in state
        if len(state) == 1:

            result = {}
            result["best_guess"] = list(state)[0]
            result["value"] = (
                Decimal("1") if list(state)[0] in possible_guesses else Decimal("0")
            )
            result["response"] = (
                {
                    (0, 0, 3): {
                        "best_guess": list(state)[0],
                        "value": Decimal("0"),
                        "response": {},
                    }
                }
                if list(state)[0] in possible_guesses
                else {}
            )

            return result

        # If we have seen this state before, retrieve the optimal solution that we found previously
        elif (frozenset(state), t) in g.cache:
            return g.cache[(frozenset(state), t)]

        # Find the best guess, save to cache, and return
        else:
            best_guess_obj = self.find_best_guess(
                t, f_str, possible_guesses, state, max_val
            )

            self.cache[(frozenset(state), t)] = best_guess_obj

            return best_guess_obj

    def find_best_guess(
        self, t, f_str=None, possible_guesses=None, state=None, max_val=Decimal("Inf")
    ):
        best_guess_obj = {"best_guess": "", "value": max_val, "response": {}}

        # Sort guesses so that those that are possible answers are evaluated first
        sorted_guesses = self.sorted_guesses(possible_guesses, state)

        for guess in sorted_guesses:

            cur_guess_obj = {"best_guess": guess, "value": 0, "response": {}}

            # get all possible future states
            future_states = self.possible_future_states(state, guess)

            # Sorted so that states with lowest transition probabilities are evaluated first
            sorted_states = self.sorted_states(future_states)

            # Optimization thing
            lower_bounds = [
                self.lower_bound(lst[0]) * lst[1] for lst in sorted_states.values()
            ]

            i = 0
            for response in sorted_states:
                # Probability of getting given future state
                probability = future_states[response][1]
                future_state = future_states[response][0]

                # There is no point of considering this guess as a possible guess in future states, so remove it
                new_possible_guesses = self.remove_guess(possible_guesses, guess)

                future_state_obj = self.value_of(
                    t - 1, f_str, new_possible_guesses, future_state, max_val
                )

                future_state_val = future_state_obj["value"]

                lower_bounds[i] = probability * future_state_val

                cur_guess_obj["response"][response] = future_state_obj

                # If lower bound value of this guess exceeds previously seen best guess, terminate
                if sum(lower_bounds) > best_guess_obj["value"]:
                    break

                i += 1

            cur_guess_obj["value"] = sum(lower_bounds) + 1

            if cur_guess_obj["value"] < best_guess_obj["value"]:
                best_guess_obj = cur_guess_obj

        return best_guess_obj

    # is_possible_answer[guess][response][answer] = True/False
    """
    def generate_answer_table(self):
        possible_responses = [(1,0,0), 
                              (0,1,0),
                              (0,0,1),
                              (0,2,0),
                              (0,1,1),
                              (0,0,2),
                              (0,3,0),
                              (0,2,1),
                              (0,0,3)]

        table = {}

        for guess in self.possible_guesses:
            table[guess] = {}
            for response in possible_responses:
                table[guess][response] = {}
                for answer in self.possible_answers:
                    if self.computeResponse(guess, answer) == response:
                        table[guess][response][answer] = True
                    else:
                        table[guess][response][answer] = False

        return table
        """


cur_solve = 4
g = OptimalGame(possible_guesses=initializePossibleAnswers(cur_solve))

f = "out.json"

with open("policies/tree" + str(cur_solve) + ".json", "w") as t:
    with open("policies/tree" + str(cur_solve) + ".pkl", "wb") as p:
        tree = g.value_of(10, max_val=Decimal("5.1"))

        records = stringify_keys(tree)

        pickle.dump(tree, p)
        json.dump(records, t, indent=4)

pprint(records)
