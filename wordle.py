# Wordle Game and Solver
# Name: Jon Paris
# Collaborators: Joey Paris, Nathan Paris
import copy
import random
import string

from solver import Solver
from wordle_common import Knowledge

WORDLIST_FILENAME = "words.txt"
ANSWERS_FILE = "words-answers.txt"
GUESSES_FILE = "words-guesses.txt"


class COLORS:
    GREEN = " \033[0;30;42m "
    BLACK = " \033[0;37;40m "
    YELLOW = " \033[0;30;43m "
    GREY = " \033[0;30;47m "
    SPACE_COLOR = " \033[0;37;48m"


def load_words(file_name):
    print("Loading word list...")
    infile = open(file_name, 'r')
    line = infile.readline()
    wordlist = line.split()
    chosen_word_length = []
    for x in wordlist:
        if len(x) == Knowledge.WORD_LENGTH:
            chosen_word_length.append(x)
    print("  ", len(chosen_word_length), "words loaded.")
    return chosen_word_length


def choose_word(wordlist):
    return random.choice(wordlist)


def populate_db():
    #  for word in WORDS:
    for word in ["salet", "arose", "arise", "raise", "crate", "trace", "slate", "crane", "argue", "ocean"]:
        print("starting word: " + word)
        auto_play(word)


def auto_play(first_guess: str):
    total_secrets = len(ANSWERS)
    total_guesses = 0
    dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0}
    dk = Knowledge.default_knowledge()
    for secret in ANSWERS:
        print("\r\033[K", "Target: " + secret, end="")
        suggestion = None
        k = copy.deepcopy(dk)
        try_count = 0

        while suggestion != secret:
            try_count += 1
            total_guesses += 1
            if try_count == 1:
                suggestion = first_guess  # force first word
            else:
                suggestion = Solver.get_suggestion(k, WORDS, ANSWERS)
            if suggestion == secret:
                dist[try_count] += 1
                print("\r\033[K", secret, "in", str(try_count), end="\n")
                break
            else:
                k = Knowledge.update_knowledge(k, secret, suggestion)
    avg = format(total_guesses / total_secrets, '.5f')
    print("\r\033[K", first_guess, total_guesses, avg, str(dist), end="\n")


def play_wordle(secret_word, wordlist):
    total_guesses = 6
    remaining_guesses = 6
    k = Knowledge.default_knowledge()

    def decorate_word_with_knowledge(kn: str, word: str) -> str:
        decorated_word = ""
        for i in range(Knowledge.WORD_LENGTH):
            c = word[i]
            color = decorate(c, i, kn)
            decorated_word += color + c + COLORS.SPACE_COLOR
        return decorated_word + "\n\n"

    def decorate(c, i, kn):
        word_pos = Knowledge.WORD_LENGTH + string.ascii_lowercase.index(c)
        if c == kn[i]:
            color = COLORS.GREEN
        elif kn[word_pos] == Knowledge.YES:
            color = COLORS.YELLOW
        elif kn[word_pos] == Knowledge.NO:
            color = COLORS.GREY
        else:
            color = COLORS.BLACK
        return color

    def show_decorated_keyboard(kn: str):
        color = {}
        for c in 'qwertyuiopasdfghjklzxcvbnm':
            color[c] = COLORS.BLACK
            if c == 'a' or c == 'z':
                print("\n")
            for i in range(Knowledge.WORD_LENGTH):
                if color[c] != COLORS.GREEN: color[c] = decorate(c, i, kn)
            print(color[c] + c, end=COLORS.SPACE_COLOR)
        print("\n")

    # starting welcome
    print("Welcome to Wordle!")
    print("I am thinking of a word that is " + str(Knowledge.WORD_LENGTH) + " letters long.")
    attempts = ""

    while remaining_guesses > 0:
        print("\nYou have " + str(remaining_guesses) + " guesses left.")
        print("Type a " + str(
            Knowledge.WORD_LENGTH) + " letter word, ! for potential word, or !! for potential words with a suggestion")

        show_decorated_keyboard(k)  # prints keyboard

        # request guess
        guess = str(input("Please guess a word " + str(len(secret_word)) + " letters long: ")).lower()[
                :Knowledge.WORD_LENGTH]

        # check if they made the correct guess!
        if guess == secret_word:
            print("Congratulations, you won!")
            print("It took you " + str(total_guesses - remaining_guesses + 1) + " guesses")
            play_again()
            break

        # if asking for potential matches show list
        if guess == "!":
            matches = Knowledge.get_possible_matches(k, ANSWERS)
            print("Total: " + str(len(matches)) + " " + str(matches))
        # if asking for potential matches show list and suggest the best match
        elif guess == "!!":
            matches = Knowledge.get_possible_matches(k, ANSWERS)
            print("Total: " + str(len(matches)) + " " + str(matches))
            print("\n", "Suggested guess: " + Solver.get_suggestion(k, WORDS, tuple(matches)))

        elif len(guess) != Knowledge.WORD_LENGTH:
            print("Sorry, " + guess + " is not a " + str(len(secret_word)) + " letter word. Try again.")
        elif guess not in wordlist:
            print("Sorry, " + guess + " is not a word I know. Try again.")

        # review guess
        else:
            k = Knowledge.update_knowledge(k, secret_word, guess)
            attempts += decorate_word_with_knowledge(k, guess)
            print(attempts)
            remaining_guesses -= 1
            if remaining_guesses == 0:
                print("Sorry, you ran out of guesses. The word was " + secret_word + ".")
                play_again()
                break


def suggestions_only():
    total_guesses = 6
    remaining_guesses = total_guesses

    k = Knowledge.default_knowledge()

    # starting welcome
    print("Welcome to Wordle Helper!")
    print("I help you guess what Wordle word is if it is " + str(Knowledge.WORD_LENGTH) + " letters long.")
    while remaining_guesses > 0:
        print("\nYou have " + str(remaining_guesses) + " guesses left.")
        print("You will first your guess " + str(
            Knowledge.WORD_LENGTH) + " letters long to the fist question. Then the response the game gives you.")

        # request guess
        guess = str(input("Type your guess:")).lower()[:Knowledge.WORD_LENGTH]
        print("Type the response you got in order.")
        print("'G' if in the right position")
        print("'Y' yellow if in the word but not in the position, and ")
        print("'R' if not in the word. Example: GRRYR")
        new_knowledge = str(input("Type the response you got:")).upper()
        if len(guess) == Knowledge.WORD_LENGTH and len(new_knowledge) == Knowledge.WORD_LENGTH:
            if new_knowledge == "GGGGG":
                print("Congrats! You won in " + str(total_guesses - remaining_guesses + 1) + " guesses!")
                break
            for i in range(len(guess)):
                c = guess[i]
                res = str(new_knowledge[i])
                if res == 'G':
                    if c not in k[Knowledge.IN_WORD]:
                        k[Knowledge.IN_WORD].append(c)
                    k[str(i)][Knowledge.IN_POSITION] = c
                elif res == 'Y':
                    if c not in k[str(i)][Knowledge.NOT_IN_POSITION]:
                        k[str(i)][Knowledge.NOT_IN_POSITION].append(c)
                    if c not in k[Knowledge.IN_WORD]:
                        k[Knowledge.IN_WORD].append(c)
                else:
                    if c not in k[Knowledge.NOT_IN_WORD]:
                        if c not in k[Knowledge.IN_WORD]:
                            k[Knowledge.NOT_IN_WORD].append(c)
                        else:
                            k[str(i)][Knowledge.NOT_IN_POSITION].append(c)

            matches = Knowledge.get_possible_matches(copy.deepcopy(k), ANSWERS)
            total_matches = len(matches)
            print("Total: " + str(total_matches) + " " + str(matches))

            hint = str(input("Want a suggestion? (y/n)")).lower()[0]
            if hint == "y":
                print("Suggested guess: " + Solver.get_suggestion(k, WORDS, ANSWERS))
            remaining_guesses -= 1
        else:
            print("try again. either your guess or feedback was the wrong length")


def play_again():
    again = str(input("Play Again? (y/n)")).lower()[0]
    if again == "y":
        play_wordle(choose_word(ANSWERS), WORDS)
    else:
        print("bye!")


if __name__ == "__main__":
    # Play wordle mode
    WORDS = tuple(load_words(GUESSES_FILE))
    ANSWERS = tuple(load_words(ANSWERS_FILE))

    print("do you want to:")
    print("A. Play Wordle here!")
    print("B. Get help playing wordle somewhere else.")
    print("C. Auto Play to test solver!")
    print("D. Populate DB!")

    menu = str(input("Your Choice:")).lower()
    if menu == 'a':
        play_wordle(choose_word(ANSWERS), WORDS)
    elif menu == 'b':
        suggestions_only()
    elif menu == 'c':
        auto_play('salet')  # todo can do more here
    elif menu == 'd':
        populate_db()
