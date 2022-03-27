import copy
import string
import time
import datetime
import hashlib
import json
import cProfile


# noinspection PyClassHasNoInit
class CONST:
    NOT_IN_WORD = "NIW"
    IN_WORD = "IW"
    IN_MULTI = "IM"
    NOT_IN_MULTI = "NIM"
    IN_POSITION = "IP"
    NOT_IN_POSITION = "NIP"
    WORD_LENGTH = 5
    ANSWERS_LEN = 2315
    GUESSES_LEN = 12972
    PER = 4  # confidence cannot be improved upon unless guess/answer list changes
    HIGH = 3  # confidence in guess after reviewing all guesses. Only needs update better sub_guess is found
    MED = 2  # confidence in guess after full optimization
    LOW = 1  # confidence in guess low, default after quick optimization
    VERY_LOW = 0  # confidence in guess very low needs optimizing
    YES = 2  # letter in position or word
    NO = 1  # letter not in position / word
    UNSURE = 0  # unsure if letter in position / word
    # kmap object positions
    GUESS = 0  # guess
    AGTS = 1  # average_guesses_to_solve
    C = 2  # confidence
    M = 3  # match_count
    OPT = 4  # optimized_to


# noinspection PyClassHasNoInit
class Knowledge:

    @staticmethod
    def update_knowledge(k: tuple, secret_word: str, guess: str) -> tuple:
        k = list(k)
        d = Knowledge.empty_k_list()  # use to track in-word in-multi locally
        guess = list(str(guess).lower())  # make sure guess is in lower case
        secret_word = list(secret_word)
        for i in range(CONST.WORD_LENGTH):
            guess[i] = string.ascii_lowercase.index(guess[i])
            secret_word[i] = string.ascii_lowercase.index(secret_word[i])
        for i in range(CONST.WORD_LENGTH):
            c = guess[i]
            if c == secret_word[i]:
                guess[i] = secret_word[i] = ""
                if d[c] == CONST.YES: k[c + 26] = d[c + 26] = CONST.YES
                k[c] = d[c] = CONST.YES
                k[c + (2 * 26) + (26 * i)] = CONST.YES
        for i in range(CONST.WORD_LENGTH):
            c = guess[i]
            if c != "":
                if c in secret_word:
                    p = secret_word.index(c)
                    guess[i] = secret_word[p] = ""
                    if d[c] == CONST.YES: k[c + 26] = d[c + 26] = CONST.YES
                    k[c] = d[c] = CONST.YES
                    k[c + (2 * 26) + (26 * i)] = CONST.NO
                else:
                    if d[c] != CONST.YES: k[c] = d[c] = CONST.NO
                    elif d[c + 26] != CONST.YES: k[c + 26] = d[c + 26] = CONST.NO
                    k[c + (2 * 26) + (26 * i)] = CONST.NO
        return tuple(k)

    @staticmethod
    def update_knowledge_from_colors(k: tuple, guess: str, color_feedback: str) -> tuple:
        k = list(k)
        d = Knowledge.empty_k_list()
        guess = list(str(guess).lower())  # make sure guess is in lower case
        color_feedback = list(color_feedback.upper())
        for i in range(CONST.WORD_LENGTH):
            guess[i] = string.ascii_lowercase.index(guess[i])
        for i in range(CONST.WORD_LENGTH):
            c = guess[i]
            if color_feedback[i] == "G":
                guess[i] = ""
                if d[c] == CONST.YES: k[c + 26] = d[c + 26] = CONST.YES
                k[c] = d[c] = CONST.YES
                k[c + (2 * 26) + (26 * i)] = CONST.YES
        for i in range(CONST.WORD_LENGTH):
            c = guess[i]
            if color_feedback[i] == "Y":
                guess[i] = ""
                if d[c] == CONST.YES: k[c + 26] = d[c + 26] = CONST.YES
                k[c] = d[c] = CONST.YES
                k[c + (2 * 26) + (26 * i)] = CONST.NO
        for i in range(CONST.WORD_LENGTH):
            c = guess[i]
            if color_feedback[i] == "Y" and c != "":
                if d[c] != CONST.YES: k[c] = d[c] = CONST.NO
                elif d[c + 26] != CONST.YES: k[c + 26] = d[c + 26] = CONST.NO
                k[c + (2 * 26) + (26 * i)] = CONST.NO
        return tuple(k)

    @staticmethod
    def k_int_to_list(k_int: int) -> tuple:
        if k_int == 0: return [0]
        k_list = []
        list_len = 7 * 26
        while k_int:
            k_list.append(int(k_int % 3))
            k_int //= 3
        for _ in range(list_len - len(k_list)): k_list.append(0)
        return tuple(k_list)  # [::-1] uncomment to reverse

    @staticmethod
    def k_list_to_int(k_list: tuple) -> int:
        k_int = 0
        for i in range(len(k_list)): k_int += k_list[i] * 3 ** i
        return k_int

    @staticmethod
    def empty_k_list():
        k_list = []
        # not or in word, not or in multi, then not or in position
        for _ in range(26 + 26 + 26 * CONST.WORD_LENGTH): k_list.append(0)
        return k_list

    @staticmethod
    def default_knowledge():
        return tuple(Knowledge.empty_k_list())


# noinspection PyClassHasNoInit
class Tools:

    first_words = ("salet", "reast", "crate", "trace", "slate", "crane","raise", "raile", "soare", "arise", "irate", "orate", "ariel", "arose", "raine", "artel", "taler", "ratel", "ocean", "steal")

    @staticmethod
    def load_words(file_name):
        print("Loading word list...")
        infile = open(file_name, 'r')
        line = infile.readline()
        infile.close()
        wordlist = line.split()
        chosen_word_length = []
        for x in wordlist:
            if len(x) == CONST.WORD_LENGTH:
                chosen_word_length.append(x)
        print("  ", len(chosen_word_length), "words loaded.")
        return chosen_word_length

    @staticmethod
    def profileme(func):
        def profiled(*args, **kwargs):
            profile = cProfile.Profile()
            try:
                profile.enable()
                result = func(*args, **kwargs)
                profile.disable()
                return result
            finally:
                profile.print_stats()

        return profiled


# noinspection PyClassHasNoInit
class COLORS:
    GREEN = " \033[0;30;42m "
    BLACK = " \033[0;37;40m "
    YELLOW = " \033[0;30;43m "
    GREY = " \033[0;30;47m "
    SPACE_COLOR = " \033[0;37;48m"
