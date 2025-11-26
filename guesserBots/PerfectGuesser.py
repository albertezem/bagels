from guesser import AbstractGuesser

class PerfectGuesser(AbstractGuesser):

    def __init__(self, name, policy) -> None:
        super().__init__(name)
        self.policy = policy
        self.cur_state = policy

    def initializePossibleAnswers(self, answers=None):

        self.cur_state = self.policy

    def guessAnswer(self):
        return self.cur_state["best_guess"]

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

            
        self.cur_state = self.cur_state["response"][decoded_response]
