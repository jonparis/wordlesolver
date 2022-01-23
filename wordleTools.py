import copy
import string
import time
import datetime


class KNOWLEDGE:
    NOT_IN_WORD = "NIW"
    IN_WORD = "IW"
    IN_POSITION = "IP"
    NOT_IN_POSITION = "NIP"
    WORD_LENGTH = 5


class WordleTools:
    DEPTH_OF_SUGGESTION = 10**7 # (bigger numbers take longer)
    SHOW_TIMER = True
    LOOK_FOR_MATCHES_ONLY = 2 # at what match count do you prioritize picking the right match vs eliminating options

    """
    knowledge_as_string: can be used to create a lookup table form any state of knowledge matches and suggested_guesses
    """
    @staticmethod
    def knowledge_as_string(knowledge):
        word_length_string = str(KNOWLEDGE.WORD_LENGTH)
        if KNOWLEDGE.WORD_LENGTH < 10:
            word_length_string = "0" + word_length_string
        in_word = ""
        not_in_word = ""
        in_position = ""
        not_in_position = ""
        in_position_string = ""
        not_in_position_string = ""
        for c in string.ascii_lowercase:
            if c in knowledge.IN_WORD:
                in_word += "c"
            else:
                in_word += "0"
            if c in knowledge.NOT_IN_WORD:
                not_in_word += c
            else:
                not_in_word += "0"
            for i in range(KNOWLEDGE.WORD_LENGTH):
                if c in knowledge.NOT_IN_POSITION:
                    not_in_position[str(i)] += c
                else:
                    not_in_position[str(i)] += "0"
                if c == knowledge.IN_POSITION:
                    in_position[str(i)] = c
                else:
                    in_position[str(i)] = "0"
        for i in KNOWLEDGE.WORD_LENGTH:
            in_position_string += in_position[str(i)]
            not_in_position_string += not_in_position[str(i)]
        return word_length_string + in_word + not_in_word + in_position_string + not_in_position_string


    @staticmethod
    def create_match_map(answers, guesses, knowledge):
        match_map = {}
        total_words = len(answers)
        counter = 0
        start_time = time.time()

        for guess in guesses:
            match_map[guess] = {}
            match_map[guess]["average_match_count"] = 0.0
            if WordleTools.SHOW_TIMER:
                counter = WordleTools.status_time_estimate(counter, start_time, len(guesses))

            for secret_word in answers:
                k = WordleTools.update_knowledge(copy.deepcopy(knowledge), secret_word, guess)
                matches = WordleTools.get_possible_matches(k, answers)
                match_map[guess][secret_word] = matches
                match_map[guess]["average_match_count"] += len(matches)/total_words
        return match_map

    @staticmethod
    def union_of_lists(list_of_lists):
        return list(set().union(list_of_lists))

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
    def get_suggestion(knowledge, guess_options):
        exclusions_by_guess = {}
        matches = WordleTools.get_possible_matches(copy.deepcopy(knowledge), guess_options)
        total_matches = len(matches)
        # once narrow ensure guess has a chance of being in the set.
        if total_matches < 5:
            guess_options = matches

        guess_ct = len(guess_options)
        search_scale = total_matches * total_matches * guess_ct
        count = 0
        start_time = time.time()
        fast_suggest = WordleTools.get_suggestion_fast(knowledge, guess_options)
        if search_scale > WordleTools.DEPTH_OF_SUGGESTION:
            return fast_suggest

        match_map = WordleTools.create_match_map(matches, guess_options, knowledge)
        avg_exg_maybe_match = total_matches
        avg_exc_match = total_matches
        suggested_guess_matching = matches[0]
        suggested_guess_maybe_matching = fast_suggest

        for guess in guess_options:
            if match_map[guess]["average_match_count"] < avg_exc_match and guess in matches:
                suggested_guess_matching = guess
                avg_exc_match = match_map[guess]["average_match_count"]
            if match_map[guess]["average_match_count"] < avg_exg_maybe_match:
                suggested_guess_maybe_matching = guess
                avg_exg_maybe_match = match_map[guess]["average_match_count"]
        suggested_guess = suggested_guess_matching

        narrow_over_try = 1 / avg_exg_maybe_match - 1 / avg_exc_match - 1 / total_matches
        if narrow_over_try > 0:
            suggested_guess = suggested_guess_maybe_matching

        return suggested_guess

    @staticmethod
    def get_suggestion_fast(knowledge, guess_options):
        # get as much insight into the letters we don't know about that are in the remaining words
        # exclude words that

        matches = WordleTools.get_possible_matches(copy.deepcopy(knowledge), guess_options)
        letter_count = {}
        focus_letter_count = {}
        in_word_letters = knowledge[KNOWLEDGE.IN_WORD]
        total_matches = len(matches)

        for c in "qwertyuiopasdfghjklzxcvbnm":
            letter_count[c] = 0.0
            focus_letter_count[c] = 0.0
        for word in matches:
            for c in word:
                letter_count[c] += 1.0
                if c not in in_word_letters:
                    focus_letter_count[c] += 1.0

        max_cov = 0.0
        suggested_guess = guess_options[0]
        max_focus = 0.0
        focus_suggested_guess = guess_options[0]

        if total_matches < 5:
            guess_options = matches
        for word in guess_options:
            coverage = sum([letter_count[c] for c in set([c for c in word])])
            focus_coverage = sum([focus_letter_count[c] for c in set([c for c in word])])
            if coverage > max_cov:
                max_cov = coverage
                suggested_guess = word
            if focus_coverage > max_focus:
                max_focus = focus_coverage
                focus_suggested_guess = word
        # 500 is a guess. might be worth focusing to a lower word count

        match_map = WordleTools.create_match_map(matches, [focus_suggested_guess, suggested_guess], knowledge)

        narrow_over_try = 1/match_map[focus_suggested_guess]["average_match_count"] - 1/match_map[suggested_guess]["average_match_count"] - 1/total_matches
        if focus_suggested_guess and narrow_over_try > 0:
            suggested_guess = focus_suggested_guess

        return suggested_guess

    @staticmethod
    def status_time_estimate(count, start_time, total_matches):
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
                    # could optimize if also in word, then the match will have two of that letter
            else:
                if c not in knowledge[KNOWLEDGE.NOT_IN_WORD] and c not in knowledge[KNOWLEDGE.IN_WORD]:
                    knowledge[KNOWLEDGE.NOT_IN_WORD].append(c)
                # could optimize be removing words with 2+, of c if get back not in work when in word
        return knowledge

    @staticmethod
    def default_knowledge():
        knowledge = {KNOWLEDGE.IN_WORD: [], KNOWLEDGE.NOT_IN_WORD: []}
        for i in range(KNOWLEDGE.WORD_LENGTH):
            knowledge[str(i)] = {KNOWLEDGE.NOT_IN_POSITION: [], KNOWLEDGE.IN_POSITION: False}
        return knowledge
