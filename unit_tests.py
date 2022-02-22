import string

from wordle_common import Knowledge
from solver import Solver
import unittest


# noinspection SpellCheckingInspection
class UnitTestCase(unittest.TestCase):
    def setUp(self):
        self.secret = "prick"
        self.knowledge = Knowledge.default_knowledge()
        self.suggestion = "salet"

    def test_guesses_to_solve(self):
        knowledge = Knowledge.default_knowledge()
        guesses = ["salet", "prick"]
        answers = ["salet", "prick"]
        gtoc = Solver.get_suggestion_exp(knowledge, guesses, answers, 0, True)
        self.assertEqual("salet", gtoc['g'], 'wrong best word')

    def test_guesses_to_solve_count(self):
        knowledge = Knowledge.default_knowledge()
        guesses = ["salet", "prick"]
        answers = ["prick"]
        knowledge = Knowledge.update_knowledge(knowledge, "prick", "salet")
        gtoc = Solver.get_suggestion_exp(knowledge, guesses, answers, 0, True)
        self.assertEqual(1, gtoc['c'], 'wrong confidence')

    def test_guesses_to_solve_two_results(self):
        knowledge = Knowledge.default_knowledge()
        guesses = ["salet", "prick", "brick"]
        answers = ["prick", "brick"]
        knowledge = Knowledge.update_knowledge(knowledge, "prick", "salet")
        gtoc = Solver.get_suggestion_exp(knowledge, guesses, answers, 0, True)
        self.assertEqual(1.5, gtoc['c'], 'wrong best guess confidence')

    def test_guesses_to_solve_known_answer(self):
        knowledge = Knowledge.default_knowledge()
        guesses = ["salet", "prick"]
        answers = ["prick", "salet"]
        knowledge = Knowledge.update_knowledge(knowledge, "prick", "salet")
        gtoc = Solver.get_suggestion_exp(knowledge, guesses, answers, 0, True)
        self.assertEqual(1, gtoc['c'], 'wrong best confidence')

    def test_guesses_to_solve_prefect_guess_results(self):
        knowledge = Knowledge.default_knowledge()
        guesses = ["prick", "brick", "trick", "pbfti"]
        answers = ["prick", "brick", "trick", "pbfti"]
        gtoc = Solver.get_suggestion_exp(knowledge, guesses, answers, 0, True)
        self.assertEqual(2 - 1 / len(answers), gtoc['c'], 'wrong best confidence')

    def test_guesses_to_solve_good_guess(self):
        knowledge = Knowledge.default_knowledge()
        guesses = ["prick", "brick", "frick", "pbfti", "trick"]
        answers = ["prick", "brick", "frick", "trick"]
        gtoc = Solver.get_suggestion_exp(knowledge, guesses, answers, 0, True)
        self.assertEqual(2, gtoc['c'], 'wrong best confidence')

    def test_guesses_to_solve_average_others(self):
        answers = ["prick", "brick", "frick", "trick"]
        gts_good = {'g': "good1", 'c': 2}
        gts_perfect = {'g': "perfe", "c": 2 - 1 / len(answers)}
        gts_two = {'g': "twooo", "c": 1.5}
        gts_one = {'g': "oneee", "c": 1}
        gts_answer = {'g': "answe", "c": 1}  # This should be checked!
        bgts_ave = (gts_good["c"] + gts_perfect["c"] + gts_two["c"] + gts_one["c"] - gts_answer["c"]) / len(answers)
        self.assertEqual(1.3125, bgts_ave, 'wrong best confidence')
    def test_guesses_to_solve_average_others(self):
        alpha = string.ascii_lowercase
        alpha_len = len(alpha)
        Knowledge.WORD_LENGTH
        INCORRECT = -1
        CORRECT = 1
        UNKNOWN = 0
        k = ""
        # word knowledge
        for n in range(alpha_len):
            k += "0"
        # place knowledge
        for n in range(Knowledge.WORD_LENGTH):
            k += "0"
        print(k)



        bgts_ave = (gts_good["c"] + gts_perfect["c"] + gts_two["c"] + gts_one["c"] - gts_answer["c"]) / len(answers)
        self.assertEqual(1.3125, bgts_ave, 'wrong best confidence')
    """ TODO: test solutions that will deal with averaging a number of best guesses """


if __name__ == "__main__":
    unittest.main()