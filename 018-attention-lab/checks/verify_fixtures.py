"""SPDX-License-Identifier: MIT — confere cinco casos fechados, sem importar o starter."""
from decimal import Decimal, localcontext
import json
from pathlib import Path
import sys
import unittest
sys.dont_write_bytecode = True
from check import close_tree


class FixtureChecks(unittest.TestCase):
    def test_closed_forms(self):
        cases = json.loads((Path(__file__).resolve().parents[1] /
                           'materials/fixtures/cases.json').read_text())['cases']
        self.assertEqual(len(cases), 5)
        with localcontext() as context:
            context.prec = 60
            one = Decimal(1)
            p = one / (one + (-one).exp())
            r = one / (one + Decimal(3).exp())
            # Apenas expressões escalares destes casos; não é um algoritmo geral.
            for case, causal in zip(cases[:2], (False, True)):
                self.assertEqual(case['q'], [[2, 0, 0, 0], [2, 4, 0, 0]])
                self.assertEqual(case['k'], [[1, 0, 0, 0], [0, 2, 0, 0]])
                self.assertEqual(case['v'], [[2, 4, 1], [-2, 0, 3]])
                self.assertIs(case['causal'], causal)
                first_p = [1, 0] if causal else [float(p), float(1-p)]
                first_o = [2, 4, 1] if causal else [float(4*p-2), float(4*p), float(3-2*p)]
                close_tree(self, case['expected'], {
                    'scores': [[1, 0], [1, 4]],
                    'probabilities': [first_p, [float(r), float(1-r)]],
                    'output': [first_o, [float(4*r-2), float(4*r), float(3-2*r)]]})
            uniform = cases[2]
            self.assertEqual(uniform['q'], [[0, 0]]*3)
            self.assertEqual(uniform['k'], [[3, -1], [-2, 5], [7, 4]])
            self.assertEqual(uniform['v'], [[3, -3], [0, 6], [-6, 0]])
            self.assertIs(uniform['causal'], False)
            close_tree(self, uniform['expected'], {
                'scores': [[0, 0, 0]]*3,
                'probabilities': [[float(one/3)]*3]*3, 'output': [[-1, 1]]*3})
            single = cases[3]
            self.assertEqual([single['q'], single['k'], single['v']], [[[-2]], [[3]], [[-7, 4]]])
            self.assertIs(single['causal'], True)
            close_tree(self, single['expected'], {'scores': [[-6]], 'probabilities': [[1]],
                                                  'output': [[-7, 4]]})
            irrational = cases[4]
            self.assertEqual(irrational['name'], 'irrational-scale')
            self.assertEqual(irrational['q'], [[1, 0], [0, 1]])
            self.assertEqual(irrational['k'], [[1, 0], [0, 2]])
            self.assertEqual(irrational['v'], [[1, 0], [0, 1]])
            self.assertIs(irrational['causal'], False)
            root_two = Decimal(2).sqrt()
            a = one / (one + (-one/root_two).exp())
            b = one / (one + root_two.exp())
            probabilities = [[float(a), float(one-a)], [float(b), float(one-b)]]
            close_tree(self, irrational['expected'], {
                'scores': [[float(one/root_two), 0], [0, float(root_two)]],
                'probabilities': probabilities, 'output': probabilities})

    def test_rejects_integer_square_root_vectors(self):
        cases = json.loads((Path(__file__).resolve().parents[1] /
                           'materials/fixtures/cases.json').read_text())['cases']
        case = next(case for case in cases if case['name'] == 'irrational-scale')
        # int(sqrt(2)) = 1: produtos diagonais 1 e 2 continuam sem escala.
        wrong_scores = [[1.0, 0.0], [0.0, 2.0]]
        wrong_probabilities = [[0.7310585786300049, 0.2689414213699951],
                               [0.11920292202211755, 0.8807970779778824]]
        # V é identidade: a saída incorreta coincide com os pesos incorretos.
        for field, wrong in [('scores', wrong_scores),
                             ('probabilities', wrong_probabilities),
                             ('output', wrong_probabilities)]:
            with self.subTest(field=field):
                with self.assertRaises(AssertionError):
                    close_tree(self, wrong, case['expected'][field])


if __name__ == '__main__':
    unittest.main(verbosity=2)
