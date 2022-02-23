import time
from functools import lru_cache

from wordle_common import Knowledge, TimeTools
from solver_model import MapsDB


class Solver:
    def __init__(self, answers, guesses):
        self.answers = answers
        self.guesses = guesses
        self.kmap = {}

    WAIT_FOR_BEST_SUGGESTION = 10 * 10 * 100  # time in seconds to wait for best guess
    SHOW_TIMER = True  # toggle if you want to see what is taking so long

    # @lru_cache(maxsize=2 ** 20)
    def create_match_map(self, answers: tuple, guesses: tuple, knowledge: str, wait: bool):
        match_map = {}
        total_words = len(answers)
        counter = 0
        seconds_left = {"count": 1, "seconds_left": -1}
        start_time = time.time()
        for guess in guesses:
            match_map[guess] = 0.0

            seconds_left = TimeTools.get_time_estimate(seconds_left["count"], start_time, len(guesses))
            if not wait and seconds_left["seconds_left"] > Solver.WAIT_FOR_BEST_SUGGESTION:
                return False
            if Solver.SHOW_TIMER:
                counter = TimeTools.status_time_estimate(counter, start_time, len(guesses), "M map")

            for secret_word in answers:
                k = Knowledge.update_knowledge(knowledge, secret_word, guess)

                if guess == secret_word:
                    match_count = 0
                elif k in self.kmap:
                    match_count = self.kmap[k]
                else:
                    matches = Knowledge.get_possible_matches(k, answers)
                    match_count = len(matches)
                    self.kmap[k] = match_count
                match_map[guess] += match_count / total_words

        return match_map

    # @lru_cache(maxsize=None)
    def get_suggestion_exp(self, k: str, guesses: tuple, answers: tuple, depth: int, test: bool) -> dict:
        maps = MapsDB()
        existing_suggestion = maps.get_knowledge(k)
        if existing_suggestion and not test:
            existing_suggestion["d"] = depth + 1
            return existing_suggestion

        matches = Knowledge.get_possible_matches(k, answers)
        non_match_guesses = tuple(set(guesses).difference(matches))
        guesses = matches + non_match_guesses  # reorder guesses to try matches first
        total_matches = len(matches)
        max_depth = 5
        # "g" = guess. "c" = certainty, "d" depth (for use in recursive function)
        if total_matches == 0: return {"g": False}
        if depth > max_depth: return {"g": False}
        if total_matches == 1: return {"g": matches[0], "c": 1, "d": depth + 1}
        if total_matches == 2: return {"g": matches[0], "c": 1.5, "d": depth + 1}

        best_guess = matches[0]
        best_guess_c = total_matches  # lower is better
        guess_map = {}
        counter = 0
        start_time = time.time()
        for i in range(len(guesses)):
            guess = guesses[i]
            if Solver.SHOW_TIMER and depth == 0:
                counter = TimeTools.status_time_estimate(counter, start_time, len(guesses), "M map")

            guess_map[guess] = self.populate_guess_map(depth, guess, guesses, i, k, matches)

            if guess_map[guess] is not False:
                if guess_map[guess] <= 1 - 1 / total_matches:
                    best_guess = guess
                    best_guess_c = guess_map[guess]
                    break  # you found the best possible guess! you are done
                elif guess_map[guess] < best_guess_c:
                    best_guess = guess
                    best_guess_c = guess_map[guess]

        if not test: maps.insert_knowledge(k, best_guess, best_guess_c)
        return {"g": best_guess, "c": best_guess_c, "d": depth + 1}

    def populate_guess_map(self, depth: int, guess: str, guesses: tuple, i: int, k: str, matches: tuple) -> float:
        guess_c = 0.0
        total_matches = len(matches)
        maps = MapsDB()
        for secret in matches:
            if guess == secret:
                guess_c += 0  # is this right?
            else:
                k_r = Knowledge.update_knowledge(k, secret, guess)
                m = Knowledge.get_possible_matches(k_r, matches)
                if len(m) / total_matches > 0.9:  # if the matches is the same you didn't get knowledge
                    return False  # unsure on this one
                existing_suggestion = maps.get_knowledge(k_r)
                if existing_suggestion:
                    guess_c += (depth + 1) * existing_suggestion["c"] / total_matches
                elif depth < 1:
                    updated_guesses = guesses[:i] + guesses[i + 1:]
                    b = self.get_suggestion_exp(k_r, updated_guesses, m, depth, False)
                    if b["g"] is False: return False
                    guess_c += b["d"] * b["c"] / total_matches
                else:
                    guess_c += len(m) / total_matches
        return guess_c

    @staticmethod
    def get_suggestion(k: str, guesses: tuple, answers: tuple) -> str:
        use_stable = True  # change if chose to use non-stable
        use_fast = False
        solver = Solver(guesses, answers)
        if use_stable:
            return solver.get_suggestion_stable(k)
        elif use_fast:
            return solver.get_suggestion_fast(k)
        else:
            sug_obj = solver.get_suggestion_exp(k, solver.guesses, solver.answers, 0, False)
            return sug_obj["g"]

    #@lru_cache(maxsize=2**20)
    def get_suggestion_stable(self, k: str) -> str:
        maps = MapsDB()
        existing_suggestion_knowledge = maps.get_suggestion(k)
        if existing_suggestion_knowledge:
            return existing_suggestion_knowledge

        matches = Knowledge.get_possible_matches(k, self.answers)

        if len(matches) < 3:
            suggested_guess = matches[0]
        else:
            match_map = self.create_match_map(matches, self.guesses, k, True)

            if match_map is False: return self.get_suggestion_fast(k)
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

        maps.insert_suggestion(k, suggested_guess)
        return suggested_guess

    # @lru_cache(maxsize=2**25)
    def get_suggestion_fast(self, k: str) -> str:
        # get as much insight into the letters we don't know about that are in the remaining words
        # exclude words that

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
        suggested_guess = self.guesses[0]
        max_focus = 0.0
        focus_suggested_guess = self.guesses[0]

        for word in self.guesses:
            coverage = sum([letter_count[c] for c in set([c for c in word])])
            focus_coverage = sum([focus_letter_count[c] for c in set([c for c in word])])
            if coverage > max_cov:
                max_cov = coverage
                suggested_guess = word
            if focus_coverage > max_focus:
                max_focus = focus_coverage
                focus_suggested_guess = word

        match_map = self.create_match_map(matches, (focus_suggested_guess, suggested_guess), k, True)

        narrow_over_try = 1 / match_map[focus_suggested_guess] - 1 / match_map[suggested_guess] - 1 / total_matches
        if focus_suggested_guess and narrow_over_try > 0:
            suggested_guess = focus_suggested_guess

        return suggested_guess
