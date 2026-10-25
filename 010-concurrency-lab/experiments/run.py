# SPDX-License-Identifier: MIT
import argparse
from pathlib import Path
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
from support import compile_c, run_owned

parser = argparse.ArgumentParser(description="Diagnósticos com encerramento controlado")
parser.add_argument("--mode", choices=["unsafe", "mutex", "atomic"], default="unsafe")
parser.add_argument("--tsan", action="store_true")
args = parser.parse_args()
with tempfile.TemporaryDirectory(prefix="concurrency-experiment-") as directory:
    counter, deadlock = Path(directory) / "counter", Path(directory) / "deadlock"
    compile_c(counter, ["experiments/counter-main.c", "materials/starter/counter.c"], args.tsan)
    compile_c(deadlock, ["experiments/deadlock.c"])
    for repeat in range(3):
        code, out, err, timed_out = run_owned([counter, args.mode])
        print(f"repeat={repeat + 1} status={code} timeout={timed_out}")
        print(out.strip())
        if err:
            print(err.strip())
        if timed_out:
            raise SystemExit("Contador excedeu timeout; processo encerrado e recolhido.")
        if code:
            # Não interpretar falha do runtime como detecção de data race.
            raise SystemExit("Diagnóstico não terminou com sucesso; examine stderr e registre a causa.")
    code, out, err, timed_out = run_owned([deadlock, "bad"], timeout=2)
    print(out.strip())
    if not timed_out or "both-first-locks-held" not in out:
        print(err.strip())
        raise SystemExit("Falha ao estabelecer o cenário de deadlock.")
    print("Deadlock observado após os primeiros locks; timeout controlado; processo recolhido.")
