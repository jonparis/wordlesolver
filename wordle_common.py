import copy
import string
import time
import datetime


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
    PER = 4  # confidence cannot be improved upon unless guess/answer list changes
    HIGH = 3  # confidence in guess after reviewing all guesses. Only needs update better sub_guess is found
    MED = 2  # confidence in guess after full optimization
    LOW = 1  # confidence in guess low, default after quick optimization
    VERY_LOW = 0  # confidence in guess very low needs optimizing
    YES = 2  # letter in position or word
    NO = 1  # letter not in position / word
    UNSURE = 0  # unsure if letter in position / word
    GUESS = 0  # guess
    AGTS = 1  # average_guesses_to_solve
    C = 2  # confidence
    M = 3  # match_count
    OPT = 4  # optimized_to
    map = {PER: "Perfect", HIGH: "High", MED: "Medium", LOW: "Low", VERY_LOW: "Very low"}


# noinspection PyClassHasNoInit
class Knowledge:
    @staticmethod
    def standardize_knowledge(k: dict) -> dict:
        k[CONST.IN_WORD] = sorted(set(k[CONST.IN_WORD]))
        k[CONST.NOT_IN_WORD] = sorted(set(k[CONST.NOT_IN_WORD]))
        k[CONST.IN_MULTI] = sorted(set(k[CONST.IN_MULTI]))
        k[CONST.NOT_IN_MULTI] = sorted(set(k[CONST.NOT_IN_MULTI]))
        for i in range(CONST.WORD_LENGTH):
            k[i][CONST.NOT_IN_POSITION] = sorted(set(k[i][CONST.NOT_IN_POSITION]))
        return k

    @staticmethod
    def test_word_for_match(test_word: str, k: dict) -> bool:
        # remove words that include letters known not to be in word
        for c in k[CONST.IN_WORD]:
            if c not in test_word:
                return False
        for c in k[CONST.IN_MULTI]:
            if test_word.count(c) < 2:
                return False
        for c in k[CONST.NOT_IN_MULTI]:
            if test_word.count(c) > 1:
                return False
        for i in range(CONST.WORD_LENGTH):
            c = test_word[i]
            if c in k[CONST.NOT_IN_WORD]:
                return False
            if k[i][CONST.IN_POSITION] and c != k[i][CONST.IN_POSITION]:
                return False
            if c in k[i][CONST.NOT_IN_POSITION]:
                return False
        return True

    @staticmethod
    def get_possible_matches(k: dict, possible_words: tuple) -> tuple:
        matches = []
        for word in possible_words:
            if Knowledge.test_word_for_match(word, k):
                matches.append(word)
        return tuple(matches)

    @staticmethod
    def update_knowledge(k: dict, secret_word: str, guess: str) -> dict:
        k = copy.deepcopy(k)
        d = Knowledge.default_knowledge()
        guess = list(str(guess).lower())  # make sure guess is in lower case
        secret_word = list(secret_word)
        for i in range(CONST.WORD_LENGTH):
            c = guess[i]
            if c == secret_word[i]:
                guess[i] = secret_word[i] = ""
                if c in d[CONST.IN_WORD]: d[CONST.IN_MULTI].append(c)
                d[CONST.IN_WORD].append(c)
                d[i][CONST.IN_POSITION] = c
        for i in range(CONST.WORD_LENGTH):
            c = guess[i]
            if c != "":
                if c in secret_word:
                    p = secret_word.index(c)
                    guess[i] = secret_word[p] = ""
                    if c in d[CONST.IN_WORD]: d[CONST.IN_MULTI].append(c)
                    d[CONST.IN_WORD].append(c)
                    d[i][CONST.NOT_IN_POSITION].append(c)
                else:
                    if c not in d[CONST.IN_WORD]: d[CONST.NOT_IN_WORD].append(c)
                    elif c not in d[CONST.IN_MULTI]: d[CONST.NOT_IN_MULTI].append(c)
                    d[i][CONST.NOT_IN_POSITION].append(c)
        k = Knowledge.join_knowledge(k, d)
        return Knowledge.standardize_knowledge(k)

    @staticmethod
    def update_knowledge_from_colors(k: dict, guess: str, color_feedback: str) -> dict:
        k = copy.deepcopy(k)
        d = Knowledge.default_knowledge()
        guess = list(str(guess).lower())  # make sure guess is in lower case
        color_feedback = list(color_feedback.upper())
        for i in range(CONST.WORD_LENGTH):
            c = guess[i]
            f = color_feedback[i]
            if f == "G":
                guess[i] = color_feedback[i] = ""
                if c in d[CONST.IN_WORD]: d[CONST.IN_MULTI].append(c)
                d[CONST.IN_WORD].append(c)
                d[i][CONST.IN_POSITION] = c
        for i in range(CONST.WORD_LENGTH):
            c = guess[i]
            f = color_feedback[i]
            if f == "Y":
                guess[i] = ""
                if c in d[CONST.IN_WORD]: d[CONST.IN_MULTI].append(c)
                d[CONST.IN_WORD].append(c)
                d[i][CONST.NOT_IN_POSITION].append(c)
        for i in range(CONST.WORD_LENGTH):
            c = guess[i]
            f = color_feedback[i]
            if c != "" and f == "R":
                if c not in d[CONST.IN_WORD]:
                    d[CONST.NOT_IN_WORD].append(c)
                elif c not in d[CONST.IN_MULTI]:
                    d[CONST.NOT_IN_MULTI].append(c)
                d[i][CONST.NOT_IN_POSITION].append(c)
        k = Knowledge.join_knowledge(k, d)
        return Knowledge.standardize_knowledge(k)

    @staticmethod
    def join_knowledge(k1: dict, k2: dict) -> dict:
        k = {CONST.IN_WORD: list(set(k1[CONST.IN_WORD]) | set(k2[CONST.IN_WORD])),
             CONST.NOT_IN_WORD: list(set(k1[CONST.NOT_IN_WORD]) | set(k2[CONST.NOT_IN_WORD])),
             CONST.IN_MULTI: list(set(k1[CONST.IN_MULTI]) | set(k2[CONST.IN_MULTI])),
             CONST.NOT_IN_MULTI: list(set(k1[CONST.NOT_IN_MULTI]) | set(k2[CONST.NOT_IN_MULTI]))}
        for i in range(CONST.WORD_LENGTH):
            k[i] = {CONST.IN_POSITION: False, CONST.NOT_IN_POSITION: []}
            if k1[i][CONST.IN_POSITION]: k[i][CONST.IN_POSITION] = k1[i][CONST.IN_POSITION]
            elif k2[i][CONST.IN_POSITION]: k[i][CONST.IN_POSITION] = k2[i][CONST.IN_POSITION]
            k[i][CONST.NOT_IN_POSITION] = list(set(k1[i][CONST.NOT_IN_POSITION]) | set(k2[i][CONST.NOT_IN_POSITION]))
        return k

    @staticmethod
    def default_knowledge() -> dict:
        k = {CONST.IN_WORD: [], CONST.NOT_IN_WORD: [], CONST.IN_MULTI: [], CONST.NOT_IN_MULTI: []}
        for i in range(CONST.WORD_LENGTH):
            k[i] = {CONST.NOT_IN_POSITION: [], CONST.IN_POSITION: False}
        return Knowledge.standardize_knowledge(k)

    @staticmethod
    def k_int_to_list(k_int: int) -> list:
        if k_int == 0: return [0]
        k_list = []
        while k_int:
            k_list.append(int(k_int % 3))
            k_int //= 3
        return k_list  # [::-1] uncomment to reverse

    @staticmethod
    def k_list_to_int(k_list: list) -> int:
        k_int = 0
        for i in range(len(k_list)): k_int += k_list[i] * 3 ** i
        return k_int

    @staticmethod
    def k_dict_to_list(k_dict: dict) -> list:
        k_list = Knowledge.empty_k_list()
        ps = 0  # work info in positions 0-25. 26-52 position 1, etc
        for c in k_dict[CONST.IN_WORD]:
            k_list[string.ascii_lowercase.index(c)] = CONST.YES
        for c in k_dict[CONST.NOT_IN_WORD]:
            k_list[string.ascii_lowercase.index(c)] = CONST.NO
        ps += 26
        for c in k_dict[CONST.IN_MULTI]:
            k_list[ps + string.ascii_lowercase.index(c)] = CONST.YES
        for c in k_dict[CONST.NOT_IN_MULTI]:
            k_list[ps + string.ascii_lowercase.index(c)] = CONST.NO
        for i in range(CONST.WORD_LENGTH):
            ps += 26
            c = k_dict[i][CONST.IN_POSITION]
            if c: k_list[ps + string.ascii_lowercase.index(c)] = CONST.YES
            for c in k_dict[i][CONST.NOT_IN_POSITION]:
                k_list[ps + string.ascii_lowercase.index(c)] = CONST.NO

        return k_list

    @staticmethod
    def k_dict_to_int(k_dict: dict) -> int:
        k_list = Knowledge.k_dict_to_list(k_dict)
        return Knowledge.k_list_to_int(k_list)

    @staticmethod
    def k_list_to_dict(k_list: list) -> dict:
        k_len = len(k_list)
        k_dict = Knowledge.default_knowledge()
        sp = 0
        for i in range(26):
            c = string.ascii_lowercase[i]
            if i >= k_len: return k_dict  # no more info. Return!
            if k_list[i] == CONST.YES and c not in k_dict[CONST.IN_WORD]:
                k_dict[CONST.IN_WORD].append(c)
            if k_list[i] == CONST.NO and c not in k_dict[CONST.NOT_IN_WORD]:
                k_dict[CONST.NOT_IN_WORD].append(c)
        sp += 26
        for i in range(26):
            c = string.ascii_lowercase[i]
            if i + sp >= k_len: return k_dict  # no more info. Return!
            if k_list[i + sp] == CONST.YES and c not in k_dict[CONST.IN_MULTI]:
                k_dict[CONST.IN_MULTI].append(c)
            if k_list[i + sp] == CONST.NO and c not in k_dict[CONST.NOT_IN_MULTI]:
                k_dict[CONST.NOT_IN_MULTI].append(c)
        for p in range(CONST.WORD_LENGTH):
            sp += 26
            for i in range(26):
                c = string.ascii_lowercase[i]
                if i + sp >= k_len: return k_dict  # no more info Return!
                if k_list[i + sp] == CONST.YES: k_dict[p][CONST.IN_POSITION] = c
                if k_list[i + sp] == CONST.NO and c not in k_dict[p][CONST.NOT_IN_POSITION]:
                    k_dict[p][CONST.NOT_IN_POSITION].append(c)
        return k_dict

    @staticmethod
    def k_int_to_dict(k_int: int) -> dict:
        k_list = Knowledge.k_int_to_list(k_int)
        k_dict = Knowledge.k_list_to_dict(k_list)
        return Knowledge.standardize_knowledge(k_dict)

    @staticmethod
    def empty_k_list():
        k_list = []
        # not or in word, not or in multi, then not or in position
        for _ in range(26 + 26 + 26 * CONST.WORD_LENGTH): k_list.append(0)
        return k_list


# noinspection PyClassHasNoInit
class Tools:

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
    def get_time_estimate(count: int, start_time: time, total_count: int) -> dict:
        time_now = time.time()
        elapsed_time = int(time_now - start_time)

        if total_count == 0:
            return -1
        progress = count / total_count
        progress_to_finish = 1 - count / total_count

        seconds_left = -1
        if count > 1:
            seconds_left = int(elapsed_time * progress_to_finish / progress)

        return seconds_left

    @staticmethod
    def timer(count: int, start_time: time, total_matches: int, description: str) -> int:
        # Set timer to make sure the process won't take too long
        time_now = time.time()
        elapsed_time = int(time_now - start_time)

        if total_matches == 0:
            return 0
        progress = count / total_matches
        progress_to_finish = 1 - count / total_matches
        if progress != 0:
            time_left = int(elapsed_time * progress_to_finish / progress)
            time_left_str = str(datetime.timedelta(seconds=time_left))
            if time_left > 10:
                print("\r\033[K", description + " {0}% done. Time left ~{2}".format(format(progress * 100, '.2f'),
                                                                                    str(datetime.timedelta(
                                                                                        seconds=elapsed_time)),
                                                                                    time_left_str), end="")
        else:
            print("", description, "...")
        count += 1

        return count


# noinspection PyClassHasNoInit
class COLORS:
    GREEN = " \033[0;30;42m "
    BLACK = " \033[0;37;40m "
    YELLOW = " \033[0;30;43m "
    GREY = " \033[0;30;47m "
    SPACE_COLOR = " \033[0;37;48m"
