# SPDX-License-Identifier: MIT
from pathlib import Path
import tempfile
import unittest
from support import compile_c, run_owned


class QueueStartupHarnessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory(prefix="queue-wrapper-test-")
        cls.addClassCleanup(cls.directory.cleanup)
        cls.executable = Path(cls.directory.name) / "queue-startup"
        compile_c(cls.executable, ["checks/queue-startup.c", "materials/starter/queue.c"],
                  extra=[f"-Wl,--wrap={name}" for name in
                         ("pthread_mutex_init", "pthread_cond_init",
                          "pthread_mutex_destroy", "pthread_cond_destroy")])

    def test_tracks_two_orders_and_cleans_successful_initializations(self):
        code, out, err, timed_out = run_owned([self.executable, "selftest"])
        self.assertEqual((code, out, err, timed_out), (0, "PASS\n", "", False))

    def test_rejects_destroy_after_failed_initialization(self):
        code, out, err, timed_out = run_owned([self.executable, "selftest-failed-destroy"])
        self.assertEqual(code, 1)
        self.assertFalse(timed_out)
        self.assertIn("record->initialized && !record->destroyed", err)

    def test_rejects_missing_destroy(self):
        code, out, err, timed_out = run_owned([self.executable, "selftest-leak"])
        self.assertEqual(code, 1)
        self.assertFalse(timed_out)
        self.assertIn("records[i].destroyed == records[i].initialized", err)


if __name__ == "__main__":
    unittest.main()
