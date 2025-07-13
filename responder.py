import random

class Responder:

    def __init__(self, name) -> None:
        self.name = name
        self.answer = []

    def initializeAnswer(self):
        pass

    def processGuess(self, guess):
        clues = [0, 0, 0]

        for i in range(3):
            if guess[i] == self.answer[i]:
                clues[2] += 1
            elif guess[i] in self.answer:
                clues[1] += 1

        if clues == [0,0,0]:
            clues[0] += 1

        return tuple(clues)

    def respond(self, guess):
        response = self.processGuess(guess)
        string_response = []

        if response == (1, 0, 0):
            string_response.append("Bagels")
        elif response == (0, 0, 3):
            string_response.append("You win!")
        else:
            for i in range(response[1]):
                string_response.append("Pico")

            for j in range(response[2]):
                string_response.append("Fermi")

        return ",".join(string_response)

class DeterministicResponder(Responder):

    def __init__(self, name, answer) -> None:
        self.name = name
        self.answer = answer

    def initializeAnswer(self):

        self.answer = list(self.answer)

        for i in range(len(self.answer)):
            self.answer[i] = int(self.answer[i])

        self.answer = tuple(self.answer)

    def encodeGuess(self, guess):
        guess = list(guess)

        for i in range(len(guess)):
            guess[i] = int(guess[i])

        return tuple(guess)

    def processGuess(self, guess):
        guess = self.encodeGuess(guess)
        clues = [0, 0, 0]

        for i in range(3):
            if guess[i] == self.answer[i]:
                clues[2] += 1
            elif guess[i] in self.answer:
                clues[1] += 1

        if clues == [0, 0, 0]:
            clues[0] += 1

        return tuple(clues)

    def respond(self, guess):
        response = self.processGuess(guess)
        string_response = []

        if response == (1, 0, 0):
            string_response.append("Bagels")
        elif response == (0, 0, 3):
            string_response.append("You win!")
        else:
            for i in range(response[1]):
                string_response.append("Pico")

            for j in range(response[2]):
                string_response.append("Fermi")

        return ",".join(string_response)


class ComputerResponder(Responder):
    def __init__(self, name) -> None:
        self.name = name
        self.answer = []

    def initializeAnswer(self):
        possible = []

        for i in range(0, 10):
            for j in range(0, 10):
                for k in range(0, 10):
                    if i != j and j != k and i != k:
                        possible.append((i, j, k))

        self.answer = random.choice(possible)
        
    def encodeGuess(self, guess):
        guess = list(guess)
        
        for i in range(len(guess)):
            guess[i] = int(guess[i])
            
        return tuple(guess)
            

    def processGuess(self, guess):
        guess = self.encodeGuess(guess)
        clues = [0, 0, 0]

        for i in range(3):
            if guess[i] == self.answer[i]:
                clues[2] += 1
            elif guess[i] in self.answer:
                clues[1] += 1

        if clues == [0,0,0]:
            clues[0] += 1

        return tuple(clues)

    def respond(self, guess):
        response = self.processGuess(guess)
        string_response = []

        if response == (1,0,0):
            string_response.append("Bagels")
        elif response == (0,0,3):
            string_response.append("You win!")
        else:
            for i in range(response[1]):
                string_response.append("Pico")

            for j in range(response[2]):
                string_response.append("Fermi")

        return ",".join(string_response)


def main():
    r = ComputerResponder("hello")
    r.initializeAnswer()
    print("answer:",r.answer)
    print("response:", r.respond("481"))


if __name__ == "__main__":
    main()
