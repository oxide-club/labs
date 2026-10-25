# SPDX-License-Identifier: MIT
import os
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
    exe=Path(tmp)/"check"
    subprocess.run([os.environ.get("CC","cc"),"-std=c11","-Wall","-Wextra","-Wpedantic","-O2","-I",str(root/"materials/starter"),str(root/"checks/check.c"),str(root/"materials/starter/matrix.c"),"-lm","-o",str(exe)],check=True)
    raise SystemExit(subprocess.run([str(exe)],timeout=30).returncode)
