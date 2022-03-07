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
        self.assertEqual(["a"], knowledge2[CONST.IN_WORD], 'Failed default in_word')

    def test_not_in_word_from_default(self):
        knowledge = Knowledge.default_knowledge()
        knowledge2 = Knowledge.update_knowledge(knowledge, "abbbb", "cccca")
        self.assertEqual(["c"], knowledge2[CONST.NOT_IN_WORD], 'Failed default not_in_word')

    def test_kdict_to_list(self):
        knowledge = Knowledge.default_knowledge()
        knowledge2 = Knowledge.update_knowledge(knowledge, "abbbb", "cccca")
        self.assertEqual(["c"], knowledge2[CONST.NOT_IN_WORD], 'Failed default not_in_word')

    def test_join_defaults(self):
        k1 = Knowledge.default_knowledge()
        k2 = Knowledge.default_knowledge()
        k3 = Knowledge.join_knowledge(k1, k2)
        self.assertEqual(k1[CONST.IN_WORD], k3[CONST.IN_WORD], 'in-word same')
        self.assertEqual(k1[CONST.NOT_IN_WORD], k3[CONST.NOT_IN_WORD], 'not-in-word same')
        self.assertEqual(k1[CONST.IN_MULTI], k3[CONST.IN_MULTI], 'in_multi same')
        self.assertEqual(k1[4][CONST.NOT_IN_POSITION], k3[4][CONST.NOT_IN_POSITION], 'not in position same')

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

    def test_join_non_default_w_default_same(self):
        iniw = [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        inim = [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        inp0 = [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 2, 0, 0, 0, 1, 0, 1, 2, 0, 0]
        inp1 = [0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0]
        inp2 = [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0]
        inp3 = [0, 2, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0]
        inp4 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        k_list = iniw + inim + inp0 + inp1 + inp2 + inp3 + inp4
        kint = Knowledge.k_list_to_int(k_list)
        k1 = Knowledge.k_int_to_dict(kint)
        k2 = Knowledge.default_knowledge()
        k3 = Knowledge.standardize_knowledge(Knowledge.join_knowledge(k1, k2))
        self.assertEqual(k1[CONST.IN_WORD], k3[CONST.IN_WORD], 'in-word same')
        self.assertEqual(k1[CONST.NOT_IN_WORD], k3[CONST.NOT_IN_WORD], 'not-in-word same')
        self.assertEqual(k1[CONST.IN_MULTI], k3[CONST.IN_MULTI], 'in_multi same')
        self.assertEqual(k1[CONST.NOT_IN_MULTI], k3[CONST.NOT_IN_MULTI], 'not_in_multi same')
        self.assertEqual(k1[4][CONST.IN_POSITION], k3[4][CONST.IN_POSITION], 'in position same')
        self.assertEqual(k1[0][CONST.NOT_IN_POSITION], k3[0][CONST.NOT_IN_POSITION], 'not in position 0 same')
        self.assertEqual(k1[1][CONST.NOT_IN_POSITION], k3[1][CONST.NOT_IN_POSITION], 'not in position 1 same')
        self.assertEqual(k1[2][CONST.NOT_IN_POSITION], k3[2][CONST.NOT_IN_POSITION], 'not in position 2 same')
        self.assertEqual(k1[3][CONST.NOT_IN_POSITION], k3[3][CONST.NOT_IN_POSITION], 'not in position 3 same')
        self.assertEqual(k1[4][CONST.NOT_IN_POSITION], k3[4][CONST.NOT_IN_POSITION], 'not in position 4 same')

    def test_k_dict_list(self):
        k_dict = Knowledge.default_knowledge()
        k_dict[CONST.IN_WORD] = ["a"]
        k_dict[CONST.NOT_IN_WORD] = ["c"]
        k_dict[0][CONST.IN_POSITION] = "a"
        k_dict[0][CONST.NOT_IN_POSITION] = ["b"]
        k_dict[4][CONST.NOT_IN_POSITION] = ["z"]

        k_list_return = Knowledge.k_dict_to_list(k_dict)
        self.assertEqual(2, k_list_return[0], '"a" in word')
        self.assertEqual(1, k_list_return[2], '"c" in word')
        self.assertEqual(1, k_list_return[53], '"b" not in pos 0')
        self.assertEqual(2, k_list_return[52], '"a" in pos 0')
        self.assertEqual(0, k_list_return[78], '"a" unknown in pos 1')
        self.assertEqual(1, k_list_return[181], '"z" not in pos 4')

    def test_k_dict_list(self):
        k_dict = Knowledge.default_knowledge()
        k = Knowledge.update_knowledge(k_dict, "paddy", "salet")
        k = Knowledge.update_knowledge(k, "paddy", "daddy")
        GUESSES_FILE = "words-guesses.txt"
        self.guesses = tuple(Tools.load_words(GUESSES_FILE))
        self.answers = self.guesses[:CONST.ANSWERS_LEN]
        m = Knowledge.get_possible_matches(k, self.answers)
        print(k)
        self.assertTrue("daddy" not in m, 'prev guesses excluded from answers')

    def test_k_list_dict(self):
        iniw = [2, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0]
        inim = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 0]
        inp0 = [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        inp1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        inp2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        inp3 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        inp4 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        k_list = iniw + inim + inp0 + inp1 + inp2 + inp3 + inp4
        k_dict = Knowledge.k_list_to_dict(k_list)
        self.assertTrue("a" in k_dict[CONST.IN_WORD], '"a" in word')
        self.assertTrue("c" in k_dict[CONST.NOT_IN_WORD], '"c" not in word')
        self.assertTrue("a" == k_dict[0][CONST.IN_POSITION], '"a" in pos 1')
        self.assertTrue("y" in k_dict[CONST.IN_MULTI], '"y" in multi')
        self.assertTrue("x" in k_dict[CONST.NOT_IN_MULTI], '"x" in not in multi')
        self.assertTrue("b" != k_dict[1][CONST.IN_POSITION], '"b" not in in position 2')
        self.assertTrue("z" in k_dict[4][CONST.NOT_IN_POSITION], '"z" not in pos4')

    def test_knowledge_conserved_on_transfer_not_in_word(self):
        knowledge = Knowledge.default_knowledge()
        knowledge2 = Knowledge.update_knowledge(knowledge, "abbbb", "cccca")
        khash = Knowledge.k_dict_to_int(knowledge2)
        knowledge3 = Knowledge.k_int_to_dict(khash)
        self.assertEqual(knowledge2[CONST.NOT_IN_WORD], knowledge3[CONST.NOT_IN_WORD], 'not_in_word knowledge failed')

    def test_broken_repeat_map(self):
        GUESSES_FILE = "words-guesses.txt"
        self.guesses = tuple(Tools.load_words(GUESSES_FILE))
        self.answers = self.guesses[:CONST.ANSWERS_LEN]
        kint = 152354696091732784678579455441231125755110878486640801808020634401034184421252340234736
        k = Knowledge.k_int_to_dict(kint)
        matches = Knowledge.get_possible_matches(k, self.answers)
        print("self answers: ", str(len(self.answers)))
        k2 = Knowledge.update_knowledge(k, "paddy", "daddy")
        m2 = Knowledge.get_possible_matches(k2, matches)
        self.assertEqual(matches, ('daddy', 'paddy'), 'not_in_word knowledge failed')
        self.assertEqual(m2, ('paddy',), 'paddy final option')

    def test_default_knowledge_(self):
        knowledge = Knowledge.default_knowledge()
        self.assertEqual([], knowledge[CONST.IN_WORD], 'in_word empty')
        self.assertEqual([], knowledge[CONST.NOT_IN_WORD], 'not_in_word default empty')
        self.assertEqual(False, knowledge[0][CONST.IN_POSITION], 'in_position empty')
        self.assertEqual([], knowledge[1][CONST.NOT_IN_POSITION], 'not_in_position empty')

    def test_knowledge_conserved_default_to_list(self):
        knowledge = Knowledge.default_knowledge()
        k_list = Knowledge.k_dict_to_list(knowledge)
        iniw = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.assertEqual(k_list[:26], iniw[:26], 'not_in_word default to list')
        self.assertEqual(k_list[26:52], iniw[:26], 'not_in_multi default to list')

    def test_knowledge_conserved_to_list(self):
        knowledge = Knowledge.default_knowledge()
        knowledge2 = Knowledge.update_knowledge(knowledge, "abbbb", "cccca")
        k_list = Knowledge.k_dict_to_list(knowledge2)
        iniw = [2, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.assertEqual(iniw[:26], k_list[:26], 'not_in_word dict to list')

    def test_knowledge_conserved_list_from_int(self):
        knowledge = Knowledge.default_knowledge()
        knowledge2 = Knowledge.update_knowledge(knowledge, "abbbb", "cccca")

        khash = Knowledge.k_dict_to_int(knowledge2)
        k_list = Knowledge.k_int_to_list(khash)
        iniw = [2, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.assertEqual(k_list[:26], iniw[:26][:len(k_list[:26])], 'not_in_word knowledge failed')

    def test_knowledge_in_position_last(self):
        knowledge = Knowledge.default_knowledge()
        knowledge2 = Knowledge.update_knowledge(knowledge, "abbbb", "cccca")
        self.assertEqual(False, knowledge2[4][CONST.IN_POSITION], 'in_position should be false')

    def test_in_matches(self):
        GUESSES_FILE = "words-guesses.txt"
        self.guesses = tuple(Tools.load_words(GUESSES_FILE))
        self.answers = self.guesses[:CONST.ANSWERS_LEN]
        k = {'IW': ['e', 'l', 't'], 'NIW': ['a', 'i', 's'], 'IM': [], 'NIM': ['t'], 0: {'IP': False, 'NIP': ['s', 't']}, 1: {'IP': False, 'NIP': ['a', 'i']}, 2: {'IP': False, 'NIP': ['l', 't']}, 3: {'IP': False, 'NIP': ['e', 'l']}, 4: {'IP': False, 'NIP': ['e', 't']}}
        m = Knowledge.get_possible_matches(k, self.answers)
        self.assertEqual(m, ('lefty',), 'matches should be equal')

    def test_knowledge_conserved_on_transfer_in_position_last(self):
        knowledge = Knowledge.default_knowledge()
        knowledge2 = Knowledge.update_knowledge(knowledge, "abbbb", "cccca")
        khash = Knowledge.k_dict_to_int(knowledge2)
        knowledge3 = Knowledge.k_int_to_dict(khash)
        self.assertEqual(knowledge2[4][CONST.NOT_IN_POSITION], knowledge3[4][CONST.NOT_IN_POSITION], 'wrong in-position info')

    def test_db_khash(self):
        GUESSES_FILE = "words-guesses.txt"
        self.guesses = tuple(Tools.load_words(GUESSES_FILE))
        self.answers = self.answers[CONST.ANSWERS_LEN:]
        self.maps = MapsDB()
        self.kmap = self.maps.get_all_kmap()
        k = Knowledge.default_knowledge()
        k = Knowledge.update_knowledge(k, "abase", "salet")
        k_hash = Knowledge.k_dict_to_int(k)
        self.assertTrue(type(k_hash) is int, 'wrong best confidence')
        if k_hash in self.kmap:
            kmap = self.kmap[k_hash]
            self.assertTrue(type(kmap[CONST.M]) is int, 'wrong best confidence')
            self.assertTrue(type(kmap[CONST.AGTS]) is float, 'wrong best confidence')
            self.assertTrue(type(kmap[CONST.C]) is int, 'wrong best confidence')
            self.assertTrue(type(kmap[CONST.GUESS]) is str, 'wrong best confidence')


if __name__ == "__main__":
    unittest.main()
