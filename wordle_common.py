import string
import time
import datetime
from functools import lru_cache


class Knowledge:
    WORD_LENGTH = 5
    YES = "Y"
    NO = "N"
    UNSURE = "_"

    @staticmethod
    # @lru_cache(maxsize=2 * 20)
    def test_word_for_match(test_word: str, k: str) -> bool:
        """
        @type test_word: basestring
        @type k: object
        """
        # remove words that include letters known not to be in word or position
        for i in range(Knowledge.WORD_LENGTH):
            c = test_word[i]
            in_word = Knowledge.WORD_LENGTH + string.ascii_lowercase.index(c)
            pos_range_start = (1 + i) * 26
            in_pos = pos_range_start + in_word
            if k[in_word] == Knowledge.NO: return False  # false if c not in word is known
            if k[in_pos] == Knowledge.NO: return False  # false if c not in pos is known
            if k[i] != Knowledge.UNSURE and c != k[i]: return False

        # false if c not in word, but knowledge says it should be
        for j in range(Knowledge.WORD_LENGTH, Knowledge.WORD_LENGTH + 26):
            c = string.ascii_lowercase[j - Knowledge.WORD_LENGTH]
            if j == Knowledge.YES and c not in test_word:
                return False
        return True

    @staticmethod
    # @lru_cache(maxsize=2 ** 20)
    def get_possible_matches(k: str, possible_words: tuple) -> tuple:
        matches = []
        for word in possible_words:

            if len(word) == Knowledge.WORD_LENGTH and Knowledge.test_word_for_match(word, k):
                matches.append(word)
        return tuple(matches)

    @staticmethod
    def new_str(s: str, i: int, c: str):
        return s[:i] + c + s[i + 1:]

    @staticmethod
    def update_knowledge(k: str, secret_word: str, guess: str) -> str:
        guess = str(guess).lower()  # make sure guess is in lower case
        for i in range(Knowledge.WORD_LENGTH):
            c = guess[i]
            in_word = Knowledge.WORD_LENGTH + string.ascii_lowercase.index(c)
            in_pos = (1 + i) * 26 + in_word
            if c == secret_word[i]:
                k = Knowledge.new_str(k, i, c)  # save the character
                k = Knowledge.new_str(k, in_word, Knowledge.YES)  # in word
                k = Knowledge.new_str(k, in_pos, Knowledge.YES)  # in position
            elif c in secret_word:
                k = Knowledge.new_str(k, in_word, Knowledge.YES)
                k = Knowledge.new_str(k, in_pos, Knowledge.NO)
            else:
                if k[in_word] == Knowledge.UNSURE:
                    k = Knowledge.new_str(k, in_word, Knowledge.NO)
        return k

    @staticmethod
    @lru_cache(maxsize=1)
    def default_knowledge() -> str:
        k = ""
        for n in range(Knowledge.WORD_LENGTH):
            k += Knowledge.UNSURE
        for n in range(26):
            k += Knowledge.UNSURE
        # place knowledge
        for n in range(Knowledge.WORD_LENGTH):
            for a in range(26):
                k += Knowledge.UNSURE
        return k


class TimeTools:

    @staticmethod
    def get_time_estimate(count: int, start_time: time, total_count: int) -> dict:
        time_now = time.time()
        elapsed_time = int(time_now - start_time)

        if total_count == 0:
            return {"count": 0, "seconds_left": -1}
        progress = count / total_count
        progress_to_finish = 1 - count / total_count

        seconds_left = -1
        if count > 1:
            seconds_left = int(elapsed_time * progress_to_finish / progress)
        count += 1
        return {"count": count, "seconds_left": seconds_left}

    @staticmethod
    def status_time_estimate(count: int, start_time: time, total_matches: int, description: str) -> int:
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
            print("...", end="\r")
        count += 1

        return count
