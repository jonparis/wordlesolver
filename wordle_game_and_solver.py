# Wordle Game and Solver
# Name: Jon Paris
# Collaborators: Joey Paris, Nathan Paris

import random
from random import sample
import time
import datetime

WORDLIST_FILENAME = "words.txt"
WORD_LENGTH = 5


class KNOWLEDGE:
    NOT_IN_WORD = "NIW"
    IN_WORD = "IW"
    IN_POSITION = "IP"
    NOT_IN_POSITION = "NIP"


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
        if len(x) == WORD_LENGTH:
            chosen_word_length.append(x)
    print("  ", len(chosen_word_length), "words loaded.")
    return chosen_word_length


def choose_word(wordlist):
    return random.choice(wordlist)


class Tools:
    @staticmethod
    def test_word_for_match(test_word, knowledge):
        # remove words that include letters known not to be in word
        for c in knowledge[KNOWLEDGE.IN_WORD]:
            if c not in test_word:
                return False
        for i in range(WORD_LENGTH):
            c = test_word[i]
            k = knowledge[str(i)]
            if c in knowledge[KNOWLEDGE.NOT_IN_WORD]:
                return False
            if k[KNOWLEDGE.IN_POSITION] and c != k[KNOWLEDGE.IN_POSITION]:
                return False
            if c in k[KNOWLEDGE.NOT_IN_POSITION]:
                return False
        return True

    @staticmethod
    def get_possible_matches(knowledge, possible_words):
        matches = []
        for word in possible_words:
            if Tools.test_word_for_match(word, knowledge):
                matches.append(word)
        return matches

    @staticmethod
    def get_suggestion(secret_word_options, guess_options):
        # WIP use exclusion map and combine knowledge to figure out which words will increase knowledge the most
        exclusions_by_guess = {}
        total_matches = len(secret_word_options)
        count = 0
        start_time = time.time()
        show_timer = True

        for guess in guess_options:
            exclusions_by_guess[guess] = 0

        sample_count = 200

        if total_matches < 100:
            sample_count = total_matches
        for secret in sample(secret_word_options, sample_count):
            # Set timer to make sure the process won't take too long
            time_now = time.time()
            elapsed_time = int(time_now - start_time)
            progress = count / total_matches
            progress_to_finish = 1 - count / total_matches

            if progress == 0:
                time_left_str = "TBD"
            else:
                time_left = int(elapsed_time * progress_to_finish / progress)
                time_left_str = str(datetime.timedelta(seconds=time_left))

            if show_timer:
                print("{0}% done over ~{1}. Estimated {2} time left".format(str(round(progress * 100, 2)),
                                                                            str(datetime.timedelta(
                                                                                seconds=elapsed_time)),
                                                                            time_left_str))
            count += 1
            # END TIMER CODE

            for guess in guess_options:
                for answer in secret_word_options:
                    if not Tools.test_word_for_match(answer, Tools.update_knowledge(Tools.default_knowledge(), secret, guess)):
                        exclusions_by_guess[guess] += 1 / total_matches
        # sort
        suggested_guess = ""
        max_excl = 0
        for g in exclusions_by_guess:
            if exclusions_by_guess[g] > max_excl or not suggested_guess:
                max_excl = exclusions_by_guess[g]
                suggested_guess = g

        return suggested_guess

    @staticmethod
    def update_knowledge(knowledge, secret_word, guess):
        for i in range(WORD_LENGTH):
            k = knowledge[str(i)]
            c = guess[i]
            if c == secret_word[i]:
                if c not in knowledge[KNOWLEDGE.IN_WORD]:
                    knowledge[KNOWLEDGE.IN_WORD].append(c)
                k[KNOWLEDGE.IN_POSITION] = c
            elif c in secret_word:
                if c not in knowledge[KNOWLEDGE.IN_WORD]:
                    knowledge[KNOWLEDGE.IN_WORD].append(c)
                if c not in k[KNOWLEDGE.NOT_IN_POSITION]:
                    k[KNOWLEDGE.NOT_IN_POSITION].append(c)
            else:
                if c not in knowledge[KNOWLEDGE.NOT_IN_WORD]:
                    knowledge[KNOWLEDGE.NOT_IN_WORD].append(c)
        return knowledge

    @staticmethod
    def default_knowledge():
        knowledge = {KNOWLEDGE.IN_WORD: [], KNOWLEDGE.NOT_IN_WORD: []}
        for i in range(WORD_LENGTH):
            knowledge[str(i)] = {KNOWLEDGE.NOT_IN_POSITION: [], KNOWLEDGE.IN_POSITION: False}
        return knowledge


def play_wordle(secret_word, wordlist):
    total_guesses = 6
    remaining_guesses = 6
    knowledge = Tools.default_knowledge()

    def decorate_word_with_knowledge(knowledge, word):
        decorated_word = ""
        for i in range(WORD_LENGTH):
            c = word[i]
            k = knowledge[str(i)]
            if c == k[KNOWLEDGE.IN_POSITION]:
                color = COLORS.GREEN
            elif c in knowledge[KNOWLEDGE.IN_WORD]:
                color = COLORS.YELLOW
            elif c in knowledge[KNOWLEDGE.NOT_IN_WORD]:
                color = COLORS.GREY
            else:
                color = " "
            decorated_word += color + c + COLORS.SPACE_COLOR
        return decorated_word + "\n\n"

    def show_decorated_keyboard(knowledge):
        for c in 'qwertyuiopasdfghjklzxcvbnm':
            if c == 'a' or c == 'z':
                print("\n")
            in_position = False
            for i in range(WORD_LENGTH):
                k = knowledge[str(i)]
                if c == k[KNOWLEDGE.IN_POSITION]:
                    in_position = True
            if in_position:
                color = COLORS.GREEN
            elif c in knowledge[KNOWLEDGE.IN_WORD]:
                color = COLORS.YELLOW
            elif c in knowledge[KNOWLEDGE.NOT_IN_WORD]:
                color = COLORS.GREY
            else:
                color = COLORS.BLACK
            print(color + c, end=COLORS.SPACE_COLOR)
        print("\n")

    # starting welcome
    print("Welcome to Wordle!")
    print("I am thinking of a word that is " + str(WORD_LENGTH) + " letters long.")
    attempts = ""
    while remaining_guesses > 0:
        print("\nYou have " + str(remaining_guesses) + " guesses left.")
        print("Type a " + str(
            WORD_LENGTH) + " letter word, ! for potential word, or !! for potential words with a suggestion")

        show_decorated_keyboard(knowledge)  # prints keyboard

        # request guess
        guess = str(input("Please guess a word " + str(len(secret_word)) + " letters long: ")).lower()[:WORD_LENGTH]

        # check if they made the correct guess!
        if guess == secret_word:
            print("Congratulations, you won!")
            print("It took you " + str(total_guesses - remaining_guesses + 1) + " guesses")
            play_again()
            break

        # if asking for potential matches show list
        if guess == "!":
            matches = Tools.get_possible_matches(knowledge, WORDS)
            print("Total: " + str(len(matches)) + " " + str(matches))
        # if asking for potential matches show list and suggest the best match
        elif guess == "!!":
            matches = Tools.get_possible_matches(knowledge, WORDS)
            print("Total: " + str(len(matches)) + " " + str(matches))
            if len(matches) > 5:
                print("Suggested guess: " + Tools.get_suggestion(matches, WORDS))
            else:
                print("Suggested guess: " + Tools.get_suggestion(matches, matches))
        elif len(guess) != WORD_LENGTH:
            print("Sorry, " + guess + " is not a " + str(len(secret_word)) + " letter word. Try again.")
        elif guess not in wordlist:
            print("Sorry, " + guess + " is not a word I know. Try again.")

        # review guess
        else:
            knowledge = Tools.update_knowledge(knowledge, secret_word, guess)
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

    knowledge = Tools.default_knowledge()

    # starting welcome
    print("Welcome to Wordle Helper!")
    print("I help you guess what Wordle word is if it is " + str(WORD_LENGTH) + " letters long.")
    while remaining_guesses > 0:
        print("\nYou have " + str(remaining_guesses) + " guesses left.")
        print("You will first your guess " + str(
            WORD_LENGTH) + " letters long to the fist question. Then the response the game gives you.")

        # request guess
        guess = str(input("Type your guess:")).lower()[:WORD_LENGTH]
        print(
            "Type the response you got in order. 'G' if in the right position, 'Y' yellow if in the word but not in the position, and 'R' if not in the word. Example: GRRYR")
        new_knowledge = str(input("Type the response you got:")).upper()
        if len(guess) == WORD_LENGTH and len(new_knowledge) == WORD_LENGTH:
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

            matches = Tools.get_possible_matches(knowledge, WORDS)
            total_matches = len(matches)
            if total_matches < 1:
                print("something went wrong. Start over")
                break
            print("There are " + str(len(matches)) + " possible matches.")
            print(matches)
            matches = Tools.get_possible_matches(knowledge, WORDS)
            print("Total: " + str(len(matches)) + " " + str(matches))
            if len(matches) > 5:
                print("Suggested guess: " + Tools.get_suggestion(matches, WORDS))
            else:
                print("Suggested guess: " + Tools.get_suggestion(matches, matches))
            hint = str(input("Want a suggestion? (y/n)")).lower()[0]
            if hint == "y":
                if total_matches > 4000:
                    print("Try 'argue'")
                elif total_matches < 5:
                    print("Suggested guess: " + Tools.get_suggestion(matches, matches))
                else:
                    print("this may take some time")
                    print("Suggested guess: " + Tools.get_suggestion(matches, WORDS))
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
