import copy
import operator
import math
import time
from wordle_common import Knowledge, Tools, COLORS, CONST
from solver_model import MapsDB
import json
import string


class Solver:
    def __init__(self, guesses: tuple, config: dict):
        self.guesses = guesses
        self.answers = self.guesses[:CONST.ANSWERS_LEN]
        
        # purge and print
        self.first_guesses = []
        self.purge_flag = False
        self.save_post_purge = False

        # config
        self.max_depth = 0
        self.to_test_depth = 15
        self.hard = config['hard'] if "hard" in config else False
        self.fast = config['fast'] if "fast" in config else False
        self.to_print = config["to_print"] if "to_print" in config else False
        self.optimize = config["optimize"] if "optimize" in config else False
        self.top_level = config["top_level"] if "top_level" in config else 10
        self.next_levels = config["next_levels"] if "next_levels" in config else 10
        self.starting_guess = config["starting_word"] if "starting_word" in config else ""
        
        # maps to save state and suggestions
        self.maps = MapsDB()
        self.kmap = self.maps.get_all_kmap(self.hard)
        self.kmap_new = {}
        self.e_map = {}
        self.answer_map = self.build_answer_map()
        if self.hard: self.guess_map = self.build_guess_map()
        if self.fast is False: self.bucket_lookup = self.build_bucket_lookup()

    def build_answer_map(self):
        answer_map = {}
        for i in range(CONST.WORD_K_START, CONST.WORD_K_START + 26):
            answer_map[i] = {CONST.YES: [], CONST.NO: []}
            let = string.ascii_lowercase[i - CONST.WORD_K_START]
            for j in range(CONST.ANSWERS_LEN):
                a = self.answers[j]
                if let not in a: answer_map[i][CONST.NO].append(j)
                if let in a: answer_map[i][CONST.YES].append(j)
        for p in range(CONST.WORD_LENGTH):
            start = CONST.POSITION_START + 26 * p
            for i in range(start, start + 26):
                answer_map[i] = {CONST.NO: [], CONST.YES: []}
                let = string.ascii_lowercase[i - start]
                for j in range(CONST.ANSWERS_LEN):
                    a = self.answers[j]
                    if let != a[p]: answer_map[i][CONST.NO].append(j)
                    if let == a[p]: answer_map[i][CONST.YES].append(j)
        for i in range(CONST.MULTI2, CONST.MULTI2 + 26):
            answer_map[i] = {CONST.NO: [], CONST.YES: []}
            let = string.ascii_lowercase[i - CONST.MULTI2]
            for j in range(CONST.ANSWERS_LEN):
                a = self.answers[j]
                if a.count(let) == 1: answer_map[i][CONST.NO].append(j)
                if a.count(let) > 1: answer_map[i][CONST.YES].append(j)
        for i in range(CONST.MULTI3, CONST.MULTI3 + 26):
            answer_map[i] = {CONST.NO: [], CONST.YES: []}
            let = string.ascii_lowercase[i - CONST.MULTI3]
            for j in range(CONST.ANSWERS_LEN):
                a = self.answers[j]
                if a.count(let) < 3: answer_map[i][CONST.NO].append(j)
                if a.count(let) >= 3: answer_map[i][CONST.YES].append(j)
        print("answer_map built")
        return answer_map

    def build_guess_map(self):
        guess_map = {}
        for i in range(CONST.WORD_K_START, CONST.WORD_K_START + 26):
            guess_map[i] = []
            let = string.ascii_lowercase[i - CONST.WORD_K_START]
            for j in range(CONST.GUESSES_LEN):
                if let in self.guesses[j]: guess_map[i].append(j)
        for p in range(CONST.WORD_LENGTH):
            start = CONST.POSITION_START + 26 * p
            for i in range(start, start + 26):
                guess_map[i] = []
                let = string.ascii_lowercase[i - start]
                for j in range(CONST.GUESSES_LEN):
                    if let == self.guesses[j][p]: guess_map[i].append(j)
        print("guess_map built")
        return guess_map

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
        print("bucket lookup built")
        return tuple(lookup)

    def get_matches_ints(self, k: tuple):
        k_len = 26 * (CONST.WORD_LENGTH + 3)
        match_ints = CONST.EMPTY_MATCH_INTS
        for i in range(k_len):
            if k[i] == CONST.UNSURE: continue
            else: temp = set(self.answer_map[i][k[i]])
            match_ints = [v for v in match_ints if v in temp]
        return tuple(match_ints)

    def get_guess_ints(self, k: tuple):
        if not self.hard: return range(CONST.GUESSES_LEN)
        k_len = 26 * (CONST.WORD_LENGTH + 1)
        guess_ints = CONST.EMPTY_GUESS_INTS
        for i in range(k_len):
            if k[i] == CONST.YES: temp = set(self.guess_map[i])
            else: continue
            guess_ints = [v for v in guess_ints if v in temp]
        return tuple(guess_ints)

    def get_matches(self, k: tuple):
        return [self.answers[v] for v in self.get_matches_ints(k)]

    def save_maps_to_db(self):
        if self.fast: return
        for k in self.kmap_new: 
            if self.kmap_new[k][1] == 2: self.kmap_new[k] = (self.kmap_new[k][0], 0)
            self.maps.insert_knowledge(k, self.kmap_new[k], self.hard)
        self.kmap_new = {}

    def create_entropy_map(self, matches: tuple, guess_ints) -> dict:
        e_map = {}
        m_count = len(matches)
        for g in guess_ints:
            e_map[g] = 0
            if g in matches: e_map[g] = 1 / m_count
            frequency = {}
            for s in matches:
                bucket = self.bucket_lookup[g][s]
                if bucket in frequency:
                    frequency[bucket] += 1
                else:
                    frequency[bucket] = 1
            for bucket in frequency:
                p = frequency[bucket] / m_count  # fraction of matches left after guess
                e_map[g] -= (p * math.log(p, 2))

        return {k: v for k, v in sorted(e_map.items(), key=operator.itemgetter(1), reverse=True)}

    def get_suggestion_stable(self, k: tuple, prev_guesses: tuple) -> str:
        kint = Knowledge.k_list_to_int(k)

        if kint in self.kmap and (self.kmap[kint][1] >= 1 or self.optimize is False):
            if self.save_post_purge: self.kmap_new[kint] = self.kmap[kint]
            return self.guesses[self.kmap[kint][0]]

        match_ints = self.get_matches_ints(k)
        total_matches = len(match_ints)
        default_gint = match_ints[0]
        if total_matches <= 2: return self.guesses[default_gint]

        if self.fast: return self.get_suggestion_fast(k)


        if prev_guesses + match_ints in self.e_map:
            guesses_to_test = self.e_map[prev_guesses + match_ints]
        else:
            e_map = self.create_entropy_map(match_ints, self.get_guess_ints(k))
            guesses_to_test = self.e_map[match_ints] = list(e_map.keys())
        pg_ints = [self.guesses.index(g) for g in prev_guesses]
        self.e_map[prev_guesses + match_ints] = guesses_to_test = [gint for gint in guesses_to_test if gint not in pg_ints][:self.to_test_depth]


        # avoid regressing if we've found a better guess in previous deeper pass
        if kint in self.kmap:
            guesses_to_test = self.e_map[match_ints] = [self.kmap[kint][0]] + guesses_to_test

        if kint == 0 and len(self.first_guesses) == 0 and self.purge_flag:
            for g in guesses_to_test: self.first_guesses.append(self.guesses[g])
            self.optimize = False
            return self.guesses[guesses_to_test[0]]
        if kint == 0: print("First approximation of best guesses", str([self.guesses[i] for i in guesses_to_test]))

        best_agts = 10  # arbitrarily high
        prev_kint_agts = 10  # default
        best_gint = guesses_to_test[0] if 0 in guesses_to_test else match_ints[0]  # not sure why len guesses_to_test is 0

        pos = 0
        perfect = 2  # will be converted to 0 on save
        match_ints_tested = 0
        found_pos = 0
        matches = [self.answers[i] for i in match_ints]
        for gint in guesses_to_test:
            agts = self.get_agts(self.guesses[gint], matches, k, prev_guesses)
            if gint in match_ints: match_ints_tested += 1
            if kint in self.kmap and gint == self.kmap[kint][0]: prev_kint_agts = agts
            if agts and (agts < best_agts or (total_matches == 3 and agts == best_agts)):
                best_agts = agts
                best_gint = gint
                found_pos = pos
                if pos > self.max_depth: self.max_depth = pos
            if agts == 2 - 1 / total_matches:
                perfect = 1
                break
            if pos > len(match_ints) and agts <= 2.0 and match_ints_tested == len(match_ints):
                perfect = 1  # perfect guess if not a match is a 2.0
                break
            pos += 1

        if self.optimize and kint in self.kmap and best_gint != self.kmap[kint][0] and best_agts < prev_kint_agts:
            print(COLORS.GREEN, "improvement found!", COLORS.SPACE_COLOR)

        if not self.fast: self.kmap[kint] = self.kmap_new[kint] = (best_gint, perfect)

        return self.guesses[best_gint]

    def get_suggestion_fast(self, k: tuple) -> str:
        # get as much insight into the letters we don't know about that are in the remaining words
        guesses = self.guesses
        matches = [self.answers[i] for i in self.get_matches_ints(k)]

        letter_count = {}
        focus_letter_count = {}
        in_word_letters = [string.ascii_lowercase[i] for i in k[0:26]]
        total_matches = len(matches)

        for c in string.ascii_lowercase:
            letter_count[c] = 0.0
            focus_letter_count[c] = 0.0
        for word in matches:
            for c in word:
                letter_count[c] += 1.0
                if c not in in_word_letters:
                    focus_letter_count[c] += 1.0

        max_cov = 0.0
        suggested_guess = guesses[0]

        if total_matches <= 3:
            guesses = matches
        for word in guesses:
            coverage = sum([letter_count[c] for c in set([c for c in word])])
            if coverage > max_cov:
                max_cov = coverage
                suggested_guess = word

        return suggested_guess

    def get_agts(self, first_guess: str, matches: tuple, starting_knowledge: tuple, starting_prev_guesses: tuple):
        total_matches = len(matches)
        total_guesses = 0
        dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0}
        max_guesses = 6
        starting_kint = Knowledge.k_list_to_int(starting_knowledge)
        for i in range(len(matches)):
            secret = matches[i]
            guess = None
            k = starting_knowledge
            kint = Knowledge.k_list_to_int(k)
            prev_guesses = starting_prev_guesses
            try_count = 0
            while guess != secret:
                try_count += 1
                total_guesses += 1
                if first_guess == self.starting_guess: self.to_test_depth = self.top_level
                else: self.to_test_depth = self.next_levels
                if try_count == 1 and first_guess and len(first_guess) == CONST.WORD_LENGTH: guess = first_guess
                else: guess = self.get_suggestion_stable(k, prev_guesses)
                if len(prev_guesses) > max_guesses and guess != secret: return False  # allow miss by one (not 2)
                prev_guesses = prev_guesses + tuple([guess])
                if try_count == 2: kint = Knowledge.k_list_to_int(k)
                if guess == secret:
                    dist[try_count] += 1
                    if self.to_print and starting_kint == 0: print(str(prev_guesses)[1:-1], end="\n")
                    break
                k = Knowledge.update_knowledge(k, secret, guess)
        avg = total_guesses / total_matches
        avg_f = format(avg, '.9f')
        if total_guesses > 7900:
            self.save_maps_to_db()
            print("\r\033[K", first_guess, total_guesses, avg_f, str(dist), self.max_depth, end="\n")
            self.max_depth = 0
        return avg

    def auto_play(self):
        self.get_agts(self.starting_guess, self.answers, CONST.EMPTY_KNOWLEDGE, ())
        self.save_maps_to_db()

    @Tools.profileme  # remove comment to get profile where there are bottlenecks
    def auto_play_profile(self):
        self.get_agts(self.starting_guess, self.answers, CONST.EMPTY_KNOWLEDGE, ())
        self.save_maps_to_db()

    def purge_unused(self):
        self.purge_flag = True
        self.get_agts("", self.answers, CONST.EMPTY_KNOWLEDGE, ())
        self.save_post_purge = True
        self.maps.purge_db(self.hard)
        self.optimize = False
        for g in self.first_guesses:
            self.get_agts(g, self.answers, CONST.EMPTY_KNOWLEDGE, ())
            self.save_maps_to_db()
        self.get_agts("", self.answers, CONST.EMPTY_KNOWLEDGE, ())
        self.save_maps_to_db()

