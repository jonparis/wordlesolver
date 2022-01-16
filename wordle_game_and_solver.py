# Wordle Game and Solver
# Name: Jon Paris
# Collaborators: Joey Paris, Nathan Paris

import random
import string
import operator
import copy

WORDLIST_FILENAME = "words.txt"
WORD_LENTH = 5

def load_words():
    print("Loading word list...")
    inFile = open(WORDLIST_FILENAME, 'r')
    line = inFile.readline()
    wordlist = line.split()
    choosen_word_length = []
    for x in wordlist:
        if len(x) == WORD_LENTH:
            choosen_word_length.append(x)
    print("  ", len(choosen_word_length), "words loaded.")
    return choosen_word_length

def choose_word(wordlist):
    return random.choice(wordlist)

wordlist = load_words()

def get_available_letter_status(letter_status):
    for i in letter_status:
        if i == 'a' or i == 'z':
            print("\n")
        if letter_status[i]['inposition']:
            print(" \033[0;30;42m " + i, end=" \033[0;37;48m")
        elif letter_status[i]['inword']:
            print(" \033[0;30;43m " + i, end=" \033[0;37;48m")
        elif letter_status[i]['tried']:
            print(" \033[0;30;47m " + i, end=" \033[0;37;48m")
        else:
            print(" \033[0;37;40m " + i, end=" \033[0;37;48m")
    print("\n")

def test_word_for_match(test_word, letter_status):
    '''
    test_word: string with word to test as a possible match
    letter_status: with current status
    returns: boolean, True if the word has 
        a. no letters known not to be in the word is in the word
        b. all the letters known to be found in the word
        c. all letters in the place known places
        d. remove words that have letter in known wrong place
    otherwise, returns False
    '''

    # remove words that include letters known not to be in word
    for i in test_word:
        if letter_status[i]['tried']:
            return False
    for j in letter_status:
        # remove words without letters known to be in the word
        if letter_status[j]['inword'] and j not in test_word:
            return False
        # remove words with letters in known place
        elif letter_status[j]['inposition']:
            for i in letter_status[j]['inposition']:
                if not test_word[i] == j:
                    return False
        else:
            for i in letter_status[j]['notposition']:
                if test_word[i] == j:
                    return False
    return True


def get_possible_matches(letter_status):
    matches = []
    for other_word in wordlist:
        if test_word_for_match(other_word, letter_status):
            matches.append(other_word)
    return matches


def update_letter_status(test_letter_status, secret_word, guess, attempts):
    for i in range(WORD_LENTH):
        if guess[i] == secret_word[i]:
            test_letter_status[guess[i]]['inword'] = True
            if not test_letter_status[guess[i]]['inposition']:
                test_letter_status[guess[i]]['inposition'] = [i]
            else:
                test_letter_status[guess[i]]['inposition'].append(i)
            attempts += " \033[0;30;42m " + guess[i] + " \033[0;37;48m"
        elif guess[i] in secret_word:
            test_letter_status[guess[i]]['inword'] = True
            test_letter_status[guess[i]]['notposition'].append(i)
            attempts += " \033[0;30;43m " + guess[i] + " \033[0;37;48m"
        else:
            test_letter_status[guess[i]]['tried'] = True
            attempts += " \033[0;30;47m " + guess[i] + " \033[0;37;48m"
    attempts += "\n\n"
    return {"letter_status": test_letter_status, "attempts": attempts}


def show_possible_matches(letter_status, suggest_guess):
    '''
    returns: nothing, print out every word in wordlist that matches letter location
    '''
    matches = get_possible_matches(copy.deepcopy(letter_status))
    print(matches)

    if suggest_guess:
        # For each word in word_list and how many remaining matched would exist if guessed
        # The sum for every potential word is the word_reductive_power
        # The word with the lowest sum has the most reductive power
        # Suggest the word with the more reductive power
        reductive_power = {}

        # test every word possible word for reductive power for every remaining potential word (note: not efficent!)
        for example_secret_word in matches:
            for sample_guess in wordlist:
                test_status = update_letter_status(copy.deepcopy(letter_status), example_secret_word,
                                                   sample_guess, "")
                if sample_guess not in reductive_power.keys():
                    reductive_power[sample_guess] = 0
                reductive_power[sample_guess] += len(get_possible_matches(test_status['letter_status']))

        # rank potential guesses
        sorted_reductive_power = sorted(reductive_power.items(), key=operator.itemgetter(1))
        best_guesses_up_to_ten = list(sorted_reductive_power)[:10]

        print("The best guesses are " + str(best_guesses_up_to_ten))


def play_wordle(secret_word, wordlist):
    remaining_guesses = 6
    qwerty = 'qwertyuiopasdfghjklzxcvbnm'
    letter_status = {}
    for i in qwerty:
        letter_status[i] = {"tried": False, "inposition": False, "inword": False, "notposition": []}

    # starting welcome
    print("Welcome to Wordle!")
    print("I am thinking of a word that is " + str(len(secret_word)) + " letters long.")
    message = ""
    attempts = ""
    while remaining_guesses > 0:
        print("\nYou have " + str(remaining_guesses) + " guesses left.")
        print("Type a " + str(WORD_LENTH) + " letter word, ! for potential word, or !! for potential words with a suggestion")

        get_available_letter_status(letter_status)  # prints keyboard

        # request guess
        guess = str(input("Please guess a word " + str(len(secret_word)) + " letters long: ")).lower()[:WORD_LENTH]

        # check if they made the correct guess!
        if guess == secret_word:
            print("Congratulations, you won!")
            play_wordle(choose_word(wordlist), wordlist)

        # if asking for potential matches show list
        if guess == "!":
            show_possible_matches(letter_status, False)
        # if asking for potential matches show list and suggest the best match
        elif guess == "!!":
            show_possible_matches(letter_status, True)
        elif len(guess) != WORD_LENTH:
            print("Sorry, " + guess + " is not a " + str(len(secret_word)) + " letter word. Try again.")
        elif guess not in wordlist:
            print("Sorry, " + guess + " is not a word I know. Try again.")

        # review guess
        else:
            new_letter_status = update_letter_status(letter_status, secret_word, guess, attempts)
            letter_status = new_letter_status['letter_status']
            attempts = new_letter_status['attempts']
            print(attempts)
            remaining_guesses -= 1
            if remaining_guesses == 0:
                print("Sorry, you ran out of guesses. The word was " + secret_word + ".")
                play_wordle(choose_word(wordlist), wordlist)


if __name__ == "__main__":
    play_wordle(choose_word(wordlist), wordlist)
    # Try for a specific word
    # chose_word = "panic
    # play_wordle(chose_word, wordlist)