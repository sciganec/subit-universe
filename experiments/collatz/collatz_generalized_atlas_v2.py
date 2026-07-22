"""
collatz_generalized_atlas_v2.1.py — Generalized Collatz Atlas with Cycle Deduplication
Version 2.1 · 2026

Adds:
- Canonical cycle representation (unique attractors)
- Attractor catalog per (k,c)
- Morphodynamic Ω-vector for each parameter
- Basin entropy and stability metrics
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter
from tqdm import tqdm
import time
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# 1. GENERALIZED COLLATZ MAP (with int safety)
# ============================================================================

def generalized_collatz_trajectory(n: int, d: int, k: int, c: int,
                                   max_steps: int = 10000,
                                   max_value: int = 10**12):
    """Compute trajectory, always using Python int to avoid overflow."""
    traj = []
    seen = {}
    current = int(n)
    steps = 0

    while current not in seen:
        if current > max_value:
            return traj, "CHAOTIC", steps, (steps, current)
        if steps > max_steps:
            return traj, "UNKNOWN", steps, (steps, current)

        traj.append(current)
        seen[current] = steps

        if current == 1:
            return traj, "STABLE", steps, 1

        if current % d == 0:
            current //= d
        else:
            current = k * current + c

        steps += 1

    cycle_start = seen[current]
    cycle = traj[cycle_start:]
    return traj, "CYCLIC", steps, cycle


# ============================================================================
# 2. CYCLE CANONICALIZATION
# ============================================================================

def canonical_cycle(cycle):
    """Return the lexicographically smallest rotation of the cycle."""
    if not cycle:
        return ()
    cycle = [int(x) for x in cycle]
    rotations = [tuple(cycle[i:] + cycle[:i]) for i in range(len(cycle))]
    return min(rotations)


# ============================================================================
# 3. ATLAS WITH DEDUPLICATION
# ============================================================================

class GeneralizedCollatzAtlas:
    def __init__(self, d: int = 2,
                 k_range=range(2, 8),
                 c_range=range(1, 10),
                 n_range=(1, 2000),
                 samples_per_param: int = 100,
                 max_steps: int = 5000,
                 max_value: int = 10**12,
                 seed: int = 42):
        self.d = d
        self.k_range = list(k_range)
        self.c_range = list(c_range)
        self.n_min, self.n_max = n_range
        self.samples_per_param = samples_per_param
        self.max_steps = max_steps
        self.max_value = max_value
        self.rng = np.random.RandomState(seed)

        self.results = {}          # (k,c) -> result dict
        self.attractor_catalog = defaultdict(set)  # (k,c) -> set of canonical cycles

    def explore(self, verbose=True):
        total = len(self.k_range) * len(self.c_range)
        if verbose:
            print("="*80)
            print("GENERALIZED COLLATZ ATLAS v2.1 (Cycle Deduplication)")
            print("="*80)
            print(f"Fixed divisor d = {self.d}")
            print(f"k ∈ {self.k_range}, c ∈ {self.c_range}")
            print(f"  → {total} parameter combinations")
            print(f"  → {self.samples_per_param} samples per param")
            print(f"  → max_steps = {self.max_steps}, max_value = {self.max_value:.1e}")
            print("-"*80)

        start_time = time.time()
        with tqdm(total=total, desc="Exploring parameters", disable=not verbose) as pbar:
            for k in self.k_range:
                for c in self.c_range:
                    result = self._explore_single_param(k, c)
                    self.results[(k, c)] = result
                    pbar.update(1)

        elapsed = time.time() - start_time
        if verbose:
            print(f"\nExploration completed in {elapsed:.1f} seconds.")
            print("-"*80)
        return self.results

    def _explore_single_param(self, k: int, c: int):
        seed = hash((self.d, k, c)) % 2**32
        rng = np.random.RandomState(seed)
        starts = rng.randint(self.n_min, self.n_max + 1, self.samples_per_param)

        stable_count = 0
        cyclic_count = 0
        chaotic_count = 0
        unknown_count = 0

        # For basin analysis: store which cycles appear and frequencies
        cycle_basins = defaultdict(int)
        details = []

        for n in starts:
            traj, omega, steps, data = generalized_collatz_trajectory(
                n, self.d, k, c, self.max_steps, self.max_value
            )

            if omega == "STABLE":
                stable_count += 1
            elif omega == "CYCLIC":
                cyclic_count += 1
                # Canonicalize the cycle and store
                canon = canonical_cycle(data)
                cycle_basins[canon] += 1
                self.attractor_catalog[(k, c)].add(canon)
                if len(details) < 5:
                    details.append((n, "CYCLIC", steps, canon))
            elif omega == "CHAOTIC":
                chaotic_count += 1
                if len(details) < 5:
                    details.append((n, "CHAOTIC", steps, data))
            else:
                unknown_count += 1

        total = stable_count + cyclic_count + chaotic_count + unknown_count

        # Determine dominant omega
        if cyclic_count > 0:
            omega_dom = "CYCLIC"
        elif chaotic_count > 0:
            omega_dom = "CHAOTIC"
        elif stable_count / total > 0.95:
            omega_dom = "STABLE"
        else:
            omega_dom = "MIXED"

        # Compute morphodynamic Ω‑vector for this parameter
        basin_entropy = 0.0
        if cycle_basins:
            probs = np.array(list(cycle_basins.values())) / total
            basin_entropy = -np.sum(probs * np.log(probs + 1e-12))

        return {
            'omega': omega_dom,
            'stable_count': stable_count,
            'cyclic_count': cyclic_count,
            'chaotic_count': chaotic_count,
            'unknown_count': unknown_count,
            'total_samples': total,
            'unique_cycles': len(cycle_basins),
            'basin_entropy': basin_entropy,
            'details': details,
            'cycle_basins': dict(cycle_basins)
        }

    def get_attractor_catalog(self):
        """Return a DataFrame with unique attractors per (k,c)."""
        rows = []
        for (k, c), cycles in self.attractor_catalog.items():
            for cycle in cycles:
                rows.append({
                    'd': self.d,
                    'k': k,
                    'c': c,
                    'cycle': list(cycle),
                    'length': len(cycle),
                    'min_val': min(cycle) if cycle else None,
                    'max_val': max(cycle) if cycle else None
                })
        return pd.DataFrame(rows)

    def create_phase_diagram(self, save_path="generalized_collatz_phase_diagram_v2.1.png"):
        k_values = sorted(self.k_range)
        c_values = sorted(self.c_range)

        omega_order = {'STABLE': 0, 'MIXED': 1, 'CYCLIC': 2, 'CHAOTIC': 3}
        colors = ['#2ecc71', '#f1c40f', '#e74c3c', '#34495e']
        matrix = np.zeros((len(c_values), len(k_values)))

        for i, c in enumerate(c_values):
            for j, k in enumerate(k_values):
                result = self.results.get((k, c))
                matrix[i, j] = omega_order.get(result['omega'], 0) if result else np.nan

        fig, ax = plt.subplots(figsize=(12, 10))
        cmap = plt.cm.colors.ListedColormap(colors)
        im = ax.imshow(matrix, cmap=cmap, origin='lower', aspect='auto', vmin=0, vmax=3)

        ax.set_xticks(range(len(k_values)))
        ax.set_xticklabels(k_values)
        ax.set_yticks(range(len(c_values)))
        ax.set_yticklabels(c_values)
        ax.set_xlabel('k (multiplier for odd step)', fontsize=12)
        ax.set_ylabel('c (offset)', fontsize=12)
        ax.set_title(f'Generalized Collatz Phase Diagram (d={self.d})\n'
                     f'n ∈ [{self.n_min}, {self.n_max}], {self.samples_per_param} samples/param',
                     fontsize=14)

        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#2ecc71', label='STABLE'),
            Patch(facecolor='#f1c40f', label='MIXED'),
            Patch(facecolor='#e74c3c', label='CYCLIC'),
            Patch(facecolor='#34495e', label='CHAOTIC')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        plt.close()
        print(f"  Phase diagram saved to {save_path}")

    def print_summary(self):
        print("\n" + "="*80)
        print("EXPLORATION SUMMARY")
        print("="*80)
        omega_counts = defaultdict(int)
        for result in self.results.values():
            omega_counts[result['omega']] += 1
        print(f"  d = {self.d}")
        print(f"  Parameter combinations explored: {len(self.results)}")
        unique_cycles = sum(len(self.attractor_catalog.get(kc, set())) for kc in self.results)
        print(f"  Unique cycles found: {unique_cycles}")
        print("\n  Ω-class distribution:")
        for omega, count in sorted(omega_counts.items()):
            pct = count / len(self.results) * 100
            print(f"    {omega}: {count} ({pct:.1f}%)")
        print("="*80)


# ============================================================================
# 4. MAIN
# ============================================================================

def main():
    D = 2
    K_RANGE = range(2, 8)
    C_RANGE = range(1, 10)
    N_RANGE = (1, 2000)
    SAMPLES = 100
    MAX_STEPS = 5000
    MAX_VALUE = 10**12

    atlas = GeneralizedCollatzAtlas(
        d=D,
        k_range=K_RANGE,
        c_range=C_RANGE,
        n_range=N_RANGE,
        samples_per_param=SAMPLES,
        max_steps=MAX_STEPS,
        max_value=MAX_VALUE,
        seed=42
    )

    atlas.explore()
    atlas.print_summary()
    atlas.create_phase_diagram()

    # Save attractor catalog
    df_catalog = atlas.get_attractor_catalog()
    df_catalog.to_csv('attractor_catalog.csv', index=False)
    print("  Attractor catalog saved to attractor_catalog.csv")

    # Save full results
    rows = []
    for (k, c), result in atlas.results.items():
        rows.append({
            'd': D,
            'k': k,
            'c': c,
            'omega': result['omega'],
            'stable_count': result['stable_count'],
            'cyclic_count': result['cyclic_count'],
            'chaotic_count': result['chaotic_count'],
            'unknown_count': result['unknown_count'],
            'unique_cycles': result['unique_cycles'],
            'basin_entropy': result['basin_entropy']
        })
    df = pd.DataFrame(rows)
    df.to_csv('generalized_collatz_results_v2.1.csv', index=False)
    print("  Full results saved to generalized_collatz_results_v2.1.csv")

    # Show classic Collatz
    classic = (3, 1)
    if classic in atlas.results:
        r = atlas.results[classic]
        print(f"\n  Classic Collatz (k=3, c=1): {r['omega']} "
              f"({r['stable_count']}/{r['total_samples']} stable)")

    print("\n" + "="*80)
    print("GENERALIZED COLLATZ ATLAS v2.1 COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()