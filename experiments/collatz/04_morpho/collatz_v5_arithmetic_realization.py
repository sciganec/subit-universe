"""
collatz_v5_arithmetic_realization.py — Collatz Morphological Automaton v5.0
Arithmetic Realization of Morphological States

Fixed: type conversion for numpy.int32 in arithmetic features.
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
# 1. CAUSAL SIGNATURE (top-level)
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

# ============================================================================
# 2. LOAD CLASSIFIER
# ============================================================================

def load_classifier():
    """Load the causal classifier from v4.0 or retrain."""
    try:
        import joblib
        kmeans = joblib.load(get_data_path("causal_kmeans.pkl"))
        scaler = joblib.load(get_data_path("causal_scaler.pkl"))
        print("Loaded saved classifier.")
        return kmeans, scaler
    except:
        print("No saved classifier found. Retraining...")
        return train_classifier()

def train_classifier(n_samples=10000, n_clusters=7):
    """Retrain the causal classifier."""
    print("Generating training samples...")
    np.random.seed(42)
    samples = np.random.randint(1, 10**6, n_samples)
    signatures = []
    for n in tqdm(samples, desc="Computing signatures"):
        sig = causal_signature(n)
        if np.any(sig != 0):
            signatures.append(sig)
    signatures = np.array(signatures)
    scaler = StandardScaler()
    X = scaler.fit_transform(signatures)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(X)
    try:
        import joblib
        joblib.dump(kmeans, get_data_path("causal_kmeans.pkl"))
        joblib.dump(scaler, get_data_path("causal_scaler.pkl"))
    except:
        pass
    return kmeans, scaler

# ============================================================================
# 3. CLASSIFY
# ============================================================================

def classify_causal(n, kmeans, scaler, centroids):
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
# 4. CLASSIFY AND COLLECT
# ============================================================================

def classify_and_collect(samples, kmeans, scaler, max_steps=3000):
    centroids = kmeans.cluster_centers_
    # Macro-state mapping from v4.0 (pair -> macro)
    macro_map = {
        (1,1): 0, (1,4): 0, (4,4): 0, (4,1): 0, (0,4): 0, (5,1): 0,
        (4,0): 1, (0,0): 1, (3,0): 1, (6,0): 1,
        (1,5): 2, (5,5): 2,
        (0,3): 3, (3,3): 3, (3,6): 3, (6,6): 3, (6,3): 3,
        (6,2): 3, (2,6): 3, (2,2): 3, (0,6): 3,
        (0,5): 4
    }
    
    results = []
    for n in tqdm(samples, desc="Classifying trajectories"):
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
        morphs = [classify_causal(val, kmeans, scaler, centroids) for val in traj]
        if any(m == -1 for m in morphs):
            continue
        macro_seq = []
        for i in range(len(morphs) - 1):
            pair = (morphs[i], morphs[i+1])
            macro = macro_map.get(pair, -1)
            macro_seq.append(macro)
        if not macro_seq:
            continue
        record = {
            'n': int(n),  # ensure Python int
            'stopping_time': len(traj),
            'max_value': max(traj) if traj else 1,
            'macro_sequence': macro_seq,
            'macro_first': macro_seq[0] if macro_seq else -1,
            'macro_last': macro_seq[-1] if macro_seq else -1,
            'morph_sequence': morphs,
        }
        results.append(record)
    return results

# ============================================================================
# 5. ARITHMETIC ANALYSIS
# ============================================================================

def compute_arithmetic_features(n):
    # Ensure n is a Python int
    n = int(n)
    features = {}
    features['n'] = n
    features['log2'] = np.log2(n + 1)
    features['v2'] = (n & -n).bit_length() - 1 if n > 0 else 0
    features['v3'] = 0
    tmp = n
    while tmp % 3 == 0 and tmp > 0:
        features['v3'] += 1
        tmp //= 3
    features['mod2'] = n % 2
    features['mod3'] = n % 3
    features['mod4'] = n % 4
    features['mod5'] = n % 5
    features['mod7'] = n % 7
    features['mod8'] = n % 8
    features['mod16'] = n % 16
    features['bit_length'] = n.bit_length()
    features['popcount'] = bin(n).count('1')
    features['trailing_ones'] = 0
    tmp = n
    while tmp & 1 and tmp > 0:
        features['trailing_ones'] += 1
        tmp >>= 1
    features['trailing_zeros'] = features['v2']
    return features

def analyze_arithmetic_patterns(results):
    groups = defaultdict(list)
    for rec in results:
        macro = rec['macro_first']
        if macro >= 0:
            groups[macro].append(rec)
    
    print("\n" + "=" * 80)
    print("ARITHMETIC PATTERNS BY MACRO-STATE")
    print("=" * 80)
    
    for macro, recs in sorted(groups.items()):
        print(f"\n  Macro-state S{macro}: {len(recs)} trajectories")
        sample_n = [r['n'] for r in recs[:20]]
        print(f"    Sample numbers: {sample_n[:10]}...")
        features = ['v2', 'v3', 'mod2', 'mod3', 'mod4', 'mod5', 'mod7', 'mod8', 'mod16', 'popcount', 'bit_length']
        stats = {}
        for feat in features:
            vals = [compute_arithmetic_features(r['n'])[feat] for r in recs]
            stats[feat] = {
                'mean': np.mean(vals),
                'std': np.std(vals),
                'min': np.min(vals),
                'max': np.max(vals),
                'mode': Counter(vals).most_common(1)[0][0] if vals else None
            }
        print(f"    Statistics:")
        for feat, stat in stats.items():
            print(f"      {feat}: mean={stat['mean']:.2f}, mode={stat['mode']}, range=[{stat['min']}, {stat['max']}]")
        mod8_counts = Counter([r['n'] % 8 for r in recs])
        print(f"    mod8 distribution: {dict(mod8_counts)}")
        mod16_counts = Counter([r['n'] % 16 for r in recs])
        print(f"    mod16 distribution: {dict(mod16_counts)}")
    
    return groups

# ============================================================================
# 6. VISUALIZATION
# ============================================================================

def plot_arithmetic_distributions(groups, save_path='macro_arithmetic.png'):
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    features = ['v2', 'mod4', 'mod8', 'mod16', 'popcount', 'bit_length']
    for idx, feat in enumerate(features):
        ax = axes[idx]
        for macro, recs in groups.items():
            vals = [compute_arithmetic_features(r['n'])[feat] for r in recs]
            if vals:
                ax.hist(vals, bins=20, alpha=0.5, label=f'S{macro}')
        ax.set_title(f'{feat} distribution')
        ax.legend()
    plt.tight_layout()
    plt.savefig(get_data_path(save_path), dpi=150)
    plt.show()
    print(f"  Saved to {save_path}")

def plot_macro_transition_matrix(groups, save_path='macro_transition_matrix.png'):
    size = 5
    matrix = np.zeros((size, size))
    for rec in groups.values():
        for r in rec:
            seq = r['macro_sequence']
            for i in range(len(seq)-1):
                if seq[i] >= 0 and seq[i+1] >= 0:
                    matrix[seq[i], seq[i+1]] += 1
    for i in range(size):
        row_sum = matrix[i].sum()
        if row_sum > 0:
            matrix[i] /= row_sum
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(matrix, cmap='Blues', vmin=0, vmax=1)
    ax.set_xticks(range(size))
    ax.set_yticks(range(size))
    ax.set_xticklabels([f'S{i}' for i in range(size)])
    ax.set_yticklabels([f'S{i}' for i in range(size)])
    for i in range(size):
        for j in range(size):
            if matrix[i, j] > 0.01:
                ax.text(j, i, f'{matrix[i, j]:.2f}', ha='center', va='center', fontsize=8)
    ax.set_title('Macro-State Transition Matrix (from arithmetic data)')
    plt.tight_layout()
    plt.savefig(get_data_path(save_path), dpi=150)
    plt.show()
    print(f"  Saved to {save_path}")

# ============================================================================
# 7. MAIN
# ============================================================================

def main():
    print("=" * 80)
    print("COLLATZ MORPHOLOGICAL AUTOMATON v5.0")
    print("Arithmetic Realization of Morphological States")
    print("=" * 80)
    
    print("\n[1] Loading classifier...")
    kmeans, scaler = load_classifier()
    
    print("\n[2] Generating test samples...")
    np.random.seed(42)
    test_samples = np.random.randint(1, 10**6, 5000)
    print(f"Generated {len(test_samples)} test samples")
    
    print("\n[3] Classifying trajectories and extracting macro-states...")
    results = classify_and_collect(test_samples, kmeans, scaler, max_steps=3000)
    print(f"Collected {len(results)} trajectories")
    
    print("\n[4] Analyzing arithmetic patterns...")
    groups = analyze_arithmetic_patterns(results)
    
    print("\n[5] Visualizing distributions...")
    plot_arithmetic_distributions(groups)
    plot_macro_transition_matrix(groups)
    
    df = pd.DataFrame([{
        'n': r['n'],
        'macro_first': r['macro_first'],
        'macro_last': r['macro_last'],
        'stopping_time': r['stopping_time'],
        'max_value': r['max_value'],
        'macro_sequence': str(r['macro_sequence'])[:100]
    } for r in results])
    df.to_csv(get_data_path("macro_arithmetic_data.csv"), index=False)
    print("  Saved data to macro_arithmetic_data.csv")
    
    print("\n" + "=" * 80)
    print("EXPERIMENT COMPLETE")
    print("=" * 80)
    print("\n  Key insights will emerge from the arithmetic distributions.")
    print("  Look for simple modular rules that predict macro-state membership.")

if __name__ == "__main__":
    main()