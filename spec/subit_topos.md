# SUBIT-TOPOS Core v0.1 — Architectural Specification

**A Morphodynamic Framework for Exploration of Rule‑Defined Formal Systems**  
*Version 0.1 · 2026-07-20*  
*Status: Draft Specification*

---

## 0. Preamble

### 0.1. What This Document Is

This is the **core architectural specification** of SUBIT-TOPOS — not as a "mathematical solver," but as a **framework for exploring formal systems through evolving transformation rules, trajectory classification, and structural signatures.**

The framework is designed to be:
- **Domain‑agnostic** — can be instantiated for automata, graphs, polynomials, cellular automata, groups, or any finite formal system.
- **Self‑modifying** — the rule is part of the state; evolution changes both state and rule.
- **Exploratory** — the goal is to build **atlases of operator spaces**, not to solve specific problems.

### 0.2. Core Thesis

> **SUBIT-TOPOS explores the space of transformations over formal objects and constructs morphodynamic maps of transitions between structural regimes.**

This is fundamentally different from traditional computational search:
- Traditional: **Object → Property → Verification**
- SUBIT: **Space of objects → Space of operators → Operator evolution → Atlases of regimes → Hypotheses**

### 0.3. Domain

The framework operates on **finite or recursively enumerable formal systems** where:
- States can be encoded as finite objects.
- Rules can be defined as functions from states to states.
- Meta‑rules can change the rules themselves.

---

## 1. Core Architecture

### 1.1. Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    SUBIT-TOPOS CORE v0.1                       │
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌──────────────────┐   │
│  │   State S   │───▶│    Rule R   │───▶│   Transition F   │   │
│  │  (encoded   │    │  (operator  │    │   F(s,ρ) =       │   │
│  │   object)   │    │   on S)     │    │   (ρ(s), g(ρ,s)) │   │
│  └─────────────┘    └─────────────┘    └─────────┬────────┘   │
│                                                    │            │
│                                                    ▼            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Ω‑Classifier                               │  │
│  │  Classifies trajectories as:                            │  │
│  │  STABLE │ METASTABLE │ CYCLIC │ CHAOTIC                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Signature Φ(ρ)                                  │  │
│  │  (Ω, H, I, C, D, T, ...)  ← morphodynamic "fingerprint" │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Meta‑Signature Ψ(ℛ)                             │  │
│  │  Landscape of the entire rule space                     │  │
│  │  (phase transitions, clusters, boundaries)              │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2. The RuleVM Abstraction

The core does not know what a "polynomial" or "graph" is. It operates on abstract entities:

| Component | Description | Interface |
|-----------|-------------|-----------|
| **State `s ∈ S`** | Encoded formal object | `s: bytes` |
| **Rule `ρ ∈ ℛ`** | Operator that transforms states | `ρ: S → S` |
| **Meta‑rule `g`** | Operator that transforms rules | `g: ℛ × S → ℛ` |
| **Transition `F`** | Combined evolution | `F(s,ρ) = (ρ(s), g(ρ,s))` |

All domain‑specific logic (polynomial evaluation, graph operations, automaton steps) is **encapsulated in plugins** that implement this interface.

---

## 2. Formal Definitions

### 2.1. State Space

**Definition 2.1 (State Space).**  
Let `S` be a finite set of **states**, each representing an encoded formal object.

```
S = {0, 1, 2, ..., N−1},   N ∈ ℕ
```

For infinite domains, `S` can be defined recursively as the greatest fixed point:

```
S∞ = ν X . (X × X × X)
```

where `ν` denotes the greatest fixed point (coinductive).

---

### 2.2. Rule Space

**Definition 2.2 (Rule Space).**  
Let `ℛ` be a finite set of **rules**, each being a function:

```
ρ: S → S
```

Rules are admissible if they are computable and can be represented finitely (e.g., lookup tables, polynomial expressions, rewrite systems).

---

### 2.3. Extended State

**Definition 2.3 (Extended State).**  
An extended state is a pair:

```
ŝ = (s, ρ) ∈ S × ℛ
```

The rule is **internal** to the state — not external. This is the self‑reference mechanism.

---

### 2.4. Evolution Operator

**Definition 2.4 (Evolution Operator).**  
The full evolution operator `F` is:

```
F: S × ℛ  →  S × ℛ
```

with:

```
F(s, ρ) = ( ρ(s),  g(ρ, s) )
```

where:
- `ρ(s)` is the **state transition** (application of the active rule),
- `g(ρ, s)` is the **meta‑transition** (evolution of the rule itself).

**Axiom 2.1 (Totality).**  
`F` is total on `S × ℛ`. Every extended state has a defined next state.

---

### 2.5. Trajectory

**Definition 2.5 (Trajectory).**  
For an initial extended state `ŝ₀ = (s₀, ρ₀)`, the trajectory is:

```
τ(ŝ₀) = (ŝ₀, ŝ₁, ŝ₂, …)
```

where:

```
ŝₙ₊₁ = F(ŝₙ)
```

A trajectory is **finite** if it enters a cycle; **infinite** otherwise.

---

## 3. Ω‑Classifier (Dynamic Regime Classification)

### 3.1. Definition

**Definition 3.1 (Ω‑Classifier).**  
The Ω‑classifier assigns to each trajectory one of four dynamic regimes:

```
Ω = { STABLE, METASTABLE, CYCLIC, CHAOTIC }
```

### 3.2. Classification Criteria

| Class | Condition | Interpretation |
|-------|-----------|----------------|
| **STABLE** | `F(ŝ) = ŝ` (fixed point) | No dynamics; trivial regime |
| **METASTABLE** | `Fᵏ(ŝ) = ŝ` for some `k > 1` | Periodic; system oscillates |
| **CYCLIC** | Trajectory enters a cycle of length `L > 1` after a transient | Repetitive, predictable |
| **CHAOTIC** | No repetition within `N_max` steps | High dynamic complexity — **candidate for analysis** |

### 3.3. Important Refinement

> **CHAOTIC ≠ Interesting.**  
> CHAOTIC indicates **high dynamic complexity**, which makes a trajectory a **candidate** for further analysis, not a guarantee of structural novelty.

CHAOTIC can arise from:
- Genuine structural complexity.
- Poorly chosen metric.
- Noise in the generator.
- Inefficient operator design.

**Therefore:**

```
CHAOTIC  ⇒  Candidate
CHAOTIC  ⇏  Interesting
```

---

## 4. Signature Φ(ρ) — The Morphodynamic Fingerprint

### 4.1. Motivation

The true innovation of SUBIT-TOPOS is **not** the evolution operator `F`, but the **signature function**:

```
Φ: ℛ → ℝᵏ
```

which maps each rule to a **multidimensional structural descriptor**.

This enables **comparison of rules themselves**, not just their outputs.

### 4.2. Signature Components

For a rule `ρ`, define:

```
Φ(ρ) = ( Ω, H, I, C, D, T, … )
```

| Component | Symbol | Definition |
|-----------|--------|------------|
| **Ω‑class** | `Ω` | From trajectory classification |
| **Entropy** | `H` | `H = −∑ pᵢ log pᵢ` (spread of outputs) |
| **Information Retention** | `I` | `I = |Im(ρ)| / |S|` (fraction of domain covered) |
| **Cycle Complexity** | `C` | Length of the longest orbit cycle |
| **Structural Distance** | `D` | Distance from identity (or from canonical rules) |
| **Evolution Time** | `T` | Steps to reach cycle or stability |

### 4.3. Signature Usage

Signatures enable:

1. **Clustering** — group similar rules in signature space.
2. **Anomaly detection** — identify rules with unusual signatures.
3. **Landscape mapping** — visualize the structure of `ℛ`.
4. **Predictive selection** — use signatures to guide meta‑evolution `g`.

---

## 5. Meta‑Signature Ψ(ℛ) — Landscape of Rule Space

### 5.1. Definition

**Definition 5.1 (Meta‑Signature).**  
The meta‑signature describes the **distribution and structure of signatures across the entire rule space**:

```
Ψ(ℛ) = ( dimension, clusters, phase_transitions, topology )
```

### 5.2. Components

| Component | Description |
|-----------|-------------|
| **Rule Count** | `|ℛ|` |
| **Class Distribution** | Proportion of STABLE / METASTABLE / CYCLIC / CHAOTIC |
| **Cluster Structure** | Number and separation of signature clusters |
| **Phase Transitions** | Sharp changes in `Φ` across parameter boundaries |
| **Landscape Topology** | Connectedness, holes, high‑dimensional features |

### 5.3. Example (Polynomial Domain)

```
Polynomial Space (degree ≤ 3, coeff ∈ [-2,2], char 2)
─────────────────────────────────────────────────────────
|ℛ| = 1024

Stable:     12%   (128 rules)
Metastable:  8%   ( 82 rules)
Cyclic:      5%   ( 51 rules)
Chaotic:    75%   (763 rules)

Phase transition: degree 2 → 3
  — Information retention drops from 0.82 to 0.61
  — Entropy increases from 0.44 to 0.72
```

---

## 6. Architectural Interfaces (API)

### 6.1. Core Plugin Interface

```python
# Domain plugin must implement these:

class State:
    """Encoded formal object."""
    def encode(self) -> bytes: ...

class Rule:
    """Operator on states."""
    def apply(self, s: State) -> State: ...

class MetaRule:
    """Operator on rules."""
    def evolve(self, rho: Rule, s: State) -> Rule: ...

class DomainPlugin:
    """Domain‑specific logic."""
    def generate_state(self) -> State: ...
    def generate_rule(self) -> Rule: ...
    def signature(self, rho: Rule) -> Signature: ...
```

### 6.2. Explorer API

```python
class SUBITExplorer:
    def __init__(self, plugin: DomainPlugin):
        self.plugin = plugin

    def trajectory(self, s0: State, rho0: Rule, max_steps: int) -> Trajectory: ...

    def omega_classify(self, traj: Trajectory) -> Omega: ...

    def signature(self, rho: Rule) -> Signature: ...

    def atlas(self, num_rules: int) -> MetaSignature: ...

    def explore(self, num_trials: int) -> AtlasReport: ...
```

### 6.3. Plugin Registration

```python
# Register a new domain without modifying the core:

core.register_plugin("polynomial", PolynomialPlugin())
core.register_plugin("graph", GraphPlugin())
core.register_plugin("automaton", AutomatonPlugin())
```

---

## 7. Instantiation Guidelines

### 7.1. Best‑Fit Domains (⭐⭐⭐⭐⭐)

| Domain | Why It Fits | Key Challenge |
|--------|-------------|---------------|
| **Finite Automata** | State = transition table; Rule = minimization/equivalence; natural Ω‑classification | Explosion of state space |
| **Graphs** | State = adjacency matrix; Rule = rewiring; natural structural signatures | Isomorphism recognition |
| **Cellular Automata** | State = configuration; Rule = CA rule; evolution already matches | Large state spaces |
| **Finite Groups** | State = Cayley table; Rule = subgroup generation; natural subgroup lattice | Group generation |

### 7.2. Moderate‑Fit Domains (⭐⭐⭐)

| Domain | Why It Fits | Key Challenge |
|--------|-------------|---------------|
| **Polynomial Maps** | State = coefficients; Rule = Jacobian/inversion; clear structural invariant | Need symbolic extension |
| **Rewrite Systems** | State = term; Rule = rewrite rule; natural term‑rewriting dynamics | Termination checking |

### 7.3. Challenging Domains (⭐⭐)

| Domain | Why It's Hard | Mitigation |
|--------|---------------|------------|
| **Collatz (number theory)** | Infinite state space; requires recursive S∞ | Use S∞ encoding |
| **General algebraic geometry** | Continuous; requires symbolic methods | Hybrid numeric‑symbolic |

---

## 8. Research Value and Positioning

### 8.1. What SUBIT-TOPOS Is

> **A framework for constructing morphodynamic atlases of formal operator spaces.**

It is:
- **Exploratory** — generates hypotheses, not proofs.
- **Domain‑agnostic** — same core applies to automata, graphs, groups, polynomials.
- **Self‑modifying** — rules evolve; meta‑evolution is internal.
- **Signature‑based** — compares rules via structural fingerprints, not just their outputs.

### 8.2. What SUBIT-TOPOS Is Not

- **Not** a general theorem prover.
- **Not** a black‑box solver for open problems.
- **Not** a substitute for symbolic verification.

### 8.3. The Research Pipeline

```
1. Instantiate SUBIT-TOPOS for a formal domain.
2. Explore the rule space via chaotic trajectories.
3. Build signatures Φ(ρ) for discovered rules.
4. Construct meta‑signature Ψ(ℛ) — the landscape.
5. Detect anomalies, phase transitions, clusters.
6. Extract candidates for further verification (symbolic, manual).
7. Generate hypotheses from structural patterns.
```

### 8.4. Positioning Statement

> **SUBIT-TOPOS: A Morphodynamic Framework for Exploration of Rule‑Defined Formal Systems**

We introduce a framework for exploring finite and recursively enumerable formal systems through evolving transformation rules, trajectory classification, and structural signatures. Instead of directly solving target problems, SUBIT-TOPOS constructs morphodynamic atlases of operator spaces, identifying regions of high structural complexity and generating candidates for further verification.

---

## 9. Summary: The Core Abstraction

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SUBIT-TOPOS CORE v0.1                               │
│                                                                         │
│   State   ───▶   Rule   ───▶   Evolution   ───▶   Ω‑Class             │
│    (s)           (ρ)          F(s,ρ)               Ω                   │
│     │             │             │                    │                   │
│     ▼             ▼             ▼                    ▼                   │
│  Encoded     Operator    Self‑modifying       Dynamic Regime            │
│  Formal     on S         dynamics             Classification            │
│  Object                                    (STABLE / METASTABLE /       │
│                                              CYCLIC / CHAOTIC)         │
│                                                   │                     │
│                                                   ▼                     │
│                              Signature Φ(ρ)                             │
│                              (Ω, H, I, C, D, T)                         │
│                              ▲                                          │
│                              │                                          │
│                              │                                          │
│                         Meta‑Signature Ψ(ℛ)                           │
│                         (Landscape of Rule Space)                      │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Domain Plugin Interface:                                      │   │
│  │  State, Rule, MetaRule, Signature                              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Appendix A: Formal Notation Reference (Unicode)

| Symbol | Unicode | Meaning |
|--------|---------|---------|
| `S` | U+0053 | State space |
| `ℛ` | U+211B | Rule space |
| `ŝ` | U+015D + U+0302 | Extended state `(s, ρ)` |
| `F` | U+0046 | Evolution operator |
| `ρ` | U+03C1 | Active rule |
| `g` | U+0067 | Meta‑evolution function |
| `τ` | U+03C4 | Trajectory |
| `Ω` | U+03A9 | Dynamic classifier |
| `Φ` | U+03A6 | Signature of a rule |
| `Ψ` | U+03A8 | Meta‑signature of rule space |
| `ℕ` | U+2115 | Natural numbers |
| `ℝ` | U+211D | Real numbers |
| `→` | U+2192 | Function arrow |
| `∈` | U+2208 | Element of |
| `×` | U+00D7 | Cartesian product |
| `∑` | U+2211 | Summation |
| `∏` | U+220F | Product |
| `ν` | U+03BD | Greatest fixed point (coinduction) |

---

## Appendix B: Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2026-07-20 | Initial specification: core architecture, Ω‑classifier, signature system, domain plugin interface. |

---

*This document is part of the SUBIT-TOPOS research project. All mathematical formulas are rendered in Unicode for plain‑text compatibility and universal readability.*