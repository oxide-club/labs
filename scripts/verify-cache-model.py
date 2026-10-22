"""Modelo editorial independente; não distribuído no pacote do participante."""
def simulate(addresses):
    resident = {}
    hits = misses = evictions = 0
    for address in addresses:
        block = address // 16
        line = block % 4
        if resident.get(line) == block:
            hits += 1
        else:
            misses += 1
            evictions += line in resident
            resident[line] = block
    return hits, misses, evictions

def matrix(n, column=False):
    return [n*j+i if column else n*i+j for i in range(n) for j in range(n)]

if __name__ == '__main__':
    for n in (8, 16):
        for column in (False, True):
            print(n, 'colunas' if column else 'linhas', simulate(matrix(n, column)))
