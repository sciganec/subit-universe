"""
collatz_morphological_transition_v2.py — Collatz Morphological Transition System v1.0
Version 5.0 · 2026

Three layers:
1. Local morphotype of state (based on local window)
2. Local transition graph (Markov chain on local morphotypes)
3. Global morphotype of trajectory (for comparison)
"""

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

# ============================================================================
# 1. LOCAL SIGNATURE COMPUTATION
# ============================================================================

def local_signature(n, window=20, max_steps=5000):
    """
    Compute local signature for state n based on the next 'window' steps.
    Returns a feature vector describing the local dynamics.
    """
    # Generate forward trajectory
    traj = []
    current = n
    for _ in range(window):
        traj.append(current)
        if current == 1:
            break
        if current % 2 == 0:
            current //= 2
        else:
            current = 3 * current + 1
    if len(traj) < 2:
        return np.zeros(6)
    
    # Features
    # 1. Ratio of odd steps (U) to even steps (D)
    odd_count = sum(1 for x in traj[:-1] if x % 2 == 1)
    even_count = len(traj) - 1 - odd_count
    odd_ratio = odd_count / (len(traj) - 1) if len(traj) > 1 else 0
    
    # 2. Local growth rate (average change)
    changes = [traj[i+1] / traj[i] for i in range(len(traj)-1)]
    mean_growth = np.mean(changes)
    var_growth = np.var(changes) if len(changes) > 1 else 0
    
    # 3. Local entropy of U/D pattern
    pattern = ''.join('U' if x % 2 == 1 else 'D' for x in traj[:-1])
    if pattern:
        counts = Counter(pattern)
        total = sum(counts.values())
        entropy = -sum((c/total) * np.log2(c/total) for c in counts.values() if c > 0)
    else:
        entropy = 0
    
    # 4. Maximum local excursion (max / current)
    max_local = max(traj)
    excursion = max_local / n if n > 0 else 1
    
    # 5. Compression ratio (last / first)
    compression = traj[-1] / n if n > 0 else 1
    
    return np.array([odd_ratio, mean_growth, var_growth, entropy, excursion, compression])

# ============================================================================
# 2. BUILD LOCAL CLASSIFIER
# ============================================================================

def build_local_classifier(samples, window=20, n_clusters=7, max_steps=5000):
    """Build local morphotype classifier using K-means on local signatures."""
    print("Building local morphotype classifier...")
    signatures = []
    for n in tqdm(samples, desc="Computing local signatures"):
        sig = local_signature(n, window=window, max_steps=max_steps)
        if np.any(sig != 0):
            signatures.append(sig)
    signatures = np.array(signatures)
    
    # Normalize
    scaler = StandardScaler()
    X = scaler.fit_transform(signatures)
    
    # Cluster
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X)
    
    print(f"Built {n_clusters} local morphotypes.")
    return kmeans, scaler, labels

# ============================================================================
# 3. CLASSIFY LOCAL STATE
# ============================================================================

def classify_local(n, kmeans, scaler, window=20, max_steps=5000):
    """Classify a single state into a local morphotype."""
    sig = local_signature(n, window=window, max_steps=max_steps)
    if np.all(sig == 0):
        return -1
    X = scaler.transform([sig])
    return kmeans.predict(X)[0]

# ============================================================================
# 4. BUILD LOCAL TRANSITION MATRIX
# ============================================================================

def build_local_transition_matrix(samples, kmeans, scaler, window=20, max_steps=5000):
    """Build transition count matrix between local morphotypes."""
    trans_counts = defaultdict(lambda: defaultdict(int))
    n_clusters = len(kmeans.cluster_centers_)
    
    for n in tqdm(samples, desc="Building transitions"):
        # Generate full trajectory (up to max_steps)
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
        
        # Classify each state in trajectory
        morphs = []
        for val in traj:
            mt = classify_local(val, kmeans, scaler, window=window, max_steps=500)
            morphs.append(mt)
        
        # Count transitions
        for i in range(len(morphs)-1):
            if morphs[i] != -1 and morphs[i+1] != -1:
                trans_counts[morphs[i]][morphs[i+1]] += 1
    
    # Build matrix
    size = n_clusters
    matrix = np.zeros((size, size))
    for i in range(size):
        row_sum = sum(trans_counts[i].values())
        if row_sum > 0:
            for j in range(size):
                matrix[i, j] = trans_counts[i][j] / row_sum
    return matrix

# ============================================================================
# 5. GLOBAL MORPHOTYPE (for comparison)
# ============================================================================

def global_signature(n, max_steps=5000):
    """Compute global signature (full trajectory)."""
    traj = []
    current = n
    steps = 0
    while current != 1 and steps < max_steps:
        traj.append(current)
        if current % 2 == 0:
            current //= 2
        else:
            current = 3 * current + 1
        steps += 1
    if current == 1:
        traj.append(1)
    if not traj:
        return np.zeros(13)
    
    # Compute features (same as in atlas)
    length = len(traj)
    max_log = np.log10(max(traj) + 1)
    stopping_time = steps
    # Simple entropy of U/D
    pattern = ''.join('U' if x % 2 == 1 else 'D' for x in traj[:-1])
    if pattern:
        counts = Counter(pattern)
        total = sum(counts.values())
        entropy = -sum((c/total) * np.log2(c/total) for c in counts.values() if c > 0)
    else:
        entropy = 0
    compression = len(traj) / (max(traj) + 1) if max(traj) > 0 else 0
    peak_count = sum(1 for i in range(1, len(traj)) if traj[i] > max(traj[:i]))
    return_count = sum(1 for v in traj[1:] if v < traj[0])
    up_ratio = sum(1 for x in traj[:-1] if x % 2 == 1) / (len(traj)-1) if len(traj)>1 else 0
    return np.array([length, max_log, stopping_time, entropy, compression,
                     peak_count, return_count, 0, 0, 0, up_ratio, len(set(traj)), 0])

# ============================================================================
# 6. MAIN
# ============================================================================

def main():
    print("=" * 80)
    print("COLLATZ MORPHOLOGICAL TRANSITION SYSTEM v1.0")
    print("=" * 80)
    
    # Generate samples
    print("\n[1] Generating samples...")
    np.random.seed(42)
    samples = np.random.randint(1, 10**5, 2000)
    print(f"Generated {len(samples)} samples")
    
    # Build local classifier
    print("\n[2] Building local morphotype classifier...")
    kmeans, scaler, _ = build_local_classifier(samples, window=20, n_clusters=7)
    
    # Build transition matrix
    print("\n[3] Building local transition matrix...")
    matrix = build_local_transition_matrix(samples, kmeans, scaler, window=20, max_steps=3000)
    print("Transition matrix (first 5 rows):")
    for i in range(min(5, len(matrix))):
        print(f"  M{i}: {matrix[i, :].round(3)}")
    
    # Visualize graph
    print("\n[4] Visualizing local transition graph...")
    G = nx.DiGraph()
    threshold = 0.02
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            if matrix[i, j] > threshold:
                G.add_edge(f"M{i}", f"M{j}", weight=matrix[i, j])
    
    pos = nx.spring_layout(G, seed=42, k=2)
    plt.figure(figsize=(12, 8))
    nx.draw_networkx_nodes(G, pos, node_size=800, node_color='lightblue')
    nx.draw_networkx_labels(G, pos, font_size=14)
    edges = G.edges(data=True)
    widths = [d['weight']*5 for (u,v,d) in edges]
    nx.draw_networkx_edges(G, pos, edgelist=edges, width=widths, edge_color='gray', arrows=True, arrowsize=20)
    plt.title("Local Morphotype Transition Graph (probabilities ≥ 0.02)")
    plt.axis('off')
    plt.tight_layout()
    plt.savefig("local_transition_graph.png", dpi=150)
    plt.show()
    print("  Saved to local_transition_graph.png")
    
    # Compare with global morphotypes (optional)
    print("\n[5] Comparing local vs global morphotypes...")
    # Compute global signatures for a subset
    global_features = []
    for n in samples[:200]:
        sig = global_signature(n)
        if np.any(sig != 0):
            global_features.append(sig)
    if global_features:
        g_scaler = StandardScaler()
        Xg = g_scaler.fit_transform(global_features)
        g_kmeans = KMeans(n_clusters=7, random_state=42, n_init=10)
        global_labels = g_kmeans.fit_predict(Xg)
        print("  Global morphotypes assigned.")
        # Map local to global (just a simple comparison)
        print("  (Full comparison requires more samples and a proper mapping.)")
    
    print("\n" + "=" * 80)
    print("EXPERIMENT COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()