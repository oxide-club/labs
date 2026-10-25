#!/usr/bin/env python3
# SPDX-License-Identifier: MIT — Oxide Club, 2026.
"""Regressão do parser com traces SINTÉTICOS; não são medições de processos."""
import contextlib
import io
import unittest
from audit_trace import audit, events
from check import IDS, PROTECTION


def fixture():
    rows, lines = [], []
    page = 16384  # Dado sintético: não presume páginas de 4096 no experimento.
    base, parent = 0x80000, 100
    for i, name in enumerate(IDS):
        pid, protection = 200+i, PROTECTION[i]
        setup, hang = name in ['unaligned', 'zero-length'], name == 'hang'
        segv = name in ['none-read', 'none-write', 'r-write']
        result = 'setup_error' if setup else 'timeout' if hang else 'signal' if segv else 'ok'
        code, sig = (2, 0) if setup else (-1, 9) if hang else (-1, 11) if segv else (0, 0)
        rows.append(dict(id=name, protection=protection, reaped=True, pid=pid, page_size=page, pages=3,
                         duration_ms=200, result=result, exit_code=code, signal=sig, errno=22 if setup else 0,
                         byte=-1 if setup or hang or segv else 90 if name in ['w-write','rw-write','transition'] else 165,
                         permissions='----' if setup else 'rw-p', detail='165,165,90' if name=='transition' else '-',
                         operation='setup' if setup else 'wait' if hang else 'transition' if name=='transition' else
                         'write' if name.endswith('write') else 'read'))
        lines.append(f'{parent} fork() = {pid}')
        if name == 'zero-length':
            lines.append(f'{pid} mmap(NULL, 0, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = -1 EINVAL (Invalid argument)')
        else:
            lines.append(f'{pid} mmap(NULL, {3*page}, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = {hex(base)}')
            if name == 'unaligned':
                lines.append(f'{pid} mprotect({hex(base+page+1)}, {page}, PROT_READ) = -1 EINVAL (Invalid argument)')
            else:
                changes = ['PROT_READ|PROT_WRITE','PROT_READ','PROT_READ|PROT_WRITE'] if name=='transition' else [dict(NONE='PROT_NONE', R='PROT_READ', W='PROT_WRITE', RW='PROT_READ|PROT_WRITE')[protection]]
                if name == 'w-write':
                    changes.append('PROT_READ')
                for prot in changes:
                    lines.append(f'{pid} mprotect({hex(base+page)}, {page}, {prot}) = 0')
        if sig:
            signal_name = 'SIGSEGV' if segv else 'SIGKILL'
            if segv:
                lines.append(f'{pid} --- SIGSEGV {{si_code=SEGV_ACCERR}} ---')
            else:
                lines.append(f'{parent} kill({pid}, SIGKILL) = 0')
            lines.append(f'{pid} +++ killed by {signal_name} +++')
            status=f'WIFSIGNALED(s) && WTERMSIG(s) == {signal_name}'
        else:
            lines.append(f'{pid} +++ exited with {code} +++')
            status=f'WIFEXITED(s) && WEXITSTATUS(s) == {code}'
        lines.append(f'{parent} wait4({pid}, [{{{status}}}], WNOHANG, NULL) = {pid}')
    lines.append(f'{parent} +++ exited with 0 +++')
    return '\n'.join(lines), rows


class AuditTests(unittest.TestCase):
    def check(self, trace, records):
        with contextlib.redirect_stdout(io.StringIO()):
            audit(trace, records)

    def test_complete(self):
        self.check(*fixture())

    def test_exit139_is_not_sigsegv(self):
        trace, rows = fixture()
        trace = trace.replace('200 +++ killed by SIGSEGV +++', '200 +++ exited with 139 +++')
        with self.assertRaisesRegex(AssertionError, 'terminação real diverge'):
            self.check(trace, rows)

    def test_exit137_is_not_sigkill(self):
        trace, rows = fixture()
        trace = trace.replace('211 +++ killed by SIGKILL +++', '211 +++ exited with 137 +++')
        with self.assertRaisesRegex(AssertionError, 'terminação real diverge'):
            self.check(trace, rows)

    def test_wait_status_must_agree(self):
        trace, rows = fixture()
        trace = trace.replace('WIFSIGNALED(s) && WTERMSIG(s) == SIGSEGV', 'WIFEXITED(s) && WEXITSTATUS(s) == 139')
        with self.assertRaisesRegex(AssertionError, 'status real de wait4'):
            self.check(trace, rows)

    def test_missing_mapping(self):
        trace, rows = fixture()
        trace = '\n'.join(line for line in trace.splitlines() if not line.startswith('200 mmap('))
        with self.assertRaisesRegex(AssertionError, 'três páginas'):
            self.check(trace, rows)

    def test_errno_must_be_observed(self):
        trace, rows = fixture()
        trace = trace.replace('= -1 EINVAL', '= 0')
        with self.assertRaisesRegex(AssertionError, 'EINVAL real'):
            self.check(trace, rows)

    def test_zero_length_is_second_argument(self):
        trace, rows = fixture()
        trace = trace.replace('210 mmap(NULL, 0, ', '210 mmap(NULL, 16384, ')
        with self.assertRaisesRegex(AssertionError, 'mmap inválido/EINVAL real'):
            self.check(trace, rows)

    def test_unfinished_syscall_spacing(self):
        self.assertEqual(events('2 mprotect(0x4000, 4096, PROT_NONE <unfinished ...>\n2 <... mprotect resumed>) = 0'),
                         [(2, 'mprotect(0x4000, 4096, PROT_NONE) = 0')])


if __name__ == '__main__':
    unittest.main()
