"""The allocation probe must actually call malloc at optimization level O2."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]

class IsolationBuild(unittest.TestCase):
    @unittest.skipUnless(shutil.which('clang') and shutil.which('nm'), 'Clang and nm required')
    def test_optimized_probe_keeps_allocation_call(self):
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run(['make','-C',str(ROOT/'016-isolation-lab/materials'),
                                     'CC=clang','CFLAGS=-std=c11 -Wall -Wextra -Werror -pedantic -O2',
                                     'BUILD='+temp,temp+'/probe'],
                                    capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            symbols = subprocess.check_output(['nm','-D',temp+'/probe'],text=True)
            # Only inspect ELF; isolation binaries must never execute on the host.
            self.assertRegex(symbols,r'\bU malloc(?:@[^\s]+)?\s')

if __name__ == '__main__': unittest.main()
