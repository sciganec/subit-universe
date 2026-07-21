# SUBIT Universe

**A recursive semantic universe where the rule belongs to the state, truth is stability under evolution, and 64 archetypes map to the I-Ching hexagrams.**

```
┌─────────────────────────────────────────────────────────────┐
│  SUBIT_∞ = ( S_∞, ℛ, F, g, Ω, d_Ω, U )                      │
│                                                             │
│  S_∞ = νX.(X × X × X)        — recursive state space        │
│  ℛ    — rule space (internal to the state)                  │
│  F(s,ρ) = (f_ρ(s), g(ρ,s))   — evolution of state AND rule  │
│  Ω = {stable, metastable, cyclic, chaotic} — dynamic truth  │
│  d_Ω  — semantic ultrametric on trajectories                │
│  U    — universal interpreter (self-referential)            │
└─────────────────────────────────────────────────────────────┘
```

> **Core thesis:** *P is true ⟺ F(P) ⊆ P*.  
> Truth is not static correspondence — it is dynamic invariance.

---

## What is SUBIT?

SUBIT is a **self-referential dynamic system** that erases the boundary between data, program, and metaprogram:

| Classical System | SUBIT |
|:---|:---|
| Rule is external to state | Rule ρ is **part of** state ŝ = (s, ρ) |
| Truth is static (⊤/⊥) | Truth is **dynamic** (Ω-classifier) |
| Program and data are separate | Program = data = metaprogram |
| Evolution changes only state | Evolution changes **state and rule** |
| No internal interpreter | Universal object **U simulates everything** |

Three semantic coordinates — **WHO, WHERE, WHEN** — each taking one of four values, generate **64 archetypal states** isomorphic to the I-Ching hexagrams.

---

## Recent Experimental Results

SUBIT-TOPOS has been successfully applied to two major mathematical problems, yielding novel structural insights:

### 1. Jacobian Conjecture (Algebraic Geometry)

Using the SUBIT-TOPOS framework, we built an automated explorer for polynomial maps over various fields and rings. Key findings:
- **Characteristic-dependent anomalies:** Non‑injective maps with constant non‑zero Jacobian exist in 𝔽₂, 𝔽₃, and ℤ/4ℤ, but not in 𝔽₅, 𝔽₇, or characteristic‑0 samples.
- **Phase transition:** The relationship between local invertibility and global injectivity changes qualitatively as field characteristic varies.
- **Morphodynamic signatures:** Each polynomial rule receives a signature Φ(ρ) = (Ω, entropy, information retention, cycle complexity, etc.), enabling clustering and anomaly detection.

📂 **Lab:** `experiments/jacobian/` — see [`SUBIT-JACOBIAN_LAB_REPORT.md`](experiments/jacobian/jacobian_report.md) for full details.

### 2. Collatz Conjecture (Number Theory)

Instead of searching for counterexamples, we applied morphodynamic classification to the trajectory space of the Collatz map:
- **7 stable morphotypes** discovered from 2,919 trajectories (n ≤ 50,000).
- **Event genomes** (`U`, `D`, `P`, `R`, `S`) provide a symbolic language for trajectory structure.
- **Phylogenetic tree** reveals evolutionary relationships between morphotypes, with a central attractor (M5, 23.5%) and an extreme regime (M3, 5.1%).
- **Transition graph** shows that most trajectories flow through the central hub, with rare excursions into the extreme morphotype.

📂 **Atlas:** `experiments/collatz/` — see [`COLLATZ_MORPHODYNAMIC_ATLAS.md`](experiments/collatz/collatz_report.md) for the full analysis.

These experiments demonstrate that SUBIT-TOPOS is not a theorem prover, but a **morphodynamic discovery engine** that uncovers hidden structure in formal dynamical systems.

---

## Repository Structure

| Document | Purpose | Start Here If You... |
|:---|:---|:---|
| **[`SPECIFICATION.md`](SPECIFICATION.md)** | Full formal theory: recursive spaces, dynamics, Ω‑stability, metric, category, topos, type theory | Want the complete mathematical picture |
| **[`AXIOMS.md`](AXIOMS.md)** | 27 axioms (A1–A27), symbol table, reference map to specification | Need a quick reference or want to verify formal structure |
| **[`HEXAGRAMS.md`](HEXAGRAMS.md)** | Complete 64‑state table: binary ↔ hexagram glyph ↔ WHO/WHERE/WHEN coordinates | Care about the I‑Ching mapping or concrete state enumeration |
| **[`IMPLEMENTATION.md`](IMPLEMENTATION.md)** | Algorithms, pseudocode, Python sketches, testing strategy, roadmap | Want to build or simulate SUBIT |
| **[`experiments/jacobian/`](experiments/jacobian/)** | Jacobian Conjecture lab: polynomial map exploration, characteristic atlas, counterexample search | Are interested in algebraic geometry or the Jacobian problem |
| **[`experiments/collatz/`](experiments/collatz/)** | Collatz morphodynamic atlas: trajectory clustering, event genomes, phylogenetic tree | Are interested in number theory or structural analysis of iterated maps |
| **This file** | Entry point, motivation, navigation | Are new to the project |

---

## The 64 Archetypes

Every state is a 6‑bit word encoding three semantic coordinates:

```
b₁b₂ | b₃b₄ | b₅b₆  =  WHO | WHERE | WHEN

10 = ME / EAST / SPRING        (Yang-active)
11 = WE / SOUTH / SUMMER       (Yang-Yang)
01 = YOU / WEST / AUTUMN       (Yin-active)
00 = THEY / NORTH / WINTER     (Yin-passive)
```

Partitioned into two trigrams:

```
Lower Trigram = b₁b₂b₃  →  WHO + first bit of WHERE
Upper Trigram = b₄b₅b₆  →  second bit of WHERE + WHEN
```

Example: **䷀ (Hexagram 01)** = `111111` = WE + SOUTH + SUMMER = ☰ Heaven over ☰ Heaven.

Full table with all 64 glyphs, binaries, and semantic coordinates: **[`HEXAGRAMS.md`](HEXAGRAMS.md)**.

---

## Four Levels of Hierarchy

```
Level 0:  s = (α, β, γ)              — base state (64 archetypes, static)
Level 1:  ŝ = (α, β, γ, ρ)           — state with internal rule
Level 2:  F(ŝ) = (s', ρ')            — evolution of state AND rule
Level 3:  g(ρ, s) → ρ'               — meta‑evolution: rule changes itself
```

Classical automata have only Level 0 and fixed Level 2.  
SUBIT adds **self‑reference** through Levels 1 and 3.

---

## Key Formal Results

| Result | Statement | Location |
|:---|:---|:---|
| **Ω‑Algebra** | Ω forms a Heyting algebra (not Boolean); excluded middle fails | [`SPECIFICATION.md`](SPECIFICATION.md) §3.4 |
| **Ultrametric** | d_Ω is an ultrametric; space is totally disconnected (clopen balls) | [`SPECIFICATION.md`](SPECIFICATION.md) §4 |
| **CCC** | SUBIT is a cartesian closed category with products and exponentials | [`SPECIFICATION.md`](SPECIFICATION.md) §5 |
| **Universal Object** | ∃ U ∈ SUBIT: ∀X ∃ φ: U → X (internal interpreter) | [`SPECIFICATION.md`](SPECIFICATION.md) §5.6 |
| **Internal Simulation** | Any finite automaton embeds into SUBIT⁺ | [`SPECIFICATION.md`](SPECIFICATION.md) §B.5 |
| **Dynamic Type Theory** | Types are stability classes; □A, ◇A, ◯A are modalities | [`SPECIFICATION.md`](SPECIFICATION.md) §B.4 |

---

## The Ω Classifier: Four Values of Truth

| Value | Condition | Logical Reading |
|:---|:---|:---|
| **stable** | F(P) ⊆ P and F⁻¹(P) ⊆ P | Necessary truth: □A |
| **metastable** | F(P) ⊆ P, F⁻¹(P) ⊄ P | Actual but not necessary: A ∧ ¬□A |
| **cyclic** | ∃k > 0: Fᵏ(P) = P | Orbital: ◯A ∧ ¬□A |
| **chaotic** | ∄k: Fᵏ(P) ⊆ P | Unstable: ¬◇A |

Partial order: `chaotic < cyclic < metastable < stable`

Conjunction and disjunction tables + Heyting negation: [`SPECIFICATION.md`](SPECIFICATION.md) §3.4 or [`AXIOMS.md`](AXIOMS.md) §3.

---

## Quick Start

### 1. Understand the Structure
Read [`HEXAGRAMS.md`](HEXAGRAMS.md) to see how 64 states map to I‑Ching.

### 2. Read the Formal Theory
[`SPECIFICATION.md`](SPECIFICATION.md) walks through:
- Base definitions (§I)
- Dynamics and trajectories (§II)
- Ω‑stability and truth (§III)
- Semantic metric (§IV)
- Category SUBIT (§V)
- SUBIT‑TOPOS extension (§B)

### 3. Check the Axioms
[`AXIOMS.md`](AXIOMS.md) lists all 27 axioms with cross‑references.

### 4. Explore the Experiments
- **Jacobian:** run `experiments/jacobian/subit_jacobian_lab.py` to reproduce the characteristic atlas.
- **Collatz:** run `experiments/collatz/collatz_genome_atlas.py` to build the morphodynamic atlas, then `experiments/collatz/collatz_morphogenome.py` for the phylogenetic tree.

### 5. Build Something
[`IMPLEMENTATION.md`](IMPLEMENTATION.md) provides:
- Algorithm for Ω‑class detection
- Semantic distance computation
- Python pseudocode for SUBIT‑64
- Roadmap from prototype to self‑referential U

---

## Mathematical Lineage

```
I‑Ching (64 hexagrams)  ──┐
Belnap bilattice (FOUR)  ├──►  SUBIT‑64  ──►  SUBIT⁺  ──►  SUBIT‑TOPOS
Coalgebraic fixed points   ──┘   (finite)      (dynamic)      (CCC, proto‑topos)
```

Analogies:

| SUBIT | Analog |
|:---|:---|
| State s⁺ | λ‑term |
| Rule ρ | λ‑function |
| F(s⁺) | β‑reduction |
| U | Universal Turing machine / λ‑interpreter |
| Ω | Heyting‑algebraic subobject classifier |
| d_Ω | p‑adic metric on computation trees |

---

## Open Problems

1. **Is SUBIT_∞ a topos?** — Does Ω satisfy full subobject classifier axioms?
2. **Semantic completeness** — Can every rule‑changing system be realized in SUBIT?
3. **Fractal boundary** — Is the chaotic rule set fractionally‑dimensional?
4. **Fixed point of interpretation** — Does absolute attractor s* exist where F(s*,ρ) = (s*,ρ)?
5. **Meta‑evolution g** — What is the natural/canonical choice for rule‑changing operator?
6. **Collatz morphogenetic conjecture** — Is the 7‑morphotype structure stable for all n? Can we prove that all trajectories eventually enter the canonical morphotypes that lead to 1?

See [`SPECIFICATION.md`](SPECIFICATION.md) §IX and [`IMPLEMENTATION.md`](IMPLEMENTATION.md) §8.

---

## License

MIT