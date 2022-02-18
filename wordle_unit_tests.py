import copy
import random
from wordle_common import KNOWLEDGE
from solver import Solver
import unittest

class UnitTestCase(unittest.TestCase):
    def setUp(self):
        self.secret = "prick"
        self.knowledge = Solver.default_knowledge()
        self.suggestion = "salet"
    def test_guesses_to_solve(self):
        knowledge = Solver.default_knowledge()
        guesses = ["salet", "prick"]
        answers = ["salet", "prick"]
        gtoc = Solver.guess_to_solve(knowledge, guesses, answers, 0)
        self.assertEqual(gtoc['g'], "salet", 'wrong best option')
    def test_guesses_to_solve_count(self):
        knowledge = Solver.default_knowledge()
        guesses = ["salet", "prick"]
        answers = ["prick"]
        knowledge = Solver.update_knowledge(knowledge, "prick", "salet")
        gtoc = Solver.guess_to_solve(knowledge, guesses, answers, 0)
        self.assertEqual(gtoc['c'], 1, 'wrong best option')
    def test_guesses_to_solve_two_results(self):
        knowledge = Solver.default_knowledge()
        guesses = ["salet", "prick", "brick"]
        answers = ["prick", "brick"]
        knowledge = Solver.update_knowledge(knowledge, "prick", "salet")
        gtoc = Solver.guess_to_solve(knowledge, guesses, answers, 0)
        self.assertEqual(gtoc['c'], 1.5, 'wrong best option')
    def test_guesses_to_solve_known_answer(self):
        knowledge = Solver.default_knowledge()
        guesses = ["salet", "prick"]
        answers = ["prick", "salet"]
        knowledge = Solver.update_knowledge(knowledge, "prick", "salet")
        gtoc = Solver.guess_to_solve(knowledge, guesses, answers, 0)
        self.assertEqual(gtoc['c'], 1, 'wrong best option')
    def test_guesses_to_solve_prefect_guess_results(self):
        knowledge = Solver.default_knowledge()
        guesses = ["prick", "brick", "trick", "pbfti"]
        answers = ["prick", "brick", "trick", "pbfti"]
        gtoc = Solver.guess_to_solve(knowledge, guesses, answers, 0)
        self.assertEqual(gtoc['c'], 2 - 1/len(answers), 'wrong best option')
    def test_guesses_to_solve_good_guess(self):
        knowledge = Solver.default_knowledge()
        guesses = ["prick", "brick", "frick", "pbfti", "trick"]
        answers = ["prick", "brick", "frick", "trick"]
        gtoc = Solver.guess_to_solve(knowledge, guesses, answers, 0)
        self.assertEqual(gtoc['c'], 2, 'wrong best option')
    def test_guesses_to_solve_average_others(self):
        guesses = ["prick", "brick", "frick", "trick", "pbfti"]
        answers = ["prick", "brick", "frick", "trick"]
        gts_good = {'g': "good1", 'c' : 2}
        gts_perfect = {'g': "perfe", "c" : 2 - 1/len(answers)}
        gts_two = {'g' : "twooo", "c" : 1.5} 
        gts_one = {'g' : "oneee", "c" : 1 }
        gts_answer = {'g' : "answe", "c" : 1} # This should be checked!
        bgts_ave = (gts_good["c"] + gts_perfect["c"] + gts_two["c"] + gts_one["c"] - gts_answer["c"])/len(answers)
        self.assertEqual(bgts_ave, 1.3125, 'wrong best option')
    """ TODO: test solutions that will deal with averaging a number of best guesses """

if __name__ == "__main__":
    unittest.main()