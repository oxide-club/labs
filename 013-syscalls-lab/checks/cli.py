# SPDX-License-Identifier: MIT
import subprocess
import sys
for binary in sys.argv[1:]:
    for args, status, out, err in [([], 0, b"oxide\n", b""), (["--bad-fd"], 1, b"", b"EBADF\n"), (["bad"], 2, b"", b"")]:
        r = subprocess.run([binary, *args], capture_output=True, timeout=3)
        assert (r.returncode, r.stdout, r.stderr) == (status, out, err), (binary, args, r)
print("CLI: OK")
