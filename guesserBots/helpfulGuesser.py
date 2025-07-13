from guesser import Guesser
from math import log2

class HelpfulGuesser(Guesser):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.luck = 0
        self.info_lost = 0

    def guessAnswer(self):
        # self.getRemainingPossibleAnswers()
        print("")
        answer = input("What is your guess?")

        self.last_guess = (int(answer[0]), int(answer[1]), int(answer[2]))
        self.estimateInformationLost()
        return answer

    def estimateInformationLost(self):
        info_table = self.computeEITable()

        best_guesses = [guess for guess in info_table if info_table[guess] == max(info_table.values())] 

        priority_guess = [guess for guess in best_guesses if guess in self.possible_answers]

        if priority_guess:
            best_guess = priority_guess[0]
        else:
            best_guess = best_guesses[0]

        info_lost = info_table[best_guess] - info_table[self.last_guess] # bits lost from guess
        
        info_lost = round(info_lost, 1)
        
        self.info_lost += info_lost

        best_guess = "".join(str(x) for x in best_guess)

        print("Lost", info_lost, "bits of information, best guess was", best_guess)

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
                return (0,0,3)

        return tuple(decoded_response)

    def processResponse(self, response):
        decoded_response = self.decodeResponse(response)

        self.computeLuck(decoded_response)

        # Run pattern proportions for guess
        # Find expected entropy
        # Determine actual gained entropy
        new_possible_answers = [
            answer
            for answer in self.possible_answers
            if self.computeResponse(self.last_guess, answer) == decoded_response
        ]

        self.possible_answers = new_possible_answers

    def computeLuck(self, response):
        pattern_proportions = self.computePatternProportions(self.last_guess)

        entropy = self.calculateExpectedInformation(pattern_proportions)

        prob = pattern_proportions[response]
        info_gained = -log2(prob)
        
        luck = round((info_gained - entropy), 1)

        if luck >= 0:
            print("Gained", luck, "bits of info more than expected!")
        else:
            print("Lost", -luck, "bits of info more than expected.")
            
        self.luck += luck

    def computePatternProportions(self, guess):
        pattern_proportions = {}

        for possible_answer in self.possible_answers:
            # Determine the response of guess/answer pair
            # Add answer to respective pattern in pattern_proportions

            response = self.computeResponse(guess, possible_answer)

            if response not in pattern_proportions:
                pattern_proportions[response] = 0

            pattern_proportions[response] += 1

        for pattern in pattern_proportions:
            # Find proportion of pattern
            pattern_proportions[pattern] = pattern_proportions[pattern] / len(
                self.possible_answers
            )

        return pattern_proportions

    def computeEITable(self):
        """Guesses to maximize expected information"""
        # For every guess I can still make:
        # Create dict of pattern-answer pairs (all answers associated with a given pattern)
        guess_ei = {}

        for possible_guess in self.all_possible_answers:
            # for possible_guess in self.possible_answers:

            pattern_proportions = self.computePatternProportions(possible_guess)

            expected_information = 0

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
