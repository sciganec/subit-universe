"""
collatz_fe16_fiber_scan.py

Scan the fiber of the deepest state (40479, 0).
For each representative n = 40479 + q * 65536,
compute the projection error and the time to enter the graph.
"""

import os
import csv
import sys
from tqdm import tqdm

# Константи
K = 16
M = 1 << K  # 65536
DEEP_R = 40479
DEEP_V = 0

# Функції
def v2(n):
    if n <= 0:
        return 0
    return (n & -n).bit_length() - 1

def v3(n):
    return min(v2(n), 3)

def pi(n):
    return (n % M, v3(n))

def T(n):
    if n % 2 == 0:
        return n // 2
    else:
        return 3 * n + 1

# Завантажуємо атлас, щоб отримати переходи T16 та rank
script_dir = os.path.dirname(os.path.abspath(__file__))
atlas_path = os.path.join(script_dir, "fe16_atlas_full.csv")

transitions = {}
rank = {}
with open(atlas_path, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        r = int(row['r'])
        v = int(row['v'])
        nr = int(row['next_r'])
        nv = int(row['next_v'])
        transitions[(r, v)] = (nr, nv)
        rank[(r, v)] = int(row['rank'])

# Скануємо волокно
print(f"Scanning fiber of state ({DEEP_R}, {DEEP_V})")
print(f"n = {DEEP_R} + q * {M}")

results = []
MAX_Q = 10000
MAX_STEPS = 10000

for q in tqdm(range(MAX_Q), desc="Scanning q"):
    n_start = DEEP_R + q * M
    if n_start <= 0:
        continue
    if v3(n_start) != DEEP_V:
        continue  # має бути 0 для непарних

    n = n_start
    steps = 0
    on_graph = False
    while steps < MAX_STEPS:
        state = pi(n)
        if state in transitions:
            expected_next = transitions[state]
            actual_next = pi(T(n))
            if actual_next == expected_next:
                on_graph = True
                break
        n = T(n)
        steps += 1

    results.append({
        'q': q,
        'n_start': n_start,
        'steps_to_graph': steps if on_graph else MAX_STEPS,
        'on_graph': on_graph
    })

# Статистика
on_graph_count = sum(1 for r in results if r['on_graph'])
print(f"\nTotal samples: {len(results)}")
print(f"On graph (exact projection): {on_graph_count}")
print(f"Not on graph within {MAX_STEPS} steps: {len(results) - on_graph_count}")

if on_graph_count > 0:
    times = [r['steps_to_graph'] for r in results if r['on_graph']]
    print(f"Mean time to graph: {sum(times)/len(times):.2f}")
    print(f"Max time to graph: {max(times)}")
    print(f"Min time to graph: {min(times)}")

# Збереження
output_path = os.path.join(script_dir, "fe16_fiber_scan.csv")
with open(output_path, "w") as f:
    writer = csv.writer(f)
    writer.writerow(["q", "n_start", "steps_to_graph", "on_graph"])
    for r in results:
        writer.writerow([r['q'], r['n_start'], r['steps_to_graph'], r['on_graph']])

print(f"Results saved to {output_path}")