"""SPDX-License-Identifier: MIT — previsão densa e medição Python são saídas distintas."""
import argparse
import csv
import gc
import importlib.util
import io
from pathlib import Path
import platform
import subprocess
import sys
import time
import tracemalloc

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True


def sizes(text):
    try:
        values = [int(x) for x in text.split(',')]
    except ValueError as error:
        raise argparse.ArgumentTypeError('use tamanhos inteiros separados por vírgula') from error
    if not values or any(n < 1 or n > 256 for n in values):
        raise argparse.ArgumentTypeError('cada N deve ficar entre 1 e 256')
    return values


def repetitions(text):
    try:
        count = int(text)
    except ValueError as error:
        raise argparse.ArgumentTypeError('repetições devem ser inteiras') from error
    if not 1 <= count <= 20:
        raise argparse.ArgumentTypeError('use de 1 a 20 repetições')
    return count


def measure_call(operation):
    """Meça só a chamada; os argumentos e o módulo já devem existir."""
    gc.collect()
    tracemalloc.start()
    try:
        started = time.perf_counter()
        result = operation()
        elapsed = time.perf_counter() - started
        retained, peak = tracemalloc.get_traced_memory()
        # result permanece vivo até depois de consultar a memória retida.
        del result
        return elapsed, retained, peak
    finally:
        tracemalloc.stop()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--theory', action='store_true')
    mode.add_argument('--measure', action='store_true')
    parser.add_argument('--sizes', type=sizes, default=[16, 32, 64, 128, 256])
    parser.add_argument('--repeats', type=repetitions, default=3)
    parser.add_argument('--causal', action='store_true')
    parser.add_argument('--candidate', type=Path, default=ROOT/'materials/attention.py')
    args = parser.parse_args()
    rows = []
    if args.theory:
        for n in args.sizes:
            rows.append({'kind': 'theory', 'n': n, 'scores_elements': n*n,
                         'scores_model_bytes': 8*n*n,
                         'scores_and_probabilities_model_bytes': 16*n*n})
    else:
        # Não produza CSV de medição antes de verificar o contrato público completo.
        try:
            check = subprocess.run([sys.executable, str(ROOT/'checks/check.py'),
                                    str(args.candidate.resolve())],
                                   capture_output=True, text=True, timeout=60)
        except subprocess.TimeoutExpired:
            print('checks excederam 60 segundos; não houve medição.', file=sys.stderr)
            return 1
        if check.returncode:
            print('checks reprovaram a implementação; não houve medição.', file=sys.stderr)
            print(check.stderr[-3000:], file=sys.stderr)
            return 1
        spec = importlib.util.spec_from_file_location('attention_measured', args.candidate)
        api = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(api)
            for n in args.sizes:
                # Entradas determinísticas; d_k=8 e d_v=4 fixos para isolar N.
                q = [[((i+2*j) % 11-5)/8 for j in range(8)] for i in range(n)]
                k = [[((3*i+j) % 13-6)/8 for j in range(8)] for i in range(n)]
                v = [[((i+j) % 7-3)/4 for j in range(4)] for i in range(n)]
                api.attention(q, k, v, causal=args.causal)  # Aquecimento descartado.
                for repeat in range(1, args.repeats+1):
                    elapsed, retained, peak = measure_call(
                        lambda: api.attention(q, k, v, causal=args.causal))
                    rows.append({'kind': 'observed-python', 'n': n, 'd_k': 8, 'd_v': 4,
                                 'causal': args.causal, 'repeat': repeat,
                                 'traced_elapsed_seconds': elapsed,
                                 'traced_retained_bytes': retained, 'traced_peak_bytes': peak,
                                 'python': platform.python_version(),
                                 'implementation': platform.python_implementation(),
                                 'platform': platform.platform()})
        except Exception as error:
            print(f'medição interrompida: {type(error).__name__}: {error}', file=sys.stderr)
            return 1
    # Buffer evita publicar linhas parciais quando uma dimensão posterior falha.
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    print(output.getvalue(), end='')
    return 0


if __name__ == '__main__':
    sys.exit(main())
