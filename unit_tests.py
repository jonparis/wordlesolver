from wordle_common import Knowledge, CONST, Tools
from solver import Solver
from solver_model import MapsDB
import unittest


# noinspection SpellCheckingInspection,PyAttributeOutsideInit
class UnitTestCase(unittest.TestCase):
    def setUp(self):
        self.secret = "prick"
        self.knowledge = Knowledge.default_knowledge()
        self.suggestion = "salet"
        self.prev_guesses = ()
        self.answers = ()
        self.guesses = ()
        self.maps = {}
        self.kmap = {}

    def test_default_list_len(self):
        default_list = Knowledge.empty_k_list()
        self.assertEqual(26*7, len(default_list), 'wrong best word')

    def test_in_word_from_default(self):
        knowledge = Knowledge.default_knowledge()
        knowledge2 = Knowledge.update_knowledge(knowledge, "abbbb", "cccca")
        self.assertEqual(2, knowledge2[0], 'Failed default in_word')

    def test_not_in_word_from_default(self):
        knowledge = Knowledge.default_knowledge()
        knowledge2 = Knowledge.update_knowledge(knowledge, "abbbb", "cccca")
        self.assertEqual(1, knowledge2[2], 'Failed default not_in_word')

    def test_list_to_int_a(self):
        iniw = [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        inim = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        inp0 = [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        inp1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        inp2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        inp3 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        inp4 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        k_list = iniw + inim + inp0 + inp1 + inp2 + inp3 + inp4
        kint = Knowledge.k_list_to_int(k_list)
        k_list_return = Knowledge.k_int_to_list(kint)
        self.assertEqual(2, k_list_return[0], 'wrong "a" in word')
        self.assertEqual(0, k_list_return[1], 'wrong "b" in word')
        self.assertEqual(2, k_list_return[52], 'wrong "a" in pos 0')
        self.assertEqual(0, k_list_return[78], 'wrong a in pos 2')
        self.assertEqual(1, k_list_return[181], 'wrong not "z" in pos 4')

    def test_knowledge_conserved_on_transfer_not_in_word(self):
        knowledge = Knowledge.default_knowledge()
        knowledge2 = Knowledge.update_knowledge(knowledge, "abbbb", "cccca")
        khash = Knowledge.k_list_to_int(knowledge2)
        knowledge3 = Knowledge.k_int_to_list(khash)
        self.assertEqual(knowledge2[0:26], knowledge3[0:26], 'in/not in word')
        self.assertEqual(knowledge2[26:52], knowledge3[26:52], 'in/not in multi')
        self.assertEqual(knowledge2[52:78], knowledge3[52:78], 'in/not in pos 0')

    def test_broken_repeat_map(self):
        GUESSES_FILE = "words-guesses.txt"
        WORDS = tuple(Tools.load_words(GUESSES_FILE))
        solver = Solver(WORDS, True)
        kint = 152354696091732784678579455441231125755110878486640801808020634401034184421252340234736
        k = Knowledge.k_int_to_list(kint)
        matches = solver.get_matches(k)
        print("self answers: ", str(len(solver.answers)))
        k2 = Knowledge.update_knowledge(k, "paddy", "daddy")
        m2 = solver.get_matches(k2)
        self.assertEqual(matches, ('daddy', 'paddy'), 'not_in_word knowledge failed')
        self.assertEqual(m2, ('paddy',), 'paddy final option')

    def test_knowledge_conserved_default_to_list(self):
        knowledge = Knowledge.default_knowledge()
        iniw = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.assertEqual(knowledge[:26], iniw[:26], 'not_in_word default to list')
        self.assertEqual(knowledge[26:52], iniw[:26], 'not_in_multi default to list')

    def test_knowledge_conserved_to_list(self):
        knowledge = Knowledge.default_knowledge()
        knowledge2 = Knowledge.update_knowledge(knowledge, "abbbb", "cccca")
        iniw = (2, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.assertEqual(iniw[:26], knowledge2[:26], 'not_in_word dict to list')

    def test_knowledge_conserved_list_from_int(self):
        knowledge = Knowledge.default_knowledge()
        knowledge2 = Knowledge.update_knowledge(knowledge, "abbbb", "cccca")

        khash = Knowledge.k_list_to_int(knowledge2)
        k_list = Knowledge.k_int_to_list(khash)
        iniw = (2, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.assertEqual(k_list[:26], iniw[:26][:len(k_list[:26])], 'not_in_word knowledge failed')

    def test_db_khash(self):
        GUESSES_FILE = "words-guesses.txt"
        self.guesses = tuple(Tools.load_words(GUESSES_FILE))
        self.answers = self.answers[CONST.ANSWERS_LEN:]
        self.maps = MapsDB()
        self.kmap = self.maps.get_all_kmap()
        k = Knowledge.default_knowledge()
        k = Knowledge.update_knowledge(k, "abase", "salet")
        k_hash = Knowledge.k_list_to_int(k)
        self.assertTrue(type(k_hash) is int, 'wrong best confidence')
        if k_hash in self.kmap:
            kmap = self.kmap[k_hash]
            self.assertTrue(type(kmap[CONST.M]) is int, 'wrong best confidence')
            self.assertTrue(type(kmap[CONST.AGTS]) is float, 'wrong best confidence')
            self.assertTrue(type(kmap[CONST.C]) is int, 'wrong best confidence')
            self.assertTrue(type(kmap[CONST.GUESS]) is str, 'wrong best confidence')


if __name__ == "__main__":
    unittest.main()
