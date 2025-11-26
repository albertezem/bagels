from game import *


def main():
    name = input("What name do you go by?")
    t = True
    while t:
        print(
            "Wh3at do you want to do? Enter the number corresponding with your choice"
        )
        print("1: Play a game as guesser")
        print("2: Play a game as responder")
        print("3: Play a game as guesser in training mode")
        print("4: Battle vs one of the AI bots")
        print("5: Get an evaluation of your skill as guesser")
        print("6: Get an evaluation the bots' skill as guesser")
        print("7: Quit")
        x = input("What do you want to do?")

        if x == "1":
            single_game(HumanGuesser(name))

        elif x == "2":
            print("1: Entropy")
            print("2: Minimax")
            print("3: Simple")
            i = input("Enter the number for the bot you want to guess your answer.")

            bots = [
                IntelligentGuesser("Entropy"),
                MinimaxGuesser("Minimax"),
                SimpleGuesser("Simple"),
            ]

            answer = input(
                "What should the answer be for this game? Enter a 3 digit number with no repetitions"
            )

            bot = bots[int(i) - 1]

            responder = DeterministicResponder(name, answer)

            game = Game(bot, responder, 9999, state_space=initializePossibleAnswers())
            game.startGame()

        elif x == "3":
            single_game(HelpfulGuesser(name))

        elif x == "4":
            print(
                "When battling, you get a point if you manage to guess the answer within 5 guesses."
            )
            print("The first person to create a 2 point lead wins")
            print("1: Entropy")
            print("2: Minimax")
            print("3: Simple")
            i = input("Enter the number for the bot you want to guess your answer")

            bots = [
                IntelligentGuesser("Entropy"),
                MinimaxGuesser("Minimax"),
                SimpleGuesser("Simple"),
            ]

            bot_guesser = bots[int(i) - 1]
            bot_responder = ComputerResponder("AI")
            human_guesser = HumanGuesser(name)
            human_responder = ComputerResponder(name)

            battle(bot_guesser, bot_responder, human_guesser, human_responder)

        elif x == "5":
            print("Here, you play 10 games, which we use to estimate your skills.")
            test_human_performance()
            print(
                "For comparison, the Entropy bot so far has an average guess rate of 5.02, and takes at most 7 guesses to win"
            )
            print(
                "and the Minimax bot has an average guess rate of 5.12, but takes at most 6 guesses."
            )

        elif x == "6":
            print("1: Entropy")
            print("2: Minimax")
            print("3: Simple")
            i = input("Enter the number for the bot you want to guess your answer")

            bots = [
                IntelligentGuesser("Entropy"),
                MinimaxGuesser("Minimax"),
                SimpleGuesser("Simple"),
            ]

            bot_guesser = bots[int(i) - 1]

            test_ai_guesser_performance(bot_guesser, initializePossibleAnswers())
        elif x == "7":
            t = False
        else:
            print("Error, please try again")


if __name__ == "__main__":
    main()
