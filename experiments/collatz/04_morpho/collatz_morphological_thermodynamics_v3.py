"""
collatz_morphological_thermodynamics_v3.py — Collatz Morphological Thermodynamics
Version 3.3 · 2026

Causal version: classifier trained on a large sample of starting numbers.
Uses nearest-centroid classification with fallback.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict, Counter
from tqdm import tqdm
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

def get_data_path(filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, filename)

# ============================================================================
# 1. CAUSAL LOCAL SIGNATURE (past only)
# ============================================================================

def causal_local_signature(n, history_depth=20, max_steps=5000):
    """Compute local signature using ONLY past information."""
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

# ============================================================================
# 2. BUILD CLASSIFIER (trained on starting numbers)
# ============================================================================

def build_causal_classifier(train_samples, n_clusters=7, history_depth=20):
    """Train classifier on a large set of starting numbers."""
    print("Building causal classifier from starting numbers...")
    signatures = []
    for n in tqdm(train_samples, desc="Computing signatures"):
        sig = causal_local_signature(n, history_depth=history_depth)
        if np.any(sig != 0):
            signatures.append(sig)
    signatures = np.array(signatures)
    scaler = StandardScaler()
    X = scaler.fit_transform(signatures)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X)
    print(f"Built {n_clusters} morphotypes from {len(signatures)} training samples.")
    return kmeans, scaler

# ============================================================================
# 3. CLASSIFY WITH FALLBACK (nearest centroid)
# ============================================================================

def classify_causal(n, kmeans, scaler, centroids, history_depth=20):
    """Classify state; if unknown, fallback to nearest centroid."""
    sig = causal_local_signature(n, history_depth=history_depth)
    if np.all(sig == 0):
        # Fallback: return centroid of M5 (state 5) as default
        return 5
    X = scaler.transform([sig])
    # Use predict, but if it returns -1, fallback to nearest centroid
    try:
        pred = kmeans.predict(X)[0]
        # Check if prediction is valid (cluster centroid exists)
        if pred < len(centroids):
            return pred
    except:
        pass
    # Fallback: nearest centroid by Euclidean distance
    dist = np.linalg.norm(X - centroids, axis=1)
    return np.argmin(dist)

# ============================================================================
# 4. BUILD TRANSITION MATRICES
# ============================================================================

def build_transition_matrices(samples, kmeans, scaler, centroids, history_depth=20, max_steps=3000):
    n_clusters = len(centroids)
    trans1 = defaultdict(lambda: defaultdict(int))
    trans2 = defaultdict(lambda: defaultdict(int))
    for n in tqdm(samples, desc="Building transitions"):
        traj = []
        current = n
        while current != 1 and len(traj) < max_steps:
            traj.append(current)
            if current % 2 == 0:
                current //= 2
            else:
                current = 3 * current + 1
        if len(traj) < 3:
            continue
        morphs = []
        for val in traj:
            mt = classify_causal(val, kmeans, scaler, centroids, history_depth=history_depth)
            morphs.append(mt)
        for i in range(len(morphs)-1):
            trans1[morphs[i]][morphs[i+1]] += 1
        for i in range(len(morphs)-2):
            key = (morphs[i], morphs[i+1])
            trans2[key][morphs[i+2]] += 1
    matrix1 = np.zeros((n_clusters, n_clusters))
    for i in range(n_clusters):
        row_sum = sum(trans1[i].values())
        if row_sum > 0:
            for j in range(n_clusters):
                matrix1[i, j] = trans1[i][j] / row_sum
    matrix2 = {}
    for (i, j), transitions in trans2.items():
        total = sum(transitions.values())
        if total > 0:
            matrix2[(i, j)] = {k: transitions[k] / total for k in transitions}
    return matrix1, matrix2

# ============================================================================
# 5. THERMODYNAMIC QUANTITIES
# ============================================================================

def compute_potential(matrix, target_state=5):
    n = len(matrix)
    A = np.eye(n) - matrix
    for i in range(n):
        if i == target_state:
            A[i, :] = 0
            A[i, i] = 1
    b = np.ones(n)
    b[target_state] = 0
    try:
        V = np.linalg.solve(A, b)
        return V
    except np.linalg.LinAlgError:
        V = np.linalg.lstsq(A, b, rcond=None)[0]
        return V

def compute_entropy(matrix):
    n = len(matrix)
    H = np.zeros(n)
    for i in range(n):
        for j in range(n):
            p = matrix[i, j]
            if p > 0:
                H[i] -= p * np.log2(p)
    return H

def compute_mutual_information(matrix):
    n = len(matrix)
    try:
        eigvals, eigvecs = np.linalg.eig(matrix.T)
        idx = np.argmin(np.abs(eigvals - 1.0))
        pi = np.real(eigvecs[:, idx])
        pi = pi / pi.sum()
    except:
        pi = np.ones(n) / n
    H_t = -sum(p * np.log2(p) for p in pi if p > 0)
    H_cond = 0
    for i in range(n):
        for j in range(n):
            if pi[i] > 0 and matrix[i, j] > 0:
                H_cond -= pi[i] * matrix[i, j] * np.log2(matrix[i, j])
    return H_t - H_cond

def scc_analysis(matrix, threshold=0.001):
    n = len(matrix)
    G = nx.DiGraph()
    for i in range(n):
        for j in range(n):
            if matrix[i, j] > threshold:
                G.add_edge(i, j)
    return list(nx.strongly_connected_components(G))

def plot_landscape(V, H, labels, save_path='collatz_morphological_landscape.png'):
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(H, V, s=200, c=range(len(V)), cmap='viridis', alpha=0.8)
    for i, (h, v) in enumerate(zip(H, V)):
        ax.annotate(f"M{i}", (h, v), fontsize=12, ha='center', va='bottom')
    ax.set_xlabel('Entropy H(M) [bits]', fontsize=12)
    ax.set_ylabel('Potential V(M) [expected steps to M5]', fontsize=12)
    ax.set_title('Collatz Morphological Landscape (Causal)', fontsize=14)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(get_data_path(save_path), dpi=150)
    plt.show()
    print(f"  Saved to {save_path}")

# ============================================================================
# 6. MAIN
# ============================================================================

def main():
    print("=" * 80)
    print("COLLATZ MORPHOLOGICAL THERMODYNAMICS v3.3")
    print("Causal — classifier trained on 10k starting numbers")
    print("=" * 80)

    # Generate training samples (10,000 starting numbers)
    print("\n[1] Generating training samples...")
    np.random.seed(42)
    train_samples = np.random.randint(1, 10**6, 10000)
    print(f"Generated {len(train_samples)} training samples")

    # Build classifier
    print("\n[2] Building causal classifier...")
    kmeans, scaler = build_causal_classifier(train_samples, n_clusters=7, history_depth=20)
    centroids = kmeans.cluster_centers_

    # Generate test samples (2000 numbers)
    print("\n[3] Generating test samples...")
    test_samples = np.random.randint(1, 10**5, 2000)
    print(f"Generated {len(test_samples)} test samples")

    # Build transition matrices
    print("\n[4] Building transition matrices (1st and 2nd order)...")
    matrix1, matrix2 = build_transition_matrices(
        test_samples, kmeans, scaler, centroids, history_depth=20, max_steps=3000
    )

    print("First-order matrix (first 5 rows):")
    for i in range(min(5, len(matrix1))):
        print(f"  M{i}: {matrix1[i, :].round(3)}")

    # SCC analysis
    print("\n[5] SCC analysis...")
    scc = scc_analysis(matrix1)
    print(f"Strongly Connected Components: {len(scc)}")
    for idx, comp in enumerate(scc):
        print(f"  SCC {idx}: {comp}")
    if len(scc) == 1:
        print("  -> Single SCC (entire graph)")

    # Thermodynamic quantities
    print("\n[6] Computing thermodynamic quantities...")
    n = len(matrix1)
    V = compute_potential(matrix1, target_state=5)
    print("  Potential V (expected steps to M5):")
    for i, v in enumerate(V):
        print(f"    M{i}: {v:.3f}")

    H = compute_entropy(matrix1)
    print("  Entropy H:")
    for i, h in enumerate(H):
        print(f"    M{i}: {h:.3f}")

    I = compute_mutual_information(matrix1)
    print(f"  Mutual Information I: {I:.3f} bits")

    # Second-order check
    print("\n[7] Second-order model check...")
    diff_sum, count = 0, 0
    for (i, j), transitions in matrix2.items():
        if i < n and j < n:
            for k, p in transitions.items():
                if k < n:
                    diff = abs(p - matrix1[j, k])
                    diff_sum += diff
                    count += 1
    if count > 0:
        avg_diff = diff_sum / count
        print(f"  Average diff: {avg_diff:.3f}")
        if avg_diff > 0.05:
            print("  -> Second-order model adds predictive power.")
        else:
            print("  -> First-order model is sufficient.")
    else:
        print("  No second-order data available.")

    # Visualize
    print("\n[8] Visualizing morphological landscape...")
    plot_landscape(V, H, list(range(n)))

    # Save matrix
    df = pd.DataFrame(matrix1)
    df.to_csv(get_data_path("causal_transition_matrix.csv"), index=False)
    print("  Saved matrix to causal_transition_matrix.csv")

    print("\n" + "=" * 80)
    print("EXPERIMENT COMPLETE")
    print("=" * 80)
    print(f"\n  Key insights:")
    print(f"    - SCCs: {len(scc)}")
    print(f"    - Mutual Information I = {I:.3f} bits")
    print(f"    - Second-order avg diff = {avg_diff if count > 0 else 0:.3f}")

if __name__ == "__main__":
    main()