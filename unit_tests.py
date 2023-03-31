import unittest

from wordle_common import Knowledge, CONST


# noinspection SpellCheckingInspection,PyAttributeOutsideInit
class UnitTestCase(unittest.TestCase):
    def setUp(self):
        self.secret = "prick"
        self.suggestion = "salet"
        self.prev_guesses = ()
        self.answers = ()
        self.guesses = ()
        self.maps = {}
        self.kmap = {}

    def test_default_list_len(self):
        default_list = CONST.EMPTY_KNOWLEDGE
        self.assertEqual(26 * 8, len(default_list), 'wrong best word')

    def test_in_word_from_default(self):
        knowledge = CONST.EMPTY_KNOWLEDGE
        knowledge2 = Knowledge.update_knowledge(knowledge, "abbbb", "cccca")
        self.assertEqual(2, knowledge2[0], 'Failed default in_word')

    def test_not_in_word_from_default(self):
        knowledge = CONST.EMPTY_KNOWLEDGE
        knowledge2 = Knowledge.update_knowledge(knowledge, "abbbb", "cccca")
        self.assertEqual(1, knowledge2[2], 'Failed default not_in_word')

    def test_list_to_int_a(self):
        iniw = [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        inp0 = [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        inp1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        inp2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        inp3 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        inp4 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        inm2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        inm3 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        k_list = iniw + inp0 + inp1 + inp2 + inp3 + inp4 + inm2 + inm3
        kint = Knowledge.k_list_to_int(tuple(k_list))
        k_list_return = Knowledge.k_int_to_list(kint)
        self.assertEqual(2, k_list_return[0], 'wrong "a" in word')
        self.assertEqual(0, k_list_return[1], 'wrong "b" in word')
        self.assertEqual(2, k_list_return[26], 'wrong "a" in pos 0')
        self.assertEqual(0, k_list_return[52], 'wrong a in pos 2')
        self.assertEqual(1, k_list_return[155], 'wrong not "z" in pos 4')

    def test_knowledge_conserved_on_transfer_not_in_word(self):
        knowledge = CONST.EMPTY_KNOWLEDGE
        knowledge2 = Knowledge.update_knowledge(knowledge, "abbbb", "cccca")
        khash = Knowledge.k_list_to_int(knowledge2)
        knowledge3 = Knowledge.k_int_to_list(khash)
        self.assertEqual(knowledge2[0:26], knowledge3[0:26], 'in/not in word')
        self.assertEqual(knowledge2[26:52], knowledge3[26:52], 'in/not in multi')
        self.assertEqual(knowledge2[52:78], knowledge3[52:78], 'in/not in pos 0')

    def test_knowledge_conserved_default_to_list(self):
        knowledge = CONST.EMPTY_KNOWLEDGE
        iniw = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.assertEqual(knowledge[:26], iniw[:26], 'not_in_word default to list')
        self.assertEqual(knowledge[26:52], iniw[:26], 'not_in_multi default to list')

    def test_knowledge_conserved_to_list(self):
        knowledge = CONST.EMPTY_KNOWLEDGE
        knowledge2 = Knowledge.update_knowledge(knowledge, "abbbb", "cccca")
        iniw = (2, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.assertEqual(iniw[:26], knowledge2[:26], 'not_in_word dict to list')

    def test_knowledge_conserved_list_from_int(self):
        knowledge = CONST.EMPTY_KNOWLEDGE
        knowledge2 = Knowledge.update_knowledge(knowledge, "abbbb", "cccca")

        khash = Knowledge.k_list_to_int(knowledge2)
        k_list = Knowledge.k_int_to_list(khash)
        iniw = (2, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.assertEqual(k_list[:26], iniw[:26][:len(k_list[:26])], 'not_in_word knowledge failed')


if __name__ == "__main__":
    unittest.main()
