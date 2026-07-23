"""
collatz_fe16_full_scan.py

Повне сканування FE_16 для всіх проблемних волокон.
Використовує список fe16_error_states.csv та атлас fe16_atlas_full.csv.
"""

import os
import csv
import numpy as np
from tqdm import tqdm

# -----------------------------------------------------------------------------
# 1. КОНСТАНТИ ТА ДОПОМІЖНІ ФУНКЦІЇ
# -----------------------------------------------------------------------------

K = 16
M = 1 << K
MAX_STEPS = 100000
SAMPLES_PER_STATE = 3

def v2(n: int) -> int:
    if n <= 0:
        return 0
    return (n & -n).bit_length() - 1

def v3(n: int) -> int:
    return min(v2(n), 3)

def T(n: int) -> int:
    return n // 2 if n % 2 == 0 else 3 * n + 1

# -----------------------------------------------------------------------------
# 2. ЗАВАНТАЖЕННЯ ДАНИХ
# -----------------------------------------------------------------------------

script_dir = os.path.dirname(os.path.abspath(__file__))

# Атлас: rank та transitions
atlas_path = os.path.join(script_dir, "fe16_atlas_full.csv")
rank = {}
transitions = {}
with open(atlas_path, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        r = int(row['r'])
        v = int(row['v'])
        rank[(r, v)] = int(row['rank'])
        transitions[(r, v)] = (int(row['next_r']), int(row['next_v']))

# Список проблемних станів (виправлено)
error_path = os.path.join(script_dir, "fe16_error_states.csv")
error_states = []
with open(error_path, "r") as f:
    reader = csv.DictReader(f)  # заголовки: r, v
    for row in reader:
        r = int(row['r'])
        v = int(row['v'])
        error_states.append((r, v))

print(f"Завантажено {len(error_states)} проблемних станів.")

# -----------------------------------------------------------------------------
# 3. ФУНКЦІЇ ДЛЯ ТЕСТУВАННЯ ВОЛОКНА
# -----------------------------------------------------------------------------

def sample_fiber(r, v, num_samples, M=65536):
    """Генерує num_samples представників волокна (r, v)."""
    samples = []
    q = 0
    while len(samples) < num_samples:
        n = r + q * M
        if n <= 0:
            q += 1
            continue
        if v3(n) == v:
            samples.append(n)
        q += 1
    return samples

def test_fiber_escape(r, v, rank, transitions, max_steps=MAX_STEPS, num_samples=SAMPLES_PER_STATE):
    """Тестує волокно: повертає список результатів для кожного представника."""
    initial_rank = rank.get((r, v), -1)
    if initial_rank == 0:
        return []  # термінальний стан

    samples = sample_fiber(r, v, num_samples)
    results = []
    for n_start in samples:
        n = n_start
        steps = 0
        escaped = False
        final_rank = initial_rank
        while steps < max_steps:
            curr_state = (n % M, v3(n))
            curr_rank = rank.get(curr_state, -1)
            if curr_rank < initial_rank:
                escaped = True
                final_rank = curr_rank
                break
            n = T(n)
            steps += 1
        results.append({
            'r': r,
            'v': v,
            'initial_rank': initial_rank,
            'n_start': n_start,
            'escaped': escaped,
            'escape_steps': steps if escaped else max_steps,
            'final_rank': final_rank,
        })
    return results

# -----------------------------------------------------------------------------
# 4. ЗАПУСК ТЕСТУВАННЯ
# -----------------------------------------------------------------------------

all_results = []
failed_count = 0

print(f"Тестування {len(error_states)} проблемних станів, по {SAMPLES_PER_STATE} представників...")

for r, v in tqdm(error_states, desc="Сканування"):
    res = test_fiber_escape(r, v, rank, transitions)
    all_results.extend(res)
    for item in res:
        if not item['escaped']:
            failed_count += 1

# -----------------------------------------------------------------------------
# 5. СТАТИСТИКА
# -----------------------------------------------------------------------------

total = len(all_results)
escaped = sum(1 for r in all_results if r['escaped'])
failed = total - escaped

print("\n" + "=" * 60)
print("РЕЗУЛЬТАТИ СКАНУВАННЯ FE_16")
print("=" * 60)
print(f"Всього протестовано представників: {total}")
print(f"Втекли до нижчого рангу: {escaped} ({escaped/total*100:.2f}%)")
print(f"Не втекли (перевищено ліміт): {failed}")

if failed == 0:
    print("\n✅ УСІ ПРЕДСТАВНИКИ ВТЕКЛИ!")
    print("   Це є сильним емпіричним підтвердженням гіпотези FE_16.")
else:
    print(f"\n⚠️ Знайдено {failed} представників, які не втекли за {MAX_STEPS} кроків.")

# Розподіл часів втечі
escape_times = [r['escape_steps'] for r in all_results if r['escaped']]
if escape_times:
    print(f"\nСтатистика часу втечі (для втікачів):")
    print(f"  Мінімум: {min(escape_times)}")
    print(f"  Максимум: {max(escape_times)}")
    print(f"  Середнє: {np.mean(escape_times):.2f}")
    print(f"  Медіана: {np.median(escape_times):.2f}")
    print(f"  Стандартне відхилення: {np.std(escape_times):.2f}")

# -----------------------------------------------------------------------------
# 6. ЗБЕРЕЖЕННЯ РЕЗУЛЬТАТІВ
# -----------------------------------------------------------------------------

out_path = os.path.join(script_dir, "fe16_full_scan_results.csv")
with open(out_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=['r', 'v', 'initial_rank', 'n_start', 'escaped', 'escape_steps', 'final_rank'])
    writer.writeheader()
    for row in all_results:
        writer.writerow(row)

print(f"\nРезультати збережено у {out_path}")
print("=" * 60)