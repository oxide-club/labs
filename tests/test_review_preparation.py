"""SPDX-License-Identifier: MIT — regressões editoriais da revisão de 25/10/2026."""
from pathlib import Path
import re
import unittest
ROOT=Path(__file__).resolve().parents[1]
IDS=['019-atomics-lab','020-dispatch-lab','021-fuzzing-lab','022-page-protection-lab','023-elf-hardening-lab']

def table_ids(text):
    lines=text.splitlines();start=next(i for i,line in enumerate(lines) if line.startswith('| ID |'))
    rows=[]
    for line in lines[start+2:]:
        if not line.startswith('|'):break
        match=re.match(r'\| \[(\d{3})-',line)
        if match:rows.append(match[1])
    return rows

class ReviewPreparationTests(unittest.TestCase):
    def test_policy_table_has_all_23_rows_in_one_block(self):
        text=(ROOT/'docs/politica-de-linguagens.md').read_text()
        self.assertEqual(table_ids(text),[f'{i:03}' for i in range(1,24)])
        broken=text.replace('\n| [019','\n\n| [019',1)
        self.assertEqual(len(table_ids(broken)),18,'controle da quebra Markdown deixou de reproduzir')
    def test_code_references_are_fixed_and_match_the_statement(self):
        expected={IDS[0]:['https://docs.rs/loom/0.7.2/loom/','https://github.com/rust-lang/rust/blob/1.98.1/library/core/src/sync/atomic.rs'],
                  IDS[1]:['https://github.com/rust-lang/rust/blob/1.98.1/compiler/rustc_codegen_ssa/src/mir/block.rs']}
        for lab,urls in expected.items():
            for filename in ['index.md','references.md']:
                text=(ROOT/lab/filename).read_text()
                for url in urls:self.assertIn(']('+url+')',text)
                self.assertNotIn('https://docs.rs/loom/latest/',text)
                self.assertNotIn('https://doc.rust-lang.org/nightly/nightly-rustc/src/',text)
    def test_shared_editorial_state_does_not_publish_any_lab(self):
        for lab in IDS:
            text=(ROOT/lab/'index.md').read_text()
            self.assertRegex(text,r'(?m)^draft: true$')
            self.assertIn('**Em elaboração.',text)
            self.assertNotIn('**Em revisão.',text)
if __name__=='__main__':unittest.main()
