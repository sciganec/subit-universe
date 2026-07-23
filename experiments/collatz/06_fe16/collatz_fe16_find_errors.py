"""
collatz_fe16_find_errors.py

Find states where projection error occurs.
For each state, test a few representatives and check if Π16(T(n)) == T16(Π16(n)).
"""

import os
import csv
from tqdm import tqdm

K = 16
M = 1 << K
NUM_SAMPLES = 5  # перевіряємо 5 представників на стан

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

# Завантажуємо атлас
script_dir = os.path.dirname(os.path.abspath(__file__))
atlas_path = os.path.join(script_dir, "fe16_atlas_full.csv")

transitions = {}
states = []
with open(atlas_path, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        r = int(row['r'])
        v = int(row['v'])
        nr = int(row['next_r'])
        nv = int(row['next_v'])
        transitions[(r, v)] = (nr, nv)
        states.append((r, v))

# Шукаємо проблемні стани
error_states = []
print(f"Testing {len(states)} states with {NUM_SAMPLES} samples each...")

for s in tqdm(states, desc="Scanning states"):
    r, v = s
    error_found = False
    # Шукаємо представників
    for q in range(NUM_SAMPLES * 10):
        n = r + q * M
        if n <= 0:
            continue
        if v3(n) != v:
            continue
        # Перевіряємо проекцію
        actual_next = pi(T(n))
        expected_next = transitions.get(s, None)
        if expected_next is None:
            continue
        if actual_next != expected_next:
            error_found = True
            break
        # Якщо знайшли помилку, виходимо з циклу
        if error_found:
            break
    if error_found:
        error_states.append(s)

print(f"\nFound {len(error_states)} states with projection errors.")

# Зберігаємо список
output_path = os.path.join(script_dir, "fe16_error_states.csv")
with open(output_path, "w") as f:
    writer = csv.writer(f)
    writer.writerow(["r", "v"])
    for r, v in error_states:
        writer.writerow([r, v])

print(f"Error states saved to {output_path}")