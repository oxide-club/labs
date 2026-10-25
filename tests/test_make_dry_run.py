from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]

class DryRun(unittest.TestCase):
    def test_make_dry_run_does_not_clean(self):
        with tempfile.TemporaryDirectory() as temp:
            lab=Path(temp)/'lab'
            shutil.copytree(ROOT/'007-compilation-lab',lab,ignore=shutil.ignore_patterns('build','__pycache__'))
            (lab/'materials/build').mkdir()
            binary=lab/'materials/build/program';binary.write_text('keep')
            result=subprocess.run(['make','-n','clean'],cwd=lab,capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertTrue(binary.exists(),'make -n must not run clean')
