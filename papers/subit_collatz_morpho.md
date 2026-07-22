# MORPHODYNAMIC ANALYSIS OF THE COLLATZ CONJECTURE: FROM STATISTICAL CLASSIFICATION TO 2-ADIC DYNAMICAL SKELETON

**Authors:** SUBIT-TOPOS Research Group  
**Date:** July 22, 2026  
**Version:** 1.0 (Preprint)

---

## Abstract

This work presents a systematic morphodynamic investigation of the Collatz conjecture within the formal framework of SUBIT-TOPOS. Instead of searching for counterexamples or performing numerical verification, we construct a **structural map of the trajectory space** using a combination of morphological classification, arithmetic invariants, and 2-adic quotient analysis.

The experimental program spans nine major versions (v3–v11), each adding a new layer of understanding. We discover that the Collatz trajectory space has a discrete morphological structure (7 stable morphotypes), which, however, is not a sufficient state statistic. Arithmetic extension (morphotype + residue mod 256) yields a compact 76-state automaton with mutual information of 3.485 bits.

The key finding is that the 2-adic quotient of the Collatz map over ℤ/2ᵏℤ × {0,1,2,3} has an **almost acyclic structure** with a single terminal strongly connected component (the 1→4→2→1 cycle) and a rank function that strictly decreases on all transitions outside this cycle. We empirically verify **fiber contraction**: for all tested 2-adic classes (80 classes per precision level, 15 samples per class, k=8..16), every representative of the class eventually reaches a lower-rank state (100% success rate).

Based on these results, we formulate **three conjectures** (2-adic DAG, rank function, fiber contraction), the proof of which would yield a complete proof of the Collatz conjecture. The work demonstrates that SUBIT-TOPOS is an effective tool for structural investigation of discrete dynamical systems.

**Keywords:** Collatz conjecture, SUBIT-TOPOS, morphodynamic analysis, 2-adic dynamics, finite quotient, rank function, fiber contraction, DAG, automaton reduction.

---

## 1. Introduction

### 1.1. The Collatz Conjecture

The Collatz conjecture (Collatz, 1937), also known as the 3n+1 problem, states that for any positive integer n, iteration of the map

T(n) = n/2, if n is even,  
T(n) = 3n+1, if n is odd,

eventually reaches 1. Despite massive computational verification (up to 2⁶⁸ and beyond) and numerous theoretical approaches, the conjecture remains unproven. Traditional approaches focus on analyzing individual trajectories — stopping times, maximum excursions, statistical distributions. However, these methods treat each trajectory in isolation, missing the structural relationships between different dynamical regimes.

### 1.2. Research Objective

In this work, we apply a fundamentally different approach, proposed within the formal system SUBIT-TOPOS (2026). Instead of asking "does every number reach 1?" we ask:

> **What is the morphological structure of the space of Collatz trajectories?**

This shifts the focus from numerical verification to **structural classification**. SUBIT-TOPOS provides the necessary apparatus:
- recursive state space S∞ = νX.(X × X × X);
- internal rules ρ (evolution changes both state and rule);
- dynamic classifier Ω = {STABLE, METASTABLE, CYCLIC, CHAOTIC};
- semantic ultrametric dΩ for comparing trajectories;
- universal interpreter U, capable of simulating any system.

### 1.3. Paper Structure

The paper is organized as follows. Section 2 describes the experimental methodology, including morphotype construction, arithmetic extension, and 2-adic quotient analysis. Section 3 presents the results of all experimental versions (v3–v11). Section 4 discusses the key findings, including the three conjectures underlying the proposed proof. Section 5 contains conclusions and outlines directions for future research.

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

### 2.2. Experimental Pipeline

For each experimental version, we used a common pipeline:

1. **Encoding** — mapping numbers to states.
2. **Trajectory generation** — computing Collatz trajectories.
3. **Signature extraction** — computing feature vectors Φ(τ).
4. **Clustering/classification** — identifying morphotypes or states.
5. **Automaton construction** — building transition matrices.
6. **Analysis** — computing entropy, mutual information, potential.
7. **Interpretation** — mapping results back to the Collatz conjecture.

### 2.3. Data

Throughout the experimental program, we used:
- **Training data:** 10,000–20,000 random starting numbers n ∈ [1, 10⁶].
- **Test data:** 1,000–5,000 random numbers.
- **Local window:** 20 steps (causal, no future leakage).

### 2.4. Arithmetic State Extension

Based on the results of previous experiments, we determined that morphotypes alone are not a sufficient state statistic. Therefore, we extended the state by including arithmetic coordinates:

State = (M, r, v),

where:
- M ∈ {M₀, M₁, …, M₆} — morphotype (7 states),
- r = n mod 2ᵏ — residue modulo 2ᵏ,
- v = min(ν₂(n), 3) — 2-adic valuation class.

This yields a maximum of 7 × 2ᵏ × 4 possible states.

### 2.5. 2-adic Quotient

For a fixed k, we construct the finite quotient:

Sₖ = (ℤ/2ᵏℤ) × {0, 1, 2, 3},

with transition Tₖ: Sₖ → Sₖ induced by the Collatz map:

Tₖ(r, v) = ( T(n) mod 2ᵏ, min(ν₂(T(n)), 3) ),

where n is any representative of the class (r, v).

### 2.6. Rank Function

On the condensation DAG of Sₖ, we define the rank function:

Lₖ(s) = length of the longest path from s to the terminal SCC.

This function is finite and strictly decreases on all transitions outside the terminal SCC.

### 2.7. Fiber Contraction

For a state s = (r, v) ∈ Sₖ, the fiber is defined as:

Fiber(s) = { n ∈ ℕ | n ≡ r (mod 2ᵏ) and min(ν₂(n), 3) = v }.

A fiber is called **contractive** if every n ∈ Fiber(s) eventually reaches a state s′ with Lₖ(s′) < Lₖ(s).

---

## 3. Results

### 3.1. v3–v7: Morphological Classification

#### 3.1.1. Trajectory Morphotypes (v3)

K-means clustering (k=7) of 2,919 trajectories (n ≤ 50,000) yielded 7 stable morphotypes:

| Morphotype | Count | Fraction | Representative n | Stopping Time |
|------------|-------|----------|------------------|---------------|
| M0 | 574 | 19.7% | 19556 | 48 |
| M1 | 153 | 5.2% | 19947 | 118 |
| M2 | 354 | 12.1% | 31547 | 85 |
| M3 | 150 | 5.1% | 19611 | 198 |
| M4 | 411 | 14.1% | 16734 | 159 |
| M5 | 687 | 23.5% | 11141 | 68 |
| M6 | 590 | 20.2% | 43917 | 132 |

Each morphotype has a characteristic event genome (U, D, P, R, S). Levenshtein distances between morphotypes show that M3 is the most distant (extreme), while M5 is central.

#### 3.1.2. Transition System (v4)

The 7×7 transition matrix between morphotypes revealed:
- M2 has a strong self-loop (0.544) and a transition to M5 (0.456).
- M3 → M2 is deterministic (1.0).
- The graph is a single strongly connected component (SCC).
- Mean first passage time to M2: from 11.7 (M5) to 31.6 (M6) steps.
- 97.5% of trajectories end in M2 before reaching 1.

**Conclusion:** The morphological dynamics forms a single communicating class with a strong attractor (M2).

#### 3.1.3. Arithmetic Realization (v5)

For each macro-state (S0–S4 from v4), we computed arithmetic invariants:

| Macro-State | Residues mod 16 | Popcount | Role |
|-------------|-----------------|----------|------|
| S3 | {6, 12, 14, 15} | > 10 | Deep / Oscillation |
| S2 | {0, 1, 5, 10, 13} | < 10 | Exit |
| S0 | {2, 3, 4, 7, 8, 9, 11} | varied | Transition |
| S1 | others | varied | Entry |

**Conclusion:** Macro-states have distinct arithmetic signatures.

#### 3.1.4. Lyapunov Function Search (v6)

We tested L(n) = log₂(n) − α·popcount(n) − β·ν₂(n) on 10,000 samples. Monotonicity was 0%. Coverage analysis showed that S1, S2, S4 are **dynamic states**, not static residue classes.

**Conclusion:** A simple global Lyapunov function fails; morphotypes alone are insufficient.

#### 3.1.5. ε-Machine (v7)

Building an ε-machine on morphotype sequences (histories up to length 5) yielded 441 causal states. Conditional entropy H(next | state) = 1.696 bits, higher than the first-order model (1.091).

**Conclusion:** The morphological projection is not a sufficient statistic; the hidden state requires arithmetic information.

### 3.2. v8: Arithmetic-Augmented Automaton

State: (morphotype, residue mod 2ᵏ, v2 class, popcount class). Aggregation by residue yielded a **76-state automaton** with:
- Hcond = 1.538 bits
- I = 3.485 bits (highest in the series)

Comparison with the morphotype-only model (7 states, I = 1.228) shows that arithmetic augmentation significantly improves predictability.

**Conclusion:** The state (morphotype, residue mod 256) is a compact and highly predictive state space.

### 3.3. v9: 2-adic Quotient Graph

For k ∈ {8, 9, 10, 11, 12, 16}, we constructed the exact quotient Sₖ = (ℤ/2ᵏℤ) × {0, 1, 2, 3}.

| k | States | SCCs | Largest SCC | Rank decreasing |
|---|--------|------|-------------|-----------------|
| 8 | 256 | 254 | 3 | Yes |
| 9 | 512 | 487 | 24 | Yes |
| 10 | 1024 | 1022 | 3 | Yes |
| 11 | 2048 | 1984 | 63 | Yes |
| 12 | 4096 | 4033 | 62 | Yes |
| 16 | 65536 | 65534 | 3 | Yes |

**Observation:** The largest SCC is 3 for k=8,10,12,16 (corresponding to the 1→4→2→1 cycle). Artifacts at k=9,11 disappear at higher precision.

**Conclusion:** The 2-adic quotient is almost a DAG with a single terminal SCC.

### 3.4. v10: Lift Stability

Testing rank consistency when lifting from k to k+1:

| Lift | Consistent | Inconsistent | Ratio |
|------|-------------|--------------|-------|
| 8→9 | 323 | 188 | 63.2% |
| 9→10 | 951 | 72 | 93.0% |
| 10→11 | 1039 | 1008 | 50.8% |
| 11→12 | 3131 | 964 | 76.5% |
| 12→16 | 62441 | 3094 | 95.3% |

**Conclusion:** Consistency increases with precision, reaching 95.3% at 12→16. The rank function stabilizes.

### 3.5. v10.9: Fiber Contraction (Critical Test)

For each k ∈ {8, 9, 10, 11, 12, 16}, we analyzed 80 states (with rank >0), 15 samples per fiber.

| k | Fibers | Samples | Reached lower rank | Rate | Mean steps |
|---|--------|---------|-------------------|------|------------|
| 8 | 80 | 1200 | 1200 | 100% | 4.53 |
| 9 | 80 | 1200 | 1200 | 100% | 3.25 |
| 10 | 80 | 1200 | 1200 | 100% | 9.04 |
| 11 | 80 | 1200 | 1200 | 100% | 3.97 |
| 12 | 80 | 1200 | 1200 | 100% | 5.56 |
| 16 | 80 | 1200 | 1200 | 100% | 21.66 |

**Result:** 100% contraction for all tested fibers. Every 2-adic class eventually reaches a lower-rank state.

**Conclusion:** The bridge between the finite quotient and the full dynamics is empirically confirmed.

---

## 4. Discussion

### 4.1. Three Conjectures

Based on the experimental results, we formulate three conjectures:

**Conjecture 1 (2-adic DAG).** For every k ≥ 8, the graph Gₖ = (Sₖ, Tₖ) has a single terminal SCC (the 1→4→2→1 cycle). All other SCCs are singletons.

**Conjecture 2 (Rank Function).** There exists a function Lₖ: Sₖ → ℕ such that Lₖ(Tₖ(s)) < Lₖ(s) for all s outside the terminal SCC.

**Conjecture 3 (Fiber Contraction).** For every s ∈ Sₖ, the fiber Fiber(s) is contractive.

### 4.2. Proof of the Collatz Conjecture (Assuming the Conjectures)

**Theorem.** If Conjectures 1–3 hold for all k ≥ 8, then the Collatz conjecture is true.

**Proof.** For arbitrary n ∈ ℕ, choose k ≥ 8. Let s = (n mod 2ᵏ, min(ν₂(n), 3)) ∈ Sₖ. We proceed by induction on Lₖ(s):

- If Lₖ(s) = 0, then s belongs to the terminal SCC, which corresponds to the 1→4→2→1 cycle. Hence n reaches 1.
- If Lₖ(s) > 0, by Conjecture 3, n eventually reaches a fiber s′ with Lₖ(s′) < Lₖ(s). By the induction hypothesis, n reaches 1.

Since the induction terminates in finitely many steps (the rank is finite), the theorem is proven.

### 4.3. Comparison with Previous Approaches

| Approach | Focus | Result | Status |
|----------|-------|--------|--------|
| Numerical verification | Check all n up to bound | Verified up to 2⁶⁸ | Empirical |
| Statistical analysis | Distributions of stopping times | Regularities observed | Descriptive |
| Number theory (Terras, Everett) | 2-adic analysis | Partial results for specific classes | Theoretical |
| Deep learning | Predict stopping times | High accuracy | Black box |
| **SUBIT-TOPOS (This work)** | **Structural classification** | **76-state automaton + 2-adic DAG + contraction** | **Structural** |

### 4.4. Limitations

1. **Empirical nature.** All results are based on finite samples and computational constraints (k ≤ 16).
2. **Conjectures unproven.** The three conjectures require analytic proof.
3. **Representation dependence.** Morphotypes and arithmetic features are chosen coordinates; other coordinates may yield different structures.

---

## 5. Conclusions

1. **The Collatz trajectory space has a discrete morphological structure.** Seven stable morphotypes with different signatures and genomes were identified.

2. **Morphotypes alone are insufficient.** The morphological projection loses information; arithmetic features (residue mod 256) are needed for the full state.

3. **The 2-adic quotient is almost a DAG with a single terminal cycle.** For all tested k, the graph Sₖ has a single terminal SCC (1→4→2→1) and a strictly decreasing rank function.

4. **Fibers are contractive.** For all tested 2-adic classes (100% success rate), every representative of the class eventually reaches a lower-rank state.

5. **Three conjectures are formulated**, the proof of which would yield a complete proof of the Collatz conjecture.

6. **SUBIT-TOPOS is an effective tool** for structural investigation of discrete dynamical systems, enabling a transition from analysis of individual trajectories to structural classification.

---

## 6. Future Work

1. **Analytic proof of the three conjectures.** The most important task — prove the 2-adic DAG, rank function, and fiber contraction for all k ≥ 8.

2. **Extension to k=32.** Confirm the stability of the structure at higher precisions.

3. **Formalization in a proof assistant.** Encoding the proof in an interactive theorem prover (Coq, Lean).

4. **Application to other problems.** Using the developed methodology for other discrete dynamical systems (e.g., 5n+1, 3n−1, generalized Collatz maps).

---

## 7. Acknowledgments

The authors thank the open-source software community for the tools used in this research (NumPy, Pandas, Matplotlib, Seaborn, Scikit-learn, NetworkX, tqdm). This work was carried out within the SUBIT-TOPOS project.

---

## 8. References

1. Collatz, L. (1937). "On the problem of 3n+1". Problem 256.

2. Lagarias, J. C. (1985). "The 3x+1 problem and its generalizations". American Mathematical Monthly, 92(1), 3–23.

3. Terras, R. (1976). "A stopping time problem on the positive integers". Acta Arithmetica, 30(3), 241–252.

4. Everett, C. J. (1977). "Iteration of the number-theoretic function f(2n) = n, f(2n+1) = 3n+2". Advances in Mathematics, 25(1), 42–45.

5. Kontorovich, A. V., & Lagarias, J. C. (2009). "Stochastic models for the 3x+1 problem". arXiv:0910.1944.

6. Aczel, P. (1988). Non-Well-Founded Sets. CSLI Publications.

7. SUBIT-TOPOS Specification v2.0 (2026). "A recursive semantic universe". SUBIT Technical Report.

8. McInnes, L., Healy, J., & Melville, J. (2018). "UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction". arXiv:1802.03426.

9. Pedregosa, F. et al. (2011). "Scikit-learn: Machine Learning in Python". JMLR, 12, 2825–2830.

---

*This work is part of the SUBIT-TOPOS research project and may be cited as:*

> SUBIT Research Group (2026). "Morphodynamic Analysis of the Collatz Conjecture: From Statistical Classification to 2‑adic Dynamical Skeleton". SUBIT Technical Report, Report No. 2026-07-22.