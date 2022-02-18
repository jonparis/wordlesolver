import datetime
import hashlib
import json
import time
import operator
from wordle_common import Knowledge, TimeTools
from solver_model import MapsDB


class Solver:
    WAIT_FOR_BEST_SUGGESTION = 10 * 10*100  # time in seconds to wait for best guess
    SHOW_TIMER = True  # toggle if you want to see what is taking so long

    @staticmethod
    def create_match_map(answers, guesses, knowledge, wait):
 
        origin_k_hash = Knowledge.dict_hash(knowledge)

        match_map = {}
        knowledge_map = {}
        # maps = MapsDB()

        total_words = len(answers)
        counter = 0
        seconds_left = {"count": 1, "seconds_left": -1}
        start_time = time.time()
        save_knowledge_map = False
        for guess in guesses:
            match_map[guess] = 0.0

            seconds_left = TimeTools.get_time_estimate(seconds_left["count"], start_time, len(guesses))
            if not wait and seconds_left["seconds_left"] > Solver.WAIT_FOR_BEST_SUGGESTION:
                return False
            if Solver.SHOW_TIMER:
                counter = TimeTools.status_time_estimate(counter, start_time, len(guesses), "M map")

            for secret_word in answers:
                k = Knowledge.update_knowledge(knowledge, secret_word, guess)
                k_hash = Knowledge.dict_hash(k)
                # info = maps.get_knowledge_info(k_hash)

                if guess == secret_word:
                    match_count = 0
                elif k_hash in knowledge_map:
                    match_count = knowledge_map[k_hash]
                else:
                    matches = Knowledge.get_possible_matches(k, answers)
                    match_count = len(matches)
                knowledge_map[k_hash] = match_count
                match_map[guess] += match_count / total_words
        
        return match_map


    @staticmethod
    def get_suggestion_recursive(k, guesses, answers, depth):
        maps = MapsDB()
        origin_k_hash = Knowledge.dict_hash(k)  # get hashkey for suggestion map
        existing_suggestion = maps.get_knowledge(origin_k_hash)
        if existing_suggestion:
            return existing_suggestion

        matches = Knowledge.get_possible_matches(k, answers)
        total_matches = len(matches)

        # "g" = guess. "c" = certainty
        if total_matches == 0: return {"g": False, "c": False, "d": False}
        if total_matches == 1: return {"g": matches[0], "c" : 0, "d": depth + 1} 
        if total_matches == 2: return {"g": matches[0], "c" : 1/2, "d": depth + 1}
        if depth > 5: return {"g": False, "c": False, "d": False}  
        
        best_guess = matches[0]
        best_guess_c = total_matches # lower is better
        match_map ={}
        counter = 0
        start_time = time.time()
        for guess in guesses:
            if Solver.SHOW_TIMER:
                counter = TimeTools.status_time_estimate(counter, start_time, len(guesses), "M map")

            match_map[guess] = 0.0
            for secret in matches:
                if guess == secret:
                    match_map[guess] += 0 # is this right?
                else:
                    k_r = Knowledge.update_knowledge(k, secret, guess)
                    k_hash = Knowledge.dict_hash(k_r)
                    m = Knowledge.get_possible_matches(k_r, answers)
                    match_map[guess] += len(m) / total_matches
            if match_map[guess] < best_guess_c: 
                best_guess = guess
                best_guess_c = match_map[guess]
            
        maps.insert_knowledge(origin_k_hash, best_guess, best_guess_c)
        return {"g" : best_guess, "c" : best_guess_c, "d": depth + 1}

    @staticmethod
    def guess_to_solve(knowledge, guess_options, answer_options, depth):
        MAX_DEPTH = 6  # when looking more deeply than max depth return false
        matches = Knowledge.get_possible_matches(knowledge, answer_options)
        total_matches = len(matches)
        if total_matches == 1:
            return {"g": matches[0], "c": 1, "d": depth}  # when there is a single option, guess it!
        elif total_matches == 2:
            return {"g": matches[0], "c": 1.5, "d": depth}  # when there are two options avg(1, 2) to guess it.
        elif total_matches == 0:
            print("problem! no matches")
            return False
        else:
            maps = MapsDB()
            match_map = Solver.create_match_map(matches, guess_options, knowledge, True)
            if not match_map: 
                print("problem no match map!")
                return False
            origin_k_hash = Knowledge.dict_hash(knowledge)

            # find perfect guess (in matches AND if not guessed then guess in 1)
            for guess in match_map.keys():
                if guess in match_map and match_map[guess] < 1:
                    return {"g": guess, "c": (2 - 1/total_matches), "d" : depth}

            """
                Now recursively find the best average guess. 
            """
            knowledge_map = {}
            
            bgts_obj = {}
            total_guesses = len(guess_options)
            TEST_GUESSES = 100 # ideally would be total_guesses, but too expensive.
            sorted_mm = sorted(match_map.items(), key=operator.itemgetter(1))
            guess_compare_counter = 0
            guess_map = {}
            counter = 0
            start_time = time.time()
            for index in range(total_guesses):
                guess_compare_counter += 1
                if Solver.SHOW_TIMER and depth == 0:
                    counter = TimeTools.status_time_estimate(counter, start_time, TEST_GUESSES, "B-guess")
                if guess_compare_counter > TEST_GUESSES:
                    break
                guess = sorted_mm[index][0]
                guess_map[guess] = 1  # start average guess to solve at 1 assuming it isn't hit on first guess. corrected later
                for secret in matches:
                    k = Knowledge.update_knowledge(knowledge, secret, guess)
                    k_hash = Knowledge.dict_hash(k)
                    r_bgts  = {}
                    if guess == secret:
                        guess_map[guess] -= (1 /  total_matches)
                    else:
                        # use DB to get existing knowledge
                        existing_knowledge = maps.get_knowledge(k_hash)
                        save_knowledge = False
                        if existing_knowledge: r_bgts = existing_knowledge
                        if not r_bgts or not r_bgts["c"]:
                            m = Knowledge.get_possible_matches(k, matches)
                            if len(m) > 0:
                                r_bgts = Solver.guess_to_solve(k, guess_options[:index] + guess_options[index+1:], m, depth + 1)
                                save_knowledge = True
                            else:
                                return False
                        if r_bgts and r_bgts["c"]:
                            if save_knowledge: maps.insert_knowledge(k_hash, r_bgts["g"], r_bgts["c"])
                            guess_map[guess] += (1 + r_bgts["c"]) / total_matches
                if depth == 0:
                    guess_map[guess] -= 1
            best_guess = None
            best_guess_c = None
            for guess in guess_map.keys():
                if best_guess is None or guess_map[guess] < best_guess_c:
                    best_guess = guess
                    best_guess_c = guess_map[guess]
            bgts_obj = {"g": best_guess, "c": best_guess_c}
            if bgts_obj["g"]:
                maps.insert_knowledge(origin_k_hash, bgts_obj["g"], bgts_obj["c"])
                return bgts_obj
        return False

    @staticmethod
    def get_suggestion_wip(k, guess_options, answer_options):
        maps = MapsDB()
        k_hash = Knowledge.dict_hash(k)  # get hashkey for suggestion map
        existing_suggestion = maps.get_suggestion2(k_hash)
        
        if existing_suggestion:
            return existing_suggestion

        suggestion_obj = Solver.guess_to_solve(k, guess_options, answer_options, 0)
        suggested_guess = suggestion_obj["g"]
        maps.insert_suggestion2(k_hash, suggested_guess)
        return suggested_guess


    @staticmethod
    def get_suggestion(k, guesses, answers):
        # change to redirect to right suggestion solver
        sug_obj = Solver.get_suggestion_recursive(k, guesses, answers, depth)
        return sug_obj["g"]
        #return Solver.get_suggestion_wip(k, guesses, answers)
        #return Solver.get_suggestion_stable(k, guesses, answers)

    @staticmethod
    def get_suggestion_stable(k, guess_options, answer_options):
        maps = MapsDB()
        k_hash = Knowledge.dict_hash(k)  # get hashkey for suggestion map
        existing_suggestion_knowledge = maps.get_suggestion(k_hash)
        if existing_suggestion_knowledge:
            return existing_suggestion_knowledge

        matches = Knowledge.get_possible_matches(k, answer_options)

        if len(matches) < 3:
            suggested_guess = matches[0]
        else:
            match_map = Solver.create_match_map(matches, guess_options, k, False)

            if match_map is False:
                return Solver.get_suggestion_fast(k, guess_options, matches)
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
    def get_suggestion_fast(k, guess_options, answer_options):
        # get as much insight into the letters we don't know about that are in the remaining words
        # exclude words that

        matches = Knowledge.get_possible_matches(k, answer_options)
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

        match_map = Solver.create_match_map(matches, [focus_suggested_guess, suggested_guess], k, True)

        narrow_over_try = 1 / match_map[focus_suggested_guess] - 1 / match_map[suggested_guess] - 1 / total_matches
        if focus_suggested_guess and narrow_over_try > 0:
            suggested_guess = focus_suggested_guess

        return suggested_guess