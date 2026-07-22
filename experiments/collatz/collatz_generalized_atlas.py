"""
collatz_generalized_morphotypes.py — Morphotype Analysis for Generalized Collatz
Version 3.0 · 2026

For each (k, c) in the parameter space, extracts morphotypes of trajectories
and builds a meta-atlas relating parameters to morphodynamic structure.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter
from tqdm import tqdm
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# 1. TRAJECTORY SIGNATURE FOR GENERALIZED MAP
# ============================================================================

def trajectory_signature(traj):
    """Extract morphodynamic signature from a trajectory."""
    if not traj:
        return None
    steps = len(traj) - 1
    if steps == 0:
        return None
    max_val = max(traj)
    min_val = min(traj)
    # Compute up/down ratio
    ups = sum(1 for i in range(len(traj)-1) if traj[i] % 2 == 1)
    downs = steps - ups
    up_ratio = ups / (steps + 1e-10)
    # Entropy of values (approximate)
    unique, counts = np.unique(traj, return_counts=True)
    probs = counts / len(traj)
    entropy = -np.sum(probs * np.log2(probs + 1e-10))
    # Peak count (new maxima)
    peak_count = 0
    current_max = traj[0]
    for val in traj[1:]:
        if val > current_max:
            peak_count += 1
            current_max = val
    # Return count (below start)
    start = traj[0]
    return_count = sum(1 for val in traj[1:] if val < start)
    # Compression ratio: steps / log2(max_val+1)
    import math
    compression = steps / (math.log2(max_val + 1) + 1e-10)
    return {
        'steps': steps,
        'max_log': np.log10(max_val + 1),
        'up_ratio': up_ratio,
        'entropy': entropy,
        'peak_count': peak_count,
        'return_count': return_count,
        'compression': compression,
        'unique_ratio': len(unique) / len(traj),
    }


def generalized_collatz_trajectory(n, d, k, c, max_steps=5000, max_value=10**12):
    """Same as before, but returns only trajectory for signature."""
    traj = []
    seen = {}
    current = n
    steps = 0
    while current not in seen:
        if current > max_value or steps > max_steps:
            break
        traj.append(current)
        seen[current] = steps
        if current == 1:
            break
        if current % d == 0:
            current //= d
        else:
            current = k * current + c
        steps += 1
    return traj


# ============================================================================
# 2. MORPHOTYPE EXTRACTION FOR A SINGLE (k, c)
# ============================================================================

def extract_morphotypes_for_param(d, k, c, n_samples=100, n_range=(1,2000),
                                  max_steps=5000, max_value=10**12,
                                  n_clusters=3):
    """Extract morphotypes for a single parameter combination."""
    rng = np.random.RandomState(seed=hash((d, k, c)) % 2**32)
    starts = rng.randint(n_range[0], n_range[1]+1, n_samples)
    signatures = []
    valid_starts = []
    for n in starts:
        traj = generalized_collatz_trajectory(n, d, k, c, max_steps, max_value)
        if traj and len(traj) > 2:
            sig = trajectory_signature(traj)
            if sig:
                signatures.append([sig['steps'], sig['max_log'], sig['up_ratio'],
                                   sig['entropy'], sig['peak_count'], sig['return_count'],
                                   sig['compression'], sig['unique_ratio']])
                valid_starts.append(n)
    if len(signatures) < 2:
        return None, None
    # Cluster
    X = np.array(signatures)
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_norm = scaler.fit_transform(X)
    # Use hierarchical clustering
    Z = linkage(X_norm, method='ward')
    # Determine number of clusters (max 5)
    max_clusters = min(5, len(X_norm))
    labels = fcluster(Z, t=max_clusters, criterion='maxclust')
    return labels, valid_starts


# ============================================================================
# 3. MAIN: BUILD META-ATLAS
# ============================================================================

def build_meta_atlas(d=2, k_range=range(2,8), c_range=range(1,10),
                     n_samples=50, n_range=(1,2000)):
    """Build a meta-atlas: for each (k,c), cluster trajectories into morphotypes."""
    meta_atlas = {}
    total = len(k_range) * len(c_range)
    print(f"Building meta-atlas for d={d}, {total} parameter combinations...")
    print(f"  {n_samples} samples per param, n ∈ {n_range}")
    with tqdm(total=total, desc="Parameters") as pbar:
        for k in k_range:
            for c in c_range:
                labels, starts = extract_morphotypes_for_param(
                    d, k, c, n_samples=n_samples, n_range=n_range
                )
                if labels is not None:
                    n_clusters = len(set(labels))
                    meta_atlas[(k, c)] = {
                        'n_clusters': n_clusters,
                        'labels': labels,
                        'starts': starts,
                        'sample_count': len(starts)
                    }
                else:
                    meta_atlas[(k, c)] = {
                        'n_clusters': 0,
                        'labels': [],
                        'starts': [],
                        'sample_count': 0
                    }
                pbar.update(1)
    return meta_atlas


def plot_meta_atlas(meta_atlas, d=2, save_path="generalized_collatz_meta_atlas.png"):
    """Visualize the number of morphotypes per parameter."""
    k_values = sorted({k for (k,c) in meta_atlas.keys()})
    c_values = sorted({c for (k,c) in meta_atlas.keys()})
    matrix = np.zeros((len(c_values), len(k_values)))
    for (k,c), data in meta_atlas.items():
        i = c_values.index(c)
        j = k_values.index(k)
        matrix[i, j] = data['n_clusters']
    fig, ax = plt.subplots(figsize=(12, 10))
    im = ax.imshow(matrix, cmap='viridis', origin='lower', aspect='auto')
    ax.set_xticks(range(len(k_values)))
    ax.set_xticklabels(k_values)
    ax.set_yticks(range(len(c_values)))
    ax.set_yticklabels(c_values)
    ax.set_xlabel('k (multiplier)', fontsize=12)
    ax.set_ylabel('c (offset)', fontsize=12)
    ax.set_title(f'Generalized Collatz Meta-Atlas: Number of Morphotypes (d={d})', fontsize=14)
    plt.colorbar(im, label='Number of morphotypes')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.show()
    print(f"  Meta-atlas saved to {save_path}")


def main():
    print("=" * 80)
    print("GENERALIZED COLLATZ META-ATLAS")
    print("Building morphotype structure across parameter space")
    print("=" * 80)
    
    # Build meta-atlas
    meta = build_meta_atlas(d=2, k_range=range(2,8), c_range=range(1,10),
                            n_samples=50, n_range=(1,2000))
    
    # Summarize
    print("\nMorphotype counts per parameter:")
    counts = Counter(data['n_clusters'] for data in meta.values())
    for n, cnt in sorted(counts.items()):
        print(f"  {n} morphotypes: {cnt} parameters ({cnt/len(meta)*100:.1f}%)")
    
    # Visualize
    plot_meta_atlas(meta, d=2)
    
    print("\nMETA-ATLAS COMPLETE")
    print("  The meta-atlas reveals how trajectory complexity varies across parameters.")
    print("  Use this to identify regions where dynamics are richest.")


if __name__ == "__main__":
    main()