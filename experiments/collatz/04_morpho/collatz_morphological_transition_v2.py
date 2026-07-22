"""
collatz_morphological_transition_v2.py — Collatz Morphological Transition System v2.0
Version 5.1 · 2026

Extensions:
1. SCC decomposition
2. Mean first passage time
3. Dwell time distributions
4. Causal classifier (no leakage)
5. Basin map
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
# 1. LOCAL SIGNATURE (Causal version — no future leakage)
# ============================================================================

def causal_local_signature(n, history_window=20):
    """
    Compute local signature using ONLY past information.
    For the current state n, we look at the history of the trajectory
    up to the current point (not future).
    Since we process trajectories step by step, we maintain a buffer.
    This function is called with the current n and the history buffer.
    """
    # We need to know the history. Since this is a state function,
    # we'll compute it on the fly in the trajectory processing.
    # For now, we use a simplified version: features based on current n
    # and the last few steps (which we can pass as a buffer).
    # In the full implementation, we pass a deque of last 20 values.
    # Here we implement a placeholder: use the same as before but without
    # looking ahead. We'll compute it in the trajectory loop.
    pass

# ============================================================================
# 2. TRAJECTORY PROCESSING WITH BUFFER
# ============================================================================

def compute_causal_signature(buffer):
    """
    Compute signature from a buffer of last K steps (K = window).
    buffer: list of last K values (most recent last)
    """
    if len(buffer) < 2:
        return np.zeros(6)
    
    # Features based only on past values
    # 1. Ratio of odd steps in the buffer (excluding current)
    past = buffer[:-1]
    if not past:
        return np.zeros(6)
    odd_count = sum(1 for x in past if x % 2 == 1)
    odd_ratio = odd_count / len(past)
    
    # 2. Growth rate from the buffer
    changes = [past[i+1] / past[i] for i in range(len(past)-1)] if len(past) > 1 else [1.0]
    mean_growth = np.mean(changes)
    var_growth = np.var(changes) if len(changes) > 1 else 0
    
    # 3. Pattern entropy (U/D) of the buffer
    pattern = ''.join('U' if x % 2 == 1 else 'D' for x in past)
    if pattern:
        counts = Counter(pattern)
        total = sum(counts.values())
        entropy = -sum((c/total) * np.log2(c/total) for c in counts.values() if c > 0)
    else:
        entropy = 0
    
    # 4. Current relative to buffer start
    current = buffer[-1]
    start = buffer[0] if buffer else current
    compression = current / start if start > 0 else 1
    
    # 5. Local trend (last value vs previous)
    if len(buffer) >= 2:
        trend = buffer[-1] / buffer[-2] if buffer[-2] > 0 else 1
    else:
        trend = 1
    
    return np.array([odd_ratio, mean_growth, var_growth, entropy, compression, trend])

# ============================================================================
# 3. BUILD CAUSAL CLASSIFIER
# ============================================================================

def build_causal_classifier(samples, window=20, n_clusters=7, max_steps=5000):
    """Build classifier using only causal (past) information."""
    print("Building causal local morphotype classifier...")
    signatures = []
    
    for n in tqdm(samples, desc="Computing causal signatures"):
        # Generate trajectory
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
        
        if len(traj) < window + 1:
            continue
        
        # For each position, compute signature from past window
        for i in range(window, len(traj)):
            buffer = traj[i-window:i+1]  # last window + current
            sig = compute_causal_signature(buffer)
            if np.any(sig != 0):
                signatures.append(sig)
    
    if not signatures:
        print("No signatures computed.")
        return None, None, None
    
    signatures = np.array(signatures)
    scaler = StandardScaler()
    X = scaler.fit_transform(signatures)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X)
    
    print(f"Built {n_clusters} causal morphotypes.")
    return kmeans, scaler, labels

# ============================================================================
# 4. TRANSITION MATRIX WITH CAUSAL CLASSIFIER
# ============================================================================

def build_causal_transition_matrix(samples, kmeans, scaler, window=20, max_steps=5000):
    """Build transition matrix using causal classifier."""
    trans_counts = defaultdict(lambda: defaultdict(int))
    n_clusters = len(kmeans.cluster_centers_)
    
    for n in tqdm(samples, desc="Building causal transitions"):
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
        
        if len(traj) < window + 1:
            continue
        
        # Classify each state (using causal signature)
        morphs = []
        for i in range(window, len(traj)):
            buffer = traj[i-window:i+1]
            sig = compute_causal_signature(buffer)
            if np.all(sig == 0):
                morphs.append(-1)
            else:
                X = scaler.transform([sig])
                morphs.append(kmeans.predict(X)[0])
        
        # Count transitions (i is index in morphs, corresponding to position window+i in traj)
        for i in range(len(morphs)-1):
            if morphs[i] != -1 and morphs[i+1] != -1:
                trans_counts[morphs[i]][morphs[i+1]] += 1
    
    matrix = np.zeros((n_clusters, n_clusters))
    for i in range(n_clusters):
        row_sum = sum(trans_counts[i].values())
        if row_sum > 0:
            for j in range(n_clusters):
                matrix[i, j] = trans_counts[i][j] / row_sum
    return matrix

# ============================================================================
# 5. SCC DECOMPOSITION
# ============================================================================

def scc_analysis(matrix):
    """Analyze strongly connected components."""
    n = len(matrix)
    G = nx.DiGraph()
    threshold = 0.01
    for i in range(n):
        for j in range(n):
            if matrix[i, j] > threshold:
                G.add_edge(i, j)
    
    scc = list(nx.strongly_connected_components(G))
    print("\nStrongly Connected Components:")
    for idx, comp in enumerate(scc):
        print(f"  SCC {idx}: {comp}")
    
    # Identify transient vs recurrent
    if len(scc) > 1:
        # Find the largest SCC (likely recurrent)
        sizes = [len(c) for c in scc]
        max_idx = np.argmax(sizes)
        recurrent = scc[max_idx]
        transient = [c for i, c in enumerate(scc) if i != max_idx]
        print(f"\nRecurrent core: {recurrent}")
        print(f"Transient components: {transient}")
    else:
        recurrent = scc[0]
        transient = []
        print(f"\nSingle SCC (entire graph): {recurrent}")
    return scc, recurrent, transient

# ============================================================================
# 6. MEAN FIRST PASSAGE TIME
# ============================================================================

def mean_first_passage_time(matrix, target_state):
    """
    Compute mean first passage time from each state to target.
    Solves (I - Q)^{-1} * 1 for transient states.
    """
    n = len(matrix)
    # Identify transient states (those that can reach target but not vice versa)
    # For simplicity, we compute for all states.
    # We'll use a numerical approach: solve the linear system.
    # For transient states, we compute the expected time.
    
    # Build Q (transient submatrix) and identify transient states.
    # For simplicity, we assume all states except target are transient.
    # This is a rough approximation; a proper SCC analysis is needed first.
    transient_states = [i for i in range(n) if i != target_state]
    if not transient_states:
        print("No transient states (already in target).")
        return {}
    
    # Build Q matrix (transitions among transient states)
    Q = matrix[np.ix_(transient_states, transient_states)]
    I = np.eye(len(transient_states))
    # Solve (I - Q) * t = 1
    try:
        t = np.linalg.solve(I - Q, np.ones(len(transient_states)))
        mfpt = {transient_states[i]: t[i] for i in range(len(transient_states))}
        return mfpt
    except np.linalg.LinAlgError:
        print("Could not solve MFPT (matrix singular).")
        return {}

# ============================================================================
# 7. DWELL TIME DISTRIBUTION
# ============================================================================

def dwell_time_analysis(samples, kmeans, scaler, window=20, max_steps=5000):
    """Compute dwell time distributions for each morphotype."""
    dwell_counts = defaultdict(list)
    
    for n in tqdm(samples, desc="Computing dwell times"):
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
        
        if len(traj) < window + 1:
            continue
        
        # Classify states
        morphs = []
        for i in range(window, len(traj)):
            buffer = traj[i-window:i+1]
            sig = compute_causal_signature(buffer)
            if np.all(sig == 0):
                morphs.append(-1)
            else:
                X = scaler.transform([sig])
                morphs.append(kmeans.predict(X)[0])
        
        # Compute dwell times
        if not morphs:
            continue
        current_mt = morphs[0]
        dwell = 0
        for mt in morphs:
            if mt == current_mt:
                dwell += 1
            else:
                dwell_counts[current_mt].append(dwell)
                current_mt = mt
                dwell = 1
        dwell_counts[current_mt].append(dwell)
    
    # Compute statistics
    dwell_stats = {}
    for mt, times in dwell_counts.items():
        if times:
            dwell_stats[mt] = {
                'mean': np.mean(times),
                'median': np.median(times),
                'std': np.std(times),
                'max': np.max(times),
                'count': len(times)
            }
    return dwell_stats

# ============================================================================
# 8. BASIN MAP
# ============================================================================

def basin_map(samples, kmeans, scaler, window=20, max_steps=5000, target_state=2):
    """
    For each starting number, determine the final basin (morphotype reached most often
    in the last phase, or the absorbing state if applicable).
    """
    basins = defaultdict(list)
    
    for n in tqdm(samples, desc="Computing basins"):
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
        
        if len(traj) < window + 1:
            continue
        
        # Classify states
        morphs = []
        for i in range(window, len(traj)):
            buffer = traj[i-window:i+1]
            sig = compute_causal_signature(buffer)
            if np.all(sig == 0):
                morphs.append(-1)
            else:
                X = scaler.transform([sig])
                morphs.append(kmeans.predict(X)[0])
        
        # Determine basin: if any state reaches target, it's target
        # Otherwise, take the most frequent state in the second half
        if not morphs:
            continue
        if target_state in morphs:
            basin = target_state
        else:
            # Last phase: last 50% of trajectory
            half = len(morphs) // 2
            if half > 0:
                last_phase = morphs[half:]
                if last_phase:
                    basin = Counter(last_phase).most_common(1)[0][0]
                else:
                    basin = morphs[-1]
            else:
                basin = morphs[-1]
        basins[basin].append(n)
    
    # Compute basin sizes
    basin_sizes = {mt: len(basin) for mt, basin in basins.items()}
    return basin_sizes, basins

# ============================================================================
# 9. MAIN
# ============================================================================

def main():
    print("=" * 80)
    print("COLLATZ MORPHOLOGICAL TRANSITION SYSTEM v2.0")
    print("=" * 80)
    
    # Generate samples
    print("\n[1] Generating samples...")
    np.random.seed(42)
    samples = np.random.randint(1, 10**5, 2000)
    print(f"Generated {len(samples)} samples")
    
    # Build causal classifier
    print("\n[2] Building causal local morphotype classifier...")
    kmeans, scaler, _ = build_causal_classifier(samples, window=20, n_clusters=7)
    if kmeans is None:
        print("Classifier building failed. Exiting.")
        return
    
    # Build transition matrix
    print("\n[3] Building causal transition matrix...")
    matrix = build_causal_transition_matrix(samples, kmeans, scaler, window=20, max_steps=3000)
    print("Transition matrix (first 5 rows):")
    for i in range(min(5, len(matrix))):
        print(f"  M{i}: {matrix[i, :].round(3)}")
    
    # SCC analysis
    print("\n[4] SCC analysis...")
    scc, recurrent, transient = scc_analysis(matrix)
    
    # Mean first passage time
    print("\n[5] Mean first passage time to M2...")
    mfpt = mean_first_passage_time(matrix, target_state=2)
    if mfpt:
        print("  Mean first passage times to M2:")
        for state, time in sorted(mfpt.items()):
            print(f"    M{state} → M2: {time:.3f}")
    
    # Dwell time analysis
    print("\n[6] Dwell time analysis...")
    dwell_stats = dwell_time_analysis(samples, kmeans, scaler, window=20, max_steps=3000)
    print("  Dwell time statistics:")
    for mt, stats in sorted(dwell_stats.items()):
        print(f"    M{mt}: mean={stats['mean']:.2f}, median={stats['median']:.2f}, max={stats['max']:.0f}")
    
    # Basin map
    print("\n[7] Basin map (target M2)...")
    basin_sizes, basins = basin_map(samples, kmeans, scaler, window=20, max_steps=3000, target_state=2)
    print("  Basin sizes (numbers ending in each morphotype):")
    for mt, size in sorted(basin_sizes.items()):
        print(f"    M{mt}: {size} ({size/len(samples)*100:.1f}%)")
    
    print("\n" + "=" * 80)
    print("EXPERIMENT COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()