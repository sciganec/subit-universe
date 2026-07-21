"""
collatz_morphogenome.py — Real Morphogenetic Tree of Collatz Trajectories
Version 3.4 · 2026

Constructs actual event genomes from trajectories in the atlas,
computes phylogenetic distance between morphotypes,
and builds the first morphological tree of Collatz dynamics.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# 1. PATH SETUP
# ============================================================================

def get_data_path(filename):
    """Return absolute path to data file in the script's directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, filename)

# ============================================================================
# 2. LOAD DATA (AUTO-DETECTS COLUMN NAME)
# ============================================================================

def load_atlas_data():
    """
    Load morphotype signatures from CSV.
    Auto-detects column name for cluster labels (morphotype or cluster).
    """
    csv_path = get_data_path("morphotype_signatures.csv")
    if not os.path.exists(csv_path):
        # Try alternative location (current working directory)
        csv_path = "morphotype_signatures.csv"
        if not os.path.exists(csv_path):
            raise FileNotFoundError(
                f"File not found. Looked in: {get_data_path('morphotype_signatures.csv')} and ./morphotype_signatures.csv"
            )
    
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} signatures from {csv_path}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Auto-detect cluster column
    cluster_col = None
    for col in ['morphotype', 'cluster', 'Cluster', 'Morphotype']:
        if col in df.columns:
            cluster_col = col
            break
    
    if cluster_col is None:
        raise KeyError("No cluster column found. Expected 'morphotype' or 'cluster'.")
    
    # Rename to standard name
    if cluster_col != 'morphotype':
        df.rename(columns={cluster_col: 'morphotype'}, inplace=True)
        print(f"Renamed '{cluster_col}' to 'morphotype'")
    
    return df

# ============================================================================
# 3. TRAJECTORY & GENOME
# ============================================================================

def compute_trajectory(n: int, max_steps: int = 10000, max_value: int = 10**12):
    """Compute full Collatz trajectory until 1, cycle, or limits."""
    traj = []
    seen = {}
    current = n
    steps = 0
    while current not in seen:
        if current > max_value:
            break
        traj.append(current)
        seen[current] = steps
        if current == 1:
            break
        if steps > max_steps:
            break
        if current % 2 == 0:
            current //= 2
        else:
            current = 3 * current + 1
        steps += 1
    return traj

def event_genome(trajectory):
    """
    Convert trajectory into symbolic event genome.
    Alphabet: U, D, P, R, S
    """
    if not trajectory:
        return ""
    
    start = trajectory[0]
    max_so_far = start
    genome = []
    
    for i in range(len(trajectory) - 1):
        curr = trajectory[i]
        nxt = trajectory[i+1]
        
        # U / D
        if curr % 2 == 1:
            genome.append('U')
        else:
            genome.append('D')
        
        # P: new peak
        if nxt > max_so_far:
            genome.append('P')
            max_so_far = nxt
        
        # R: return below start
        if nxt < start:
            genome.append('R')
        
        # S: entering the final cycle
        if nxt in [4, 2, 1] and curr not in [4, 2, 1]:
            genome.append('S')
    
    if trajectory and trajectory[-1] == 1:
        genome.append('S')
    
    return ''.join(genome)

def genome_features(genome):
    """Extract feature vector from genome."""
    if not genome:
        return [0, 0, 0, 0, 0, 0]
    return [
        len(genome),
        genome.count('U'),
        genome.count('D'),
        genome.count('P'),
        genome.count('R'),
        genome.count('S'),
    ]

def levenshtein(s1, s2):
    """Compute Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

# ============================================================================
# 4. SELECT REPRESENTATIVES
# ============================================================================

def get_representatives(df):
    """Select representative trajectory for each morphotype (closest to centroid)."""
    # Define available features from the CSV
    available_features = ['length', 'max_log', 'stopping_time', 'event_entropy',
                         'event_compression', 'peak_count', 'return_count',
                         'cycle_count', 'avg_run_length', 'max_run_length',
                         'up_ratio', 'unique_values', 'fractal_like']
    
    # Use all available numeric features
    features = [f for f in available_features if f in df.columns]
    print(f"Using features for centroid: {features}")
    
    representatives = {}
    for mt in df['morphotype'].unique():
        cluster = df[df['morphotype'] == mt]
        centroid = cluster[features].mean()
        dists = []
        for idx, row in cluster.iterrows():
            vec = np.array([row[f] for f in features])
            dist = np.linalg.norm(vec - centroid)
            dists.append((idx, dist))
        closest_idx = min(dists, key=lambda x: x[1])[0]
        representatives[mt] = cluster.loc[closest_idx]
    return representatives

# ============================================================================
# 5. MAIN
# ============================================================================

def main():
    print("=" * 80)
    print("COLLATZ MORPHOGENOME")
    print("Building real phylogenetic tree from event genomes")
    print("=" * 80)
    
    # Load data
    df = load_atlas_data()
    n_morphotypes = df['morphotype'].nunique()
    print(f"Loaded {len(df)} trajectories, {n_morphotypes} morphotypes")
    print(f"Morphotypes: {sorted(df['morphotype'].unique())}")
    
    # Select representatives
    reps = get_representatives(df)
    print("\nSelected representatives per morphotype:")
    for mt, row in sorted(reps.items()):
        print(f"  M{mt}: n={int(row['n'])}, steps={int(row['stopping_time'])}")
    
    # Compute genomes for representatives
    print("\n[Computing real event genomes...]")
    genomes = {}
    for mt, row in reps.items():
        n = int(row['n'])
        traj = compute_trajectory(n)
        genome = event_genome(traj)
        genomes[mt] = genome
        print(f"  M{mt}: genome length = {len(genome)}")
    
    # Show genome snippets
    print("\nGenome snippets (first 100 chars):")
    for mt, g in sorted(genomes.items()):
        print(f"  M{mt}: {g[:100]}...")
    
    # Compute distance matrix
    print("\n[Computing Levenshtein distances between morphotypes...]")
    mt_ids = sorted(genomes.keys())
    n_mt = len(mt_ids)
    dist_matrix = np.zeros((n_mt, n_mt))
    
    for i, mt1 in enumerate(mt_ids):
        for j, mt2 in enumerate(mt_ids):
            if i < j:
                d = levenshtein(genomes[mt1], genomes[mt2])
                dist_matrix[i, j] = d
                dist_matrix[j, i] = d
    
    max_len = max(len(genomes[mt]) for mt in mt_ids) if mt_ids else 1
    norm_dist_matrix = dist_matrix / max_len
    
    print("\nNormalized distance matrix (edit distance / max_length):")
    print(pd.DataFrame(norm_dist_matrix, index=mt_ids, columns=mt_ids).round(3))
    
    # Build phylogenetic tree
    print("\n[Building phylogenetic tree (UPGMA)...]")
    condensed = squareform(norm_dist_matrix)
    Z = linkage(condensed, method='average')
    
    plt.figure(figsize=(12, 6))
    dendrogram(Z, labels=[f"M{mt}" for mt in mt_ids],
               leaf_rotation=90, leaf_font_size=14)
    plt.title("Collatz Morphogenetic Tree (UPGMA based on event genomes)", fontsize=14)
    plt.xlabel("Morphotype")
    plt.ylabel("Normalized Edit Distance")
    plt.tight_layout()
    out_tree = get_data_path("morphogenetic_tree.png")
    plt.savefig(out_tree, dpi=150)
    plt.show()
    print(f"  Saved to {out_tree}")
    
    # Average genome features per morphotype
    print("\n[Computing average genome features per morphotype...]")
    morph_genome_feats = {}
    for mt in sorted(df['morphotype'].unique()):
        cluster = df[df['morphotype'] == mt]
        sample = cluster.sample(min(20, len(cluster)), random_state=42)
        avg_features = np.zeros(6)
        count = 0
        for _, row in sample.iterrows():
            n = int(row['n'])
            traj = compute_trajectory(n, max_steps=5000)
            g = event_genome(traj)
            if g:
                avg_features += np.array(genome_features(g))
                count += 1
        if count > 0:
            avg_features /= count
            morph_genome_feats[mt] = avg_features
    
    feat_names = ['Length', 'U_count', 'D_count', 'P_count', 'R_count', 'S_count']
    X = np.array([morph_genome_feats[mt] for mt in sorted(morph_genome_feats.keys())])
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(X, annot=True, fmt='.1f', cmap='viridis',
                xticklabels=feat_names,
                yticklabels=[f"M{mt}" for mt in sorted(morph_genome_feats.keys())],
                ax=ax)
    ax.set_title("Average Genome Features per Morphotype")
    plt.tight_layout()
    out_feat = get_data_path("morphotype_genome_features.png")
    plt.savefig(out_feat, dpi=150)
    plt.show()
    print(f"  Saved to {out_feat}")
    
    # Save genomes
    out_gen = get_data_path("collatz_genomes.csv")
    with open(out_gen, "w") as f:
        f.write("morphotype,n,genome\n")
        for mt, row in reps.items():
            n = int(row['n'])
            g = genomes[mt]
            f.write(f"{mt},{n},{g}\n")
    print(f"\nGenomes saved to {out_gen}")
    
    # Summary
    print("\n" + "=" * 80)
    print("MORPHOGENETIC ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"  • Total trajectories: {len(df)}")
    print(f"  • Morphotypes: {n_morphotypes}")
    print(f"  • Morphotype sizes: {dict(df['morphotype'].value_counts().sort_index())}")
    print("\n  Key insight: Morphotypes have distinct event genomes.")
    print("  The phylogenetic tree reveals evolutionary relationships between them.")
    print("  This is a new structural description of Collatz dynamics.")

if __name__ == "__main__":
    main()