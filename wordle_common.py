import copy
import time
import json
import datetime
import hashlib


class Knowledge:
    NOT_IN_WORD = "NIW"
    IN_WORD = "IW"
    IN_POSITION = "IP"
    NOT_IN_POSITION = "NIP"
    WORD_LENGTH = 5

    @staticmethod
    def dict_hash(dictionary: dict) -> str:
        dhash = hashlib.md5()
        encoded = json.dumps(dictionary, sort_keys=True).encode()
        dhash.update(encoded)
        return dhash.hexdigest()

    @staticmethod
    def standardize_knowledge(k: dict) -> dict:
        k[Knowledge.IN_WORD] = sorted(set(k[Knowledge.IN_WORD]))
        k[Knowledge.NOT_IN_WORD] = sorted(set(k[Knowledge.NOT_IN_WORD]))
        for i in range(Knowledge.WORD_LENGTH):
            k[str(i)][Knowledge.NOT_IN_POSITION] = sorted(set(k[str(i)][Knowledge.NOT_IN_POSITION]))
        return k

    @staticmethod
    def test_word_for_match(test_word: str, k: dict) -> bool:
        """
        @type test_word: basestring
        @type k: object
        """
        # remove words that include letters known not to be in word
        for c in k[Knowledge.IN_WORD]:
            if c not in test_word:
                return False
        for i in range(Knowledge.WORD_LENGTH):
            c = test_word[i]
            if c in k[Knowledge.NOT_IN_WORD]:
                return False
            if k[str(i)][Knowledge.IN_POSITION] and c != k[str(i)][Knowledge.IN_POSITION]:
                return False
            if c in k[str(i)][Knowledge.NOT_IN_POSITION]:
                return False
        return True

    @staticmethod
    def get_possible_matches(k: dict, possible_words: list) -> list:
        matches = []
        for word in possible_words:
            if Knowledge.test_word_for_match(word, k):
                matches.append(word)
        return matches

    @staticmethod
    def update_knowledge(k: dict, secret_word: str, guess: str):
        k = copy.deepcopy(k)
        guess = str(guess).lower()  # make sure guess is in lower case
        for i in range(Knowledge.WORD_LENGTH):
            c = guess[i]
            if c == secret_word[i]:
                if c not in k[Knowledge.IN_WORD]:
                    k[Knowledge.IN_WORD].append(c)
                k[str(i)][Knowledge.IN_POSITION] = c
            elif c in secret_word:
                if c not in k[Knowledge.IN_WORD]:
                    k[Knowledge.IN_WORD].append(c)
                if c not in k[str(i)][Knowledge.NOT_IN_POSITION]:
                    k[str(i)][Knowledge.NOT_IN_POSITION].append(c)
            else:
                if c not in k[Knowledge.NOT_IN_WORD]:
                    if c not in k[Knowledge.IN_WORD]:
                        k[Knowledge.NOT_IN_WORD].append(c)
                # could optimize be removing words with 2+, of c if get back not in work when in word
        return Knowledge.standardize_knowledge(k)

    @staticmethod
    def default_knowledge() -> dict:
        k = {Knowledge.IN_WORD: [], Knowledge.NOT_IN_WORD: []}
        for i in range(Knowledge.WORD_LENGTH):
            k[str(i)] = {Knowledge.NOT_IN_POSITION: [], Knowledge.IN_POSITION: False}
        return Knowledge.standardize_knowledge(k)


class TimeTools:

    @staticmethod
    def get_time_estimate(count: int, start_time: time, total_count: int) -> dict:
        time_now = time.time()
        elapsed_time = int(time_now - start_time)

        if total_count == 0:
            return 0
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
                print("\033[K", description + " {0}% done. Time left ~{2}".format(format(progress * 100, '.2f'),
                                                                                  str(datetime.timedelta(
                                                                                      seconds=elapsed_time)),
                                                                                  time_left_str), end="\r")
        else:
            print("...", end="\r")
        count += 1

        return count
