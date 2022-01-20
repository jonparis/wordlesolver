# Wordle Game and Solver
# Name: Jon Paris
# Collaborators: Joey Paris, Nathan Paris
import copy
import random
from wordleTools import KNOWLEDGE, WordleTools

WORDLIST_FILENAME = "words.txt"


class COLORS:
    GREEN = " \033[0;30;42m "
    BLACK = " \033[0;37;40m "
    YELLOW = " \033[0;30;43m "
    GREY = " \033[0;30;47m "
    SPACE_COLOR = " \033[0;37;48m"


def load_words():
    print("Loading word list...")
    infile = open(WORDLIST_FILENAME, 'r')
    line = infile.readline()
    wordlist = line.split()
    chosen_word_length = []
    for x in wordlist:
        if len(x) == KNOWLEDGE.WORD_LENGTH:
            chosen_word_length.append(x)
    print("  ", len(chosen_word_length), "words loaded.")
    return chosen_word_length


def choose_word(wordlist):
    return random.choice(wordlist)


def play_wordle(secret_word, wordlist):
    total_guesses = 6
    remaining_guesses = 6

    def decorate_word_with_knowledge(know, word):
        decorated_word = ""
        for i in range(KNOWLEDGE.WORD_LENGTH):
            c = word[i]
            k = know[str(i)]
            if c == k[KNOWLEDGE.IN_POSITION]:
                color = COLORS.GREEN
            elif c in know[KNOWLEDGE.IN_WORD]:
                color = COLORS.YELLOW
            elif c in know[KNOWLEDGE.NOT_IN_WORD]:
                color = COLORS.GREY
            else:
                color = " "
            decorated_word += color + c + COLORS.SPACE_COLOR
        return decorated_word + "\n\n"

    def show_decorated_keyboard(know):
        for c in 'qwertyuiopasdfghjklzxcvbnm':
            if c == 'a' or c == 'z':
                print("\n")
            in_position = False
            for i in range(KNOWLEDGE.WORD_LENGTH):
                k = know[str(i)]
                if c == k[KNOWLEDGE.IN_POSITION]:
                    in_position = True
            if in_position:
                color = COLORS.GREEN
            elif c in know[KNOWLEDGE.IN_WORD]:
                color = COLORS.YELLOW
            elif c in know[KNOWLEDGE.NOT_IN_WORD]:
                color = COLORS.GREY
            else:
                color = COLORS.BLACK
            print(color + c, end=COLORS.SPACE_COLOR)
        print("\n")

    # starting welcome
    print("Welcome to Wordle!")
    print("I am thinking of a word that is " + str(KNOWLEDGE.WORD_LENGTH) + " letters long.")
    attempts = ""
    knowledge = WordleTools.default_knowledge()

    while remaining_guesses > 0:
        print("\nYou have " + str(remaining_guesses) + " guesses left.")
        print("Type a " + str(
            KNOWLEDGE.WORD_LENGTH) + " letter word, ! for potential word, or !! for potential words with a suggestion")

        show_decorated_keyboard(knowledge)  # prints keyboard

        # request guess
        guess = str(input("Please guess a word " + str(len(secret_word)) + " letters long: ")).lower()[
                :KNOWLEDGE.WORD_LENGTH]

        # check if they made the correct guess!
        if guess == secret_word:
            print("Congratulations, you won!")
            print("It took you " + str(total_guesses - remaining_guesses + 1) + " guesses")
            play_again()
            break

        # if asking for potential matches show list
        if guess == "!":
            matches = WordleTools.get_possible_matches(knowledge, WORDS)
            print("Total: " + str(len(matches)) + " " + str(matches))
        # if asking for potential matches show list and suggest the best match
        elif guess == "!!":
            matches = WordleTools.get_possible_matches(knowledge, WORDS)
            print("Total: " + str(len(matches)) + " " + str(matches))
            print("alt fast option:" + WordleTools.get_suggestion_fast(knowledge, WORDS))
            print("Suggested guess: " + WordleTools.get_suggestion(copy.deepcopy(knowledge), WORDS))
        elif len(guess) != KNOWLEDGE.WORD_LENGTH:
            print("Sorry, " + guess + " is not a " + str(len(secret_word)) + " letter word. Try again.")
        elif guess not in wordlist:
            print("Sorry, " + guess + " is not a word I know. Try again.")

        # review guess
        else:
            knowledge = WordleTools.update_knowledge(knowledge, secret_word, guess)
            attempts += decorate_word_with_knowledge(knowledge, guess)
            print(attempts)
            remaining_guesses -= 1
            if remaining_guesses == 0:
                print("Sorry, you ran out of guesses. The word was " + secret_word + ".")
                play_again()
                break


def suggestions_only():
    total_guesses = 6
    remaining_guesses = total_guesses

    knowledge = WordleTools.default_knowledge()

    # starting welcome
    print("Welcome to Wordle Helper!")
    print("I help you guess what Wordle word is if it is " + str(KNOWLEDGE.WORD_LENGTH) + " letters long.")
    while remaining_guesses > 0:
        print("\nYou have " + str(remaining_guesses) + " guesses left.")
        print("You will first your guess " + str(
            KNOWLEDGE.WORD_LENGTH) + " letters long to the fist question. Then the response the game gives you.")

        # request guess
        guess = str(input("Type your guess:")).lower()[:KNOWLEDGE.WORD_LENGTH]
        print("Type the response you got in order.")
        print("'G' if in the right position")
        print("'Y' yellow if in the word but not in the position, and ")
        print("'R' if not in the word. Example: GRRYR")
        new_knowledge = str(input("Type the response you got:")).upper()
        if len(guess) == KNOWLEDGE.WORD_LENGTH and len(new_knowledge) == KNOWLEDGE.WORD_LENGTH:
            if new_knowledge == "GGGGG":
                print("Congrats! You won in " + str(total_guesses - remaining_guesses + 1) + " guesses!")
                break
            for i in range(len(guess)):
                c = guess[i]
                res = str(new_knowledge[i])
                k = knowledge[str(i)]
                if res == 'G':
                    if c not in knowledge[KNOWLEDGE.IN_WORD]:
                        knowledge[KNOWLEDGE.IN_WORD].append(c)
                    k[KNOWLEDGE.IN_POSITION] = c
                elif res == 'Y':
                    if c not in k[KNOWLEDGE.NOT_IN_POSITION]:
                        k[KNOWLEDGE.NOT_IN_POSITION].append(c)
                    if c not in knowledge[KNOWLEDGE.IN_WORD]:
                        knowledge[KNOWLEDGE.IN_WORD].append(c)
                else:
                    if c not in knowledge[KNOWLEDGE.NOT_IN_WORD]:
                        knowledge[KNOWLEDGE.NOT_IN_WORD].append(c)

            matches = WordleTools.get_possible_matches(copy.deepcopy(knowledge), WORDS)
            total_matches = len(matches)
            print("Total: " + str(total_matches) + " " + str(matches))

            hint = str(input("Want a suggestion? (y/n)")).lower()[0]
            if hint == "y":
                print("alt fast option:" + WordleTools.get_suggestion_fast(knowledge, WORDS))
                print("Suggested guess: " + WordleTools.get_suggestion(knowledge, WORDS))

            remaining_guesses -= 1
        else:
            print("try again. either your guess or feedback was the wrong length")


def play_again():
    again = str(input("Play Again? (y/n)")).lower()[0]
    if again == "y":
        play_wordle(choose_word(WORDS), WORDS)
    else:
        print("bye!")


if __name__ == "__main__":
    # Play wordle mode
    WORDS = load_words()
    print("do you want to:")
    print("A. Play Wordle here!")
    print("B. Get help playing wordle somewhere else.")

    menu = str(input(" Choose/type A or B:")).lower()
    if menu == 'a':
        play_wordle(choose_word(WORDS), WORDS)
    else:
        suggestions_only()
