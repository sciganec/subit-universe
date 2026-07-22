# SUBIT-COLLATZ v3.0: Morphodynamic Genome + Attractor Topology Map — Final Report

## 1. Overview

We have successfully applied the SUBIT-TOPOS morphodynamic genome framework to the generalized Collatz family \( T(n) = n/2 \) if even, \( k n + c \) otherwise. For 54 parameter combinations (k ∈ [2,7], c ∈ [1,9]), we computed a 10‑dimensional genome vector per rule, projected into a 2D morphospace using UMAP, and identified 4 distinct morphological clusters.

## 2. Results

### Cluster Summary

| Cluster | Size | Composition | Key Rules |
|---------|------|-------------|-----------|
| **0** | 12 | 8 CYCLIC (66.7%), 4 STABLE (33.3%) | (2,2), (3,1) classic, (4,4), (6,2), plus cyclic rules like (2,6), (3,5), (5,9) |
| **1** | 13 | 100% CHAOTIC | (2,1), (2,5), (2,9), (3,4), (4,3), (4,5), (4,6), (5,8), (6,4), (6,7), (6,9), (7,1), (7,3) |
| **2** | 20 | 100% CHAOTIC | Many others: (2,3), (2,7), (3,2), (3,6), (3,8), (4,1), (4,2), (4,7), (4,9), (5,2), (5,4), (5,6), (6,1), (6,3), (6,5), (6,8), (7,2), (7,4), (7,6), (7,8) |
| **3** | 9 | 6 CYCLIC (66.7%), 3 MIXED (33.3%) | (2,4), (2,8), (3,3), (3,9), (4,8), (5,1), (6,6), (7,7), (7,9) |

### Key Insights

1. **Stable rules form a distinct sub‑group** within a larger cluster (Cluster 0) that also contains many cyclic rules. This suggests that stability is not a separate family but a "special case" within a broader class of rules that exhibit attractors.

2. **CHAOTIC rules dominate** (Clusters 1 and 2 contain 33 out of 54 rules, i.e., 61%). They split into two distinct clusters, indicating that there are at least two qualitatively different types of "escape" behavior.

3. **Classic Collatz (3,1) is in Cluster 0** alongside other stable rules. This confirms that it is not an isolated stable point but part of a larger morphological region.

4. **Cluster 3 contains mixed and cyclic rules** but no stable rules. It represents rules where trajectories sometimes reach 1 and sometimes enter cycles, but never fully stabilize.

### Visualizations

- **Morphospace plot (`rule_morphospace.png`)**: Shows clear separation of the four clusters in 2D UMAP space.
- **Genome heatmap (`genome_heatmap.png`)**: Displays the feature values per rule, highlighting the differences between clusters.
- **Cluster summary (`cluster_summary.png`)**: Compares stability, attractor count, and cycle lengths across clusters.

---

## 3. Interpretation

The results demonstrate that the generalized Collatz parameter space is **morphologically stratified**. Rules group by their dynamic behavior rather than by specific numerical values of (k,c). This means that the "morphology" of a rule — its long‑term attractor structure — is more fundamental than its exact parameters.

In SUBIT-TOPOS terms, we have constructed a **morphodynamic atlas** of a family of discrete dynamical systems, where:
- **States** are the rules (k,c).
- **Signatures** are the genome vectors.
- **Morphotypes** are the four clusters.
- **Topology** is the UMAP embedding.

This is a direct application of the SUBIT-TOPOS pipeline to a parameterized family of maps.

---

## 4. Next Steps (v4.0)

1. **Explore d ≠ 2** – Fix k=3 and vary d (divisor) to see if the same morphological families appear.
2. **Include more features** – Add Lyapunov‑style exponents, entropy of parity sequences, and fractal dimension of basins.
3. **Attractor topology** – Analyze how cycles are nested (e.g., for (5,9) we saw cycles of lengths 4, 7, 10, 30, 90). Build a graph of cycle relationships.
4. **Inverse morphology** – Given a genome, can we predict which (k,c) produce it? This would be a generative model of rules.
5. **Integration with SUBIT‑TOPOS** – Use the Ω‑classifier to guide meta‑evolution of rules; e.g., start from a chaotic rule and let g(ρ,s) move it toward a stable cluster.

---

## 5. Final Conclusion

We have successfully built a **morphodynamic genome atlas** for the generalized Collatz family, revealing that the parameter space is structured into four distinct behavioral clusters. The classic Collatz map (3,1) resides in a cluster that includes other stable rules and many cyclic rules, confirming its exceptional yet not isolated nature. This work demonstrates that SUBIT-TOPOS can systematically map the morphology of a family of discrete dynamical systems, providing a new perspective on their global structure.

**SUBIT-COLLATZ v3.0 is complete.**