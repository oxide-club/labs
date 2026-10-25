"""SPDX-License-Identifier: MIT — verifica o suporte, sem resolver attention."""
import csv
import io
from pathlib import Path
import subprocess
import sys
import unittest
sys.dont_write_bytecode = True
from check import close_tree

ROOT = Path(__file__).resolve().parents[1]


class SupportChecks(unittest.TestCase):
    def run_experiment(self, *args):
        return subprocess.run([sys.executable, str(ROOT / 'experiments/memory.py'), *args],
                              capture_output=True, text=True, timeout=60)

    def test_theoretical_counts_are_not_measurements(self):
        run = self.run_experiment('--theory', '--sizes', '8,16,32')
        self.assertEqual(run.returncode, 0, run.stderr)
        rows = list(csv.DictReader(io.StringIO(run.stdout)))
        self.assertEqual([r['scores_elements'] for r in rows], ['64', '256', '1024'])
        self.assertEqual([r['scores_model_bytes'] for r in rows], ['512', '2048', '8192'])
        self.assertEqual([r['scores_and_probabilities_model_bytes'] for r in rows],
                         ['1024', '4096', '16384'])
        self.assertTrue(all(r['kind'] == 'theory' for r in rows))
        self.assertNotIn('traced_peak_bytes', rows[0])

    def test_experiment_rejects_invalid_sizes_and_repetitions(self):
        for args in [('--sizes', '0'), ('--sizes', '257'), ('--sizes', 'x'),
                     ('--sizes', ''), ('--repeats', '0'), ('--repeats', '21')]:
            with self.subTest(args=args):
                run = self.run_experiment('--theory', *args)
                self.assertEqual(run.returncode, 2)
                self.assertEqual(run.stdout, '')

    def test_measurement_rejects_incomplete_starter_before_emitting_csv(self):
        # Suporte de preparação: este caso vale para o starter distribuído.
        # Use um stub local para continuar válido após o participante implementar.
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            candidate = Path(folder) / 'incomplete.py'
            candidate.write_text('def attention(*args, **kwargs):\n    raise NotImplementedError("incomplete")\n')
            run = self.run_experiment('--measure', '--candidate', str(candidate), '--sizes', '8')
        self.assertEqual(run.returncode, 1)
        self.assertEqual(run.stdout, '')
        self.assertIn('checks', run.stderr)

    def test_comparison_rejects_wrong_shape_nonfinite_and_values(self):
        for actual, expected in [([1], [1, 2]), ([[1, 2]], [[1], [2]]),
                                 ([float('nan')], [1]), ([float('inf')], [1]),
                                 ([0.5], [0.7310585786300049]),
                                 ({'output': []}, {'output': [], 'scores': []})]:
            with self.subTest(actual=actual):
                with self.assertRaises(AssertionError):
                    close_tree(self, actual, expected)

    def test_measurement_helper_keeps_result_live_and_cleans_trace(self):
        import importlib.util
        import tracemalloc
        spec = importlib.util.spec_from_file_location('memory_support', ROOT/'experiments/memory.py')
        support = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(support)
        elapsed, retained, peak = support.measure_call(lambda: bytearray(8192))
        self.assertGreaterEqual(elapsed, 0)
        self.assertGreaterEqual(retained, 8192)
        self.assertGreaterEqual(peak, retained)
        self.assertFalse(tracemalloc.is_tracing())
        def fail():
            raise ValueError('falha controlada')
        with self.assertRaises(ValueError):
            support.measure_call(fail)
        self.assertFalse(tracemalloc.is_tracing())


if __name__ == '__main__':
    unittest.main(verbosity=2)
