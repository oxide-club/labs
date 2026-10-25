# SPDX-License-Identifier: MIT
import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path

def summarize(path):
    groups=defaultdict(list)
    for row in csv.DictReader(path.open()):
        groups[row['operation'],row['variant']].append((int(row['ns']),int(row['n'])))
    result=[]
    for (op,variant),pairs in sorted(groups.items()):
        data=[p[0] for p in pairs];n=pairs[0][1]
        if len(data)<2 or any(p[1]!=n for p in pairs):raise ValueError('amostras insuficientes ou tamanhos distintos')
        median=statistics.median(data)
        result.append(dict(operation=op,variant=variant,samples=len(data),minimum_ns=min(data),
            median_ns=median,mean_ns=statistics.mean(data),stdev_ns=statistics.stdev(data),
            maximum_ns=max(data),median_ns_per_element=median/n if n else None))
    return result
if __name__=='__main__':
    import json
    p=argparse.ArgumentParser();p.add_argument('csv',type=Path);a=p.parse_args()
    print(json.dumps(summarize(a.csv),indent=2))
