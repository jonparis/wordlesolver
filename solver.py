import copy
import operator
import math
import time
from wordle_common import Knowledge, Tools, COLORS, CONST
from solver_model import MapsDB
import json
import string


class Solver:
    def __init__(self, guesses: tuple, fast: bool):
        self.guesses = guesses
        self.answers = self.guesses[:CONST.ANSWERS_LEN]
        self.maps = MapsDB()
        self.kmap = self.maps.get_all_kmap()
        self.kmap_new = {}
        self.e_map = {}
        self.temp_kmap = None  # used to find agts
        self.fast = fast  # when using fast don't save knowledge or kmap
        self.debug = False
        self.max_depth = 0
        self.previous_solutions = []
        self.knowledge_default = Knowledge.default_knowledge()
        self.exclude_prev = True
        self.answer_map = self.build_answer_map()
        if self.fast is False: self.bucket_lookup = self.build_bucket_lookup()  # comment out.
        self.rec_first_words = ("salet", "reast", "crate", "trace", "slate", "crane")

    def build_answer_map(self):
        answer_map = {}
        for i in range(0, 26):
            answer_map[i] = {CONST.YES: [], CONST.NO: []}
            let = string.ascii_lowercase[i]
            for j in range(CONST.ANSWERS_LEN):
                a = self.answers[j]
                if let not in a: answer_map[i][CONST.NO].append(j)
                if let in a: answer_map[i][CONST.YES].append(j)
        for i in range(26, 52):
            answer_map[i] = {CONST.NO: [], CONST.YES: []}
            let = string.ascii_lowercase[i - 26]
            for j in range(CONST.ANSWERS_LEN):
                a = self.answers[j]
                if a.count(let) == 1: answer_map[i][CONST.NO].append(j)
                if a.count(let) > 1: answer_map[i][CONST.YES].append(j)
        for p in range(CONST.WORD_LENGTH):
            start = 52 + 26 * p
            for i in range(start, start + 26):
                answer_map[i] = {CONST.NO: [], CONST.YES: []}
                let = string.ascii_lowercase[i - start]
                for j in range(CONST.ANSWERS_LEN):
                    a = self.answers[j]
                    if let != a[p]: answer_map[i][CONST.NO].append(j)
                    if let == a[p]: answer_map[i][CONST.YES].append(j)
        return answer_map

    def build_bucket_lookup(self) -> tuple:
        lookup = []
        for j in range(len(self.guesses)):
            row = []
            for s in self.guesses[:CONST.ANSWERS_LEN]:
                g = list(self.guesses[j])
                s = list(s)
                score = 0
                for i in range(CONST.WORD_LENGTH):
                    if s[i] == g[i]:
                        score += 2 * (3 ** i)
                        s[i] = 0
                        g[i] = 0
                for i in range(CONST.WORD_LENGTH):
                    if g[i] and g[i] in s:
                        score += 3 ** i
                        s[s.index(g[i])] = 0
                row.append(score)
            lookup.append(tuple(row))
        return tuple(lookup)

    def get_matches_ints(self, k):
        match_ints = list(range(0, CONST.ANSWERS_LEN))
        k_len = 26 * 7
        for i in range(k_len):
            ki = k[i]
            if ki == CONST.UNSURE: continue
            temp = set(self.answer_map[i][ki])
            match_ints = [v for v in match_ints if v in temp]
        return tuple(match_ints)

    def get_matches(self, k):
        matches = []
        int_list = self.get_matches_ints(k)
        for i in int_list: matches.append(self.answers[i])
        return tuple(matches)

    def save_maps_to_db(self):
        if self.fast: return
        if len(self.kmap_new) > 0:
            for k in self.kmap_new: self.maps.insert_knowledge(k, self.kmap_new[k][CONST.GUESS],
                                                               self.kmap_new[k][CONST.AGTS], self.kmap_new[k][CONST.C],
                                                               self.kmap_new[k][CONST.M], self.kmap_new[k][CONST.OPT])
            print(str(len(self.kmap_new)), "kmap saved")
        # clear our kmap_new and match_map new
        self.kmap_new = {}

    def create_entropy_map(self, matches: tuple) -> dict:
        e_map = {}
        m_count = len(matches)
        for i in range(CONST.GUESSES_LEN):
            guess = self.guesses[i]
            e_map[guess] = 0
            if i in matches: e_map[guess] = 1 / m_count
            frequency = {}
            for s in matches:
                bucket = self.bucket_lookup[i][s]
                if bucket in frequency:
                    frequency[bucket] += 1
                else:
                    frequency[bucket] = 1
            for bucket in frequency:
                p = frequency[bucket] / m_count  # fraction of matches left after guess
                e_map[guess] -= (p * math.log(p, 2))

        return {k: v for k, v in sorted(e_map.items(), key=operator.itemgetter(1), reverse=True)}

    @staticmethod
    def get_suggestion(k: tuple) -> str:
        solver = Solver(guesses, True)
        suggestion = solver.get_suggestion_stable(k)
        return suggestion

    def get_suggestion_stable(self, k: tuple) -> str:
        kint = Knowledge.k_list_to_int(k)
        if kint in self.kmap and self.kmap[kint][CONST.C] >= CONST.MED:
            return self.kmap[kint][CONST.GUESS]

        match_ints = self.get_matches_ints(k)
        total_matches = len(match_ints)

        if total_matches <= 2: return self.guesses[match_ints[0]]

        if self.fast: return self.get_suggestion_fast(k)

        matches = [self.answers[i] for i in match_ints]

        to_test = 10  # guess top guesses
        if total_matches < to_test: to_test = total_matches

        if total_matches == 3:
            guesses_to_test = matches
        elif kint in self.e_map:
            guesses_to_test = self.e_map[kint]
        else:
            e_map = self.create_entropy_map(match_ints)
            guesses_to_test = self.e_map[kint] = list(e_map.keys())[:to_test]

        best_agts = 10  # arbitrarily high
        best_guess = guesses_to_test[0]

        if self.fast: return best_guess  # remove all the recursive search

        conf = CONST.MED
        pos = 0
        for guess in guesses_to_test:
            agts = self.get_agts(guess, matches, k)
            if agts and agts < best_agts:
                best_agts = agts
                best_guess = guess
                if pos > self.max_depth: self.max_depth = pos
            if agts == 2 - 1 / total_matches:
                conf = CONST.PER
                break
            pos += 1

        if kint in self.kmap and best_agts < self.kmap[kint][CONST.AGTS]:
            print(COLORS.GREEN, "IMPROVEMENT FOUND in position ", str(pos), self.kmap[kint][CONST.GUESS], "to",
                  best_guess, COLORS.SPACE_COLOR)
        if not self.fast:
            self.kmap[kint] = self.kmap_new[kint] = (best_guess, best_agts, conf, total_matches, to_test)
            if len(self.kmap_new) > 100: self.save_maps_to_db()
        return best_guess

    def get_suggestion_fast(self, k: tuple) -> str:
        # get as much insight into the letters we don't know about that are in the remaining words
        # exclude words that
        guesses = self.guesses
        matches = self.get_matches(k)
        letter_count = {}
        focus_letter_count = {}
        in_word_letters = [string.ascii_lowercase[i] for i in k[0:26]]
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

        if total_matches < 2:
            guesses = matches
        for word in guesses:
            coverage = sum([letter_count[c] for c in set([c for c in word])])
            if coverage > max_cov:
                max_cov = coverage
                suggested_guess = word

        return suggested_guess

    def get_agts(self, prev_guess: str, matches: tuple, starting_knowledge: tuple):
        temp_kmap = {}
        total_matches = len(matches)
        total_guesses = 0
        dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        for i in range(len(matches)):
            secret = matches[i]
            if self.debug: print("\r\033[K", "Target: " + secret, end="")
            guess = None
            k = starting_knowledge
            kint = Knowledge.k_list_to_int(k)
            prev_guesses = tuple()
            try_count = 0
            while guess != secret:
                try_count += 1
                total_guesses += 1
                if try_count == 1: guess = prev_guess
                else: guess = self.get_suggestion_stable(k)
                if not guess: return False  # not sure why this happens but should fail
                prev_guesses = prev_guesses + tuple([guess])
                if try_count == 2:
                    kint = Knowledge.k_list_to_int(k)
                    if kint not in temp_kmap:
                        temp_kmap[kint] = {"m": 0, "total_guesses": 0, "agts": None, "g": guess}
                    temp_kmap[kint]["m"] += 1
                if guess == secret:
                    dist[try_count] += 1
                    if try_count > 1:
                        temp_kmap[kint]["total_guesses"] += try_count - 1
                        t_g = temp_kmap[kint]["total_guesses"]
                        t_m = temp_kmap[kint]["m"]
                        temp_kmap[kint]["agts"] = t_g / t_m
                    if self.debug: print("\r\033[K", secret, "in", str(try_count), prev_guesses, end="\n")
                    if self.exclude_prev: self.previous_solutions.append(self.guesses.index(guess))
                    if prev_guess in self.rec_first_words: print(kint, prev_guesses)  # for printing answers for starting word
                    break
                k = Knowledge.update_knowledge(k, secret, guess)
        avg = total_guesses / total_matches
        avg_f = format(avg, '.9f')
        if total_guesses > 20:  # supress small options
            print("\r\033[K", prev_guess, total_guesses, avg_f, str(dist), self.max_depth, end="\n")
        if total_guesses > 7900 and prev_guess in self.rec_first_words: self.previous_solutions = []
        return avg

    # @Tools.profileme  # remove comment to get profile where there are bottlenecks
    def auto_play(self, first_guess: str):
        self.get_agts(first_guess, self.answers, self.knowledge_default)
        self.save_maps_to_db()
