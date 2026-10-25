"""SPDX-License-Identifier: MIT — checks públicos do contrato de attention."""
import copy
import importlib.util
import json
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True


def load_module(path):
    spec = importlib.util.spec_from_file_location('attention_candidate', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def close_tree(test, actual, expected):
    if isinstance(expected, dict):
        test.assertIsInstance(actual, dict)
        test.assertEqual(set(actual), set(expected))
        for key in expected:
            close_tree(test, actual[key], expected[key])
    elif isinstance(expected, list):
        test.assertIsInstance(actual, list)
        test.assertEqual(len(actual), len(expected))
        for a, b in zip(actual, expected):
            close_tree(test, a, b)
    else:
        test.assertIn(type(actual), (int, float))
        test.assertTrue(math.isfinite(actual))
        test.assertTrue(math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-12),
                        f'{actual!r} != {expected!r}')


class AttentionChecks(unittest.TestCase):
    candidate = ROOT / 'materials/attention.py'

    @classmethod
    def setUpClass(cls):
        cls.api = load_module(cls.candidate)
        cls.cases = json.loads((ROOT / 'materials/fixtures/cases.json').read_text())['cases']

    def test_known_intermediates(self):
        """Detecta transposição, escala, causal mask e multiplicação final incorretas."""
        for case in self.cases:
            with self.subTest(case=case['name']):
                q, k, v = copy.deepcopy([case['q'], case['k'], case['v']])
                close_tree(self, self.api.scaled_scores(q, k), case['expected']['scores'])
                result = self.api.attention(q, k, v, causal=case['causal'])
                close_tree(self, result, case['expected'])
                self.assertEqual([q, k, v], [case['q'], case['k'], case['v']])
                for i, row in enumerate(result['probabilities']):
                    self.assertLessEqual(abs(sum(row) - 1.0), 1e-12)
                    self.assertTrue(all(0 <= x <= 1 for x in row))
                    if case['causal']:
                        self.assertTrue(all(x == 0.0 for x in row[i+1:]))

    def test_softmax_stability_and_mask(self):
        for row, expected in [
            ([1000, 1001], [0.2689414213699951, 0.7310585786300049]),
            ([-1000, -1001], [0.7310585786300049, 0.2689414213699951]),
            ([1e15, 1e15], [0.5, 0.5]),
            ([-1e15, 1e15], [0.0, 1.0]),
            ([float('-inf'), 2], [0.0, 1.0]),
            ([0], [1.0]),
            ([0] * 256, [1/256] * 256),
        ]:
            with self.subTest(row=row[:3]):
                original = row[:]
                output = self.api.softmax(row)
                close_tree(self, output, expected)
                self.assertEqual(row, original)
                self.assertLessEqual(abs(sum(output) - 1.0), 1e-12)
                for value, p in zip(row, output):
                    if value == -math.inf:
                        self.assertEqual(p, 0.0)

    def test_softmax_rejects_invalid_and_all_masked(self):
        for row in [[], [0]*257, [math.nan], [math.inf], [-math.inf],
                    [-math.inf, -math.inf], [1e15+1], [-1e15-1], [True],
                    ['0'], [1j], (0,), None, [10**1000]]:
            with self.subTest(row=repr(row)[:60]):
                original = repr(row)
                with self.assertRaises(ValueError):
                    self.api.softmax(row)
                self.assertEqual(repr(row), original)

    def test_rejects_matrix_types_shapes_and_domain(self):
        bad = [[], [[]], [[0], [0, 1]], None, ([],), [(0,)], [0], [[True]], [['1']],
               [[1j]], [[math.nan]], [[math.inf]], [[-math.inf]],
               [[1_000_001]], [[-1_000_001]], [[10**1000]],
               [[0]] * 257, [[0] * 65]]
        for invalid in bad:
            for position in range(3):
                with self.subTest(invalid=repr(invalid)[:50], position=position):
                    args = [[[0]], [[0]], [[1]]]
                    args[position] = invalid
                    # repr permite comparar a preservação de NaN sem NaN == NaN.
                    original = repr(args)
                    with self.assertRaises(ValueError):
                        self.api.attention(*args)
                    self.assertEqual(repr(args), original)
                    if position < 2:
                        with self.assertRaises(ValueError):
                            self.api.scaled_scores(*args[:2])
                        self.assertEqual(repr(args), original)
        for args in [([[0]], [[0], [1]], [[0]]),
                     ([[0, 1]], [[0]], [[0]]),
                     ([[0]], [[0]], [[0], [1]])]:
            with self.assertRaises(ValueError):
                self.api.attention(*args)
        for q, k in [([[0]], [[0], [1]]), ([[0, 1]], [[0]])]:
            with self.assertRaises(ValueError):
                self.api.scaled_scores(q, k)
        for flag in [0, 1, None, 'true']:
            with self.assertRaises(ValueError):
                self.api.attention([[0]], [[0]], [[1]], causal=flag)

    def test_inclusive_dimension_and_value_boundaries(self):
        close_tree(self, self.api.scaled_scores([[-1e6]*64], [[1e6]*64]), [[-8e12]])
        for causal in (False, True):
            # Score = 64 * 1e12 / sqrt(64) = 8e12; uma posição tem peso 1.
            result = self.api.attention([[1e6]*64], [[1e6]*64], [[-1e6]*64], causal=causal)
            close_tree(self, result, {'scores': [[8e12]], 'probabilities': [[1.0]],
                                    'output': [[-1e6]*64]})
            # N máximo com d_k=d_v=1: distribuição uniforme no prefixo permitido.
            result = self.api.attention([[0] for _ in range(256)],
                                        [[0] for _ in range(256)],
                                        [[7] for _ in range(256)], causal=causal)
            close_tree(self, result['scores'], [[0.0]*256 for _ in range(256)])
            close_tree(self, result['output'], [[7.0] for _ in range(256)])
            self.assertEqual(len(result['probabilities']), 256)
            for i, row in enumerate(result['probabilities']):
                count = i+1 if causal else 256
                close_tree(self, row, [1/count]*count + [0.0]*(256-count))
                self.assertTrue(all(p == 0.0 for p in row[count:]))

    def test_causal_dominant_future(self):
        # Scores futuros grandes anulam probabilidades permitidas se a máscara vier depois.
        result = self.api.attention([[1e6]*64,[1e6]*64], [[0]*64,[1e6]*64], [[1,1],[2,2]], causal=True)
        self.assertEqual(result['probabilities'], [[1.0,0.0],[0.0,1.0]])
        self.assertEqual(result['output'], [[1.0,1.0],[2.0,2.0]])

    def test_causal_cannot_read_future(self):
        q = [[1, -2], [3, 1], [0, 2], [-1, 1]]
        k = [[0, 2], [1, -1], [3, 0], [-2, 4]]
        v = [[1, 5], [2, 0], [-3, 1], [4, -2]]
        baseline = self.api.attention(q, k, v, causal=True)
        # Alterar TODAS as entradas posteriores não pode afetar o prefixo.
        for end in range(1, 4):
            qq, kk, vv = copy.deepcopy([q, k, v])
            for j in range(end, 4):
                qq[j], kk[j], vv[j] = [100, -50], [-100, 100], [900, -800]
            changed = self.api.attention(qq, kk, vv, causal=True)
            close_tree(self, changed['output'][:end], baseline['output'][:end])
            close_tree(self, changed['probabilities'][:end], baseline['probabilities'][:end])
            prefix = self.api.attention(q[:end], k[:end], v[:end], causal=True)
            close_tree(self, prefix['output'], baseline['output'][:end])

    def test_returns_independent_storage(self):
        q, k, v = [[0], [0]], [[0], [0]], [[3], [7]]
        expected = {'scores': [[0.0, 0.0], [0.0, 0.0]],
                    'probabilities': [[0.5, 0.5], [0.5, 0.5]], 'output': [[5.0], [5.0]]}
        first = self.api.attention(q, k, v)
        second = self.api.attention(q, k, v)
        first['output'][0][0] = 123
        first['scores'][0][0] = 123
        first['probabilities'][0][0] = 123
        close_tree(self, second, expected)
        self.assertEqual([q, k, v], [[[0], [0]], [[0], [0]], [[3], [7]]])
        close_tree(self, first['output'][1], [5.0])
        close_tree(self, first['scores'][1], [0.0, 0.0])
        close_tree(self, first['probabilities'][1], [0.5, 0.5])


if __name__ == '__main__':
    if len(sys.argv) > 1:
        AttentionChecks.candidate = Path(sys.argv.pop(1)).resolve()
    unittest.main(verbosity=2)
