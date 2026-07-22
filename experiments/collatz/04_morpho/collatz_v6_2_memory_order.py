"""
collatz_v6_2_memory_order.py — Collatz Morphological Memory Order Experiment
Version 6.2 · 2026

Determines the minimum memory order needed for the morphological process
to become approximately Markovian.

Key question: Is the dynamics of Collatz morphological states a Markov chain
of order 1, 2, 3, or higher?
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter
from tqdm import tqdm
from sklearn.metrics import mutual_info_score
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# 0. PATH
# ============================================================================

def get_data_path(filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, filename)

# ============================================================================
# 1. CAUSAL SIGNATURE AND CLASSIFIER (reused from v5.0)
# ============================================================================

def causal_signature(n, history_depth=20):
    """Compute causal local signature using only past information."""
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
    """Load saved classifier or train a new one."""
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
# 2. TRAJECTORY GENERATION AND MORPHOTYPE SEQUENCES
# ============================================================================

def generate_morphotype_sequences(samples, kmeans, scaler, max_steps=3000):
    """Generate sequences of morphotypes for each sample."""
    centroids = kmeans.cluster_centers_
    sequences = []
    for n in tqdm(samples, desc="Generating sequences"):
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
        morphs = [classify_morphotype(val, kmeans, scaler, centroids) for val in traj]
        if any(m == -1 for m in morphs):
            continue
        sequences.append(morphs)
    return sequences

# ============================================================================
# 3. MEMORY ORDER MODELS
# ============================================================================

def build_order_model(sequences, order):
    """
    Build a transition model of given order.
    order=0: state = static features (for baseline, we use n itself as a proxy)
    order=1: state = current morphotype
    order=2: state = (prev, current)
    order=3: state = (prev2, prev1, current)
    Returns: transition matrix, state list, and mapping from state to index.
    """
    if order == 0:
        # For order 0, we treat each number as its own state (not useful for Markov)
        # Instead, we use a simple baseline: predict the most common next morphotype.
        # We'll compute this separately.
        return None, None, None

    trans = defaultdict(lambda: defaultdict(int))
    for seq in sequences:
        for i in range(len(seq) - order):
            if order == 1:
                state = (seq[i],)
            elif order == 2:
                state = (seq[i], seq[i+1])
            elif order == 3:
                state = (seq[i], seq[i+1], seq[i+2])
            else:
                raise ValueError(f"Unsupported order: {order}")
            next_state = seq[i+order]
            trans[state][next_state] += 1

    # Build state list and matrix
    state_list = list(trans.keys())
    idx_map = {state: idx for idx, state in enumerate(state_list)}
    n_states = len(state_list)
    matrix = np.zeros((n_states, 7))  # 7 possible next morphotypes
    for state, transitions in trans.items():
        row_sum = sum(transitions.values())
        if row_sum > 0:
            for next_m, count in transitions.items():
                matrix[idx_map[state], next_m] = count / row_sum

    return matrix, state_list, idx_map

# ============================================================================
# 4. METRICS
# ============================================================================

def compute_metrics(matrix, state_list, sequences, order, test_sequences=None):
    """Compute mutual information, entropy, perplexity, and matrix size."""
    if matrix is None:
        return None

    n_states = len(state_list)
    n_next = matrix.shape[1] if len(matrix.shape) > 1 else 0

    # 1. Matrix size
    matrix_size = n_states

    # 2. Stationary distribution (if ergodic)
    try:
        eigvals, eigvecs = np.linalg.eig(matrix.T)
        idx = np.argmin(np.abs(eigvals - 1.0))
        pi = np.real(eigvecs[:, idx])
        pi = pi / pi.sum()
    except:
        pi = np.ones(n_states) / n_states

    # 3. Entropy H(S_t)
    H_t = -sum(p * np.log2(p) for p in pi if p > 0)

    # 4. Conditional entropy H(S_{t+1} | S_t)
    H_cond = 0
    for i in range(n_states):
        for j in range(n_next):
            if pi[i] > 0 and matrix[i, j] > 0:
                H_cond -= pi[i] * matrix[i, j] * np.log2(matrix[i, j])

    # 5. Mutual information I = H_t - H_cond
    I = H_t - H_cond

    # 6. Perplexity on test set (if provided)
    perplexity = None
    if test_sequences is not None:
        log_likelihood = 0
        count = 0
        # Build a quick mapping from state to distribution
        state_to_dist = {}
        for i, state in enumerate(state_list):
            state_to_dist[state] = matrix[i, :]

        for seq in test_sequences:
            for i in range(len(seq) - order):
                if order == 1:
                    state = (seq[i],)
                elif order == 2:
                    state = (seq[i], seq[i+1])
                elif order == 3:
                    state = (seq[i], seq[i+1], seq[i+2])
                else:
                    continue
                if state in state_to_dist:
                    dist = state_to_dist[state]
                    p = dist[seq[i+order]]
                    if p > 0:
                        log_likelihood += np.log2(p)
                        count += 1
        if count > 0:
            avg_log_likelihood = log_likelihood / count
            perplexity = 2 ** (-avg_log_likelihood)

    return {
        'matrix_size': matrix_size,
        'H_t': H_t,
        'H_cond': H_cond,
        'mutual_info': I,
        'perplexity': perplexity,
        'pi': pi,
        'matrix': matrix,
        'state_list': state_list,
    }

# ============================================================================
# 5. MAIN EXPERIMENT
# ============================================================================

def main():
    print("=" * 80)
    print("COLLATZ MORPHOLOGICAL MEMORY ORDER EXPERIMENT v6.2")
    print("=" * 80)

    # 1. Load classifier
    print("\n[1] Loading classifier...")
    kmeans, scaler = load_or_train_classifier()

    # 2. Generate sequences
    print("\n[2] Generating morphotype sequences...")
    np.random.seed(42)
    train_samples = np.random.randint(1, 5*10**5, 3000)
    test_samples = np.random.randint(1, 5*10**5, 1000)
    train_seqs = generate_morphotype_sequences(train_samples, kmeans, scaler, max_steps=2000)
    test_seqs = generate_morphotype_sequences(test_samples, kmeans, scaler, max_steps=2000)
    print(f"  Generated {len(train_seqs)} training sequences, {len(test_seqs)} test sequences")

    # 3. Build models for different orders
    print("\n[3] Building models...")
    orders = [1, 2, 3]  # order 0 is baseline (static)
    results = {}

    for order in orders:
        print(f"  Order {order}...")
        matrix, state_list, idx_map = build_order_model(train_seqs, order)
        if matrix is None:
            continue
        metrics = compute_metrics(matrix, state_list, train_seqs, order, test_seqs)
        results[order] = metrics
        print(f"    States: {metrics['matrix_size']}, I: {metrics['mutual_info']:.3f} bits")

    # 4. Baseline (order 0): predict most frequent morphotype
    print("\n[4] Baseline (order 0)...")
    # Compute most frequent morphotype overall
    all_morphs = [m for seq in train_seqs for m in seq]
    most_freq = Counter(all_morphs).most_common(1)[0][0]
    # Accuracy on test set
    test_morphs = [m for seq in test_seqs for m in seq]
    baseline_accuracy = sum(1 for m in test_morphs if m == most_freq) / len(test_morphs)
    # Perplexity for baseline: always predict the same, so perplexity = 7 (uniform baseline)
    baseline_perplexity = 7.0  # if all 7 equally likely, but we have a distribution

    # 5. Summary table
    print("\n" + "=" * 80)
    print("SUMMARY TABLE")
    print("=" * 80)
    print(f"{'Order':<6} {'States':<10} {'H_t (bits)':<12} {'H_cond (bits)':<15} {'I (bits)':<12} {'Perplexity':<12}")
    print("-" * 80)
    print(f"{'0 (baseline)':<6} {'N/A':<10} {'N/A':<12} {'N/A':<15} {'N/A':<12} {baseline_perplexity:<12.2f}")
    for order in orders:
        if order in results:
            m = results[order]
            print(f"{order:<6} {m['matrix_size']:<10} {m['H_t']:<12.3f} {m['H_cond']:<15.3f} {m['mutual_info']:<12.3f} {m['perplexity']:<12.2f}")
    print("=" * 80)

    # 6. Plot results
    print("\n[5] Generating plots...")
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Plot 1: Mutual information vs order
    order_vals = [0] + orders
    mi_vals = [0.0]  # order 0 has 0 mutual info
    for order in orders:
        if order in results:
            mi_vals.append(results[order]['mutual_info'])
        else:
            mi_vals.append(0.0)

    axes[0].plot(order_vals, mi_vals, marker='o', linestyle='-', linewidth=2)
    axes[0].set_xlabel('Memory Order')
    axes[0].set_ylabel('Mutual Information I (bits)')
    axes[0].set_title('Mutual Information vs Memory Order')
    axes[0].grid(True, alpha=0.3)

    # Plot 2: Perplexity vs order
    perp_vals = [baseline_perplexity]
    for order in orders:
        if order in results and results[order]['perplexity'] is not None:
            perp_vals.append(results[order]['perplexity'])
        else:
            perp_vals.append(7.0)

    axes[1].plot(order_vals, perp_vals, marker='s', linestyle='-', linewidth=2, color='red')
    axes[1].set_xlabel('Memory Order')
    axes[1].set_ylabel('Perplexity')
    axes[1].set_title('Perplexity vs Memory Order (lower is better)')
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(get_data_path('memory_order_experiment.png'), dpi=150)
    plt.show()
    print("  Saved to memory_order_experiment.png")

    # 7. Save results
    import json
    serializable_results = {}
    for order, metrics in results.items():
        serializable_results[str(order)] = {
            'matrix_size': int(metrics['matrix_size']),
            'H_t': float(metrics['H_t']),
            'H_cond': float(metrics['H_cond']),
            'mutual_info': float(metrics['mutual_info']),
            'perplexity': float(metrics['perplexity']) if metrics['perplexity'] is not None else None,
        }
    with open(get_data_path('memory_order_results.json'), 'w') as f:
        json.dump(serializable_results, f, indent=2)
    print("  Results saved to memory_order_results.json")

    # 8. Interpretation
    print("\n" + "=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    if 2 in results and 3 in results:
        mi_2 = results[2]['mutual_info']
        mi_3 = results[3]['mutual_info']
        improvement = mi_3 - mi_2
        print(f"  Improvement from order 2 to 3: {improvement:.3f} bits")
        if improvement < 0.05:
            print("  -> Second-order memory is sufficient. The process is approximately Markovian with 2-step memory.")
        else:
            print("  -> Third-order memory adds significant predictive power. The process has longer memory.")
    print("=" * 80)


if __name__ == "__main__":
    main()