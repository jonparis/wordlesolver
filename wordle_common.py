import copy
import string
import time
import datetime
import hashlib
import json
import cProfile


# noinspection PyClassHasNoInit
class CONST:
    WORD_LENGTH = 5
    ANSWERS_LEN = 2315
    GUESSES_LEN = 12972

    start_option = 1
    # KNOWLEDGE ORDER: WORD / POS / MULTI2 / MULTI3
    if start_option == 1:
        MULTI2 = 26 * (1 + WORD_LENGTH)  # where in knowledge list info on 2+ characters stored
        MULTI3 = MULTI2 + 26  # where in knowledge list, info on 3+ characters stored
        POSITION_START = 26
        WORD_K_START = 0

    # KNOWELEDGE ORDER: MULTI3 / MULTI2 / POS / WORD
    if start_option == 2:
        MULTI3 = 0  # where in knowledge list, info on 3+ characters stored
        MULTI2 = 26  # where in knowledge list info on 2+ characters stored
        POSITION_START = 52
        WORD_K_START = (2 + WORD_LENGTH) * 26
    
    YES = 2  # letter in position or word
    NO = 1  # letter not in position / word
    UNSURE = 0  # unsure if letter in position / word
    EMPTY_MATCH_INTS = tuple(range(0, ANSWERS_LEN))
    EMPTY_KNOWLEDGE = tuple([0 for _ in range(26 * (3 + WORD_LENGTH))])


# noinspection PyClassHasNoInit
class Knowledge:

    @staticmethod
    def update_knowledge(k: tuple, secret_word: str, guess: str) -> tuple:
        k = list(k)
        d = list(CONST.EMPTY_KNOWLEDGE)  # use to track in-word in-multi locally
        guess = list(str(guess).lower())  # make sure guess is in lower case
        secret_word = list(secret_word)
        for i in range(CONST.WORD_LENGTH):
            c = guess[i] = string.ascii_lowercase.index(guess[i])
            secret_word[i] = string.ascii_lowercase.index(secret_word[i])
            if c == secret_word[i]:
                guess[i] = secret_word[i] = ""
                if d[c + CONST.MULTI2] == CONST.YES: k[c + CONST.MULTI3] = d[c + CONST.MULTI3] = CONST.YES  # > 2 char
                if d[c + CONST.WORD_K_START] == CONST.YES: k[c + CONST.MULTI2] = d[c + CONST.MULTI2] = CONST.YES  # > 1 char
                k[c + CONST.WORD_K_START] = d[c + CONST.WORD_K_START] = CONST.YES
                k[c + CONST.POSITION_START + (26 * i)] = CONST.YES
        for i in range(CONST.WORD_LENGTH):
            c = guess[i]
            if c != "":
                if c in secret_word:
                    p = secret_word.index(c)
                    guess[i] = secret_word[p] = ""
                    if d[c + CONST.MULTI2] == CONST.YES: k[c + CONST.MULTI3] = d[c + CONST.MULTI3] = CONST.YES
                    if d[c + CONST.WORD_K_START] == CONST.YES: k[c + CONST.MULTI2] = d[c + CONST.MULTI2] = CONST.YES
                    k[c + CONST.WORD_K_START] = d[c + CONST.WORD_K_START] = CONST.YES
                    k[c + CONST.POSITION_START + (26 * i)] = CONST.NO
                else:
                    if d[c + CONST.WORD_K_START] != CONST.YES: k[c + CONST.WORD_K_START] = d[c + CONST.WORD_K_START] = CONST.NO
                    elif d[c + CONST.MULTI2] != CONST.YES: k[c + CONST.MULTI2] = d[c + CONST.MULTI2] = CONST.NO
                    elif d[c + CONST.MULTI3] != CONST.YES: k[c + CONST.MULTI3] = d[c + CONST.MULTI3] = CONST.NO
                    if d[c + CONST.WORD_K_START] != CONST.NO: k[c + CONST.POSITION_START + (26 * i)] = CONST.NO  # ignore "not in pos" if not in word (saves time)
        if CONST.WORD_K_START == 0: r = (26, len(k))
        else: r = (CONST.MULTI3, CONST.WORD_K_START)
        for i in range(r[0], r[1]):
            if k[i] == CONST.YES: k[CONST.WORD_K_START + (i % 26)] = CONST.UNSURE  # if you know "in pos" forget "in word" save time
        return tuple(k)

    @staticmethod
    def update_knowledge_from_colors(k: tuple, guess: str, color_feedback: str) -> tuple:
        k = list(k)
        d = list(CONST.EMPTY_KNOWLEDGE)
        guess = list(str(guess).lower())  # make sure guess is in lower case
        color_feedback = list(color_feedback.upper())
        for i in range(CONST.WORD_LENGTH):
            c = guess[i] = string.ascii_lowercase.index(guess[i])
            if color_feedback[i] == "G":
                guess[i] = color_feedback[i] = ""
                if d[c + CONST.MULTI2] == CONST.YES: k[c + CONST.MULTI3] = d[c + CONST.MULTI3] = CONST.YES  # > 2 char
                if d[c + CONST.WORD_K_START] == CONST.YES: k[c + CONST.MULTI2] = d[c + CONST.MULTI2] = CONST.YES  # > 1 char
                k[c + CONST.WORD_K_START] = d[c + CONST.WORD_K_START] = CONST.YES
                k[c + CONST.POSITION_START + (26 * i)] = CONST.YES
        for i in range(CONST.WORD_LENGTH):
            c = guess[i]
            if c != "":
                if color_feedback[i] == "Y":
                    guess[i] = ""
                    if d[c + CONST.POSITION_START] == CONST.YES: k[c + CONST.MULTI3] = d[c + CONST.MULTI3] = CONST.YES
                    if d[c + CONST.WORD_K_START] == CONST.YES: k[c + CONST.POSITION_START] = d[c + CONST.POSITION_START] = CONST.YES
                    k[c + CONST.WORD_K_START] = d[c + CONST.WORD_K_START] = CONST.YES
                    if d[c + CONST.WORD_K_START] != CONST.NO: k[c + CONST.POSITION_START + (26 * i)] = CONST.NO
                else:
                    if d[c + CONST.WORD_K_START] != CONST.YES: k[c + CONST.WORD_K_START] = d[c + CONST.WORD_K_START] = CONST.NO
                    elif d[c + CONST.MULTI2] != CONST.YES: k[c + CONST.MULTI2] = d[c + CONST.MULTI2] = CONST.NO
                    elif d[c + CONST.MULTI3] != CONST.YES: k[c + CONST.MULTI3] = d[c + CONST.MULTI3] = CONST.NO
                    if d[c + CONST.WORD_K_START] != CONST.NO: k[c + CONST.POSITION_START + (26 * i)] = CONST.NO  # ignore "not in pos" if not in word (saves time)
        if CONST.WORD_K_START == 0: r = (26, len(k))
        else: r = (CONST.MULTI3, CONST.WORD_K_START)
        for i in range(r[0], r[1]):
            if k[i] == CONST.YES: k[CONST.WORD_K_START + (i % 26)] = CONST.UNSURE  # if you know "in pos" forget "in word" save time
        return tuple(k)

    @staticmethod
    def k_int_to_list(k_int: int) -> tuple:
        if k_int == 0: return [0]
        k_list = []
        list_len = (3 + CONST.WORD_LENGTH) * 26
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


# noinspection PyClassHasNoInit
class Tools:

    first_words = ("salet", "reast", "crate", "trace", "slate", "crane", "raise", "raile", "soare", "arise", "irate", "orate", "ariel", "arose", "raine", "artel", "taler", "ratel", "ocean", "steal", "raise", "raile", "soare", "arise", "irate", "orate", "ariel", "raine", "artel", "taler", "ratel", "aesir", "arles", "realo", "alter", "saner", "later", "snare", "oater", "salet", "taser", "stare", "tares", "slate", "alert", "reais", "lares", "reast", "strae", "laser", "saine", "rales", "urate", "crate", "serai", "toile", "seral", "rates", "carte", "antre", "slane", "trace", "coate", "carle", "carse", "stoae", "reals", "terai", "aeros", "liane", "tears", "caret", "stale", "alure", "slier", "resat", "sorel", "tales", "nares", "aisle", "litre", "saice", "learn", "earnt", "oriel", "earst", "lears", "paire", "reoil", "alone", "teras", "urase", "leant", "aloes", "torse", "aster", "arets", "least", "soler", "reans", "retia", "laten", "siler", "anole", "crane", "trone", "laers", "earls", "stear", "atone", "ayrie", "trail", "stane", "react", "haole", "teals", "maire", "toise", "tiler")

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
