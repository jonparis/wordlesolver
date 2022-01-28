import copy
import datetime
import hashlib
import json
import time
import sqlite3


class KNOWLEDGE:
    NOT_IN_WORD = "NIW"
    IN_WORD = "IW"
    IN_POSITION = "IP"
    NOT_IN_POSITION = "NIP"
    WORD_LENGTH = 5


class MapsDB:

    def __init__(self):
        self.db_conn = sqlite3.connect('wordle.db')
        self.db_conn.execute('''CREATE TABLE IF NOT EXISTS KMAP_TABLE
                         (ID PRIMARY KEY NOT NULL,
                         KMAP TEXT NOT NULL);''')
        self.db_conn.execute('''CREATE TABLE IF NOT EXISTS SMAP_TABLE
                         (ID PRIMARY KEY NOT NULL,
                         SUGGESTION TEXT);''')
        self.db_conn.execute('''CREATE TABLE IF NOT EXISTS MMAP_TABLE
                                 (ID PRIMARY KEY NOT NULL,
                                 MMAP TEXT);''')

    def insert_kmap(self, k_hash, kmap):
        db_conn = self.db_conn
        kmap_json = json.dumps(kmap)
        db_conn.execute("INSERT OR REPLACE INTO KMAP_TABLE (ID,KMAP) \
              VALUES ('" + k_hash + "', '" + kmap_json + "')")
        db_conn.commit()

    def insert_suggestion(self, k_hash, suggestion):
        db_conn = self.db_conn
        db_conn.execute("INSERT OR REPLACE INTO SMAP_TABLE (ID,SUGGESTION) \
              VALUES ('" + k_hash + "', '" + suggestion + "')")
        db_conn.commit()

    def get_kmap(self, k_hash):
        db_conn = self.db_conn
        cursor = db_conn.execute("SELECT KMAP FROM KMAP_TABLE WHERE ID = '" + k_hash + "'")
        kmap = cursor.fetchone()
        if kmap:
            json.load(kmap)
        else:
            return False

    def get_suggestion(self, k_hash):
        db_conn = self.db_conn
        cursor = db_conn.execute("SELECT SUGGESTION FROM SMAP_TABLE WHERE ID = '" + k_hash + "'")
        suggestion = cursor.fetchone()
        if suggestion:
            return suggestion[0]
        else:
            return False

    def insert_batch_kmap(self, kmap_dict):
        db_conn = self.db_conn
        sql_statement = "INSERT OR REPLACE INTO SMAP_TABLE (ID, KMAP) VALUES "
        for key, value in kmap_dict.items():
            sql_statement += '("' + key + '", "' + value + '"),'
        sql_statement = sql_statement[:-1] + ";"
        db_conn.execute(sql_statement)
        db_conn.commit()

    # noinspection PyTypeChecker
    def g_kmap_all(self):
        db_conn = self.db_conn
        cursor = db_conn.execute("SELECT * FROM KMAP_TABLE")
        kmap_all = cursor.fetchall()
        if kmap_all:
            return json.load(kmap_all)
        else:
            return False

    def close_db(self):
        self.db_conn.close()


class WordleTools:
    DEPTH_OF_SUGGESTION = 10 ** 100  # (bigger numbers take longer)
    SHOW_TIMER = False  # toggle if you want to see what is taking so long
    LOOK_FOR_MATCHES_ONLY = 2  # at what match count do you prioritize picking the right match vs eliminating options

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
    def create_match_map(answers, guesses, knowledge, save_it):
        maps = MapsDB()
        knowledge_map = maps.g_kmap_all()
        if not knowledge_map:
            knowledge_map = {}

        match_map = {}
        total_words = len(answers)
        counter = 0
        start_time = time.time()
        if WordleTools.SHOW_TIMER:
            print("start timer")
        save_knowledge_map = False
        for guess in guesses:
            match_map[guess] = 0.0
            if WordleTools.SHOW_TIMER:
                counter = WordleTools.status_time_estimate(counter, start_time, len(guesses), "M map")

            for secret_word in answers:
                k = WordleTools.update_knowledge(copy.deepcopy(knowledge), secret_word, guess)
                k_hash = WordleTools.dict_hash(k)

                match_count = False
                if k_hash in knowledge_map:
                    match_count = knowledge_map[k_hash]
                if not match_count:
                    matches = WordleTools.get_possible_matches(k, answers)
                    match_count = len(matches)
                    knowledge_map[k_hash] = match_count
                    save_knowledge_map = True
                match_map[guess] += match_count / total_words
        if save_it and save_knowledge_map:
            maps.insert_batch_kmap = knowledge_map

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
    def get_suggestion_new(knowledge, guess_options, answer_options, save_it):
        maps = MapsDB()
        k_hash = WordleTools.dict_hash(knowledge)  # get hashkey for suggestion map
        existing_suggestion_knowledge = maps.get_suggestion(k_hash)
        if existing_suggestion_knowledge:
            return existing_suggestion_knowledge

        matches = WordleTools.get_possible_matches(copy.deepcopy(knowledge), answer_options)

        if len(matches) < 3:
            suggested_guess = matches[0]
        else:
            match_map = WordleTools.create_match_map(matches, guess_options, knowledge, save_it)

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

        if save_it:
            maps.insert_suggestion(k_hash, suggested_guess)
        return suggested_guess

    @staticmethod
    def get_suggestion_fast(knowledge, guess_options, answer_options):
        # get as much insight into the letters we don't know about that are in the remaining words
        # exclude words that

        matches = WordleTools.get_possible_matches(copy.deepcopy(knowledge), answer_options)
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

        match_map = WordleTools.create_match_map(matches, [focus_suggested_guess, suggested_guess], knowledge, False)

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
                print(description + " {0}% done. Time left ~{2}".format(str(round(progress * 100, 2)),
                                                                        str(datetime.timedelta(
                                                                            seconds=elapsed_time)),
                                                                        time_left_str), end="\r\n")
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
        return WordleTools.standardize_knowledge(knowledge)

    @staticmethod
    def default_knowledge():
        knowledge = {KNOWLEDGE.IN_WORD: [], KNOWLEDGE.NOT_IN_WORD: []}
        for i in range(KNOWLEDGE.WORD_LENGTH):
            knowledge[str(i)] = {KNOWLEDGE.NOT_IN_POSITION: [], KNOWLEDGE.IN_POSITION: False}
        return WordleTools.standardize_knowledge(knowledge)
