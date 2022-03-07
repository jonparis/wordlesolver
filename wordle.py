# Wordle Game and Solver
# Name: Jon Paris
# Collaborators: Joey Paris, Nathan Paris
import copy
import random
from solver import Solver
from wordle_common import Knowledge, COLORS, Tools, CONST

WORDLIST_FILENAME = "words.txt"
GUESSES_FILE = "words-guesses.txt"


def choose_word(wordlist):
    return random.choice(wordlist)


def populate_db():
    top_100 = ("raise", "raile", "soare", "arise", "irate", "orate", "ariel", "arose", "raine", "artel", "taler", "ratel", "aesir", "arles", "realo", "alter", "saner", "later", "snare", "oater", "salet", "taser", "stare", "tares", "slate", "alert", "reais", "lares", "reast", "strae", "laser", "saine", "rales", "urate", "crate", "serai", "toile", "seral", "rates", "carte", "antre", "slane", "trace", "coate", "carle", "carse", "stoae", "reals", "terai", "aeros", "liane", "tears", "caret", "stale", "alure", "slier", "resat", "sorel", "tales", "nares", "aisle", "litre", "saice", "learn", "earnt", "oriel", "earst", "lears", "paire", "reoil", "alone", "teras", "urase", "leant", "aloes", "torse", "aster", "arets", "least", "soler", "reans", "retia", "laten", "siler", "anole", "crane", "trone", "laers", "earls", "stear", "atone", "ayrie", "trail", "stane", "react", "haole", "teals", "maire", "toise", "tiler")
    recs = ("salet", "reast", "crate", "trace", "slate", "crane")
    for word in recs + top_100:
        print("starting word: " + word)
        s = Solver(WORDS, False)
        s.auto_play(word)  # todo can do autoplay and optimize but will take a long time!


def play_wordle(secret_word, wordlist):
    total_guesses = 6
    remaining_guesses = 6

    def decorate_word_with_knowledge(kn: dict, word: str) -> str:
        decorated_word = ""
        word = list(word)
        local_in_word = []
        for i in range(CONST.WORD_LENGTH):
            c = word[i]
            word[i] = ""
            if c == kn[i][CONST.IN_POSITION]:
                local_in_word.append(c)
                color = COLORS.GREEN
            elif c in kn[CONST.IN_WORD] and (c not in local_in_word or c in kn[CONST.IN_MULTI]):
                local_in_word.append(c)
                color = COLORS.YELLOW
            elif c:
                color = COLORS.GREY
            else:
                color = " "
            decorated_word += color + c + COLORS.SPACE_COLOR
        return decorated_word + "\n\n"

    def show_decorated_keyboard(kn: dict):
        for c in 'qwertyuiopasdfghjklzxcvbnm':
            if c == 'a' or c == 'z':
                print("\n")
            in_position = False
            for i in range(CONST.WORD_LENGTH):
                if c == kn[i][CONST.IN_POSITION]:
                    in_position = True
            if in_position:
                color = COLORS.GREEN
            elif c in kn[CONST.IN_WORD]:
                color = COLORS.YELLOW
            elif c in kn[CONST.NOT_IN_WORD]:
                color = COLORS.GREY
            else:
                color = COLORS.BLACK
            print(color + c, end=COLORS.SPACE_COLOR)
        print("\n")

    # starting welcome
    print("Welcome to Wordle!")
    print("I am thinking of a word that is " + str(CONST.WORD_LENGTH) + " letters long.")
    attempts = ""
    k = Knowledge.default_knowledge()
    prev_guesses = ()

    while remaining_guesses > 0:
        print("\nYou have " + str(remaining_guesses) + " guesses left.")
        print("Type a " + str(
            CONST.WORD_LENGTH) + " letter word, ! for potential word, or !! for potential words with a suggestion")

        show_decorated_keyboard(k)  # prints keyboard

        # request guess
        guess = str(input("Please guess a word " + str(len(secret_word)) + " letters long: ")).lower()[
                :CONST.WORD_LENGTH]
        prev_guesses = prev_guesses + tuple([guess])

        # check if they made the correct guess!
        if guess == secret_word:
            print("Congratulations, you won!")
            print("It took you " + str(total_guesses - remaining_guesses + 1) + " guesses")
            play_again()
            break

        # if asking for potential matches show list
        if guess == "!":
            print("Total: " + str(len(m)) + " " + str(m))
        # if asking for potential matches show list and suggest the best match
        elif guess == "!!":
            print("Total: " + str(len(m)) + " " + str(m))
            print("Suggested guess: " + solver.get_suggestion_stable(k))
            print(k)

        elif len(guess) != CONST.WORD_LENGTH:
            print("Sorry, " + guess + " is not a " + str(len(secret_word)) + " letter word. Try again.")
        elif guess not in wordlist:
            print("Sorry, " + guess + " is not a word I know. Try again.")

        # review guess
        else:
            k = Knowledge.update_knowledge(k, secret_word, guess)
            m = Knowledge.get_possible_matches(k, solver.answers)
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
    prev_guesses = ()

    k = Knowledge.default_knowledge()

    # starting welcome
    print("Welcome to Wordle Helper!")
    print("I help you guess what Wordle word is if it is " + str(CONST.WORD_LENGTH) + " letters long.")
    while remaining_guesses > 0:
        print("\nYou have " + str(remaining_guesses) + " guesses left.")
        print("You will first your guess " + str(
            CONST.WORD_LENGTH) + " letters long to the fist question. Then the response the game gives you.")

        # request guess
        guess = str(input("Type your guess:")).lower()[:CONST.WORD_LENGTH]
        prev_guesses = prev_guesses + tuple([guess])
        print("Type the response you got in order.")
        print("'G' if in the right position")
        print("'Y' yellow if in the word but not in the position, and ")
        print("'R' if not in the word. Example: GRRYR")
        new_knowledge = str(input("Type the response you got:")).upper()
        if len(guess) == CONST.WORD_LENGTH and len(new_knowledge) == CONST.WORD_LENGTH:
            if new_knowledge == "GGGGG":
                print("Congrats! You won in " + str(total_guesses - remaining_guesses + 1) + " guesses!")
                break

            k = Knowledge.update_knowledge_from_colors(k, guess, new_knowledge)

            matches = Knowledge.get_possible_matches(copy.deepcopy(k), solver.answers)
            total_matches = len(matches)
            print("Total: " + str(total_matches) + " " + str(matches))
            hint = str(input("Want a suggestion? (y/n)")).lower()[0]
            if hint == "y":
                print("Suggested guess: " + solver.get_suggestion_stable(k))
                print(k)
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
    WORDS = tuple(Tools.load_words(GUESSES_FILE))
    ANSWERS = WORDS[CONST.ANSWERS_LEN:]

    print("do you want to:")
    print("A. Play Wordle here!")
    print("B. Get help playing wordle somewhere else.")
    print("C. Auto Play to test solver!")
    print("D. Populate DB!")

    menu = str(input("Your Choice:")).lower()
    solver = Solver(WORDS, False)
    if menu == 'a':
        solver = Solver(WORDS, False)
        play_wordle("lefty", WORDS)
        #play_wordle(choose_word(ANSWERS), WORDS)
    elif menu == 'b':
        solver = Solver(WORDS, True)
        suggestions_only()
    elif menu == 'c':
        solver.auto_play("salet")  # todo can do more here
    elif menu == 'd':
        populate_db()
