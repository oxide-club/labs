# SPDX-License-Identifier: MIT
"""MIT. Verifique a CLI original sem incluir ou imprimir uma chave aceita."""
import argparse
from pathlib import Path
import subprocess


def run(binary, arguments, status, stdout, stderr):
    try:
        result = subprocess.run([str(binary), *arguments], capture_output=True, timeout=5)
    except subprocess.TimeoutExpired:
        raise SystemExit("Erro: limite de execução de 5 segundos excedido; entrada omitida") from None
    except OSError:
        raise SystemExit("Erro: não foi possível executar o alvo; argumentos omitidos") from None
    if (result.returncode, result.stdout, result.stderr) != (status, stdout, stderr):
        raise AssertionError("status ou canais de saída divergentes; entrada omitida")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path)
    parser.add_argument("--accepted-file", type=Path,
                        help="arquivo local com bytes da entrada deduzida, sem nova linha")
    args = parser.parse_args()
    binary = args.binary.resolve()
    usage = ("uso: " + str(binary) + " CHAVE\n").encode()
    cases = [([], 2, b"", usage),
             ([b"ABC"], 1, b"porta fechada\n", b""),
             ([b"AAAAAA"], 1, b"porta fechada\n", b""),
             ([b""], 1, b"porta fechada\n", b""),
             ([b"AAAAAAA"], 1, b"porta fechada\n", b""),
             ([b"ABC", b"ABC"], 2, b"", usage)]
    for arguments, status, stdout, stderr in cases:
        run(binary, arguments, status, stdout, stderr)
    print("6 casos públicos: OK")
    if args.accepted_file is not None:
        candidate = args.accepted_file.read_bytes()
        if len(candidate) != 6 or b"\0" in candidate:
            raise ValueError("o arquivo deve conter seis bytes sem NUL e sem nova linha")
        run(binary, [candidate], 0, b"porta aberta\n", b"")
        print("Entrada local aceita: OK (conteúdo omitido)")
    else:
        print("Status 0: pendente da entrada deduzida pelo participante")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, ValueError, OSError):
        raise SystemExit("Erro: arquivo, status ou canais divergentes; entrada omitida") from None
