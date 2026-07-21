"""
collatz_morphodynamics.py — Morphodynamic Atlas of Collatz Trajectories
Version 3.0 · 2026

Instead of searching for counterexamples, this module explores the geometry
of the Collatz trajectory space using signature vectors Φ(n), dimensionality
reduction, clustering, and anomaly detection.

Core philosophy:
  > "Does the space of Collatz trajectories have a low-dimensional
  > morphodynamic structure that can be revealed through signatures Φ
  > and the atlas Ψ?"

Dependencies:
  pip install numpy scipy scikit-learn matplotlib seaborn umap-learn
"""

import numpy as np
from typing import List, Tuple, Dict, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict
import random
import time
import sys
import warnings
warnings.filterwarnings('ignore')

# ---------------------------------------------------------------------
# 1. CORE: Collatz Trajectory Engine
# ---------------------------------------------------------------------

class CollatzTrajectory:
    """Computes and stores a single Collatz trajectory."""
    
    def __init__(self, n: int, max_steps: int = 10000, max_value: int = 10**12):
        self.n = n
        self.max_steps = max_steps
        self.max_value = max_value
        self.trajectory: List[int] = []
        self.steps = 0
        self.max_reached = 0
        self.reached_1 = False
        self.cycle_detected = False
        self.cycle_start = -1
        self.cycle_length = 0
        self.odd_steps = 0
        self.even_steps = 0
        self.up_steps = 0   # odd steps (3n+1)
        self.down_steps = 0 # even steps (n/2)
        self._compute()
    
    def _compute(self):
        """Run trajectory until 1, cycle, or limits."""
        seen: Dict[int, int] = {}
        current = self.n
        step = 0
        
        while True:
            if current in seen:
                self.cycle_detected = True
                self.cycle_start = seen[current]
                self.cycle_length = step - seen[current]
                break
            
            if current > self.max_value:
                break  # avoid unbounded growth
            
            self.trajectory.append(current)
            seen[current] = step
            
            if current > self.max_reached:
                self.max_reached = current
            
            if current == 1:
                self.reached_1 = True
                break
            
            if step >= self.max_steps:
                break
            
            if current % 2 == 0:
                current //= 2
                self.even_steps += 1
                self.down_steps += 1
            else:
                current = 3 * current + 1
                self.odd_steps += 1
                self.up_steps += 1
            
            step += 1
        
        self.steps = step
    
    def is_interesting(self) -> bool:
        """Flag trajectories that are unusual (long, high, or cyclic)."""
        return (self.steps > 500 or 
                self.max_reached > 10**6 or 
                self.cycle_detected)
    
    def __len__(self):
        return len(self.trajectory)


# ---------------------------------------------------------------------
# 2. SIGNATURE Φ(n) — Morphodynamic Fingerprint
# ---------------------------------------------------------------------

@dataclass
class CollatzSignature:
    """Φ(n) = (stopping_time, max_excursion, entropy, ...)"""
    n: int
    stopping_time: float       # steps to reach 1
    max_excursion_log: float   # log10(max value)
    odd_even_ratio: float      # odd/even steps
    entropy: float             # entropy of the parity sequence
    compression_ratio: float   # stopping_time / log2(n)
    excursion_normalized: float # max_reached / n
    up_down_ratio: float       # up_steps / down_steps
    variance_log: float        # log variance of trajectory values
    peak_late: float           # when the max occurs (step / total_steps)
    omega: str                 # STABLE | CYCLIC | CHAOTIC
    has_cycle: bool
    cycle_length: int
    steps: int
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array for clustering."""
        return np.array([
            self.stopping_time,
            self.max_excursion_log,
            self.odd_even_ratio,
            self.entropy,
            self.compression_ratio,
            self.excursion_normalized,
            self.up_down_ratio,
            self.variance_log,
            self.peak_late,
        ])
    
    @classmethod
    def from_trajectory(cls, traj: CollatzTrajectory) -> 'CollatzSignature':
        """Build signature from a computed trajectory."""
        n = traj.n
        steps = traj.steps
        max_val = traj.max_reached
        odd = traj.odd_steps
        even = traj.even_steps
        total = odd + even
        
        # Compute parity entropy
        parities = [1 if x % 2 == 1 else 0 for x in traj.trajectory]
        if parities:
            p1 = sum(parities) / len(parities)
            p0 = 1 - p1
            entropy = 0.0
            if p1 > 0 and p1 < 1:
                entropy = -(p1 * np.log2(p1) + p0 * np.log2(p0))
            else:
                entropy = 0.0
        else:
            entropy = 0.0
        
        # Compression ratio: steps / log2(n)
        log2n = np.log2(n) if n > 1 else 1.0
        compression = steps / log2n if log2n > 0 else 0.0
        
        # Normalized excursion
        exc_norm = max_val / n if n > 0 else 0.0
        
        # Up/down ratio
        up_down = traj.up_steps / (traj.down_steps + 1)
        
        # Variance (log)
        vals = traj.trajectory
        if vals:
            log_vals = np.log10([v for v in vals if v > 0] + [1])
            variance_log = np.var(log_vals) if len(log_vals) > 1 else 0.0
        else:
            variance_log = 0.0
        
        # Peak late: when does the max occur?
        if vals:
            max_idx = np.argmax(vals)
            peak_late = max_idx / len(vals) if len(vals) > 0 else 0.0
        else:
            peak_late = 0.0
        
        # Omega class
        if traj.reached_1:
            omega = "STABLE"
        elif traj.cycle_detected:
            omega = "CYCLIC"
        else:
            omega = "CHAOTIC"
        
        return cls(
            n=n,
            stopping_time=float(steps),
            max_excursion_log=np.log10(max_val + 1),
            odd_even_ratio=odd / (even + 1),
            entropy=entropy,
            compression_ratio=compression,
            excursion_normalized=exc_norm,
            up_down_ratio=up_down,
            variance_log=variance_log,
            peak_late=peak_late,
            omega=omega,
            has_cycle=traj.cycle_detected,
            cycle_length=traj.cycle_length,
            steps=steps,
        )


# ---------------------------------------------------------------------
# 3. ATLAS BUILDER — The Landscape Ψ(ℛ)
# ---------------------------------------------------------------------

class CollatzAtlas:
    """
    Builds the morphodynamic atlas of Collatz trajectories.
    Ψ(ℛ) = (signatures, clusters, anomalies, phase transitions)
    """
    
    def __init__(self, max_steps: int = 5000, max_value: int = 10**12):
        self.max_steps = max_steps
        self.max_value = max_value
        self.signatures: List[CollatzSignature] = []
        self.data_matrix: Optional[np.ndarray] = None
        self.cluster_labels: Optional[np.ndarray] = None
        self.outlier_scores: Optional[np.ndarray] = None
        self.projection: Optional[np.ndarray] = None
    
    def add_numbers(self, numbers: List[int], progress: bool = True) -> int:
        """Add trajectories for a list of starting numbers."""
        added = 0
        for i, n in enumerate(numbers):
            if progress and i % 1000 == 0:
                print(f"  Processing {i}/{len(numbers)}...")
            traj = CollatzTrajectory(n, self.max_steps, self.max_value)
            sig = CollatzSignature.from_trajectory(traj)
            self.signatures.append(sig)
            added += 1
        return added
    
    def build_matrix(self) -> np.ndarray:
        """Convert all signatures to a numpy matrix."""
        self.data_matrix = np.array([sig.to_array() for sig in self.signatures])
        return self.data_matrix
    
    def normalize(self) -> np.ndarray:
        """Z-score normalize the data matrix."""
        if self.data_matrix is None:
            self.build_matrix()
        mean = np.mean(self.data_matrix, axis=0)
        std = np.std(self.data_matrix, axis=0)
        std[std == 0] = 1.0
        self.data_matrix = (self.data_matrix - mean) / std
        return self.data_matrix
    
    def project_pca(self, n_components: int = 3) -> np.ndarray:
        """Project to 2D/3D using PCA."""
        from sklearn.decomposition import PCA
        if self.data_matrix is None:
            self.build_matrix()
        pca = PCA(n_components=n_components)
        self.projection = pca.fit_transform(self.data_matrix)
        print(f"  PCA explained variance: {pca.explained_variance_ratio_.sum():.3f}")
        return self.projection
    
    def project_umap(self, n_components: int = 2) -> np.ndarray:
        """Project to 2D using UMAP (if available)."""
        try:
            import umap
            if self.data_matrix is None:
                self.build_matrix()
            reducer = umap.UMAP(n_components=n_components, random_state=42)
            self.projection = reducer.fit_transform(self.data_matrix)
            return self.projection
        except ImportError:
            print("  UMAP not installed. Falling back to PCA.")
            return self.project_pca(n_components)
    
    def cluster_kmeans(self, n_clusters: int = 5) -> np.ndarray:
        """Cluster signatures using KMeans."""
        from sklearn.cluster import KMeans
        if self.data_matrix is None:
            self.build_matrix()
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.cluster_labels = kmeans.fit_predict(self.data_matrix)
        return self.cluster_labels
    
    def cluster_dbscan(self, eps: float = 0.5, min_samples: int = 10) -> np.ndarray:
        """Cluster signatures using DBSCAN."""
        from sklearn.cluster import DBSCAN
        if self.data_matrix is None:
            self.build_matrix()
        db = DBSCAN(eps=eps, min_samples=min_samples)
        self.cluster_labels = db.fit_predict(self.data_matrix)
        return self.cluster_labels
    
    def detect_outliers(self, contamination: float = 0.05) -> np.ndarray:
        """Detect outliers using Isolation Forest."""
        from sklearn.ensemble import IsolationForest
        if self.data_matrix is None:
            self.build_matrix()
        iso = IsolationForest(contamination=contamination, random_state=42)
        preds = iso.fit_predict(self.data_matrix)
        self.outlier_scores = preds
        # -1 = outlier, 1 = inlier
        return preds
    
    def get_summary(self) -> Dict:
        """Return statistics about the atlas."""
        if not self.signatures:
            return {}
        
        n = len(self.signatures)
        stopping_times = [s.stopping_time for s in self.signatures]
        max_vals = [s.max_excursion_log for s in self.signatures]
        entropies = [s.entropy for s in self.signatures]
        
        stable = sum(1 for s in self.signatures if s.omega == "STABLE")
        cyclic = sum(1 for s in self.signatures if s.omega == "CYCLIC")
        chaotic = sum(1 for s in self.signatures if s.omega == "CHAOTIC")
        
        return {
            "total": n,
            "stable": stable,
            "cyclic": cyclic,
            "chaotic": chaotic,
            "avg_stopping_time": np.mean(stopping_times),
            "max_stopping_time": np.max(stopping_times),
            "avg_max_excursion": np.mean(max_vals),
            "avg_entropy": np.mean(entropies),
            "cluster_count": len(set(self.cluster_labels)) if self.cluster_labels is not None else 0,
            "outlier_count": np.sum(self.outlier_scores == -1) if self.outlier_scores is not None else 0,
        }


# ---------------------------------------------------------------------
# 4. VISUALIZATION
# ---------------------------------------------------------------------

def plot_atlas(atlas: CollatzAtlas, title: str = "Collatz Morphodynamic Atlas"):
    """Create a visualization of the atlas."""
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        sns.set_style("darkgrid")
        
        if atlas.projection is None:
            print("No projection found. Run project_pca() or project_umap() first.")
            return
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Plot 1: Colored by cluster
        if atlas.cluster_labels is not None:
            scatter1 = axes[0].scatter(
                atlas.projection[:, 0], atlas.projection[:, 1],
                c=atlas.cluster_labels, cmap='tab10', alpha=0.6, s=20
            )
            axes[0].set_title(f"Clusters (k={len(set(atlas.cluster_labels))})")
            plt.colorbar(scatter1, ax=axes[0])
        else:
            axes[0].scatter(atlas.projection[:, 0], atlas.projection[:, 1], alpha=0.5, s=10)
            axes[0].set_title("Projection (no clusters)")
        
        # Plot 2: Colored by stopping time
        stopping_times = [s.stopping_time for s in atlas.signatures]
        scatter2 = axes[1].scatter(
            atlas.projection[:, 0], atlas.projection[:, 1],
            c=stopping_times, cmap='viridis', alpha=0.6, s=20
        )
        axes[1].set_title("Stopping Time")
        plt.colorbar(scatter2, ax=axes[1], label="Steps to 1")
        
        plt.suptitle(title, fontsize=14)
        plt.tight_layout()
        plt.savefig("collatz_atlas.png", dpi=150)
        plt.show()
        print("  Saved to collatz_atlas.png")
    
    except ImportError:
        print("  matplotlib/seaborn not installed. Skipping visualization.")


def plot_anomalies(atlas: CollatzAtlas):
    """Highlight outliers in the atlas."""
    try:
        import matplotlib.pyplot as plt
        if atlas.projection is None or atlas.outlier_scores is None:
            print("  No outliers or projection found.")
            return
        
        fig, ax = plt.subplots(figsize=(10, 7))
        
        inliers = atlas.outlier_scores == 1
        outliers = atlas.outlier_scores == -1
        
        ax.scatter(
            atlas.projection[inliers, 0], atlas.projection[inliers, 1],
            alpha=0.3, s=10, label="Inliers", color='blue'
        )
        ax.scatter(
            atlas.projection[outliers, 0], atlas.projection[outliers, 1],
            alpha=0.8, s=40, label="Outliers", color='red'
        )
        
        # Annotate top outliers
        if np.sum(outliers) > 0:
            outlier_indices = np.where(outliers)[0]
            top_anomalies = sorted(outlier_indices, 
                key=lambda i: atlas.signatures[i].stopping_time, reverse=True)[:5]
            for idx in top_anomalies:
                ax.annotate(
                    f"n={atlas.signatures[idx].n}",
                    (atlas.projection[idx, 0], atlas.projection[idx, 1]),
                    fontsize=8
                )
        
        ax.set_title("Anomaly Detection in Collatz Space")
        ax.legend()
        plt.tight_layout()
        plt.savefig("collatz_anomalies.png", dpi=150)
        plt.show()
        print("  Saved to collatz_anomalies.png")
    except ImportError:
        pass


# ---------------------------------------------------------------------
# 5. REVERSE COLLATZ TREE
# ---------------------------------------------------------------------

def build_reverse_tree(root: int, depth: int = 6) -> Dict[int, List[int]]:
    """
    Builds the reverse Collatz tree: preimages of a number.
    For odd n, the preimages are 2n and (n-1)/3 (if divisible).
    For even n, the preimages are 2n and (n-1)/3 (if divisible).
    Actually, the standard reverse: for any k, preimages are:
    - 2k (always)
    - (k-1)/3 if k ≡ 1 (mod 3)
    """
    tree = {0: [root]}
    current_level = {root}
    
    for d in range(depth):
        next_level = set()
        for n in current_level:
            # Preimage 1: 2n (always)
            p1 = 2 * n
            # Preimage 2: (n-1)/3 if n ≡ 1 (mod 3) and (n-1)/3 is odd
            p2 = None
            if n % 3 == 1 and n > 1:
                p2 = (n - 1) // 3
                if p2 % 2 == 0:  # must be odd
                    p2 = None
            
            if p2 not in tree:
                tree.setdefault(d+1, []).append(p1)
                next_level.add(p1)
            if p2 is not None and p2 not in tree:
                tree.setdefault(d+1, []).append(p2)
                next_level.add(p2)
        
        current_level = next_level
    
    return tree


def analyze_reverse_tree(root: int, depth: int = 6) -> Dict:
    """Analyze the structure of a reverse Collatz tree."""
    tree = build_reverse_tree(root, depth)
    total = sum(len(v) for v in tree.values())
    depths = list(tree.keys())
    counts = [len(tree.get(d, [])) for d in range(depth+1)]
    
    return {
        "root": root,
        "depth": depth,
        "total_nodes": total,
        "levels": depths,
        "counts": counts,
        "growth_factor": np.mean([counts[i+1] / (counts[i] + 1) for i in range(len(counts)-1)]) if len(counts) > 1 else 0,
    }


# ---------------------------------------------------------------------
# 6. MAIN — Orchestrate the Atlas
# ---------------------------------------------------------------------

def main():
    print("=" * 80)
    print("COLLATZ MORPHODYNAMIC ATLAS")
    print("Using SUBIT-TOPOS Core v0.1")
    print("Exploring the hidden geometry of Collatz trajectory space")
    print("=" * 80)
    
    # ---- Configuration ----
    N_SAMPLES = 5000          # Starting numbers to analyze
    RANGE_START = 1
    RANGE_END = 50000        # Generate numbers in this range
    MAX_STEPS = 5000
    MAX_VALUE = 10**12
    
    # ---- 1. Generate numbers ----
    print(f"\n[Phase 1] Generating {N_SAMPLES} numbers from {RANGE_START} to {RANGE_END}...")
    rng = random.Random(42)
    numbers = [rng.randint(RANGE_START, RANGE_END) for _ in range(N_SAMPLES)]
    # Ensure we have some interesting numbers like 27, 703, 6171
    special = [27, 703, 6171, 837799, 9780657631]
    for n in special:
        if n <= RANGE_END:
            numbers.append(n)
    numbers = list(set(numbers))
    print(f"  Generated {len(numbers)} unique numbers.")
    
    # ---- 2. Build trajectories and signatures ----
    print("\n[Phase 2] Computing trajectories and signatures Φ(n)...")
    atlas = CollatzAtlas(max_steps=MAX_STEPS, max_value=MAX_VALUE)
    start_time = time.time()
    atlas.add_numbers(numbers, progress=True)
    elapsed = time.time() - start_time
    print(f"  Computed {len(atlas.signatures)} signatures in {elapsed:.1f}s.")
    
    # ---- 3. Build matrix and normalize ----
    print("\n[Phase 3] Building data matrix...")
    atlas.build_matrix()
    atlas.normalize()
    print(f"  Matrix shape: {atlas.data_matrix.shape}")
    
    # ---- 4. Project to 2D ----
    print("\n[Phase 4] Projecting to 2D (PCA)...")
    atlas.project_pca(n_components=2)
    
    # Also try UMAP if available
    try:
        print("  Attempting UMAP projection...")
        atlas.project_umap(n_components=2)
    except Exception as e:
        print(f"  UMAP failed: {e}. Using PCA only.")
        atlas.project_pca(n_components=2)
    
    # ---- 5. Cluster ----
    print("\n[Phase 5] Clustering signatures...")
    atlas.cluster_kmeans(n_clusters=5)
    print(f"  Found {len(set(atlas.cluster_labels))} clusters.")
    
    # ---- 6. Detect outliers ----
    print("\n[Phase 6] Detecting outliers...")
    atlas.detect_outliers(contamination=0.05)
    outlier_count = np.sum(atlas.outlier_scores == -1)
    print(f"  Found {outlier_count} outliers ({outlier_count/len(atlas.signatures)*100:.1f}%).")
    
    # ---- 7. Summary ----
    print("\n" + "=" * 80)
    print("ATLAS SUMMARY")
    print("=" * 80)
    summary = atlas.get_summary()
    for key, val in summary.items():
        print(f"  {key}: {val}")
    
    # ---- 8. Find most interesting numbers ----
    print("\n" + "=" * 80)
    print("MOST INTERESTING TRAJECTORIES")
    print("=" * 80)
    
    # Sort by stopping time (longest)
    sorted_by_time = sorted(atlas.signatures, key=lambda s: s.stopping_time, reverse=True)
    print("\nLongest stopping times:")
    for sig in sorted_by_time[:10]:
        print(f"  n={sig.n}: {sig.stopping_time:.0f} steps, max={10**sig.max_excursion_log:.1e}")
    
    # Sort by max excursion
    sorted_by_max = sorted(atlas.signatures, key=lambda s: s.max_excursion_log, reverse=True)
    print("\nHighest excursions:")
    for sig in sorted_by_max[:10]:
        print(f"  n={sig.n}: max={10**sig.max_excursion_log:.1e}, steps={sig.stopping_time:.0f}")
    
    # ---- 9. Visualize ----
    try:
        print("\n[Phase 9] Visualizing atlas...")
        plot_atlas(atlas, title="Collatz Morphodynamic Atlas")
        plot_anomalies(atlas)
        print("  Visualization complete.")
    except Exception as e:
        print(f"  Visualization error: {e}")
    
    # ---- 10. Reverse tree analysis for a couple of numbers ----
    print("\n" + "=" * 80)
    print("REVERSE COLLATZ TREE ANALYSIS")
    print("=" * 80)
    
    for n in [27, 703, 6171]:
        if n in [s.n for s in atlas.signatures]:
            tree_info = analyze_reverse_tree(n, depth=6)
            print(f"\n  Tree for n={n}:")
            print(f"    Total nodes: {tree_info['total_nodes']}")
            print(f"    Level counts: {tree_info['counts']}")
            print(f"    Avg growth factor: {tree_info['growth_factor']:.2f}")
    
    # ---- 11. Save data ----
    print("\n" + "=" * 80)
    print("SAVING RESULTS")
    print("=" * 80)
    
    # Save signatures to CSV
    try:
        import csv
        with open("collatz_signatures.csv", "w", newline="") as f:
            writer = csv.writer(f)
            header = ["n", "stopping_time", "max_excursion_log", "odd_even_ratio",
                     "entropy", "compression_ratio", "excursion_normalized",
                     "up_down_ratio", "variance_log", "peak_late", "omega", "steps"]
            writer.writerow(header)
            for sig in atlas.signatures:
                writer.writerow([
                    sig.n, sig.stopping_time, sig.max_excursion_log,
                    sig.odd_even_ratio, sig.entropy, sig.compression_ratio,
                    sig.excursion_normalized, sig.up_down_ratio,
                    sig.variance_log, sig.peak_late, sig.omega, sig.steps
                ])
        print("  Signatures saved to collatz_signatures.csv")
    except Exception as e:
        print(f"  Could not save CSV: {e}")
    
    # Save projection and clusters
    if atlas.projection is not None and atlas.cluster_labels is not None:
        np.savez("collatz_atlas_data.npz",
                 projection=atlas.projection,
                 labels=atlas.cluster_labels,
                 outliers=atlas.outlier_scores)
        print("  Projection data saved to collatz_atlas_data.npz")
    
    print("\n" + "=" * 80)
    print("MORPHODYNAMIC ATLAS COMPLETE")
    print("=" * 80)
    print("\nKey findings:")
    print(f"  • Total trajectories: {len(atlas.signatures)}")
    print(f"  • Clusters found: {len(set(atlas.cluster_labels))}")
    print(f"  • Outliers detected: {outlier_count}")
    print(f"  • Longest trajectory: n={sorted_by_time[0].n} with {sorted_by_time[0].stopping_time:.0f} steps")
    print(f"  • Highest excursion: n={sorted_by_max[0].n} reaching {10**sorted_by_max[0].max_excursion_log:.1e}")
    print("\n  The atlas reveals the hidden geometry of Collatz trajectory space.")
    print("  Use the CSV file for further analysis, and the PNG files for visualization.")


if __name__ == "__main__":
    main()