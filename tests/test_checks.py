import subprocess
import tempfile
import unittest
from pathlib import Path
ROOT = Path(__file__).parents[1]
class ChecksTests(unittest.TestCase):
    def test_accepts_model_and_rejects_constant(self):
        with tempfile.TemporaryDirectory() as d:
            program = Path(d)/'cache'
            program.write_text('#!/usr/bin/env python3\nimport runpy,sys\nm=runpy.run_path('+repr(str(ROOT/'scripts/verify-cache-model.py'))+')\nr=m["simulate"]([int(line.split()[1],16) for line in sys.stdin])\nprint("hits=%d misses=%d evictions=%d" % r)\n')
            program.chmod(0o755)
            check = ROOT/'005-cache-e-localidade/checks/check.py'
            self.assertEqual(subprocess.run(['python3',str(check),str(program)],capture_output=True).returncode,0)
            program.write_text('#!/usr/bin/env python3\nprint("hits=0 misses=0 evictions=0")\n')
            self.assertEqual(subprocess.run(['python3',str(check),str(program)],capture_output=True).returncode,1)
