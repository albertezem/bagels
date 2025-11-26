from guesser import Guesser

class HumanGuesser(Guesser):
    """
    Basic code that allows for a human to guess in this game.
    """
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
