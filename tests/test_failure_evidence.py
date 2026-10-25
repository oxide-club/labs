import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import test_make
ROOT = test_make.ROOT

class FailureEvidence(unittest.TestCase):
    package = test_make.MakeInterface.package
    make = test_make.MakeInterface.make
    def test_timeout_keeps_partial_output(self):
        spec = importlib.util.spec_from_file_location('dispatcher', ROOT / 'templates/make/lab.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / '00'
            with self.assertRaises(subprocess.TimeoutExpired):
                module.command([sys.executable, '-c', 'import time; print("before timeout", flush=True); time.sleep(5)'], timeout=.2, log=log)
            self.assertIn('before timeout', Path(str(log) + '-stdout.txt').read_text())
            self.assertEqual(Path(str(log) + '-status.txt').read_text(), 'timeout\n')

    def test_failed_run_keeps_declared_evidence(self):
        lab = self.package('018')
        path = lab / 'materials/lab.json'
        manifest = json.loads(path.read_text())
        cfg = manifest['variants']['reference']
        cfg['experiments']['default'] = [[sys.executable, '-c', 'from pathlib import Path; Path("build/trace.txt").write_text("partial"); raise SystemExit(1)']]
        cfg['evidence'] = ['build/trace.txt']
        path.write_text(json.dumps(manifest))
        self.assertNotEqual(self.make(lab, 'run').returncode, 0)
        evidence = list((lab / 'results').glob('*/trace.txt'))
        self.assertEqual(len(evidence), 1)
        self.assertEqual(evidence[0].read_text(), 'partial')
