from random import sample
import time
import datetime


class KNOWLEDGE:
    NOT_IN_WORD = "NIW"
    IN_WORD = "IW"
    IN_POSITION = "IP"
    NOT_IN_POSITION = "NIP"
    WORD_LENGTH = 5


class WordleTools:
    @staticmethod
    def test_word_for_match(test_word, knowledge):
        # remove words that include letters known not to be in word
        for c in knowledge[KNOWLEDGE.IN_WORD]:
            if c not in test_word:
                return False
        for i in range(KNOWLEDGE.WORD_LENGTH):
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
            if WordleTools.test_word_for_match(word, knowledge):
                matches.append(word)
        return matches

    @staticmethod
    def get_suggestion(secret_word_options, guess_options):
        # WIP use exclusion map and combine knowledge to figure out which words will increase knowledge the most
        exclusions_by_guess = {}
        total_matches = len(secret_word_options)
        count = 0
        start_time = time.time()

        for guess in guess_options:
            exclusions_by_guess[guess] = 0

        sample_count = 200

        if total_matches < 100:
            sample_count = total_matches
        for secret in sample(secret_word_options, sample_count):
            count = WordleTools.status_time_estimate(count, start_time, total_matches)

            for guess in guess_options:
                for answer in secret_word_options:
                    if not WordleTools.test_word_for_match(answer,
                                                           WordleTools.update_knowledge(WordleTools.default_knowledge(),
                                                                                        secret, guess)):
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
    def status_time_estimate(count, start_time, total_matches):
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

        print("{0}% done over ~{1}. Estimated {2} time left".format(str(round(progress * 100, 2)),
                                                                    str(datetime.timedelta(
                                                                        seconds=elapsed_time)),
                                                                    time_left_str))
        count += 1
        return count
        # END TIMER CODE

    @staticmethod
    def update_knowledge(knowledge, secret_word, guess):
        for i in range(KNOWLEDGE.WORD_LENGTH):
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
        for i in range(KNOWLEDGE.WORD_LENGTH):
            knowledge[str(i)] = {KNOWLEDGE.NOT_IN_POSITION: [], KNOWLEDGE.IN_POSITION: False}
        return knowledge
