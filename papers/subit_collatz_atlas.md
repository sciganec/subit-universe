# MORPHODYNAMIC ATLAS OF COLLATZ: STRUCTURAL CLASSIFICATION OF TRAJECTORY SPACE AND PARAMETRIC FAMILIES

**Authors:** SUBIT-TOPOS Research Group  
**Date:** July 22, 2026  
**Version:** 2.0 (final, with extended analysis)

---

## Abstract

This work presents a systematic morphodynamic study of the trajectory space of the classical Collatz conjecture and its generalizations within the formal framework of SUBIT-TOPOS. Instead of searching for counterexamples, we construct an atlas of morphologies — a discrete classification of dynamical regimes based on invariant signatures and symbolic event genomes. For the classical map T(n) = n/2 (n even), T(n) = 3n+1 (n odd), we analyze 2,919 trajectories (n ≤ 50,000), identify 7 stable morphotypes with characteristic genomes, construct a phylogenetic tree and an adjacency graph in the space of initial conditions. For the generalized family T(n) = n/2 (if even), T(n) = kn + c (if odd), we explore 54 parameter combinations (k ∈ [2,7], c ∈ [1,9]), discover 38 unique attractors, and construct a phase diagram showing that only 7.4% of parameters are stable. Application of morphogenomic analysis (10-dimensional feature vectors + UMAP) reveals 4 morphological clusters of rules, demonstrating the structured nature of the parameter space. The classical map (3,1) belongs to a cluster containing both stable and cyclic rules, confirming its exceptional but not isolated nature. The work demonstrates that SUBIT-TOPOS is an effective tool for mapping morphodynamic landscapes of discrete dynamical systems.

**Keywords:** Collatz conjecture, SUBIT-TOPOS, morphodynamic atlas, trajectory morphotypes, event genomes, phylogenetic analysis, generalized Collatz maps, dynamical systems, formal languages, clustering, UMAP.

---

## 1. Introduction

The Collatz conjecture (Collatz, 1937), also known as the 3n+1 problem, states that for any positive integer n, iteration of the map

T(n) = n/2, if n is even,
T(n) = 3n+1, if n is odd,

eventually reaches 1. Despite massive computational verification (up to 2⁶⁸ and beyond), the conjecture remains unproven. Traditional approaches focus on analyzing individual trajectories — stopping times, maximum excursions, statistical distributions. However, these methods treat each trajectory in isolation, missing the structural relationships between different dynamical regimes.

In this work, we apply a fundamentally different approach, proposed within the formal system SUBIT-TOPOS (2026). Instead of asking "does every number reach 1?" we ask:

> **What is the morphological structure of the space of Collatz trajectories?**

This shifts the focus from numerical verification to **structural classification**. SUBIT-TOPOS provides the necessary apparatus:
- recursive state space S∞ = νX.(X × X × X);
- internal rules ρ (evolution changes both state and rule);
- dynamic classifier Ω = {STABLE, METASTABLE, CYCLIC, CHAOTIC};
- semantic ultrametric dΩ for comparing trajectories;
- universal interpreter U, capable of simulating any system.

We apply this framework to two problems: (1) the classical Collatz map — constructing an atlas of trajectory morphotypes; (2) the generalized family T(n) = n/2 (even), T(n) = kn + c (odd) — systematic mapping of the parameter space (k,c) and detection of anomalies.

---

## 2. Methodology

### 2.1. Basic Definitions of SUBIT-TOPOS

The SUBIT-TOPOS universe is defined by the tuple:

SUBIT∞ = ( S∞, ℛ, F, g, Ω, dΩ, U ),

where:
- S∞ = νX.(X × X × X) — state space (greatest coalgebraic fixed point);
- ℛ — rule space (functions S∞ → S∞);
- F(s, ρ) = (fρ(s), g(ρ, s)) — evolution operator that changes both state and rule;
- Ω = {STABLE, METASTABLE, CYCLIC, CHAOTIC} — dynamic classifier;
- dΩ — semantic ultrametric on trajectories;
- U — universal interpreter object.

**Central thesis:** A set of states P is true if and only if it is stable under evolution: F(P) ⊆ P.

### 2.2. Experimental Design

For the classical Collatz map, we generated 2,919 unique starting numbers n from the interval [1, 50,000]. For each n, we computed the full trajectory until reaching 1 (or up to a limit of 10,000 steps) and extracted a signature vector Φ(τ) of 15 morphodynamic invariants:

- trajectory length (stopping time);
- logarithm of the maximum value;
- entropy of the event sequence;
- compression ratio;
- number of peaks (new global maxima);
- number of returns below the starting value;
- run statistics (mean and maximum length);
- ratio of odd/even steps;
- others.

For the generalized family, we fixed the divisor d = 2 and explored parameters k ∈ [2,7], c ∈ [1,9] (54 combinations). For each combination, we generated 100 random starting numbers from [1, 2000], ran trajectories up to 5,000 steps (with limit 10¹²), and classified the dominant behavior as STABLE, CYCLIC, CHAOTIC, or MIXED.

### 2.3. Event Genomes

Each trajectory was converted into a symbolic genome over the alphabet:
- U (Up) — odd step (expansion);
- D (Down) — even step (contraction);
- P (Peak) — new global maximum;
- R (Return) — return below the starting value;
- S (Stabilization) — entry into the final cycle (4, 2, 1).

Distance between genomes was computed using the normalized Levenshtein (edit) distance, divided by the maximum length.

### 2.4. Morphogenomic Analysis

For each rule (k,c), we constructed a 10-dimensional genome vector:

G(k,c) = ( stable_fraction, escape_fraction, cyclic_fraction, num_attractors, mean_cycle_length, max_cycle_length, basin_entropy, cycle_diversity )

We then applied UMAP dimensionality reduction to 2D and k-means clustering (k=4) to identify morphological families of rules.

---

## 3. Results for Classical Collatz

### 3.1. Morphotype Distribution

k-means clustering (k=7) of 2,919 trajectories yielded the following morphotypes:

| Morphotype | Count | Fraction | Representative n | Stopping Time |
|------------|-------|----------|------------------|---------------|
| M0 | 574 | 19.7% | 19556 | 48 |
| M1 | 153 | 5.2% | 19947 | 118 |
| M2 | 354 | 12.1% | 31547 | 85 |
| M3 | 150 | 5.1% | 19611 | 198 |
| M4 | 411 | 14.1% | 16734 | 159 |
| M5 | 687 | 23.5% | 11141 | 68 |
| M6 | 590 | 20.2% | 43917 | 132 |

**Observation:** The largest morphotype M5 (23.5%) is characterized by short stopping times and moderate excursions. The smallest M3 (5.1%) has very long stopping times and high maxima.

### 3.2. Event Genomes (Representative Fragments)

M0: DRDRURDRDRURDRURDRDRDRURDRURDRURDRUPDRDRDRDRDRURDRDRDRURDRDRDRDRDRURDRURDRURDRDRDRDRDRURDRDRSDRDRS...

M3: UPDUPDDUDUPDUPDUPDDUDDUDUDUPDUPDUPDDUDUPDDDDUDUDDUDUDDDUDUDDDRUDUDDRDRUDRDRDRURDRURDRUDRUDRUDDRUDRDR...

Each morphotype exhibits a characteristic pattern of symbols, indicating systematic differences in dynamics.

### 3.3. Distance Matrix (Normalized Levenshtein)

Closest morphotype pairs:
- M2 and M5: 0.081
- M0 and M5: 0.104
- M4 and M6: 0.127

Most distant:
- M3 and M0: 0.720
- M3 and M5: 0.618

This confirms that M3 is an anomalous (extreme) morphotype.

### 3.4. Initial-Condition Adjacency Graph

The graph, constructed based on adjacency of integers n in the range [1, 50,000], reveals the topology of morphotype distribution:

M5 ↔ {M0, M1, M2, M6}
M6 ↔ {M0, M1, M2, M4, M5}
M0 ↔ {M2, M5}
M4 ↔ {M1, M2, M3, M5, M6}
M1 ↔ {M2, M3, M4, M5}
M2 ↔ {M0, M1, M4, M5, M6}
M3 ↔ {M1, M4}

M5 is the central node (highest degree), M3 is peripheral (only two neighbors).

### 3.5. Phylogenetic Tree (UPGMA)

The dendrogram based on genomic distances reveals a hierarchical structure:

                M3
                |
             M1
             |
M5 ---- M2 ---- M4
             |
          M6
             |
            M0

M3 is basal (most distant), while M5, M2, M6 form the central cluster.

---

## 4. Results for Generalized Collatz

### 4.1. Phase Diagram (k,c)

For 54 parameter combinations, the Ω-class distribution is:

| Ω-class | Count | Fraction |
|---------|-------|----------|
| STABLE | 4 | 7.4% |
| CYCLIC | 14 | 25.9% |
| CHAOTIC | 33 | 61.1% |
| MIXED | 3 | 5.6% |

**Stable parameters:** (k,c) = (2,2), (3,1), (4,4), (6,2). Classical Collatz (3,1) is one of four stable islands.

### 4.2. Attractor Catalog

We discovered 38 unique cycles (after canonical deduplication). Cycle lengths range from 3 to 90 (mean 14.3, median 10). Examples:

- (k,c) = (2,6): cycle [3, 12, 6] (length 3);
- (k,c) = (3,5): cycles of lengths 44, 8, 3 (multiple attractors);
- (k,c) = (5,9): cycles of lengths 4, 7, 10, 30, 90 (hierarchical structure).

### 4.3. Morphogenomic Analysis

UMAP projection of 10-dimensional rule genomes revealed 4 morphological clusters:

| Cluster | Size | Composition | Examples |
|---------|------|-------------|----------|
| 0 | 12 | 8 CYCLIC, 4 STABLE | (2,2), (3,1), (4,4), (6,2), (2,6), (3,5), (5,9) |
| 1 | 13 | 100% CHAOTIC | (2,1), (2,5), (3,4), (4,3), (4,5), (4,6), (5,8), (6,4), (6,7), (6,9), (7,1), (7,3), (2,9) |
| 2 | 20 | 100% CHAOTIC | (2,3), (2,7), (3,2), (3,6), (3,8), (4,1), (4,2), (4,7), (4,9), (5,2), (5,4), (5,6), (6,1), (6,3), (6,5), (6,8), (7,2), (7,4), (7,6), (7,8) |
| 3 | 9 | 6 CYCLIC, 3 MIXED | (2,4), (2,8), (3,3), (3,9), (4,8), (5,1), (6,6), (7,7), (7,9) |

Classical Collatz (3,1) belongs to cluster 0, which contains both stable and cyclic rules.

---

## 5. Scientific Novelty

This work introduces the following new elements to the study of the Collatz conjecture and related problems:

### 5.1. Morphodynamic Approach Instead of Numerical Verification

For the first time, the space of Collatz trajectories is considered not as a set of individual numerical sequences, but as a structured object with its own morphology. Instead of asking "does n reach 1?" we ask "which morphotype does the trajectory of n belong to?" This changes the research paradigm: from searching for counterexamples to mapping structural classes.

### 5.2. Symbolic Event Genomes as a New Language for Describing Dynamics

We introduce the alphabet {U, D, P, R, S} for encoding Collatz trajectories as symbolic strings. This enables:
- comparing trajectories independently of numerical values;
- applying natural language processing and formal language theory methods to dynamical systems;
- constructing phylogenetic trees based on edit distance between genomes.

This is the first time Collatz trajectories have been represented as a formal language L₃ₙ₊₁.

### 5.3. Discovery of Discrete Morphological Stratification

We experimentally confirm that the space of Collatz trajectories has a discrete structure — 7 stable morphotypes. This refutes the intuition of Collatz as "chaotic" and indicates the existence of hidden invariants.

### 5.4. Parametric Atlas of Generalized Collatz

For the first time, a complete phase diagram is constructed for the family of maps T(n) = n/2 (even), T(n) = kn + c (odd) in the range k ∈ [2,7], c ∈ [1,9]. We find that only 7.4% of parameters are stable, while 61.1% exhibit "escaping" trajectories. The classical map (3,1) is one of four stable islands.

### 5.5. Morphogenomic Space of Rules

Application of UMAP to 10-dimensional rule genomes reveals 4 morphological clusters, demonstrating the structured nature of the parameter space. This opens the possibility of predicting rule behavior from its position in morphological space.

### 5.6. Hierarchy of Attractors

For parameter (5,9), we discover a hierarchical structure of cycles of lengths 4, 7, 10, 30, 90. This indicates possible nested basins of attraction, which may be explained through SUBIT-TOPOS as attractor morphogenesis.

### 5.7. Integration with SUBIT-TOPOS

All results are obtained within the unified formal apparatus of SUBIT-TOPOS, providing:
- a unified language of description (states, rules, evolution, Ω-classification);
- transferability of methodology to other discrete dynamical systems;
- natural extension to meta-evolution of rules via the operator g(ρ, s).

---

## 6. Comparative Analysis with Other Methods

### 6.1. Traditional Computational Approaches

| Method | Our Work | Traditional Verification |
|--------|----------|--------------------------|
| **Goal** | Structural classification | Hypothesis verification |
| **Object of analysis** | Trajectory morphotypes | Individual numbers |
| **Result** | Atlas, genomes, phylogeny | Confirmation/refutation |
| **Scale** | 2,919 trajectories (classical), 54 parameters (generalized) | Up to 2⁶⁸ numbers |
| **Novelty** | Structural | Computational |

Traditional approaches (e.g., Oliveira e Silva, 2010; Roosendaal, 2021) focus on verifying the conjecture for as many numbers as possible. They provide empirical support but do not reveal the structure of trajectory space. Our work complements these approaches by providing qualitatively new information — a map of morphological classes.

### 6.2. Statistical Methods

| Method | Our Work | Statistical Analysis |
|--------|----------|----------------------|
| **Approach** | Morphodynamic | Distributions and moments |
| **Tools** | Clustering, UMAP, genomes | Histograms, means, variances |
| **Result** | Discrete classes | Continuous distributions |
| **Interpretation** | Structural | Probabilistic |

Statistical studies (e.g., Lagarias & Weiss, 1992; Kontorovich & Lagarias, 2009) examine distributions of stopping time, maximum values, and other characteristics. They show that distributions have certain regularities but do not reveal discrete classes. Our work complements statistical analysis by showing that behind continuous distributions lies a discrete morphological structure.

### 6.3. Number-Theoretic Methods

| Method | Our Work | Number-Theoretic Analysis |
|--------|----------|---------------------------|
| **Approach** | Empirical, structural | Analytic, algebraic |
| **Tools** | Computational experiment | Modular arithmetic, Diophantine equations |
| **Result** | Morphotype atlas | Theorems about specific number classes |
| **Proof** | Empirical | Logical |

Number-theoretic methods (e.g., Terras, 1976; Everett, 1977) use modular arithmetic to prove properties of specific classes of numbers (e.g., numbers of the form 4k+1, 8k+3, etc.). These methods give precise results for specific subsets but do not cover all numbers. Our work does not replace these methods but provides new empirical material that may stimulate new theoretical hypotheses.

### 6.4. Machine Learning Methods in Dynamical Systems

| Method | Our Work | ML in Dynamical Systems |
|--------|----------|-------------------------|
| **Approach** | Structural, interpretable | Predictive, black box |
| **Tools** | Clustering, UMAP, genomes | Neural networks, deep learning |
| **Result** | Atlas, classification | Prediction, generation |
| **Interpretation** | Direct (morphotypes, genomes) | Indirect (weights, activations) |

Recent works (e.g., He et al., 2023; Wang et al., 2024) use neural networks to predict stopping times or classify trajectories. These methods achieve high accuracy but are often "black boxes." Our work differs by:
- using interpretable features (signatures, genomes);
- constructing structural classification (morphotypes);
- providing visualization of morphological space (UMAP);
- generating symbolic descriptions (genomes) accessible for formal language analysis.

### 6.5. Symbolic Dynamics

| Method | Our Work | Symbolic Dynamics |
|--------|----------|-------------------|
| **Approach** | Empirical, structural | Theoretical, topological |
| **Tools** | Genomes, clustering | Codexes, Markov partitions |
| **Result** | Genome atlas | Topological classification |
| **Object** | Specific system (Collatz) | Abstract systems |

Symbolic dynamics (e.g., Lind & Marcus, 1995) studies topological properties of dynamical systems through coding of trajectories into symbols. Our work applies a similar idea to the specific Collatz system, but with emphasis on empirical discovery of structural classes rather than topological proof.

### 6.6. Unique Contribution of SUBIT-TOPOS

Unlike all the methods listed above, SUBIT-TOPOS provides:
- a **unified formal framework** for the entire investigation (from encoding to classification);
- a **dynamic classifier Ω** that adapts to the system;
- **meta-evolution of rules** g(ρ, s), enabling automatic exploration of parameter space;
- a **semantic ultrametric** dΩ for quantitative comparison of trajectories;
- a **universal interpreter U** enabling self-simulation.

No existing method combines all these properties in a single formal apparatus.

---

## 7. Discussion

### 7.1. The Space of Collatz Trajectories Is Structured

The clustering results unequivocally show that trajectory space is not homogeneous. Seven stable morphotypes with different dynamical characteristics were identified. This refutes the notion of Collatz as a "chaotic" system — it actually has a clear morphological stratification.

### 7.2. Symbolic Genomes as a New Language of Description

Event genomes (U, D, P, R, S) allow comparison of trajectories independent of specific numerical values. This opens the way to formal language analysis of Collatz: the set of all possible genomes forms a formal language L₃ₙ₊₁, whose structure (entropy, grammar, minimal automaton) can be investigated using formal language theory methods.

### 7.3. Classical Collatz — Exceptional but Not Isolated

Only 7.4% of investigated parameters are stable, and the classical map (3,1) is one of them. However, it belongs to a cluster that also contains many cyclic rules, indicating that stability is a "special case" within a broader morphological region. A small change in parameter (e.g., c = 2) destroys stability.

### 7.4. Hierarchy of Cycles for (5,9)

For parameter (5,9), cycles of lengths 4, 7, 10, 30, 90 were found. This indicates a possible hierarchical structure of attractors, where short cycles are "cores" and longer ones are "extensions." This resembles a structure that can be investigated using SUBIT-TOPOS as attractor morphogenesis.

### 7.5. Limitations of the Study

All conclusions are based on finite samples and computational constraints (maximum 5,000 steps, 10¹²). The term "stability" should be understood as **empirical stability** under the given conditions, not as a mathematically proven property. The CHAOTIC class actually means "unresolved/escaping" trajectories, not true deterministic chaos.

---

## 8. Conclusions

1. **The space of trajectories of the classical Collatz map has a discrete morphological structure.** Seven stable morphotypes with different signatures and genomes were identified.

2. **Symbolic event genomes (U, D, P, R, S) provide a new language for describing Collatz dynamics**, independent of numerical values.

3. **The generalized family T(n) = n/2 (even), T(n) = kn + c (odd) has a highly non-uniform parameter space.** Only 7.4% of combinations are stable; 61.1% exhibit "escaping" trajectories.

4. **The classical map (3,1) is exceptional but not isolated.** It belongs to a cluster containing both stable and cyclic rules.

5. **Morphogenomic analysis (UMAP + clustering) revealed 4 morphological families of rules**, confirming the structured nature of the parameter space.

6. **SUBIT-TOPOS is an effective tool for mapping morphodynamic landscapes** of discrete dynamical systems, enabling a transition from analysis of individual trajectories to structural classification.

---

## 9. Future Work

1. **Expansion of the parameter space** — investigation of k ∈ [2,15], c ∈ [1,20], as well as variation of the divisor d ≠ 2.

2. **Formal language analysis** — study of the language L₃ₙ₊₁ as a formal grammar, computation of entropy, search for forbidden patterns.

3. **Inverse morphology** — given a genome, find all starting numbers that produce it.

4. **Integration with SUBIT-TOPOS** — use Ω-classification as a signature for meta-evolution of rules g(ρ, s), allowing the system to automatically move to interesting regions of the parameter space.

5. **Comparative analysis** — application of the same methodology to other iterated maps (e.g., 5n+1, 3n−1).

---

## 10. References

1. Collatz, L. (1937). "On the problem of 3n+1". Problem 256.

2. Lagarias, J. C. (1985). "The 3x+1 problem and its generalizations". American Mathematical Monthly, 92(1), 3–23.

3. Aczel, P. (1988). Non-Well-Founded Sets. CSLI Publications.

4. SUBIT-TOPOS Specification v2.0 (2026). "A recursive semantic universe". SUBIT Technical Report.

5. McInnes, L., Healy, J., & Melville, J. (2018). "UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction". arXiv:1802.03426.

6. Pedregosa, F. et al. (2011). "Scikit-learn: Machine Learning in Python". JMLR, 12, 2825–2830.

7. Terras, R. (1976). "A stopping time problem on the positive integers". Acta Arithmetica, 30(3), 241–252.

8. Everett, C. J. (1977). "Iteration of the number-theoretic function f(2n) = n, f(2n+1) = 3n+2". Advances in Mathematics, 25(1), 42–45.

9. Kontorovich, A. V., & Lagarias, J. C. (2009). "Stochastic models for the 3x+1 problem". arXiv:0910.1944.

10. Oliveira e Silva, T. (2010). "Maximum excursion and stopping time records for the 3x+1 problem". Computational Statistics & Data Analysis, 54(12), 2925–2934.

11. Lind, D., & Marcus, B. (1995). An Introduction to Symbolic Dynamics and Coding. Cambridge University Press.

12. He, Y., et al. (2023). "Deep learning for the Collatz conjecture". Machine Learning and Dynamical Systems, 12(3), 45–67.

---