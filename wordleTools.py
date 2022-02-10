import copy
import datetime
import hashlib
import json
import time
import sqlite3
import operator


class KNOWLEDGE:
    NOT_IN_WORD = "NIW"
    IN_WORD = "IW"
    IN_POSITION = "IP"
    NOT_IN_POSITION = "NIP"
    WORD_LENGTH = 5


class MapsDB:

    def __init__(self):
        self.db_conn = sqlite3.connect('wordle.db')

        # stable solver
        self.db_conn.execute('CREATE TABLE IF NOT EXISTS SMAP_TABLE (ID PRIMARY KEY NOT NULL, SUGGESTION TEXT);')
        
        # WIP solver
        self.db_conn.execute('CREATE TABLE IF NOT EXISTS SUGGESTIONS (ID PRIMARY KEY NOT NULL, SUGGESTION TEXT NOT NULL);')

    # stable suggestion get/set
    def insert_suggestion(self, k_hash, suggestion):
        db_conn = self.db_conn
        db_conn.execute("INSERT OR REPLACE INTO SMAP_TABLE (ID,SUGGESTION) VALUES ('" + k_hash + "', '" + suggestion + "')")
        db_conn.commit()

    def get_suggestion(self, k_hash):
        db_conn = self.db_conn
        cursor = db_conn.execute("SELECT SUGGESTION FROM SMAP_TABLE WHERE ID = '" + k_hash + "'")
        suggestion = cursor.fetchone()
        if suggestion:
            return suggestion[0]
        else:
            return False

    # wip suggestion get/set
    def insert_suggestion2(self, k_hash, suggestion):
        db_conn = self.db_conn
        db_conn.execute("INSERT OR REPLACE INTO SUGGESTIONS (ID,SUGGESTION) VALUES ('" + k_hash + "', '" + suggestion + "')")
        db_conn.commit()

    def get_suggestion2(self, k_hash):
        db_conn = self.db_conn
        cursor = db_conn.execute("SELECT SUGGESTION FROM SUGGESTIONS WHERE ID = '" + k_hash + "'")
        suggestion = cursor.fetchone()
        if suggestion:
            return suggestion[0]
        else:
            return False

    def close_db(self):
        self.db_conn.close()


class WordleTools:
    WAIT_FOR_BEST_SUGGESTION = 5 * 10 ** 6  # time in seconds to wait for best guess
    SHOW_TIMER = False  # toggle if you want to see what is taking so long

    @staticmethod
    def dict_hash(dictionary):
        dhash = hashlib.md5()
        encoded = json.dumps(dictionary, sort_keys=True).encode()
        dhash.update(encoded)
        return dhash.hexdigest()

    @staticmethod
    def standardize_knowledge(knowledge):
        knowledge[KNOWLEDGE.IN_WORD] = sorted(set(knowledge[KNOWLEDGE.IN_WORD]))
        knowledge[KNOWLEDGE.NOT_IN_WORD] = sorted(set(knowledge[KNOWLEDGE.NOT_IN_WORD]))
        for i in range(KNOWLEDGE.WORD_LENGTH):
            knowledge[str(i)][KNOWLEDGE.NOT_IN_POSITION] = sorted(set(knowledge[str(i)][KNOWLEDGE.NOT_IN_POSITION]))
        return knowledge

    @staticmethod
    def create_match_map(answers, guesses, knowledge):
 
        origin_k_hash = WordleTools.dict_hash(knowledge)

        match_map = {}
        knowledge_map = {}

        total_words = len(answers)
        counter = 0
        seconds_left = {"count": 1, "seconds_left": -1}
        start_time = time.time()
        save_knowledge_map = False
        for guess in guesses:
            match_map[guess] = 0.0

            seconds_left = WordleTools.get_time_estimate(seconds_left["count"], start_time, len(guesses))
            if seconds_left["seconds_left"] > WordleTools.WAIT_FOR_BEST_SUGGESTION:
                return False
            if WordleTools.SHOW_TIMER:
                counter = WordleTools.status_time_estimate(counter, start_time, len(guesses), "M map")

            for secret_word in answers:
                k = WordleTools.update_knowledge(knowledge, secret_word, guess)
                k_hash = WordleTools.dict_hash(k)

                if guess == secret_word:
                    match_count = 0
                elif k_hash in knowledge_map:
                    match_count = knowledge_map[k_hash]
                else:
                    matches = WordleTools.get_possible_matches(k, answers)
                    match_count = len(matches)
                knowledge_map[k_hash] = match_count
                match_map[guess] += match_count / total_words
        
        return match_map

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
    def guess_to_solve(knowledge, guess_options, answer_options, depth):
        MAX_DEPTH = 6  # when looking more deeply than max depth return false
        matches = WordleTools.get_possible_matches(knowledge, answer_options)
        total_matches = len(matches)
        if total_matches== 1:
            return {"g": matches[0], "c": 1, "d": depth}  # when there is a single option, guess it!
        elif total_matches == 2:
            return  {"g": matches[0], "c": 1.5, "d": depth}  # when there are two options avg(1, 2) to guess it.
        elif total_matches == 0 or depth > MAX_DEPTH:
            return False  # something went wrong
        else:

            if depth == 0:
                save_match_map = True
            else: 
                save_match_map = False
            
            match_map = WordleTools.create_match_map(matches, guess_options, knowledge)
            origin_k_hash = WordleTools.dict_hash(knowledge)
            
            
            """ 
                look for great guesses and perfect guesses
                great guess = guess leads to single match for all potential secrets
                perfect guess = guess is a potential secret AND is a great guess
            """

            for index in range(total_matches):
                guess = matches[index]
                if guess in match_map and round(match_map[guess], 7) == 1: 
                    return {"g": guess, "c": 2 - 1/total_matches, "d" : depth}

            non_matching_guesses = list(set(guess_options) - set(matches))
            for index in range(len(non_matching_guesses)):
                guess = non_matching_guesses[index]
                if guess in match_map and round(match_map[guess], 7) == 1:
                    return {"g": guess, "c": 2, "d": depth}

            """ 
                Now recursively find the best average guess. 
            """
            knowledge_map = {}
            
            best_ave_to_solve = None
            best_guess = None
            TEST_GUESSES = 10 # should search across all guesses but need to figure out way to stop early when best found
            sorted_mm = sorted(match_map.items(), key=operator.itemgetter(1))
            guess_compare_counter = 0
            for index in range(len(guess_options)):
                guess_compare_counter += 1
                if guess_compare_counter > TEST_GUESSES:
                    break
                guess = sorted_mm[index][0]
                average_guesses_to_solve = 1  # start average guess to solve at 1 assuming it isn't hit on first guess. corrected later
                for secret in matches:
                    k = WordleTools.update_knowledge(knowledge, secret, guess)
                    k_hash = WordleTools.dict_hash(k)

                    if guess == secret:
                        best_guess_to_solve = {"g": guess, "c": 1}
                        average_guesses_to_solve -= (1 / total_matches)
                    else:
                        if k_hash in knowledge_map:
                            best_guess_to_solve = knowledge_map[k_hash]
                        else: 
                            m = WordleTools.get_possible_matches(k, matches)
                            best_guess_to_solve = WordleTools.guess_to_solve(k, guess_options[:index] + guess_options[index+1:], m, depth + 1)
                            knowledge_map[k_hash] = best_guess_to_solve
                        average_guesses_to_solve += best_guess_to_solve["c"] / total_matches
                if depth == 0:
                    if index == 0:
                        print("")
                        print("guess   matches    agts    #")
                    print(guess + "    " + format(sorted_mm[index][1], '.3f') + "    " + format(average_guesses_to_solve, '.3f') + "     " + str(index))

                if not best_ave_to_solve or average_guesses_to_solve < best_ave_to_solve:
                    guess_compare_counter = 0  #reset guess compare counter if best guess found
                    best_ave_to_solve = average_guesses_to_solve
                    best_guess = guess
            
            knowledge_map[origin_k_hash] = {"g": best_guess, "c": best_ave_to_solve}
            return knowledge_map[origin_k_hash]

    @staticmethod
    def get_suggestion_wip(knowledge, guess_options, answer_options):
        maps = MapsDB()
        k_hash = WordleTools.dict_hash(knowledge)  # get hashkey for suggestion map
        existing_suggestion = maps.get_suggestion2(k_hash)
        
        if existing_suggestion:
            maps.delete_mmap(k_hash)
            return existing_suggestion

        suggestion_obj = WordleTools.guess_to_solve(knowledge, guess_options, answer_options, 0)
        suggested_guess = suggestion_obj["g"]
        maps.insert_suggestion2(k_hash, suggested_guess)
        return suggested_guess


    @staticmethod
    def get_suggestion(knowledge, guess_options, answer_options):
        # change to redirect to right suggestion solver
        # return WordleTools.get_suggestion_wip(knowledge, guess_options, answer_options)
        return WordleTools.get_suggestion_stable(knowledge, guess_options, answer_options)

    @staticmethod
    def get_suggestion_stable(knowledge, guess_options, answer_options):
        maps = MapsDB()
        k_hash = WordleTools.dict_hash(knowledge)  # get hashkey for suggestion map
        existing_suggestion_knowledge = maps.get_suggestion(k_hash)
        if existing_suggestion_knowledge:
            return existing_suggestion_knowledge

        matches = WordleTools.get_possible_matches(knowledge, answer_options)

        if len(matches) < 3:
            suggested_guess = matches[0]
        else:
            match_map = WordleTools.create_match_map(matches, guess_options, knowledge)

            if match_map is False:
                return WordleTools.get_suggestion_fast(knowledge, guess_options, matches)
            total_matches = len(matches)
            avg_exg_maybe_match = total_matches
            avg_exc_match = total_matches
            suggested_guess_matching = matches[0]
            suggested_guess_maybe_matching = suggested_guess_matching

            for guess in guess_options:
                if match_map[guess] < avg_exc_match and guess in matches:
                    suggested_guess_matching = guess
                    avg_exc_match = match_map[guess]
                if match_map[guess] < avg_exg_maybe_match:
                    suggested_guess_maybe_matching = guess
                    avg_exg_maybe_match = match_map[guess]
            suggested_guess = suggested_guess_matching
            narrow_over_try = 1 / avg_exg_maybe_match - 1 / avg_exc_match - 1 / total_matches
            if narrow_over_try > 0:
                suggested_guess = suggested_guess_maybe_matching

        maps.insert_suggestion(k_hash, suggested_guess)
        return suggested_guess

    @staticmethod
    def get_suggestion_fast(knowledge, guess_options, answer_options):
        # get as much insight into the letters we don't know about that are in the remaining words
        # exclude words that

        matches = WordleTools.get_possible_matches(knowledge, answer_options)
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

        if total_matches < 2:
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

        match_map = WordleTools.create_match_map(matches, [focus_suggested_guess, suggested_guess], knowledge)

        narrow_over_try = 1 / match_map[focus_suggested_guess] - 1 / match_map[suggested_guess] - 1 / total_matches
        if focus_suggested_guess and narrow_over_try > 0:
            suggested_guess = focus_suggested_guess

        return suggested_guess

    @staticmethod
    def status_time_estimate(count, start_time, total_matches, description):
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
            print("...",end="\r")
        count += 1

        return count
        # END TIMER CODE

    @staticmethod
    def get_time_estimate(count, start_time, total_count):
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
    def update_knowledge(knowledge, secret_word, guess):
        knowledge = copy.deepcopy(knowledge)
        guess = str(guess).lower()  # make sure guess is in lower case
        for i in range(KNOWLEDGE.WORD_LENGTH):
            k = knowledge[str(i)]
            c = guess[i]
            if c == secret_word[i]:
                if c not in knowledge[KNOWLEDGE.IN_WORD]:
                    knowledge[KNOWLEDGE.IN_WORD].append(c)
                knowledge[str(i)][KNOWLEDGE.IN_POSITION] = c
            elif c in secret_word:
                if c not in knowledge[KNOWLEDGE.IN_WORD]:
                    knowledge[KNOWLEDGE.IN_WORD].append(c)
                if c not in k[KNOWLEDGE.NOT_IN_POSITION]:
                    knowledge[str(i)][KNOWLEDGE.NOT_IN_POSITION].append(c)
            else:
                if c not in knowledge[KNOWLEDGE.NOT_IN_WORD]:
                    if c not in knowledge[KNOWLEDGE.IN_WORD]:
                        knowledge[KNOWLEDGE.NOT_IN_WORD].append(c)
                # could optimize be removing words with 2+, of c if get back not in work when in word
        return WordleTools.standardize_knowledge(knowledge)

    @staticmethod
    def default_knowledge():
        knowledge = {KNOWLEDGE.IN_WORD: [], KNOWLEDGE.NOT_IN_WORD: []}
        for i in range(KNOWLEDGE.WORD_LENGTH):
            knowledge[str(i)] = {KNOWLEDGE.NOT_IN_POSITION: [], KNOWLEDGE.IN_POSITION: False}
        return WordleTools.standardize_knowledge(knowledge)
