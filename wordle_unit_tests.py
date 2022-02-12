import copy
import random
from wordleTools import KNOWLEDGE, WordleTools
import unittest

class UnitTestCase(unittest.TestCase):
    def setUp(self):
        self.secret = "prick"
        self.knowledge = WordleTools.default_knowledge()
        self.suggestion = "salet"
    def test_guesses_to_solve(self):
        knowledge = WordleTools.default_knowledge()
        guesses = ["salet", "prick"]
        answers = ["salet", "prick"]
        gtoc = WordleTools.guess_to_solve(knowledge, guesses, answers, 0)
        self.assertEqual(gtoc['g'], "salet", 'wrong best option')
    def test_guesses_to_solve_count(self):
        knowledge = WordleTools.default_knowledge()
        guesses = ["salet", "prick"]
        answers = ["prick"]
        knowledge = WordleTools.update_knowledge(knowledge, "prick", "salet")
        gtoc = WordleTools.guess_to_solve(knowledge, guesses, answers, 0)
        self.assertEqual(gtoc['c'], 1, 'wrong best option')
    def test_guesses_to_solve_two_results(self):
        knowledge = WordleTools.default_knowledge()
        guesses = ["salet", "prick", "brick"]
        answers = ["prick", "brick"]
        knowledge = WordleTools.update_knowledge(knowledge, "prick", "salet")
        gtoc = WordleTools.guess_to_solve(knowledge, guesses, answers, 0)
        self.assertEqual(gtoc['c'], 1.5, 'wrong best option')
    def test_guesses_to_solve_known_answer(self):
        knowledge = WordleTools.default_knowledge()
        guesses = ["salet", "prick"]
        answers = ["prick", "salet"]
        knowledge = WordleTools.update_knowledge(knowledge, "prick", "salet")
        gtoc = WordleTools.guess_to_solve(knowledge, guesses, answers, 0)
        self.assertEqual(gtoc['c'], 1, 'wrong best option')
    def test_guesses_to_solve_prefect_guess_results(self):
        knowledge = WordleTools.default_knowledge()
        guesses = ["prick", "brick", "crick"]
        answers = ["prick", "brick", "crick"]
        # knowledge = WordleTools.update_knowledge(knowledge, "prick", "salet")
        gtoc = WordleTools.guess_to_solve(knowledge, guesses, answers, 0)
        self.assertEqual(gtoc['c'], 2 - 1/len(answers), 'wrong best option')
    def test_guesses_to_solve_good_guess(self):
        knowledge = WordleTools.default_knowledge()
        guesses = ["prick", "brick", "crick","trick","pbcti"]
        answers = ["prick", "brick", "crick","trick"]
        # knowledge = WordleTools.update_knowledge(knowledge, "prick", "salet")
        gtoc = WordleTools.guess_to_solve(knowledge, guesses, answers, 0)
        self.assertEqual(gtoc['c'], 2, 'wrong best option')
    def test_guesses_to_solve_average_others(self):
        guesses = ["prick", "brick", "crick","trick","pbcti"]
        answers = ["prick", "brick", "crick","trick"]
        gts_good = {'g': "prick", 'c' : 2}
        gts_perfect = {'g': "brick", "c" : 2 - 1/len(answers)}
        gts_two = {'g' : "crick", "c" : 1.5} 
        gts_one = {'g' : "trick", "c" : 1 }
        gts_answer = {'g' : "pbcti", "c" : 1} # This should be checked!
        bgts_ave = (gts_good["c"] + gts_perfect["c"] + gts_two["c"] + gts_one["c"] - gts_answer["c"])/len(answers)
        print("average" + str(bgts_ave))
        self.assertEqual(bgts_ave, 1.3125, 'wrong best option')
    """ TODO: test solutions that will deal with averaging a number of best guesses """

if __name__ == "__main__":
    unittest.main()