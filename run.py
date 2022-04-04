# Wordle Game and Solver
# Name: Jon Paris
# Collaborators: Joey Paris, Nathan Paris
import copy
import random
from solver import Solver
from wordle_common import Knowledge, COLORS, Tools, CONST
import string

GUESSES_FILE = "words-guesses.txt"


def choose_word(wordlist):
    return random.choice(wordlist)


def letter_count(answers):
    multi3 = []
    multi4 = []
    for a in answers:
        for i in string.ascii_lowercase:
            if a.count(i) == 3: multi3.append(a)
            if a.count(i) >= 4: multi4.append(a)

    print("words with 3 of the same:", str(multi3))
    print("words with 4 or more of same:", str(multi4))




def play_wordle(secret_word, wordlist):
    total_guesses = 6
    remaining_guesses = 6

    def decorate_word_with_knowledge(kn: list, word: str) -> str:
        decorated_word = ""
        local_in_word = []
        word = list(word)
        for i in range(CONST.WORD_LENGTH):
            c = string.ascii_lowercase.index(word[i])
            p = 26 + 26 * i

            if kn[p] == CONST.YES:
                local_in_word.append(c)
                color = COLORS.GREEN
            elif kn[c] == CONST.YES and (c not in local_in_word or kn[c + 26] == CONST.YES):
                local_in_word.append(c)
                color = COLORS.YELLOW
            else:
                color = COLORS.GREY
            decorated_word += color + string.ascii_lowercase[c] + COLORS.SPACE_COLOR
        return decorated_word + "\n\n"

    def show_decorated_keyboard(kn: list):
        i = 0
        for c in 'qwertyuiopasdfghjklzxcvbnm':
            if c == 'a' or c == 'z':
                print("\n")
            ci = string.ascii_lowercase.index(c)
            in_pos = False
            for j in range(CONST.WORD_LENGTH):
                p = 26 + (26 * j) + ci
                if kn[p] == CONST.YES: in_pos = True

            i += 1
            if in_pos: color = COLORS.GREEN
            elif kn[ci] == CONST.YES: color = COLORS.YELLOW
            elif kn[ci] == CONST.NO: color = COLORS.GREY
            else: color = COLORS.BLACK

            print(color + c, end=COLORS.SPACE_COLOR)
        print("\n")

    # starting welcome
    print("Welcome to Wordle!")
    print("I am thinking of a word that is " + str(CONST.WORD_LENGTH) + " letters long.")
    attempts = ""
    k = CONST.EMPTY_KNOWLEDGE
    m = ANSWERS
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

        elif len(guess) != CONST.WORD_LENGTH:
            print("Sorry, " + guess + " is not a " + str(len(secret_word)) + " letter word. Try again.")
        elif guess not in wordlist:
            print("Sorry, " + guess + " is not a word I know. Try again.")

        # review guess
        else:
            k = Knowledge.update_knowledge(k, secret_word, guess)
            m = solver.get_matches(k)
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

    k = CONST.EMPTY_KNOWLEDGE

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

            matches = solver.get_matches(k)
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
    ANSWERS = WORDS[:CONST.ANSWERS_LEN]

    print("do you want to:")
    print("A. Play Wordle here!")
    print("B. Get help playing wordle somewhere else.")
    print("C. Auto Play to test solver!")
    print("D. Populate DB!")
    print("E. Optimize Solver!")

    menu = str(input("Your Choice:")).lower()
    if menu == 'a':
        solver = Solver(WORDS, True, {"optimize": False})
        play_wordle(choose_word(ANSWERS), WORDS)
    elif menu == 'b':
        solver = Solver(WORDS, True, {"optimize": False})
        suggestions_only()
    elif menu == 'c':
        solver = Solver(WORDS, False, {"optimize": False})
        solver.auto_play("salet")  # todo can do more here
    elif menu == 'd':
        s = Solver(WORDS, False, {"optimize": False})
        s.auto_play()
    elif menu == 'e':
        min_depth = int(input("min_depth for optimization (recommend '0'): "))
        max_depth = int(input("max depth for optimization (recommend '200'): "))
        starting_word = str(input("word starting guess to optimize for (e.g. 'reast'): ")).lower()
        s = Solver(WORDS, False, {"optimize": True, "min": min_depth, "max": max_depth, "starting_word": starting_word})
        s.auto_play()
    elif menu == 'f':
        letter_count(ANSWERS)
    elif menu == 'g':
        s = Solver(WORDS, False, {"optimize": True, "min": 0, "max": 15, "starting_word": ""})
        s.purge_unused()

