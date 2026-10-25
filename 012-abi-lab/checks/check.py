# SPDX-License-Identifier: MIT
import json
import os
from pathlib import Path
import platform
import subprocess
import tempfile
root = Path(__file__).resolve().parents[1]
if platform.system() != "Linux" or platform.machine() != "x86_64":
    raise SystemExit("Ambiente exigido: Linux x86-64 System V AMD64")
vectors = json.loads((root / "materials/vectors.json").read_text())
# Vetores adicionais independem da implementação C.
for i in range(8):
    a = [0]*8
    a[i] = 17
    vectors.append({"args":a,"expected":17*(i+1)})
for seed in range(32):
    a = [((seed+1)*0x9e3779b97f4a7c15 + i*0x123456789abcdef) % (1<<64) for i in range(8)]
    vectors.append({"args":a,"expected":sum((i+1)*x for i,x in enumerate(a)) % (1<<64)})
for v in vectors:
    assert v["expected"] == sum((i+1)*x for i,x in enumerate(v["args"])) % (1<<64)
data = "".join(" ".join(map(str,v["args"]+[v["expected"]]))+"\n" for v in vectors)
with tempfile.TemporaryDirectory(prefix="oxide-abi-") as d:
    for optimization in ("-O0", "-O2"):
        binary = Path(d)/"check"
        subprocess.run([os.environ.get("CC","cc"),"-std=c11","-Wall","-Wextra","-Werror",optimization,"-I",str(root/"materials"),str(root/"checks/check.c"),str(root/"checks/probe.S"),str(root/"materials/calls.c"),str(root/"materials/arithmetic.S"),"-o",str(binary)],check=True)
        try:
            result = subprocess.run([str(binary)],input=data,text=True,timeout=5)
        except subprocess.TimeoutExpired:
            raise SystemExit("FAIL: timeout de 5 s no probe ABI; verifique stack e retorno") from None
        if result.returncode:
            detail = f"sinal {-result.returncode}" if result.returncode < 0 else f"status {result.returncode}"
            raise SystemExit(f"FAIL: probe ABI terminou com {detail}")
print(f"OK: {len(vectors)} vetores, O0 e O2")
