# Wordle Game and Solver
# Name: Jon Paris
# Collaborators: Joey Paris, Nathan Paris

import random
import string
import operator
import copy
import time

WORDLIST_FILENAME = "words.txt"
WORD_LENGTH = 5
NOT_IN_WORD = "NIW"
IN_WORD = "IW"
IN_POSITION = "IP"
NOT_IN_POSITION = "NIP"
QWERTY = 'qwertyuiopasdfghjklzxcvbnm'

GREEN = " \033[0;30;42m "
BLACK = " \033[0;37;40m "
YELLOW = " \033[0;30;43m "
GREY = " \033[0;30;47m "
SPACE_COLOR = " \033[0;37;48m"


def load_words():
    print("Loading word list...")
    inFile = open(WORDLIST_FILENAME, 'r')
    line = inFile.readline()
    wordlist = line.split()
    choosen_word_length = []
    for x in wordlist:
        if len(x) == WORD_LENGTH:
            choosen_word_length.append(x)
    print("  ", len(choosen_word_length), "words loaded.")
    return choosen_word_length


def choose_word(wordlist):
    return random.choice(wordlist)


wordlist = load_words()


def get_available_knowledge(knowledge):
    for i in knowledge:
        if i == 'a' or i == 'z':
            print("\n")
        if knowledge[i][IN_POSITION]:
            print(GREEN + i, end=SPACE_COLOR)
        elif knowledge[i][IN_WORD]:
            print(YELLOW + i, end=SPACE_COLOR)
        elif knowledge[i][NOT_IN_WORD]:
            print(GREY + i, end=SPACE_COLOR)
        else:
            print(BLACK + i, end=SPACE_COLOR)
    print("\n")


def test_word_for_match(test_word, knowledge):
    '''
    test_word: string with word to test as a possible match
    knowledge: with current status
    returns: boolean, True if the word has 
        a. no letters known not to be in the word is in the word
        b. all the letters known to be found in the word
        c. all letters in the place known places
        d. remove words that have letter in known wrong place
    otherwise, returns False
    '''

    # remove words that include letters known not to be in word
    for i in test_word:
        if knowledge[i][NOT_IN_WORD]:
            return False
    for j in knowledge:
        # remove words without letters known to be in the word
        if knowledge[j][IN_WORD] and j not in test_word:
            return False
        # remove words with letters in known place
        elif knowledge[j][IN_POSITION]:
            for i in knowledge[j][IN_POSITION]:
                if not test_word[i] == j:
                    return False
        else:
            for i in knowledge[j][NOT_IN_POSITION]:
                if test_word[i] == j:
                    return False
    return True


def get_possible_matches(knowledge):
    matches = []
    for word in wordlist:
        if test_word_for_match(word, knowledge):
            matches.append(word)
    return matches


def generate_exclusion_knowledge(secret_word_options, guess_options):
    # WIP use exclusion map and combine knowledge to figure out which words will reduce knowledge the most
    exclusions_by_guess = {}
    total_matches = len(secret_word_options)
    count = 0
    start_time = time.time()

    for guess in guess_options:
        exclusions_by_guess[guess] = 0

    for secret in secret_word_options:
        # Set timer to make sure the process won't take too long
        time_now = time.time()
        elapsed_minutes = (time_now - start_time) / 60
        progress = count / total_matches
        progress_to_finish = 1 - count / total_matches

        if progress == 0:
            time_left = "TBD"
        else:
            time_left = str(round(elapsed_minutes * progress_to_finish / progress, 0))

        print(str(round(progress * 100, 2)) + "% done over ~" + str(
            round(elapsed_minutes, 1)) + " minutes. Estimated " + time_left + " minutes left")
        count += 1
        # END TIMER CODE

        for guess in guess_options:
            for answer in secret_word_options:
                if not test_word_for_match(answer, update_knowledge(default_knowledge(), secret, guess)):
                    exclusions_by_guess[guess] += 1
    # sort
    exclusions_by_guess = sorted(exclusions_by_guess.items(), key=operator.itemgetter(1), reverse=True)
    return list(exclusions_by_guess)[:10]


def update_knowledge(knowledge, secret_word, guess):
    for i in range(WORD_LENGTH):
        if guess[i] == secret_word[i]:
            knowledge[guess[i]][IN_WORD] = True
            knowledge[guess[i]][IN_POSITION].append(i)
        elif guess[i] in secret_word:
            knowledge[guess[i]][IN_WORD] = True
            knowledge[guess[i]][NOT_IN_POSITION].append(i)
        else:
            knowledge[guess[i]][NOT_IN_WORD] = True
    return knowledge


def default_knowledge():
    knowledge = {}
    for i in QWERTY:
        knowledge[i] = {NOT_IN_WORD: 0, IN_POSITION: [], IN_WORD: 0, NOT_IN_POSITION: []}
    return knowledge


def combined_knowledge(k1, k2):
    for i in QWERTY:
        combined_knowledge[i][NOT_IN_WORD] = k1[i][NOT_IN_WORD] + k2[i][NOT_IN_WORD]
        combined_knowledge[i][IN_WORD] = k1[i][IN_WORD] + k2[i][IN_WORD]
        combined_knowledge[i][NOT_IN_POSITION] = list(set(k1[i][IN_POSITION] + k2[i][IN_POSITION]))
        combined_knowledge[i][NOT_IN_POSITION] = list(set(k1[i][NOT_IN_POSITION] + k2[i][NOT_IN_POSITION]))
    return combined_knowledge


def decorate_word_with_knowledge(knowledge, word):
    decorated_word = ""
    for i in range(WORD_LENGTH):
        if i in knowledge[word[i]][IN_POSITION]:
            decorated_word += GREEN + word[i] + SPACE_COLOR
        elif knowledge[word[i]][IN_WORD]:
            decorated_word += YELLOW + word[i] + SPACE_COLOR
        elif knowledge[word[i]][NOT_IN_WORD]:
            decorated_word += GREY + word[i] + SPACE_COLOR
        else:
            decorated_word += " " + word[i] + " "
    return decorated_word + "\n\n"


def show_possible_matches(knowledge, suggest_guess):
    '''
    returns: nothing, print out every word in wordlist that matches letter location
    '''
    matches = get_possible_matches(copy.deepcopy(knowledge))
    print(matches)

    if suggest_guess:
        # For each word in word_list and how many remaining matched would exist if guessed
        # The sum for every potential word is the word_reductive_power
        # The word with the lowest sum has the most reductive power
        # Suggest the word with the more reductive power

        """
        reductive_power = {}

        # test every word possible word for reductive power for every remaining potential word (note: not efficent!)
        total_matches = len(matches)
        count = 0
        start_time = time.time()
        for example_secret_word in matches:
            time_now = time.time()
            elapsed_minutes = (time_now - start_time) / 60
            progress = count / total_matches
            progress_to_finish = 1 - count / total_matches

            if progress == 0:
                time_left = "TBD"
            else:
                time_left = str(round(elapsed_minutes * progress_to_finish / progress, 0))

            print(str(round(progress * 100, 2)) + "% done over ~" + str(
                round(elapsed_minutes, 1)) + " minutes. Estimated " + time_left + " minutes left")
            count += 1
            for sample_guess in wordlist:
                test_status = update_knowledge(copy.deepcopy(knowledge), example_secret_word,
                                                   sample_guess, "")
                if sample_guess not in reductive_power.keys():
                    reductive_power[sample_guess] = 0
                reductive_power[sample_guess] += len(get_possible_matches(test_status['knowledge']))

        # rank potential guesses
        sorted_reductive_power = sorted(reductive_power.items(), key=operator.itemgetter(1))
        best_guesses_up_to_ten = list(sorted_reductive_power)[:10]
        """

        print("The best guesses are " + str(generate_exclusion_knowledge(matches, wordlist)))


def play_wordle(secret_word, wordlist):
    remaining_guesses = 6
    knowledge = default_knowledge()

    # starting welcome
    print("Welcome to Wordle!")
    print("I am thinking of a word that is " + str(len(secret_word)) + " letters long.")
    message = ""
    attempts = ""
    while remaining_guesses > 0:
        print("\nYou have " + str(remaining_guesses) + " guesses left.")
        print("Type a " + str(
            WORD_LENGTH) + " letter word, ! for potential word, or !! for potential words with a suggestion")

        get_available_knowledge(knowledge)  # prints keyboard

        # request guess
        guess = str(input("Please guess a word " + str(len(secret_word)) + " letters long: ")).lower()[:WORD_LENGTH]

        # check if they made the correct guess!
        if guess == secret_word:
            print("Congratulations, you won!")
            play_wordle(choose_word(wordlist), wordlist)

        # if asking for potential matches show list
        if guess == "!":
            show_possible_matches(knowledge, False)
        # if asking for potential matches show list and suggest the best match
        elif guess == "!!":
            show_possible_matches(knowledge, True)
        elif len(guess) != WORD_LENGTH:
            print("Sorry, " + guess + " is not a " + str(len(secret_word)) + " letter word. Try again.")
        elif guess not in wordlist:
            print("Sorry, " + guess + " is not a word I know. Try again.")

        # review guess
        else:
            knowledge = update_knowledge(knowledge, secret_word, guess)
            attempts += decorate_word_with_knowledge(knowledge, guess)
            print(attempts)
            remaining_guesses -= 1
            if remaining_guesses == 0:
                print("Sorry, you ran out of guesses. The word was " + secret_word + ".")
                play_wordle(choose_word(wordlist), wordlist)


if __name__ == "__main__":
    play_wordle(choose_word(wordlist), wordlist)
    # Try for a specific word
    # chose_word = "panic"
    # play_wordle(chose_word, wordlist)
