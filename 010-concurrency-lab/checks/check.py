# SPDX-License-Identifier: MIT
import argparse
import json
from pathlib import Path
import tempfile
from support import ROOT, compile_c, run_owned

parser = argparse.ArgumentParser(description="Checks do participante; starter deve falhar.")
parser.add_argument("--tsan", action="store_true", help="Instrumentar contador correto e fila")
args = parser.parse_args()
failed = 0
with tempfile.TemporaryDirectory(prefix="concurrency-check-") as directory:
    exe, deadlock = Path(directory) / "check", Path(directory) / "deadlock"
    compile_c(exe, ["checks/check.c", "materials/starter/counter.c", "materials/starter/queue.c"], args.tsan)
    compile_c(deadlock, ["experiments/deadlock.c"])
    startup = Path(directory) / "startup"
    compile_c(startup, ["checks/startup.c", "materials/starter/counter.c"], args.tsan,
              [f"-Wl,--wrap={name}" for name in
               ("pthread_create", "pthread_join", "pthread_mutex_init", "pthread_mutex_destroy")])
    code, out, err, timed_out = run_owned([startup])
    ok = not timed_out and code == 0 and out.strip() == "PASS"
    failed += not ok
    print(f"{'PASS' if ok else 'FAIL'} counter-startup: status={code} timeout={timed_out}")
    if err:
        print(err.strip())
    queue_startup = Path(directory) / "queue-startup"
    compile_c(queue_startup, ["checks/queue-startup.c", "materials/starter/queue.c"], args.tsan,
              [f"-Wl,--wrap={name}" for name in
               ("pthread_mutex_init", "pthread_cond_init", "pthread_mutex_destroy", "pthread_cond_destroy")])
    code, out, err, timed_out = run_owned([queue_startup])
    ok = not timed_out and code == 0 and out.splitlines()[-1:] == ["PASS"]
    failed += not ok
    print(f"{'PASS' if ok else 'FAIL'} queue-startup: status={code} timeout={timed_out}")
    if out:
        print(out.strip())
    if err:
        print(err.strip())
    cases = [[name] for name in ("invalid", "mutex", "atomic", "fifo", "empty", "full", "close-empty", "close-full")]
    for case in json.loads((ROOT / "materials/cases.json").read_text())["queue_cases"]:
        cases.append(["stress", *(str(case[k]) for k in ("capacity", "producers", "consumers", "items_per_producer"))])
    for case in cases:
        code, out, err, timed_out = run_owned([exe, *case], timeout=60 if args.tsan else 30)
        ok = not timed_out and code == 0 and out.strip() == "PASS"
        failed += not ok
        print(f"{'PASS' if ok else 'FAIL'} {' '.join(case)}: status={code} timeout={timed_out}")
        if err:
            print(err.strip())
    code, out, err, timed_out = run_owned([deadlock, "bad"], timeout=2)
    ok = timed_out and "both-first-locks-held" in out
    failed += not ok
    print(f"{'PASS' if ok else 'FAIL'} deadlock bad: timeout={timed_out}; processo recolhido")
    code, out, err, timed_out = run_owned([deadlock, "ordered"])
    ok = not timed_out and code == 0 and out.strip() == "completed"
    failed += not ok
    print(f"{'PASS' if ok else 'FAIL'} deadlock ordered: status={code} timeout={timed_out}")
    if err:
        print(err.strip())
print(f"Falhas: {failed}")
raise SystemExit(bool(failed))
