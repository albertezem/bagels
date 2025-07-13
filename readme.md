# Pico Fermi Bagels Environment

## Rules

There are 2 players, the guesser and responder. The responder chooses a 3 digit number 
such that no digit is repeated twice. The guesser then tries to guess the number the 
responder chose. Each time the guesser guesses, the responder responds with a code 
comprised of the following words:

1. Bagels - None of the digits in the guess are in the answer
2. Pico - A digit in the guess is in the answer, but not in the right place
3. Fermi - A digit in the guess is in the answer and in the right place

For a more popular comparison, Pico is basically a yellow tile in Wordle, Fermi is a 
green tile, and Bagels is the same as a row of grey tiles.

So, for example, if the responder chooses 012 to be the answer, then these are some possible
guesses the guesser can make with its corresponding response code:

1. 345 - Bagels (no digit is in answer)
2. 134 - Pico (1 is in answer, but wrong spot)
3. 312 - Fermi, Fermi (1 and 2 in answer and in right spot)
4. 025 - Pico, Fermi (0 is in answer and right spot, 2 is in answer and wrong spot)

Note that for the guess 025, the response is Pico, Fermi, and not Fermi, Pico. This is because 
all Pico's come before all Fermi's in any response code that has both.

The guesser's job is to get the answer in as few guesses as possible.

## Quick Start

To interact with the bots, simply run interface.py. You can do that by pressing the play button
in the top right, or by typing ``python3 interface.py`` in your terminal. You will be presented
with a list of options.

## Guessing Bot Options

1. IntelligentGuesser - Uses information theory to pick the guess with the highest entropy 
(to learn more, click here: https://youtu.be/v68zYyaEmEA?si=uVytYRXchE6Zxjnw)
2. MinimaxGuesser - Selects the guess that minimizes the largest possible answer set after making a guess
3. SimpleGuesser - Selects the first guess that could still possibly be the answer
4. PerfectGuesser (WIP) - Selects a guess using the optimal strategy for the game 
(optimal strategy meaning the strategy minimizing the average number of guesses to get every possible answer)

### Some notes

While in a normal game of Pico Fermi Bagels, the responder is tasked with giving accurate response codes,
I automated that away so that the computer provides the response code given the answer you chose and the guess
made by the computer. So as responder, the only thing you have to do is provide the answer you want to be guessed.

If you decide to do a battle vs an AI bot, then when it is your turn as responder, an answer will be randomly chosen 
by the code. This is to prevent the user from exploiting the bot by picking guesses that you know it cannot solve in
5 turns.