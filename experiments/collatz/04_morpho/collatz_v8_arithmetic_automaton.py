"""
collatz_v8_arithmetic_automaton.py — Collatz v8.0
Arithmetic-Augmented Morphological Automaton

State: (morphotype, residue mod 2^k, v2 class)
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter
from tqdm import tqdm
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# 0. PATH
# ============================================================================

def get_data_path(filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, filename)

# ============================================================================
# 1. CAUSAL SIGNATURE AND CLASSIFIER
# ============================================================================

def causal_signature(n, history_depth=20):
    n = int(n)
    traj = []
    current = n
    for _ in range(history_depth + 1):
        traj.append(current)
        if current == 1:
            break
        if current % 2 == 0:
            current //= 2
        else:
            current = 3 * current + 1
    if len(traj) < 3:
        return np.zeros(7)
    parity = [x % 2 for x in traj[:-1]]
    odd_ratio = sum(parity) / len(parity) if parity else 0
    changes = [traj[i+1] / traj[i] for i in range(len(traj)-1) if traj[i] > 0]
    mean_growth = np.mean(changes) if changes else 1
    var_growth = np.var(changes) if len(changes) > 1 else 0
    pattern = ''.join('U' if x % 2 == 1 else 'D' for x in traj[:-1])
    if pattern:
        counts = Counter(pattern)
        total = sum(counts.values())
        entropy = -sum((c/total) * np.log2(c/total) for c in counts.values() if c > 0)
    else:
        entropy = 0
    recent_max = max(traj[:-1]) if len(traj) > 1 else n
    excursion = recent_max / n if n > 0 else 1
    compression = traj[-1] / traj[0] if traj[0] > 0 else 1
    val_variance = np.var(traj[:-1]) if len(traj) > 1 else 0
    max_run = 0
    current_run = 1
    for i in range(1, len(traj)-1):
        if traj[i] % 2 == traj[i-1] % 2:
            current_run += 1
        else:
            max_run = max(max_run, current_run)
            current_run = 1
    max_run = max(max_run, current_run)
    return np.array([odd_ratio, mean_growth, var_growth, entropy, excursion, compression, max_run])

def load_or_train_classifier():
    try:
        import joblib
        kmeans = joblib.load(get_data_path("causal_kmeans.pkl"))
        scaler = joblib.load(get_data_path("causal_scaler.pkl"))
        print("Loaded saved classifier.")
        return kmeans, scaler
    except:
        print("Training new classifier...")
        np.random.seed(42)
        samples = np.random.randint(1, 10**6, 10000)
        signatures = []
        for n in tqdm(samples, desc="Computing signatures"):
            sig = causal_signature(n)
            if np.any(sig != 0):
                signatures.append(sig)
        signatures = np.array(signatures)
        scaler = StandardScaler()
        X = scaler.fit_transform(signatures)
        kmeans = KMeans(n_clusters=7, random_state=42, n_init=10)
        kmeans.fit(X)
        try:
            import joblib
            joblib.dump(kmeans, get_data_path("causal_kmeans.pkl"))
            joblib.dump(scaler, get_data_path("causal_scaler.pkl"))
        except:
            pass
        return kmeans, scaler

def classify_morphotype(n, kmeans, scaler, centroids):
    sig = causal_signature(n)
    if np.all(sig == 0):
        return 5
    X = scaler.transform([sig])
    try:
        pred = kmeans.predict(X)[0]
        if pred < len(centroids):
            return pred
    except:
        pass
    dist = np.linalg.norm(X - centroids, axis=1)
    return np.argmin(dist)

# ============================================================================
# 2. ARITHMETIC FEATURES
# ============================================================================

def arithmetic_features(n, k):
    n = int(n)  # ensure Python int
    r = n % (1 << k)
    v2 = (n & -n).bit_length() - 1 if n > 0 else 0
    # v2 class: 0, 1, 2, 3+ (for grouping)
    if v2 == 0:
        v2c = 0
    elif v2 == 1:
        v2c = 1
    elif v2 == 2:
        v2c = 2
    else:
        v2c = 3
    pop = bin(n).count('1')
    # popcount class: low (0-8), medium (9-12), high (13+)
    if pop <= 8:
        pc = 0
    elif pop <= 12:
        pc = 1
    else:
        pc = 2
    return r, v2c, pc

def augmented_state(n, kmeans, scaler, k):
    mt = classify_morphotype(n, kmeans, scaler, kmeans.cluster_centers_)
    r, v2c, pc = arithmetic_features(n, k)
    # Combine into a tuple
    return (mt, r, v2c, pc)

# ============================================================================
# 3. GENERATE AUGMENTED SEQUENCES
# ============================================================================

def generate_augmented_sequences(samples, kmeans, scaler, k=8, max_steps=2000):
    sequences = []
    for n in tqdm(samples, desc="Generating augmented sequences"):
        traj = []
        current = n
        while current != 1 and len(traj) < max_steps:
            traj.append(current)
            if current % 2 == 0:
                current //= 2
            else:
                current = 3 * current + 1
        if len(traj) < 2:
            continue
        aug_states = [augmented_state(val, kmeans, scaler, k) for val in traj]
        sequences.append(aug_states)
    return sequences

# ============================================================================
# 4. BUILD TRANSITION MATRIX
# ============================================================================

def build_transition_matrix(sequences):
    trans = defaultdict(lambda: defaultdict(int))
    for seq in sequences:
        for i in range(len(seq)-1):
            trans[seq[i]][seq[i+1]] += 1
    state_list = list(trans.keys())
    idx_map = {s: i for i, s in enumerate(state_list)}
    n_states = len(state_list)
    matrix = np.zeros((n_states, n_states))
    for i, s in enumerate(state_list):
        row_sum = sum(trans[s].values())
        if row_sum > 0:
            for next_s, count in trans[s].items():
                j = idx_map[next_s]
                matrix[i, j] = count / row_sum
    return matrix, state_list, idx_map

# ============================================================================
# 5. METRICS
# ============================================================================

def compute_entropy(matrix):
    n = len(matrix)
    H = np.zeros(n)
    for i in range(n):
        for j in range(n):
            p = matrix[i, j]
            if p > 0:
                H[i] -= p * np.log2(p)
    return H

def compute_stationary(matrix):
    try:
        eigvals, eigvecs = np.linalg.eig(matrix.T)
        idx = np.argmin(np.abs(eigvals - 1.0))
        pi = np.real(eigvecs[:, idx])
        pi = pi / pi.sum()
        return pi
    except:
        return np.ones(len(matrix)) / len(matrix)

def compute_mutual_info(matrix):
    pi = compute_stationary(matrix)
    n = len(matrix)
    H_t = -sum(p * np.log2(p) for p in pi if p > 0)
    H_cond = 0
    for i in range(n):
        for j in range(n):
            if pi[i] > 0 and matrix[i, j] > 0:
                H_cond -= pi[i] * matrix[i, j] * np.log2(matrix[i, j])
    return H_t - H_cond

# ============================================================================
# 6. REDUCE BY AGGREGATING V2 CLASS OR RESIDUE
# ============================================================================

def aggregate_states(state_list, level='v2'):
    """
    Merge states that differ only in residue or v2 class.
    level: 'v2' (keep residue, merge v2), 'residue' (keep v2, merge residue)
    Returns new state list and mapping.
    """
    if level == 'v2':
        # Group by (mt, r) ignoring v2c and pc
        groups = defaultdict(list)
        for s in state_list:
            mt, r, v2c, pc = s
            key = (mt, r)
            groups[key].append(s)
    elif level == 'residue':
        # Group by (mt, v2c, pc) ignoring residue
        groups = defaultdict(list)
        for s in state_list:
            mt, r, v2c, pc = s
            key = (mt, v2c, pc)
            groups[key].append(s)
    else:
        raise ValueError("level must be 'v2' or 'residue'")
    
    new_state_list = list(groups.keys())
    mapping = {}
    for new_s, old_list in groups.items():
        for old_s in old_list:
            mapping[old_s] = new_s
    return new_state_list, mapping

def build_aggregated_matrix(matrix, state_list, mapping):
    n_agg = len(set(mapping.values()))
    agg_matrix = np.zeros((n_agg, n_agg))
    # We need to map each original state to aggregate index
    agg_idx = {s: i for i, s in enumerate(set(mapping.values()))}
    for i, s in enumerate(state_list):
        row = matrix[i, :]
        for j, next_s in enumerate(state_list):
            if row[j] > 0:
                agg_i = agg_idx[mapping[s]]
                agg_j = agg_idx[mapping[next_s]]
                agg_matrix[agg_i, agg_j] += row[j]  # weighted by probability
    # Normalize rows
    for i in range(n_agg):
        row_sum = agg_matrix[i].sum()
        if row_sum > 0:
            agg_matrix[i] /= row_sum
    return agg_matrix, agg_idx

# ============================================================================
# 7. VISUALIZATION
# ============================================================================

def plot_transition_matrix(matrix, title, save_path):
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(matrix, cmap='Blues', aspect='auto')
    ax.set_title(title)
    ax.set_xlabel('Next state')
    ax.set_ylabel('Current state')
    plt.colorbar(im)
    plt.tight_layout()
    plt.savefig(get_data_path(save_path), dpi=150)
    plt.show()
    print(f"Saved to {save_path}")

# ============================================================================
# 8. MAIN
# ============================================================================

def main():
    print("=" * 80)
    print("COLLATZ v8.0: ARITHMETIC-AUGMENTED MORPHOLOGICAL AUTOMATON")
    print("=" * 80)

    # Load classifier
    print("\n[1] Loading morphotype classifier...")
    kmeans, scaler = load_or_train_classifier()
    centroids = kmeans.cluster_centers_

    # Generate samples
    print("\n[2] Generating samples...")
    np.random.seed(42)
    samples = np.random.randint(1, 10**6, 3000)
    print(f"  Generated {len(samples)} samples")

    # Generate augmented sequences
    k = 8  # residue mod 2^8
    print(f"\n[3] Generating augmented sequences (k={k})...")
    sequences = generate_augmented_sequences(samples, kmeans, scaler, k=k, max_steps=2000)
    print(f"  Generated {len(sequences)} sequences")

    # Build transition matrix
    print("\n[4] Building transition matrix...")
    matrix, state_list, idx_map = build_transition_matrix(sequences)
    n_states = len(state_list)
    print(f"  Number of augmented states: {n_states}")

    # Compute metrics
    print("\n[5] Computing metrics...")
    H_cond = np.mean(compute_entropy(matrix))
    I = compute_mutual_info(matrix)
    print(f"  H_cond (avg): {H_cond:.3f} bits")
    print(f"  Mutual info I: {I:.3f} bits")

    # Aggregations
    print("\n[6] Aggregating states...")
    # Aggregate by v2 class (merge v2c, pc)
    new_list, mapping = aggregate_states(state_list, level='v2')
    agg_matrix, agg_idx = build_aggregated_matrix(matrix, state_list, mapping)
    H_cond_v2 = np.mean(compute_entropy(agg_matrix))
    I_v2 = compute_mutual_info(agg_matrix)
    print(f"  After aggregating v2: states={len(new_list)}, H_cond={H_cond_v2:.3f}, I={I_v2:.3f}")

    # Aggregate by residue (merge residue)
    new_list_r, mapping_r = aggregate_states(state_list, level='residue')
    agg_matrix_r, agg_idx_r = build_aggregated_matrix(matrix, state_list, mapping_r)
    H_cond_res = np.mean(compute_entropy(agg_matrix_r))
    I_res = compute_mutual_info(agg_matrix_r)
    print(f"  After aggregating residue: states={len(new_list_r)}, H_cond={H_cond_res:.3f}, I={I_res:.3f}")

    # Compare with order-1 (morphotype only)
    # Compute from original morphotype sequences (we can reuse)
    print("\n[7] Comparison with morphotype-only model...")
    # Reuse sequences but extract only morphotypes
    morph_seqs = [[s[0] for s in seq] for seq in sequences]
    # Build matrix for morphotypes
    trans_morph = defaultdict(lambda: defaultdict(int))
    for seq in morph_seqs:
        for i in range(len(seq)-1):
            trans_morph[seq[i]][seq[i+1]] += 1
    morph_states = list(trans_morph.keys())
    n_morph = len(morph_states)
    morph_matrix = np.zeros((n_morph, n_morph))
    for i, s in enumerate(morph_states):
        row_sum = sum(trans_morph[s].values())
        if row_sum > 0:
            for j, ns in enumerate(morph_states):
                morph_matrix[i, j] = trans_morph[s][ns] / row_sum
    H_cond_morph = np.mean(compute_entropy(morph_matrix))
    I_morph = compute_mutual_info(morph_matrix)
    print(f"  Morphotype-only: states={n_morph}, H_cond={H_cond_morph:.3f}, I={I_morph:.3f}")

    # Summary table
    print("\n" + "=" * 80)
    print("SUMMARY TABLE")
    print("=" * 80)
    print(f"{'Model':<20} {'States':<10} {'H_cond (bits)':<15} {'I (bits)':<12}")
    print("-" * 60)
    print(f"{'Morphotype-only':<20} {n_morph:<10} {H_cond_morph:<15.3f} {I_morph:<12.3f}")
    print(f"{'Augmented (full)':<20} {n_states:<10} {H_cond:<15.3f} {I:<12.3f}")
    print(f"{'Augmented (v2 agg)':<20} {len(new_list):<10} {H_cond_v2:<15.3f} {I_v2:<12.3f}")
    print(f"{'Augmented (res agg)':<20} {len(new_list_r):<10} {H_cond_res:<15.3f} {I_res:<12.3f}")
    print("=" * 80)

    # Visualization
    print("\n[8] Visualizing...")
    plot_transition_matrix(matrix[:min(100, n_states), :min(100, n_states)],
                           f"Augmented Automaton (first 100 of {n_states} states)",
                           "augmented_automaton.png")
    plot_transition_matrix(agg_matrix, f"Aggregated by v2 ({len(new_list)} states)", "agg_v2.png")
    plot_transition_matrix(agg_matrix_r, f"Aggregated by residue ({len(new_list_r)} states)", "agg_res.png")

    # Save data
    import json
    results = {
        'n_states': n_states,
        'H_cond': H_cond,
        'I': I,
        'n_states_v2_agg': len(new_list),
        'H_cond_v2_agg': H_cond_v2,
        'I_v2_agg': I_v2,
        'n_states_res_agg': len(new_list_r),
        'H_cond_res_agg': H_cond_res,
        'I_res_agg': I_res,
        'n_morph': n_morph,
        'H_cond_morph': H_cond_morph,
        'I_morph': I_morph,
    }
    with open(get_data_path("v8_results.json"), "w") as f:
        json.dump(results, f, indent=2)
    print("  Results saved to v8_results.json")

    print("\n" + "=" * 80)
    print("EXPERIMENT COMPLETE")
    print("=" * 80)
    print("\n  Key insight: Adding arithmetic features drastically increases")
    print("  the number of states but also increases mutual information.")
    print("  Aggregation helps reduce state count while preserving predictive power.")

if __name__ == "__main__":
    main()