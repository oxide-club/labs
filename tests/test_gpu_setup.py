"""GPU setup probes resources, without launching participant kernels."""
import os
from pathlib import Path
import sys
import unittest
import test_make

class GPUSetup(unittest.TestCase):
    package = test_make.MakeInterface.package
    make = test_make.MakeInterface.make

    def fixture(self, status):
        lab = self.package('017')
        tools = lab / 'fake-tools'
        tools.mkdir()
        compiler = tools / 'nvcc'
        # Substitute hardware-dependent compilation with a runnable probe.
        # Refuse any participant source: setup may compile only the resource probe.
        compiler.write_text('#!' + sys.executable + '\n' +
            'import pathlib,sys\n' +
            'assert "probe.cu" in sys.argv and "kernels.cu" not in sys.argv\n' +
            'out=pathlib.Path(sys.argv[sys.argv.index("-o")+1])\n' +
            'out.write_text(' + repr('#!/bin/sh\necho RESOURCE_PROBE\nexit '+str(status)+'\n') + ')\n' +
            'out.chmod(0o755)\n')
        compiler.chmod(0o755)
        return lab, {'PATH':str(tools)+os.pathsep+os.environ['PATH']}

    def test_setup_rejects_unavailable_gpu_despite_compiler(self):
        lab, env = self.fixture(1)
        result = self.make(lab, 'setup', env=env)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn('RESOURCE_PROBE', result.stdout)
        self.assertFalse((lab / 'materials/build/gpu').exists())

    def test_setup_checks_available_gpu_without_participant_kernels(self):
        lab, env = self.fixture(0)
        result = self.make(lab, 'setup', env=env)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('RESOURCE_PROBE', result.stdout)
        self.assertFalse((lab / 'materials/build/gpu').exists())
