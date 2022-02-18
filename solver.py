import copy
import operator
import time
from wordle_common import Knowledge, Tools, COLORS
from solver_model import MapsDB


class Solver:
    WAIT_FOR_BEST_SUGGESTION = 10  # time in seconds to wait for best guess
    SHOW_TIMER = True  # toggle if you want to see what is taking so long

    def __init__(self, answers: tuple, guesses: tuple, fast: bool):
        self.answers = answers
        self.guesses = guesses
        self.maps = MapsDB()
        self.kmap = self.maps.get_all_kmap()
        self.kmap_new = {}
        self.match_map = None
        self.match_map_new = {}
        self.temp_kmap = {}  # used to find agts
        self.kmap_to_optimize = {}
        self.fast = fast  # when using fast don't save knowledge or kmap

    def save_maps_to_db(self):
        if len(self.kmap_new) > 0:
            for k in self.kmap_new: self.maps.insert_knowledge(k, self.kmap_new[k][0], self.kmap_new[k][1],
                                                               self.kmap_new[k][2])
            print(str(len(self.kmap_new)), "kmap saved")
        # clear our kmap_new and match_map new
        self.kmap_new = {}
        self.match_map_new = {}


    @staticmethod
    def create_match_map(answers: tuple, guesses: tuple, knowledge: dict, fast: bool) -> dict:

        match_map = {}
        knowledge_map = {}
        total_words = len(answers)
        counter = 0
        est_time = {"c": 1, "s": -1}
        t = time.time()
        for guess in guesses:
            match_map[guess] = 0.0

            est_time = Tools.get_time_estimate(est_time["c"], t, len(guesses))
            if fast and est_time["s"] > Solver.WAIT_FOR_BEST_SUGGESTION:
                return {guess: False}
            if Solver.SHOW_TIMER: counter = Tools.timer(counter, t, len(guesses), "M map")

            for secret_word in answers:
                k = Knowledge.update_knowledge(knowledge, secret_word, guess)
                k_hash = Knowledge.dict_hash(k)

                if guess == secret_word:
                    match_count = 0
                elif k_hash in knowledge_map:
                    match_count = knowledge_map[k_hash]
                else:
                    matches = Knowledge.get_possible_matches(k, answers)
                    match_count = len(matches)
                knowledge_map[k_hash] = match_count
                match_map[guess] += match_count / total_words
        return {k: v for k, v in sorted(match_map.items(), key=operator.itemgetter(1))}

    def get_saved_match_map(self, k_hash: str):
        match_map = {}
        if self.match_map is None:
            self.match_map = {}
            return {}
        if k_hash not in self.match_map: return False
        match_map_memory = self.match_map[k_hash]
        total_items = len(self.guesses)
        if len(match_map_memory) != total_items: return False

        for i in range(total_items): match_map[self.guesses[i]] = match_map_memory[i]
        return {k: v for k, v in sorted(match_map.items(), key=operator.itemgetter(1))}


    def save_match_map(self, k_hash: str, match_map: dict, depth: int):
        mm_name_sort = {k: match_map[k] for k in sorted(match_map)}
        match_map_count_list = []
        for mc in mm_name_sort:
            match_map_count_list.append(mm_name_sort[mc])
        self.match_map[k_hash] = match_map_count_list
        if depth < 2:  # only save match maps for 1 or 2 word combos.
            self.match_map_new[k_hash] = match_map_count_list


    @staticmethod
    def get_suggestion(k: dict, guesses: tuple, answers: tuple) -> str:
        solver = Solver(answers, guesses, True)
        suggestion = solver.get_suggestion_stable(k, ())
        return suggestion


    def get_suggestion_stable(self, k: dict, prev_guesses: tuple) -> str:
        k_hash = Knowledge.dict_hash(k)  # get hash key for suggestion map
        existing_suggestion_knowledge = self.maps.get_suggestion(k_hash)
        if k_hash in self.kmap and self.kmap[k_hash][2] > Knowledge.MED:
            return self.kmap[k_hash][0]
        if existing_suggestion_knowledge:
            return existing_suggestion_knowledge

        matches = Knowledge.get_possible_matches(k, self.answers)

        if len(matches) < 3: return matches[0]

        match_map = self.get_saved_match_map(k_hash)
        if not match_map:
            match_map = Solver.create_match_map(matches, self.guesses, k, self.fast)
            if self.fast and list(match_map.values())[0] is False: return self.get_suggestion_fast(k)
            if not self.fast: self.save_match_map(k_hash, match_map, len(prev_guesses))

        total_matches = len(matches)
        avg_exg_maybe_match = total_matches
        avg_exc_match = total_matches
        suggested_guess_matching = matches[0]
        suggested_guess_maybe_matching = suggested_guess_matching

        for guess in self.guesses:
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
        if not self.fast: self.maps.insert_suggestion(k_hash, suggested_guess)
        return suggested_guess

    def get_suggestion_fast(self, k: dict) -> str:
        # get as much insight into the letters we don't know about that are in the remaining words
        # exclude words that
        guesses = self.guesses
        matches = Knowledge.get_possible_matches(k, self.answers)
        letter_count = {}
        focus_letter_count = {}
        in_word_letters = k[Knowledge.IN_WORD]
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
        suggested_guess = guesses[0]
        max_focus = 0.0
        focus_suggested_guess = guesses[0]

        if total_matches < 2:
            guesses = matches
        for word in guesses:
            coverage = sum([letter_count[c] for c in set([c for c in word])])
            focus_coverage = sum([focus_letter_count[c] for c in set([c for c in word])])
            if coverage > max_cov:
                max_cov = coverage
                suggested_guess = word
            if focus_coverage > max_focus:
                max_focus = focus_coverage
                focus_suggested_guess = word

        match_map = Solver.create_match_map(matches, tuple([focus_suggested_guess, suggested_guess]), k, self.fast)

        narrow_over_try = 0
        if len(match_map) == 0: return suggested_guess

        if match_map[focus_suggested_guess] and match_map[suggested_guess] and total_matches:
            narrow_over_try = 1 / match_map[focus_suggested_guess] - 1 / match_map[suggested_guess] - 1 / total_matches
        if focus_suggested_guess and narrow_over_try > 0:
            suggested_guess = focus_suggested_guess

        return suggested_guess

    def auto_play(self, first_guess: str):
        self.optimize_agts_for_k(first_guess, self.answers, Knowledge.default_knowledge(), True)
        self.save_maps_to_db()

    def auto_play_and_optimize(self, first_guess: str):
        self.optimize_agts_for_k(first_guess, self.answers, Knowledge.default_knowledge(), True)
        to_update = copy.deepcopy(self.temp_kmap[first_guess])
        count = 0
        start_time = time.time()
        total = len(to_update)

        menu = str(input("Start optimizer? p (partial), f(full):")).lower()
        max_guess_to_test = len(self.guesses)
        optimize_to = Knowledge.PER
        if menu == 'p':
            max_guess_to_test = 100
            optimize_to = Knowledge.LOW
        elif menu == 'f':
            optimize_to = Knowledge.HIGH
        else:
            exit()

        low_count = 0
        match_list = {}
        for k_hash in to_update:
            if to_update[k_hash]["c"] <= optimize_to:
                match_list[k_hash] = to_update[k_hash]["matches"]
                low_count += 1

        match_list = {k: v for k, v in sorted(match_list.items(), key=operator.itemgetter(1))}

        print(str(low_count), "of", str(total), "to optimize!")

        for k_hash in match_list:
            count = Tools.timer(count, start_time, low_count, "optimizer")
            k = to_update[k_hash]["k"]
            matches = Knowledge.get_possible_matches(k, self.answers)

            print("\n", "optimizing for ", len(matches), "matches")
            best_guess = None
            best_agts = None
            match_map = self.create_match_map(matches, self.guesses, k, True)
            i = 0
            for guess in match_map:  # use match map to order by top 50 guesses
                i += 1
                if i > max_guess_to_test: break
                if guess == self.kmap[k_hash][0]: continue
                agts = self.optimize_agts_for_k(guess, matches, k, False)
                if best_guess is None or agts < best_agts:
                    best_guess = guess
                    best_agts = agts
            i = 0
            for guess in match_map:  # use match map to order by top 5 matching guesses
                if i > 5: break  # use match map to order by top 5 matching guesses
                if guess == self.kmap[k_hash][0]: continue
                if guess not in matches: continue  # skip non-matching guesses
                i += 1
                agts = self.optimize_agts_for_k(guess, matches, k, False)
                if best_guess is None or agts < best_agts:
                    best_guess = guess
                    best_agts = agts

            if best_agts < self.kmap[k_hash][1]:
                print(COLORS.GREEN, "improvement found!", str(best_agts), "better than", str(self.kmap[k_hash][1]), COLORS.SPACE_COLOR)
                self.kmap[k_hash] = self.kmap_new[k_hash] = (best_guess, best_agts, Knowledge.HIGH)
            elif best_agts == self.kmap[k_hash][1]:
                print(COLORS.YELLOW, "increased certainty!", str(best_agts), "same as", str(self.kmap[k_hash][1]), COLORS.SPACE_COLOR)
                self.kmap[k_hash] = self.kmap_new[k_hash] = (best_guess, best_agts, Knowledge.MED)
            else:  # use medium for previously reviewed but not improved upon through optimize
                print(COLORS.YELLOW, "increased certainty!", str(best_agts), "not as good as", str(self.kmap[k_hash][1]),
                      COLORS.SPACE_COLOR)
                self.kmap[k_hash] = self.kmap_new[k_hash] = (self.kmap[k_hash][0], self.kmap[k_hash][1], Knowledge.MED)
            self.save_maps_to_db()

    def optimize_agts_for_k(self, prev_guess: str, matches: tuple, starting_knowledge: dict, debug: bool):
        self.temp_kmap[prev_guess] = {}
        total_matches = len(matches)
        total_guesses = 0
        dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
        for secret in matches:
            if debug: print("\r\033[K", "Target: " + secret, end="")
            guess = None
            k = starting_knowledge
            k_hash = Knowledge.dict_hash(k)
            prev_guesses = tuple()
            try_count = 0
            while guess != secret:
                try_count += 1
                total_guesses += 1
                if try_count == 1:
                    guess = prev_guess
                else:
                    guess = self.get_suggestion_stable(k, prev_guesses)
                if try_count == 2:
                    k_hash = Knowledge.dict_hash(k)
                    if k_hash not in self.temp_kmap[prev_guess]:
                        self.temp_kmap[prev_guess][k_hash] = {"matches": 0, "total_guesses": 0, "agts": None,
                                                              "g": guess, "k": k}
                    self.temp_kmap[prev_guess][k_hash]["matches"] += 1
                if guess == secret:
                    dist[try_count] += 1
                    if try_count > 1:
                        self.temp_kmap[prev_guess][k_hash]["total_guesses"] += try_count - 1
                        t_g = self.temp_kmap[prev_guess][k_hash]["total_guesses"]
                        t_m = self.temp_kmap[prev_guess][k_hash]["matches"]
                        self.temp_kmap[prev_guess][k_hash]["agts"] = t_g / t_m
                    if debug: print("\r\033[K", secret, "in", str(try_count), end="\n")
                    break
                else:
                    k = Knowledge.update_knowledge(k, secret, guess)
                    prev_guesses = prev_guesses + tuple([guess])
        avg = total_guesses / total_matches
        avg_f = format(avg, '.5f')
        count = 1
        kmap_distro = {"PER": 0, "HIGH": 0, "MED": 0, "LOW": 0, "VERY LOW": 0}
        for kmap in self.temp_kmap[prev_guess]:
            g = self.temp_kmap[prev_guess][kmap]["g"]
            c = self.temp_kmap[prev_guess][kmap]["agts"]
            m = self.temp_kmap[prev_guess][kmap]["matches"]
            if c <= 2 - 1 / m:
                self.temp_kmap[prev_guess][kmap]["c"] = Knowledge.PER
                self.kmap[kmap] = self.kmap_new[kmap] = (g, c, Knowledge.PER)
                kmap_distro["PER"] += 1
            elif kmap in self.kmap and self.kmap[kmap][2] >= Knowledge.HIGH:
                self.temp_kmap[prev_guess][kmap]["c"] = Knowledge.HIGH
                kmap_distro["HIGH"] += 1  # avoids re-optimizing previously optimized solutions
            elif kmap in self.kmap and self.kmap[kmap][2] >= Knowledge.MED:
                self.temp_kmap[prev_guess][kmap]["c"] = Knowledge.MED
                kmap_distro["MED"] += 1  # avoid re-optimizing previously assessed solutions
            elif c <= 2.0:
                self.kmap[kmap] = self.kmap_new[kmap] = (g, c, Knowledge.LOW)
                self.temp_kmap[prev_guess][kmap]["c"] = Knowledge.LOW
                kmap_distro["LOW"] += 1
            else:
                self.kmap[kmap] = self.kmap_new[kmap] = (g, c, Knowledge.VERY_LOW)
                self.temp_kmap[prev_guess][kmap]["c"] = Knowledge.VERY_LOW
                kmap_distro["VERY LOW"] += 1
            count += 1
        if debug: print("\r\033[K", prev_guess, total_guesses, avg_f, str(dist), end="\n")
        if debug: print(kmap_distro)
        return avg
