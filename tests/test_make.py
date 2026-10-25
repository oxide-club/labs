"""Behavior of the independent participant interface."""
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class MakeInterface(unittest.TestCase):
    def package(self, number):
        source = next(ROOT.glob(number + '-*'))
        temp = tempfile.TemporaryDirectory(prefix='oxide package ')
        self.addCleanup(temp.cleanup)
        target = Path(temp.name) / source.name
        shutil.copytree(source, target, ignore=shutil.ignore_patterns('build', 'target', '__pycache__', 'results'))
        return target

    def make(self, lab, *args, env=None):
        return subprocess.run(['make', '--no-print-directory', *args], cwd=lab,
                              env={**os.environ, **(env or {})}, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=90)

    def test_all_packages_offer_help_without_building(self):
        for number in range(1, 19):
            with self.subTest(number=number):
                lab = self.package(f'{number:03}')
                result = self.make(lab)
                self.assertEqual(result.returncode, 0, result.stdout)
                for action in ('setup', 'build', 'test', 'run', 'clean', 'verify-preparation'):
                    self.assertIn(action, result.stdout)
                self.assertFalse((lab / 'build').exists())

    def test_invalid_variant_fails_even_during_setup(self):
        result = self.make(self.package('007'), 'setup', 'VARIANT=bogus')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('VARIANT', result.stdout)

    def test_build_and_solution_test_have_different_results(self):
        lab = self.package('001')
        result = self.make(lab, 'build')
        self.assertEqual(result.returncode, 0, result.stdout)
        result = self.make(lab, 'test')
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn('falhas', result.stdout)
        result = self.make(lab, 'verify-preparation')
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_compilation_preserves_incremental_build(self):
        lab = self.package('007')
        result = self.make(lab, 'build')
        self.assertEqual(result.returncode, 0, result.stdout)
        binary = lab / 'materials/build/program'
        before = binary.stat().st_mtime_ns
        self.assertEqual(self.make(lab, 'build').returncode, 0)
        self.assertEqual(binary.stat().st_mtime_ns, before)
        source = lab / 'materials/starter/main.c'
        source.write_text(source.read_text() + '\n/* rebuild */\n')
        self.assertEqual(self.make(lab, 'build').returncode, 0)
        self.assertGreater(binary.stat().st_mtime_ns, before)
        result = self.make(lab, 'test')
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_clean_preserves_foreign_files_and_evidence(self):
        lab = self.package('007')
        self.assertEqual(self.make(lab, 'build').returncode, 0)
        foreign = lab / 'materials/build/notes.txt'
        foreign.write_text('keep')
        (lab / 'results').mkdir()
        evidence = lab / 'results/evidence.txt'
        evidence.write_text('keep')
        result = self.make(lab, 'clean', 'BUILD=/tmp')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertFalse((lab / 'materials/build/program').exists())
        self.assertEqual(foreign.read_text(), 'keep')
        self.assertEqual(evidence.read_text(), 'keep')
        self.assertTrue((lab / 'report-template.md').exists())

    def test_clean_refuses_symlink_build_directory(self):
        lab = self.package('007')
        external = lab / 'elsewhere'
        external.mkdir()
        (external / 'program').write_text('keep')
        (lab / 'materials/build').symlink_to(external, target_is_directory=True)
        result = self.make(lab, 'clean')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((external / 'program').read_text(), 'keep')

    def test_missing_compiler_does_not_pass_setup(self):
        result = self.make(self.package('007'), 'setup', 'CC=oxide-missing-compiler')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('oxide-missing-compiler', result.stdout)

    def test_guarded_actions_refuse_unprepared_host(self):
        for number in ('002', '003', '016'):
            lab = self.package(number)
            for action in ('run', 'test', 'verify-preparation'):
                with self.subTest(number=number, action=action):
                    result = self.make(lab, action)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('env-setup', result.stdout)
                    self.assertFalse((lab / 'materials/build').exists())

    def test_run_records_output_and_status(self):
        lab = self.package('018')
        result = self.make(lab, 'run')
        self.assertEqual(result.returncode, 0, result.stdout)
        files = list((lab / 'results').glob('*/*'))
        self.assertTrue(any(p.name.endswith('stdout.txt') and 'theory' in p.read_text() for p in files))
        self.assertTrue(any(p.name.endswith('status.txt') and p.read_text().strip() == '0' for p in files))

    def test_python_package_relocated_using_distribution_allowlist(self):
        spec = importlib.util.spec_from_file_location('validate', ROOT / 'scripts/validate.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        source = ROOT / '018-attention-lab'
        with tempfile.TemporaryDirectory() as temp:
            lab = Path(temp)
            for path in source.rglob('*'):
                rel = path.relative_to(source)
                if path.is_file() and module.distributed(rel):
                    (lab / rel).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(path, lab / rel)
            self.assertEqual(self.make(lab, 'setup').returncode, 0)
            result = self.make(lab, 'run')
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn('theory', result.stdout)
            self.assertNotEqual(self.make(lab, 'test').returncode, 0)

    def test_gpu_mode_never_falls_back_to_cpu(self):
        lab = self.package('017')
        result = self.make(lab, 'help')
        self.assertIn('nvcc', result.stdout)
        result = self.make(lab, 'setup', 'MODE=unknown')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('MODE', result.stdout)
        result = self.make(lab, 'test', 'MODE=cpu')
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_distribution_includes_root_makefile(self):
        spec = importlib.util.spec_from_file_location('validate', ROOT / 'scripts/validate.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertTrue(module.distributed(Path('Makefile')))
        self.assertFalse(module.distributed(Path('results/evidence.json')))

if __name__ == '__main__':
    unittest.main()
