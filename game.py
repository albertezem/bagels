from guesser import (
    Guesser,
    IntelligentGuesser,
    MinimaxGuesser,
    HumanGuesser,
    SimpleGuesser,
    AbstractGuesser,
)
from IntelligentGuesserN import AbstractGuessesEntropyGuesser
from responder import Responder, ComputerResponder, DeterministicResponder
from guesserBots.helpfulGuesser import HelpfulGuesser
import random
from pprint import pprint
import numpy as np
from PerfectGuesser import PerfectGuesser
import pickle


class Game:
    def __init__(
        self,
        guesser: AbstractGuesser,
        responder: Responder,
        guessesAllowed: int,
        state_space=None,
    ):
        self.guesser = guesser
        self.responder = responder
        self.guessesAllowed = guessesAllowed
        self.guesses = 0
        self.cur_guess = ""
        self.cur_response = ""
        self.guesser_won = False
        self.responder_won = False
        self.state_space = state_space

    def startGame(self):
        self.guess_history = []

        self.guesser.initializePossibleAnswers(self.state_space)
        self.responder.initializeAnswer()
        response = -1
        # print("answer is", self.responder.answer)

        while not self.gameOver():
            guess = self.guesser.guessAnswer()
            self.cur_guess = guess
            self.guess_history.append(self.cur_guess)

            print(self.guesser.name, "guessed", guess)

            response = self.responder.respond(guess)
            self.cur_response = response

            print(self.responder.name, "responded", response)

            self.guesses += 1
            """
            if self.gameOver():
                if self.guesser_won:
                    print("guesser won")

                if self.responder_won:
                    print("responder won")

                break
            """

            self.guesser.processResponse(response)

        if self.guesser_won:
            print("guesser won")

        if self.responder_won:
            print("responder won")

    def gameOver(self):  # Checks to see if the game is over
        if self.cur_response == "You win!":
            self.guesser_won = True

            return True

        elif self.guesses >= self.guessesAllowed:
            self.responder_won = True

            return True

        return False


def initializePossibleAnswers(n=10):
    possible = []

    for i in range(0, n):
        for j in range(0, n):
            for k in range(0, n):
                if i != j and j != k and i != k:
                    possible.append(str(i) + str(j) + str(k))

    return possible


def median(lst):
    n = len(lst)
    s = sorted(lst)
    return (s[n // 2 - 1] / 2.0 + s[n // 2] / 2.0, s[n // 2])[n % 2] if n else None


def test_human_performance(n=10):
    guesses = {}
    guesses_arr = []
    guess_count = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    guesser = HumanGuesser("shev")
    responder = ComputerResponder("AI")
    for i in range(n):
        game = Game(guesser, responder, 9999)
        game.startGame()

        guesses[game.responder.answer] = game.guess_history
        guesses_arr.append(game.guesses)
        guess_count[game.guesses] += 1

    pprint(guesses)
    print("Summary stats:")
    pprint(guess_count)
    print("Num guesses:", len(guesses))
    max_key = max(guesses, key=lambda k: len(guesses[k]))
    min_key = min(guesses, key=lambda k: len(guesses[k]))
    print("max guesses:", max_key, len(guesses[max_key]))
    print("min guesses:", min_key, len(guesses[min_key]))
    print("mean guesses:", sum(guesses_arr) / len(guesses_arr))
    print("median guesses:", median(guesses_arr))
    print("STD", np.std(guesses_arr))


# Attempt 1: 6.9 guesses per round for 10 rounds, 4-10
# Averaged 5 guesses, 10 rounds, 4.5 median, min 3 max 8
# averaged 5.4 guesses, 10 rounds, 5.5 median, min 4 max 7
# averaged 5.3, still worse than simple


def battle(
    p1Guesser: Guesser,
    p1Responder: Responder,
    p2Guesser: Guesser,
    p2Responder: Responder,
):
    p1_score = 0
    p2_score = 0

    while abs(p1_score - p2_score) < 2:
        print("")
        game1 = Game(p1Guesser, p2Responder, 5)
        game1.startGame()

        if game1.guesser_won:
            p1_score += 1

        print("")

        game2 = Game(p2Guesser, p1Responder, 5)
        game2.startGame()

        if game2.guesser_won:
            p2_score += 1

        print(p1Guesser.name, "score:", p1_score)
        print(p2Guesser.name, "score:", p2_score)


def test_ai_guesser_performance(guesser: Guesser, possible_answers):
    guesses = {}
    guesses_arr = []
    guess_count = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    for answer in possible_answers:
        responder = DeterministicResponder("AI", answer)
        game = Game(guesser, responder, 9999, state_space=possible_answers)
        game.startGame()

        guesses[answer] = game.guesses
        guesses_arr.append(game.guesses)

        guess_count[game.guesses] += 1

    pprint(guesses)
    print("Summary stats:")
    pprint(guess_count)
    print("Num guesses:", len(guesses))
    max_key = max(guesses, key=guesses.get)
    min_key = min(guesses, key=guesses.get)
    print("max guesses:", max_key, guesses[max_key])
    print("min guesses:", min_key, guesses[min_key])
    print("mean guesses:", sum(guesses_arr) / len(guesses_arr))
    print("median guesses:", median(guesses_arr))
    print("STD", np.std(guesses_arr))


def use_training_guesser(answer=None):
    guesser = HelpfulGuesser("shev")
    if answer:
        responder = DeterministicResponder("AI", answer)
    else:
        responder = ComputerResponder("AI")
    g = Game(guesser, responder, 9999)
    g.startGame()
    print("Info lost:", guesser.info_lost, "bits")
    print("Luck:", round(guesser.luck, 1), "bits")
    print("Guesses:", g.guesses)


def single_game(guesser: Guesser = IntelligentGuesser("AI")):
    responder = ComputerResponder("AI")
    g = Game(guesser, responder, 9999)
    g.startGame()


def main():
    cur_solve = 6
    
    with open("policies/tree" +str(cur_solve)+ ".pkl", "rb") as f:
        pol = pickle.load(f)
    guesser = PerfectGuesser("PP", pol)

    test_ai_guesser_performance(guesser, initializePossibleAnswers(cur_solve))



# it has 197 over 5
# mm has 272 over 5
if __name__ == "__main__":
    main()
