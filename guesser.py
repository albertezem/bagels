from math import log2


class AbstractGuesser:

    def __init__(self, name) -> None:
        self.name = name
        self.guess_history = []
        self.all_possible_answers = []
        self.possible_answers = []
        self.last_guess = []

    def initializePossibleAnswers(self, answers=None):
        pass

    def guessAnswer(self):
        return ""

    def processResponse(self, response):
        return []


class Guesser(AbstractGuesser):
    def __init__(self, name) -> None:
        self.name = name
        self.guess_history = []
        self.all_possible_answers = []
        self.possible_answers = []
        self.last_guess = []

    def initializePossibleAnswers(self, answers=None):
        possible = []

        for i in range(0, 10):
            for j in range(0, 10):
                for k in range(0, 10):
                    if i != j and j != k and i != k:
                        possible.append((i, j, k))

        self.possible_answers = possible
        self.all_possible_answers = possible

    def guessAnswer(self):
        return ""

    def processResponse(self, response):
        return []


class HumanGuesser(Guesser):

    def guessAnswer(self):
        # self.getRemainingPossibleAnswers()
        answer = ""
        while not self.isValidGuess(answer):
            answer = input("What is your guess?")
            
            if not self.isValidGuess(answer):
                print("Invalid guess. Please try again")

        self.last_guess = (int(answer[0]), int(answer[1]), int(answer[2]))
        self.guess_history.append(self.last_guess)
        return answer

    """
    def getRemainingPossibleAnswers(self):
        print(self.possible_answers)
    
    def initializePossibleAnswers(self):
        possible = []

        for i in range(0, 10):
            for j in range(0, 10):
                for k in range(0, 10):
                    if i != j and j != k and i != k:
                        possible.append((i, j, k))

        self.possible_answers = possible
    """

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
    
    def isValidGuess(self, guess):  
        try:  # If the number is not a number
            int(guess)
        except:
            return False

        if len(guess) != 3:  # If the number doesn't have 3 digits
            return False

        if (guess[0] in guess[1:]) or (guess[1] == guess[2]):
            return False
        
        return True

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

    def processResponse(self, response):
        decoded_response = self.decodeResponse(response)

        new_possible_answers = [
            answer
            for answer in self.possible_answers
            if self.computeResponse(self.last_guess, answer) == decoded_response
        ]

        self.possible_answers = new_possible_answers


class IntelligentGuesser(Guesser):
    def __init__(self, name) -> None:
        super().__init__(name)

    def guessAnswer(self):  # type: ignore
        if len(self.possible_answers) == 1:
            best_guess = self.possible_answers[0]
        else:
            ei_table = self.computeEITable()
            best_guesses = [guess for guess in ei_table if ei_table[guess] == max(ei_table.values())]  # type: ignore

            priority_guess = [
                guess for guess in best_guesses if guess in self.possible_answers
            ]

            if priority_guess:
                best_guess = priority_guess[0]
            else:
                best_guess = best_guesses[0]

            self.last_guess = best_guess

        best_guess = "".join(str(x) for x in best_guess)

        return best_guess

    def computeEITable(self):
        """Guesses to maximize expected information"""
        # For every guess I can still make:
        # Create dict of pattern-answer pairs (all answers associated with a given pattern)
        guess_ei = {}

        for possible_guess in self.all_possible_answers:
            # for possible_guess in self.possible_answers:

            pattern_proportions = {}

            expected_information = 0
            for possible_answer in self.possible_answers:
                # Determine the response of guess/answer pair
                # Add answer to respective pattern in pattern_proportions

                response = self.computeResponse(possible_guess, possible_answer)

                if response not in pattern_proportions:
                    pattern_proportions[response] = 0

                pattern_proportions[response] += 1

            for pattern in pattern_proportions:
                # Find proportion of pattern
                pattern_proportions[pattern] = pattern_proportions[pattern] / len(
                    self.possible_answers
                )

            expected_information += self.calculateExpectedInformation(
                pattern_proportions
            )

            guess_ei[possible_guess] = round(expected_information, 3)

        return guess_ei

    def calculateExpectedInformation(self, prob_dict):
        total = 0
        for pattern in prob_dict:
            prob = prob_dict[pattern]
            total += prob * -log2(prob)

        return total

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

    def processResponse(self, response):
        decoded_response = self.decodeResponse(response)
        new_possible_answers = [
            answer
            for answer in self.possible_answers
            if self.computeResponse(self.last_guess, answer) == decoded_response
        ]

        self.possible_answers = new_possible_answers

    def updatePossibleAnswers(self, response):
        self.possible_answers = self.processResponse(response)


class SimpleGuesser(Guesser):
    def __init__(self, name) -> None:
        super().__init__(name)

    def guessAnswer(self):
        best_guess = self.possible_answers[0]
        self.last_guess = best_guess

        best_guess = "".join(str(x) for x in best_guess)

        return best_guess

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

    def processResponse(self, response):
        decoded_response = self.decodeResponse(response)
        new_possible_answers = [
            answer
            for answer in self.possible_answers
            if self.computeResponse(self.last_guess, answer) == decoded_response
        ]

        self.possible_answers = new_possible_answers


class MinimaxGuesser(Guesser):
    def __init__(self, name) -> None:
        super().__init__(name)

    def guessAnswer(self):  # type: ignore
        if len(self.possible_answers) == 1:
            best_guess = self.possible_answers[0]
        else:
            ei_table = self.computeEITable()

            best_guesses = [
                guess for guess in ei_table if ei_table[guess] == min(ei_table.values())
            ]  # type: ignore

            priority_guess = [
                guess for guess in best_guesses if guess in self.possible_answers
            ]

            if priority_guess:
                best_guess = priority_guess[0]
            else:
                best_guess = best_guesses[0]
            """
            best_guess = min(
                ei_table, key=lambda k: len(ei_table[k])
            )  # min(ei_table, key=lambda k: len(ei_table[k]))
            """

        self.last_guess = best_guess

        best_guess = "".join(str(x) for x in best_guess)

        return best_guess

    def computeEITable(self):
        """Guesses to maximize expected information"""
        # For every guess I can still make:
        # Create dict of pattern-answer pairs (all answers associated with a given pattern)
        #
        guess_ei = {}

        for possible_guess in self.all_possible_answers:

            pattern_proportions = {}

            expected_information = 0
            for possible_answer in self.possible_answers:
                # Determine the response of guess/answer pair
                # Add answer to respective pattern in pattern_proportions

                response = self.computeResponse(possible_guess, possible_answer)
                """
                if response not in pattern_proportions:
                    pattern_proportions[response] = 0

                pattern_proportions[response] += 1
                """
                if response not in pattern_proportions:
                    pattern_proportions[response] = 0

                pattern_proportions[response] += 1

            # pattern_proportions.pop((0,0,3), None)
            expected_information = max(
                pattern_proportions.values()
            )  # max(len(v) for v in pattern_proportions.values())

            guess_ei[possible_guess] = expected_information

        return guess_ei

    def calculateExpectedInformation(self, prob_dict):
        total = 0
        for pattern in prob_dict:
            prob = prob_dict[pattern]
            total += prob * -log2(prob)

        return total

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

    def processResponse(self, response):
        decoded_response = self.decodeResponse(response)
        new_possible_answers = [
            answer
            for answer in self.possible_answers
            if self.computeResponse(self.last_guess, answer) == decoded_response
        ]

        self.possible_answers = new_possible_answers

    def updatePossibleAnswers(self, response):
        self.possible_answers = self.processResponse(response)


def main():
    g = IntelligentGuesser("text")
    g.initializePossibleAnswers()
    print(g.guessAnswer())


if __name__ == "__main__":
    main()
