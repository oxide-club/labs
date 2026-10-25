"""SPDX-License-Identifier: MIT"""
import importlib.util
from pathlib import Path
import tempfile
import unittest
SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'validate.py'
class ValidationTests(unittest.TestCase):
    def module(self):
        self.assertTrue(SCRIPT.exists(), 'validador ainda não implementado')
        spec=importlib.util.spec_from_file_location('validation', SCRIPT)
        module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        return module
    def fixture(self, root, module):
        lab=root/'001-test-lab'; lab.mkdir()
        (lab/'index.md').write_text('''---
title: Laboratório de Teste
slug: 001-test-lab
summary: Investigue o teste.
question: Por que o teste falha?
draft: true
topics: [Teste]
prerequisites: [Python]
tools: [Python 3]
environment: Linux
difficulty: intermediate
---
'''+'\n'.join('## '+title+'\n\nTexto.\n' for title in module.SECTIONS))
        for name in ['README.md','references.md','report-template.md','materials/README.md']:
            p=lab/name; p.parent.mkdir(parents=True,exist_ok=True); p.write_text('Texto.\n')
        return lab
    def test_valid_then_rejects_slug_and_missing_link(self):
        module=self.module()
        with tempfile.TemporaryDirectory() as d:
            lab=self.fixture(Path(d),module);p=lab/'index.md';original=p.read_text()
            self.assertEqual(module.validate_lab(lab),[])
            p.write_text(original.replace('slug: 001-test-lab','slug: 002-wrong'))
            self.assertTrue(any('slug' in e for e in module.validate_lab(lab)))
            p.write_text(original+'\n[entrada](materials/missing.txt)\n')
            self.assertTrue(any('missing.txt' in e for e in module.validate_lab(lab)))
    def test_rejects_link_to_file_excluded_from_package(self):
        module=self.module()
        with tempfile.TemporaryDirectory() as d:
            lab=self.fixture(Path(d),module)
            target=lab/'materials/example.o'; target.write_text('artifact')
            readme=lab/'README.md'; readme.write_text('[objeto](materials/example.o)\n')
            self.assertTrue(any('pacote' in e for e in module.validate_lab(lab)))
    def test_rejects_title_without_published_prefix(self):
        module=self.module()
        with tempfile.TemporaryDirectory() as d:
            lab=self.fixture(Path(d),module);index=lab/'index.md'
            index.write_text(index.read_text().replace('title: Laboratório de Teste','title: Teste'))
            self.assertTrue(any('title' in e for e in module.validate_lab(lab)))
    def test_rejects_duplicate_number_and_unregistered_lab(self):
        module=self.module()
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); lab=self.fixture(root,module)
            duplicate=root/'001-other-lab'; duplicate.mkdir()
            self.assertTrue(module.validate_catalog(root,[{'id':lab.name},{'id':duplicate.name}]))
            self.assertTrue(module.validate_catalog(root,[]))
            self.assertEqual(module.validate_catalog(root,[{'id':lab.name},{'id':'002-future-lab'}])[:1],
                             ['diretório não registrado: 001-other-lab'])
    def test_fixture_manifest_excludes_build_outputs(self):
        module=self.module()
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); lab=self.fixture(root,module)
            build=lab/'materials/build';build.mkdir();(build/'trace.txt').write_text('observação variável')
            self.assertNotIn('001-test-lab/materials/build/trace.txt',module.fixture_manifest(root))
    def test_manifest_covers_experiment_datasets(self):
        module=self.module()
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); lab=self.fixture(root,module)
            dataset=lab/'experiments/datasets.csv';dataset.parent.mkdir()
            dataset.write_text('size\n1024\n')
            manifest=module.fixture_manifest(root)
            self.assertIn('001-test-lab/experiments/datasets.csv',manifest)
            dataset.write_text('size\n2048\n')
            self.assertTrue(module.check_manifest(root,manifest))
    def test_rejects_symlink_and_tampered_fixture(self):
        module=self.module()
        with tempfile.TemporaryDirectory() as d:
            lab=self.fixture(Path(d),module)
            (lab/'materials/escape').symlink_to('/tmp')
            self.assertTrue(any('simbólico' in e for e in module.validate_lab(lab)))
            (lab/'materials/escape').unlink()
            fixture=lab/'materials/data.txt';fixture.write_text('original\n')
            manifest=module.fixture_manifest(Path(d));fixture.write_text('alterado\n')
            self.assertTrue(module.check_manifest(Path(d),manifest))
if __name__=='__main__': unittest.main()
