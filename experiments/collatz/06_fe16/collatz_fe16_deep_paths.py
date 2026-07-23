"""
collatz_fe16_deep_paths.py

Analyzes the deepest states in G_16 (rank = 220).
Reconstructs the full path from each deep state to the terminal cycle.
"""

import os
import csv
import networkx as nx

# Визначаємо шлях до папки, де знаходиться цей скрипт
script_dir = os.path.dirname(os.path.abspath(__file__))
atlas_path = os.path.join(script_dir, "fe16_atlas_full.csv")

# Завантажуємо атлас
atlas = []
with open(atlas_path, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        row['r'] = int(row['r'])
        row['v'] = int(row['v'])
        row['rank'] = int(row['rank'])
        row['rank_next'] = int(row['rank_next'])
        row['next_r'] = int(row['next_r'])
        row['next_v'] = int(row['next_v'])
        atlas.append(row)

# Будуємо граф
G = nx.DiGraph()
for entry in atlas:
    r, v = entry['r'], entry['v']
    nr, nv = entry['next_r'], entry['next_v']
    if nr >= 0:
        G.add_edge((r, v), (nr, nv))

# Шукаємо максимальний ранг
max_rank = max(entry['rank'] for entry in atlas)
print(f"Max rank: {max_rank}")

# Знаходимо всі стани з максимальним рангом
deep_states = [(entry['r'], entry['v']) for entry in atlas if entry['rank'] == max_rank]
print(f"Number of deep states (rank={max_rank}): {len(deep_states)}")

# Відновлюємо шляхи
paths = []
for start in deep_states:
    path = [start]
    current = start
    while current in G and G.out_degree(current) > 0:
        nxt = list(G.successors(current))[0]
        if nxt == current:
            break
        path.append(nxt)
        current = nxt
    paths.append(path)

# Зберігаємо результати
output_txt = os.path.join(script_dir, "fe16_deep_paths.txt")
with open(output_txt, "w") as f:
    f.write(f"Deep states (rank={max_rank}): {len(deep_states)}\n")
    f.write("=" * 60 + "\n")
    for i, path in enumerate(paths):
        f.write(f"\nPath {i+1} (length {len(path)}):\n")
        for step, (r, v) in enumerate(path):
            f.write(f"  {step}: ({r}, {v})\n")
        f.write("\n")

output_csv = os.path.join(script_dir, "fe16_deep_paths.csv")
with open(output_csv, "w") as f:
    writer = csv.writer(f)
    writer.writerow(["path_id", "step", "r", "v"])
    for i, path in enumerate(paths):
        for step, (r, v) in enumerate(path):
            writer.writerow([i, step, r, v])

print(f"Saved {len(paths)} deep paths to:")
print(f"  {output_txt}")
print(f"  {output_csv}")