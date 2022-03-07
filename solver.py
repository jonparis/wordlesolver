import copy
import operator
import math
import time
from wordle_common import Knowledge, Tools, COLORS, CONST
from solver_model import MapsDB
import json

class Solver:
    WAIT_FOR_BEST_SUGGESTION = 10  # time in seconds to wait for best guess
    SHOW_TIMER = True  # toggle if you want to see what is taking so long

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

    def save_maps_to_db(self):
        if len(self.kmap_new) > 0:
            for k in self.kmap_new: self.maps.insert_knowledge(k, self.kmap_new[k][CONST.GUESS],
                                                               self.kmap_new[k][CONST.AGTS], self.kmap_new[k][CONST.C],
                                                               self.kmap_new[k][CONST.M], self.kmap_new[k][CONST.OPT])
            print(str(len(self.kmap_new)), "kmap saved")
        # clear our kmap_new and match_map new
        self.kmap_new = {}

    def create_entropy_map(self, knowledge, matches: tuple) -> dict:
        e_map = {}
        m_count = len(matches)
        for guess in self.guesses:
            e_map[guess] = 0
            if guess in matches: e_map[guess] = 1 / m_count
            frequency = {}
            for secret in matches:
                k = Knowledge.update_knowledge(knowledge, secret, guess)
                kint = Knowledge.k_dict_to_int(k)
                if kint in frequency:
                    frequency[kint] += 1
                else:
                    frequency[kint] = 1
            for kint in frequency:
                p = frequency[kint] / m_count  # fraction of matches left after guess
                e_map[guess] -= (p * math.log(p, 2))

        return {k: v for k, v in sorted(e_map.items(), key=operator.itemgetter(1), reverse=True)}

    @staticmethod
    def get_suggestion(k: dict, guesses: tuple) -> str:
        solver = Solver(guesses, True)
        suggestion = solver.get_suggestion_stable(k)
        return suggestion

    def get_suggestion_stable(self, k: dict) -> str:
        kint = Knowledge.k_dict_to_int(k)
        if kint in self.kmap and self.kmap[kint][CONST.C] >= CONST.MED:
            return self.kmap[kint][CONST.GUESS]

        matches = Knowledge.get_possible_matches(k, self.answers)
        total_matches = len(matches)

        if total_matches <= 2: return matches[0]

        to_test = 8  # guess top ten guesses
        if total_matches < to_test: to_test = total_matches

        if matches == 3:
            guesses_to_test = matches

        elif kint in self.e_map:
            guesses_to_test = self.e_map[kint]
        else:
            e_map = self.create_entropy_map(k, matches)
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

    def get_agts(self, prev_guess: str, matches: tuple, starting_knowledge: dict):
        temp_kmap = {}
        total_matches = len(matches)
        total_guesses = 0
        dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        for i in range(len(matches)):
            secret = matches[i]
            if self.debug: print("\r\033[K", "Target: " + secret, end="")
            guess = None
            k = starting_knowledge
            kint = Knowledge.k_dict_to_int(k)
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
                    kint = Knowledge.k_dict_to_int(k)
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
                    if prev_guess == "salet": print(kint, prev_guesses)  # for printing answers
                    break
                k = Knowledge.update_knowledge(k, secret, guess)
        avg = total_guesses / total_matches
        avg_f = format(avg, '.9f')
        if total_guesses > 20:  # supress small options
            print("\r\033[K", prev_guess, total_guesses, avg_f, str(dist), self.max_depth, end="\n")
        return avg

    def auto_play(self, first_guess: str):
        self.get_agts(first_guess, self.answers, Knowledge.default_knowledge())
        self.save_maps_to_db()
