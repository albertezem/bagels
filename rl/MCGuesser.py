from guesser import AbstractGuesser
from collections import defaultdict
import numpy as np
import random

def initializePossibleAnswers(n=10):
    possible = []

    for i in range(0, n):
        for j in range(0, n):
            for k in range(0, n):
                if i != j and j != k and i != k:
                    possible.append(str(i) + str(j) + str(k))

    return possible

class MCGuesser(AbstractGuesser):

    def __init__(self, name) -> None:
        super().__init__(name)
        self.Q = defaultdict(lambda: np.zeros(720))
        self.epsilon = 0.999997 # decaying randomness rate
        self.alpha = 0.01 # update rate
        self.guesses = 0
        self.episode = []

        # self.Q[frozen set of state][possible guesses] = q-value

    def create_map(self):
        lst = initializePossibleAnswers()
        mp = {}
        action_to_index = {}

        for i in range(len(lst)):
            mp[i] = lst[i]
            action_to_index[lst[i]] = i

        self.index_to_action = mp
        self.action_to_index = action_to_index

    def initializePossibleAnswers(self, answers=None):
        self.guesses = 0
        self.create_map()
        self.episode = []

        possible = []

        for i in range(0, 10):
            for j in range(0, 10):
                for k in range(0, 10):
                    if i != j and j != k and i != k:
                        possible.append((i, j, k))

        self.possible_answers = possible
        self.all_possible_answers = possible

    def guessAnswer(self):
        cur_state = frozenset(self.possible_answers)
        prob = random.random()

        self.Q[cur_state]

        if prob < self.epsilon:
            action = random.randint(0,719)
        else:
            action = np.argmin(self.Q[cur_state])

        self.guesses += 1
        self.epsilon = self.epsilon * 0.999997

        guess = self.index_to_action[action]
        self.last_guess = (
            int(guess[0]),
            int(guess[1]),
            int(guess[2]),
        )
        self.episode.append((cur_state, guess, 1))

        return guess

    def decodeResponse(self, response: str):
        # Process fermi, bagels,etc.

        split_response = response.split(",")
        decoded_response = [0, 0, 0]

        for i in split_response:
            if i == "Bagels":
                decoded_response[0] += 1
            elif i == "Pico":
                decoded_response[1] += 1
            elif i == "Fermi":
                decoded_response[2] += 1
            elif i == "You win!":
                return (0, 0, 3)

        return tuple(decoded_response)

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

    def processResponse(self, response):
        decoded_response = self.decodeResponse(response)

        if decoded_response == (0,0,3):
            self.updateQValues()

        new_possible_answers = [
            answer
            for answer in self.possible_answers
            if self.computeResponse(self.last_guess, answer) == decoded_response
        ]

        self.possible_answers = new_possible_answers

    def updateQValues(self):
        states, actions, rewards = zip(*self.episode)

        for i, state in enumerate(states):
            returns = sum(rewards[i:])

            self.Q[state][self.action_to_index[actions[i]]] += self.alpha * (
                returns - self.Q[state][self.action_to_index[actions[i]]]
            )
