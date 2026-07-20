# SUBIT Universe — Formal Specification

**Version 2.0 · 2026**

---

## I. Primitives

### 1.1 Alphabet

Finite set of primitive markers:

```
A = { a₁, a₂, …, aₖ }
```

Minimal implementation (SUBIT-64):

```
A_WHO   = { ME, WE, YOU, THEY }              (4)
A_WHERE = { EAST, SOUTH, WEST, NORTH }       (4)
A_WHEN  = { SPRING, SUMMER, AUTUMN, WINTER } (4)
```

Total atoms: |A| = 4³ = 64.

Binary encoding (example): ME = 10, EAST = 10, SPRING = 10.

### 1.2 State Space (Recursive)

**Definition 1.1.** State space S_∞ is the greatest coalgebraic fixed point:

```
S_∞ = νX. (X × X × X)
```

Explicitly: S_∞ is the set of all finite and infinite trees of depth ≤ ω, where each node has exactly three children, and leaves belong to A. Bisimilarity collapse (Aczel, 1988) allows cycles.

Notation: element s ∈ S_∞ written as triple:

```
s = ( w, x, y )
```

where w, x, y ∈ S_∞. If s is a leaf (primitive marker), then w, x, y are interpreted as fictitious (or identical to s itself).

### 1.3 Rule Space

**Definition 1.2.** Rule space ℛ is the set of all admissible functions f: S_∞ → S_∞, i.e., computable in the extended sense (e.g., given by finite description).

For practical purposes ℛ may be restricted to functions depending only on finite recursion depth (approximation).

### 1.4 Extended State

**Definition 1.3.** Extended state is a pair:

```
ŝ = ( s, ρ ) ∈ S_∞ × ℛ
```

where s is the semantic state and ρ is the active evolution rule.

---

## II. Dynamics

### 2.1 Evolution Operator

**Definition 2.1.** Evolution operator F: S_∞ × ℛ → S_∞ × ℛ is defined as:

```
F( s, ρ ) = ( f_ρ(s),  g(ρ, s) )
```

where:
- f_ρ: S_∞ → S_∞ — application of rule ρ to state s;
- g: ℛ × S_∞ → ℛ — meta-evolution function (rule change).

**Axiom 2.1 (Determinism).** F is a total function (defined for all (s, ρ)).

### 2.2 Trajectories

**Definition 2.2.** Trajectory (orbit) of extended state ŝ₀ is the sequence:

```
τ( ŝ₀ ) = ( ŝ₀, ŝ₁, ŝ₂, … )
```

where ŝ_{n+1} = F( ŝ_n ) for all n ≥ 0.

### 2.3 Projections

For convenience, define projections:

```
π_S( ŝ ) = s
π_ℛ( ŝ ) = ρ
```

Then evolution can be written as:

```
π_S( ŝ_{n+1} ) = f_{ π_ℛ(ŝ_n) }( π_S(ŝ_n) )
π_ℛ( ŝ_{n+1} ) = g( π_ℛ(ŝ_n), π_S(ŝ_n) )
```

---

## III. Ω-Stability and Truth

### 3.1 Dynamic Classifier

**Definition 3.1.** Ω-classifier is the set of four values:

```
Ω = { STABLE, METASTABLE, CYCLIC, CHAOTIC }
```

### 3.2 Classification of Sets

Let P ⊆ S_∞ × ℛ be an arbitrary set of extended states.

**Definition 3.2.** Stability class of P is defined by:

1. **STABLE** if F(P) ⊆ P.
2. **METASTABLE** if F(P) ⊆ P, but P ⊈ F(P).
3. **CYCLIC** if ∃ k > 0 such that Fᵏ(P) = P, and neither of the above holds.
4. **CHAOTIC** — in all other cases.

### 3.3 Semantic Truth

**Definition 3.3 (Truth).** Proposition (set of states) P is true if and only if it is stable:

```
P is true  ⟺  F(P) ⊆ P
```

**Remark.** This definition requires no external observer — it is an internal criterion derived from system dynamics. Truth becomes a dynamic invariant, not static correspondence.

### 3.4 Ω Algebra

**Theorem 3.1.** Ω with operations ∧, ∨, ¬ defined below forms a Heyting algebra (not Boolean).

**Conjunction ∧:**

| ∧ | STABLE | METASTABLE | CYCLIC | CHAOTIC |
|---|--------|------------|--------|---------|
| STABLE | STABLE | METASTABLE | CYCLIC | CHAOTIC |
| METASTABLE | METASTABLE | METASTABLE | CYCLIC | CHAOTIC |
| CYCLIC | CYCLIC | CYCLIC | CYCLIC | CHAOTIC |
| CHAOTIC | CHAOTIC | CHAOTIC | CHAOTIC | CHAOTIC |

**Disjunction ∨:**

| ∨ | STABLE | METASTABLE | CYCLIC | CHAOTIC |
|---|--------|------------|--------|---------|
| STABLE | STABLE | STABLE | STABLE | STABLE |
| METASTABLE | STABLE | METASTABLE | METASTABLE | METASTABLE |
| CYCLIC | STABLE | METASTABLE | CYCLIC | CYCLIC |
| CHAOTIC | STABLE | METASTABLE | CYCLIC | CHAOTIC |

**Negation ¬a** is defined as a → CHAOTIC in the Heyting sense.

**Consequence:** Law of excluded middle a ∨ ¬a = STABLE fails for a = METASTABLE (since METASTABLE ∨ ¬METASTABLE = METASTABLE ∨ CYCLIC = CYCLIC ≠ STABLE).

---

## IV. Semantic Metric

### 4.1 Metric Definition

**Definition 4.1.** Let δ: (S_∞ × ℛ)² → {0,1} be the divergence function:

```
δ( ŝ, t̂ ) = 0, if ŝ and t̂ belong to the same Ω-class,
δ( ŝ, t̂ ) = 1, otherwise.
```

**Definition 4.2.** Semantic metric d_Ω: (S_∞ × ℛ)² → [0, 2] is defined as:

```
d_Ω( ŝ, t̂ ) = Σ_{n=0}^{∞} 2^{-n} · δ( Fⁿ(ŝ), Fⁿ(t̂) )
```

### 4.2 Properties

**Theorem 4.1.** d_Ω is an ultrametric:

1. d_Ω(ŝ, t̂) = 0 ⟺ ŝ = t̂ (indistinguishability by Ω-classes at all steps);
2. d_Ω(ŝ, t̂) = d_Ω(t̂, ŝ) (symmetry);
3. d_Ω(ŝ, û) ≤ max( d_Ω(ŝ, t̂), d_Ω(t̂, û) ) (strong triangle inequality).

**Proof (sketch).** Property (3) follows from δ taking only values 0/1, and the sum with weights 2^{-n} preserves ultrametricity. Details — by analogy with p-adic metrics.

**Theorem 4.2.** Space (S_∞ × ℛ, d_Ω) is totally disconnected: every ball is simultaneously open and closed (clopen). Hence the topology is zero-dimensional.

---

## V. Category SUBIT

### 5.1 Objects

**Definition 5.1.** Object of category SUBIT is a system:

```
X = ( S_X, ℛ_X, F_X, g_X )
```

where:
- S_X ⊆ S_∞ — state space (may be proper subspace);
- ℛ_X ⊆ ℛ — rule space;
- F_X: S_X × ℛ_X → S_X × ℛ_X — restriction of global F to X;
- g_X: ℛ_X × S_X → ℛ_X — restriction of global meta-evolution.

**Axiom 5.1 (Closure).** F_X(S_X × ℛ_X) ⊆ S_X × ℛ_X.

### 5.2 Morphisms

**Definition 5.2.** Morphism φ: X → Y is a pair of maps:

```
φ = ( φ_S, φ_ℛ )
```

where:
- φ_S: S_X → S_Y;
- φ_ℛ: ℛ_X → ℛ_Y;

satisfying dynamic compatibility:

```
φ_S( π_S( F_X(ŝ) ) ) = π_S( F_Y( φ_S(π_S(ŝ)), φ_ℛ(π_ℛ(ŝ)) ) )
```

for all ŝ ∈ S_X × ℛ_X. In other words, the diagram commutes:

```
X  --F_X-->  X
|            |
φ            φ
↓            ↓
Y  --F_Y-->  Y
```

### 5.3 Composition and Identity

**Definition 5.3.** Composition ψ ∘ φ is defined componentwise:

```
(ψ ∘ φ)_S = ψ_S ∘ φ_S
(ψ ∘ φ)_ℛ = ψ_ℛ ∘ φ_ℛ
```

Identity morphism id_X = ( id_{S_X}, id_{ℛ_X} ).

**Theorem 5.1.** SUBIT is a category (associativity holds, identities are neutral).

### 5.4 Special Objects

**Terminal object 1:** S_1 = {*} (single state), ℛ_1 = {id} (single identity rule). For any X there exists exactly one morphism X → 1.

**Product X × Y:** S_{X×Y} = S_X × S_Y, ℛ_{X×Y} = ℛ_X × ℛ_Y, F_{X×Y}( (s₁,s₂), (ρ₁,ρ₂) ) = ( F_X(s₁,ρ₁), F_Y(s₂,ρ₂) ).

**Theorem 5.2.** SUBIT has finite products.

### 5.5 Exponentials

**Definition 5.4.** Exponential Y^X is the object such that:
- S_{Y^X} = { morphisms from X × 1 to Y } (i.e., dynamically compatible maps, parameterized);
- ℛ_{Y^X} is defined via evaluation map.

**Theorem 5.3 (CCC).** SUBIT is a cartesian closed category. Consequence: for any X, Y, Z there exists a natural isomorphism:

```
Hom( X × Y, Z ) ≅ Hom( X, Z^Y )
```

### 5.6 Universal Object

**Theorem 5.4 (Existence of U).** There exists object U ∈ SUBIT which is universal: for any X ∈ SUBIT there exists morphism φ_X: U → X.

**Construction.** U is defined as:
- S_U = S_∞ (entire state space);
- ℛ_U = ℛ (all admissible rules);
- F_U — global evolution operator;
- g_U — global meta-evolution.

Embeddings φ_X are built via encoding states and rules of X into corresponding subsets of S_∞ and ℛ.

**Theorem 5.5.** U is an internal interpreter: it can simulate any system X. This is the analog of a universal Turing machine in the category SUBIT.

---

## VI. Axiomatic System

| Axiom | Statement |
|-------|-----------|
| **A1** (Recursion) | S_∞ = νX.(X × X × X) |
| **A2** (Internal Rule) | State always includes active rule: ŝ = (s, ρ) |
| **A3** (Evolution) | F(s, ρ) = ( f_ρ(s), g(ρ, s) ) |
| **A4** (Totality) | F is defined for all (s, ρ) |
| **A5** (Ω-Classification) | Ω = {STABLE, METASTABLE, CYCLIC, CHAOTIC} with operations from §3.4 |
| **A6** (Truth) | P is true ⟺ F(P) ⊆ P |
| **A7** (Metric) | d_Ω(ŝ, t̂) = Σ 2^{-n} δ(Fⁿ(ŝ), Fⁿ(t̂)) |
| **A8** (Category) | SUBIT is a cartesian closed category with terminal object, products, and exponentials |
| **A9** (Universality) | ∃ object U such that ∀X ∃ φ: U → X |

---

## VII. Constructive Procedures

### 7.1 Computing Ω-Class (Finite Approximation)

**Input:** ŝ₀ = (s₀, ρ₀), where s₀ has finite recursion depth d, and ρ₀ is given by finite description.

**Algorithm:**
1. Initialize visited ← ∅.
2. For n = 0, 1, …, N_max:
   - If ŝ_n ∈ visited, then cycle found of length L = n - visited(ŝ_n).
     - If L = 1: return STABLE.
     - If L ≤ L_thresh (e.g., 8): return CYCLIC.
     - If L > L_thresh: return METASTABLE.
   - Add ŝ_n to visited.
   - Compute ŝ_{n+1} = F(ŝ_n).
3. If N_max reached without repetition: return CHAOTIC.

### 7.2 Computing Semantic Distance

**Input:** ŝ, t̂, maximum depth K.

```
d ← 0
for n = 0 to K:
    if Ω(ŝ_n) ≠ Ω(t̂_n):
        d ← d + 2^{-n}
    ŝ_{n+1} ← F(ŝ_n)
    t̂_{n+1} ← F(t̂_n)
return d
```

For K → ∞ we obtain approximation of d_Ω.

### 7.3 Constructing Universal Object U

U is realized as an interpreter:
- State of U — encoded representation of arbitrary system X.
- Rule of U — universal function eval, which:
  - takes code (s, ρ) of system X;
  - computes f_ρ(s) (simulation of one step of X);
  - returns code of new state.

**Theorem 7.1.** Such U satisfies the universality axiom.

---

## VIII. Summary Formula

SUBIT universe is defined by the tuple:

```
SUBIT_∞ = ( S_∞, ℛ, F, g, Ω, d_Ω, U )
```

where:
- S_∞ = νX.(X × X × X) — recursive state space;
- ℛ — rule space (functions S_∞ → S_∞);
- F(s, ρ) = ( f_ρ(s), g(ρ, s) ) — evolution operator;
- g — meta-evolution of rules;
- Ω = {STABLE, METASTABLE, CYCLIC, CHAOTIC} — dynamic stability classifier;
- d_Ω — semantic ultrametric;
- U — universal interpreter object.

**Central Thesis:** In this universe:
- The rule belongs to the state.
- Truth is defined by stability: F(P) ⊆ P.
- Distance measures trajectory divergence.
- A universal interpreter exists.
- The category is cartesian closed (exponentials of meaning).

---

## IX. Open Problems and Hypotheses

**Hypothesis 1 (Semantic Completeness).** Any system describable by changing rules is realizable as an object in SUBIT_∞.

**Hypothesis 2 (Fractal Boundary).** The set of rules ρ for which the trajectory of a fixed initial state s₀ is chaotic (CHAOTIC) forms a set with fractional Hausdorff dimension with respect to the natural topology on ℛ.

**Hypothesis 3 (Fixed Point of Interpretation).** There exists state s* such that F(s, ρ) = (s, ρ) — "absolute interpretation" that no longer changes.

**Open Question.** Is SUBIT_∞ a topos in the classical sense (i.e., does it have a subobject classifier)? Our Ω is a candidate but requires verification of axioms.

---

## Appendix A. SUBIT-64 Correspondence

Finite space SUBIT-64 (64 I-Ching hexagrams) embeds into S_∞ as the set of leaves at depth 1:

```
S_64 = { (w, x, y) | w, x, y ∈ A }
```

where A are primitive markers. Evolution F is restricted to S_64 if rules ρ are also restricted. Thus SUBIT-64 is a finite approximation of SUBIT_∞.

---

## Appendix B. SUBIT-TOPOS Extension

### B.1 Bilattice Base

Base set 𝔸 = {T, F, B, N} (Belnap bilattice) with two partial orders:
- Truth order: F <ₜ N <ₜ T, F <ₜ B <ₜ T
- Information order: N <ᵢ F <ᵢ B, N <ᵢ T <ᵢ B

### B.2 Bit Encoding

| Value | Binary | WHO | WHERE | WHEN |
|-------|--------|-----|-------|------|
| 10 | ME | EAST | SPRING |
| 11 | WE | SOUTH | SUMMER |
| 01 | YOU | WEST | AUTUMN |
| 00 | THEY | NORTH | WINTER |

### B.3 Hexagram Encoding

6-bit words b₁b₂b₃b₄b₅b₆ where:
- Lower trigram b₁b₂b₃ → WHO + first bit of WHERE
- Upper trigram b₄b₅b₆ → second bit of WHERE + WHEN

Trigram correspondence:
- 111 → Heaven (☰) → North-East
- 110 → Lake (☱) → East-East
- 101 → Fire (☲) → South-East
- 100 → Thunder (☳) → South-South
- 011 → Wind (☴) → South-West
- 010 → Water (☵) → West-West
- 001 → Mountain (☶) → North-West
- 000 → Earth (☷) → North-North

### B.4 Dynamic Type Theory

Judgment: Γ ⊢ t : A @ τ — in context Γ, state t has type A at evolution phase τ.

Modalities:
- □A — stable truth (necessary): F(A) ⊆ A
- ◇A — potential stabilization: ∃k: Fᵏ(s) ∈ A
- ◯A — cyclic return: ∃k > 0: Fᵏ(A) = A

Equality as attractor equivalence: s ~_F t ⟺ ∃k: Fᵏ(s) = Fᵏ(t).

### B.5 Internal Simulation Theorem

Any finite automaton (Q, δ) can be embedded into SUBIT⁺:
- States q ↦ s_q ∈ S₀
- Transitions δ(q, a) = q' ↦ F(s_q, ρ_a) = s_{q'}

SUBIT⁺ is a **conditionally universal simulation system**: universality is achieved not through infinity, but through **internal self-reference**.

---
