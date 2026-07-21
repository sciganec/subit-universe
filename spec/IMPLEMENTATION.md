# SUBIT — Implementation Notes

**Algorithms, pseudocode, and practical considerations for SUBIT-64 and SUBIT-∞**

---

## 1. Computing Ω-Class (Algorithm 7.1)

Detects stability class of a finite extended state by trajectory analysis.

### Pseudocode

```python
def omega_class(s_hat_0, N_max=1000, L_thresh=8):
    """
    s_hat_0: extended state (s_0, rho_0)
    N_max: maximum steps before declaring CHAOTIC
    L_thresh: cycle length threshold (METASTABLE vs CYCLIC)
    Returns: STABLE | METASTABLE | CYCLIC | CHAOTIC
    """
    visited = {}  # state -> first_visit_index
    
    for n in range(N_max + 1):
        s_hat_n = s_hat_0 if n == 0 else F(s_hat_{n-1})
        
        if s_hat_n in visited:
            L = n - visited[s_hat_n]
            
            if L == 1:
                return STABLE      # Fixed point: F(s) = s
            
            if L <= L_thresh:
                return CYCLIC      # Short cycle
            
            return METASTABLE      # Long cycle / quasi-periodic
        
        visited[s_hat_n] = n
    
    return CHAOTIC                   # No repetition within N_max
```

### Complexity
- Time: O(N_max) evaluations of F
- Space: O(N_max) for visited map
- For SUBIT-64 (finite): N_max = 64 suffices for exact classification

### Notes
- `L_thresh` is heuristic; for SUBIT-64, set to 8 (half of trigram space)
- In infinite S_∞, this is an approximation; exact classification may be undecidable

---

## 2. Computing Semantic Distance (Algorithm 7.2)

Computes ultrametric distance between two extended states up to depth K.

### Pseudocode

```python
def semantic_distance(s_hat, t_hat, K=20):
    """
    s_hat, t_hat: extended states
    K: maximum trajectory depth
    Returns: d_Omega in [0, 2]
    """
    d = 0.0
    
    for n in range(K + 1):
        # Evaluate at step n
        s_n = s_hat if n == 0 else F(s_{n-1})
        t_n = t_hat if n == 0 else F(t_{n-1})
        
        # Divergence check
        if omega_class_at_step(s_n) != omega_class_at_step(t_n):
            d += 2 ** (-n)
        
        # Prepare next step
        s_hat, t_hat = s_n, t_n  # (implicit: advance both trajectories)
    
    return d
```

### Properties
- d ∈ [0, 2] (geometric series with ratio 1/2)
- d = 0 iff both trajectories have identical Ω-class at every step
- Strong triangle inequality: d(s, u) ≤ max(d(s, t), d(t, u))

### Optimization
For SUBIT-64, precompute Ω-class for all 64 × |ℛ| extended states. Store in lookup table for O(1) divergence checks.

---

## 3. Constructing Universal Object U (Algorithm 7.3)

U is an interpreter that simulates any SUBIT-system X from within.

### Architecture

```python
class UniversalObject:
    """
    U = (S_U, R_U, F_U, g_U)
    S_U = encoded representations of arbitrary systems
    R_U = universal eval function
    """
    
    def __init__(self):
        self.S_U = []  # all encodable systems
        self.R_U = [self.eval_rule]
    
    def encode_system(self, X):
        """
        X = (S_X, R_X, F_X, g_X)
        Returns: code_X ∈ S_U
        """
        return {
            'states': [self.encode_state(s) for s in X.S_X],
            'rules': [self.encode_rule(rho) for rho in X.R_X],
            'F_X': self.encode_operator(X.F_X),
            'g_X': self.encode_meta(X.g_X)
        }
    
    def eval_rule(self, code_X, s_code, rho_code):
        """
        Simulate one step of X from within U
        """
        # Decode
        X = self.decode_system(code_X)
        s = self.decode_state(s_code)
        rho = self.decode_rule(rho_code)
        
        # Compute f_rho(s)
        s_next = X.F_X(s, rho)
        
        # Compute g(rho, s)
        rho_next = X.g_X(rho, s)
        
        # Re-encode
        return (self.encode_state(s_next), 
                self.encode_rule(rho_next))
    
    def F_U(self, u_state):
        """
        U's own evolution: interpret and step
        """
        code_X, s_code, rho_code = self.parse(u_state)
        return self.eval_rule(code_X, s_code, rho_code)
```

### Key Property
For any X ∈ SUBIT, there exists morphism φ_X: U → X such that:
```
φ_X ∘ F_U = F_X ∘ φ_X
```
(diagram commutes).

### Self-Reference
U can simulate itself by encoding its own code as a state:
```
U_code = U.encode_system(U)
```
This enables fixed-point constructions and meta-circular interpretation.

---

## 4. SUBIT-64: Concrete Implementation

### 4.1 State Encoding

```python
# 6-bit state: b1 b2 | b3 b4 | b5 b6
# WHO: b1b2, WHERE: b3b4, WHEN: b5b6

ENCODING = {
    'WHO':   {'ME': '10', 'WE': '11', 'YOU': '01', 'THEY': '00'},
    'WHERE': {'EAST': '10', 'SOUTH': '11', 'WEST': '01', 'NORTH': '00'},
    'WHEN':  {'SPRING': '10', 'SUMMER': '11', 'AUTUMN': '01', 'WINTER': '00'}
}

def state_to_bits(who, where, when):
    return ENCODING['WHO'][who] + ENCODING['WHERE'][where] + ENCODING['WHEN'][when]

def bits_to_hexagram(bits):
    """Map 6 bits to I-Ching hexagram (1-64)"""
    lower = bits[0:3]  # trigram 1
    upper = bits[3:6]  # trigram 2
    trigram_val = {
        '111': 1, '110': 2, '101': 3, '100': 4,
        '011': 5, '010': 6, '001': 7, '000': 8
    }
    return trigram_val[lower] * 8 + trigram_val[upper] - 8  # 1-64
```

### 4.2 Rule Space for SUBIT-64

Finite rule space: all functions S_64 → S_64.
```
|ℛ_64| = 64^64 ≈ 10^115
```
In practice, restrict to:
- **Local rules**: depend only on one coordinate
- **Linear rules**: bit-wise XOR/AND combinations
- **Cyclic rules**: permutation of 64 states

### 4.3 Example Rule: Seasonal Rotation

```python
def rule_seasonal_cycle(s):
    """Rotate WHEN: Spring→Summer→Autumn→Winter→Spring"""
    who, where, when = s  # unpack
    next_when = {
        'SPRING': 'SUMMER',
        'SUMMER': 'AUTUMN',
        'AUTUMN': 'WINTER',
        'WINTER': 'SPRING'
    }
    return (who, where, next_when[when])

# Meta-evolution: rule itself rotates
def g_seasonal(rho, s):
    return rho  # identity: rule doesn't change
```

### 4.4 Trajectory Analysis for SUBIT-64

```python
def analyze_trajectory(s0, rho0, g, max_steps=100):
    """
    Full trajectory with rule evolution
    """
    trajectory = [(s0, rho0)]
    s, rho = s0, rho0
    
    for _ in range(max_steps):
        s_next = rho(s)          # f_rho(s)
        rho_next = g(rho, s)     # meta-evolution
        trajectory.append((s_next, rho_next))
        s, rho = s_next, rho_next
        
        # Check for fixed point
        if s_next == s and rho_next == rho:
            return trajectory, 'STABLE'
    
    # Check for cycle in full state
    seen = {}
    for i, (s_i, rho_i) in enumerate(trajectory):
        key = (s_i, rho_i)
        if key in seen:
            cycle_len = i - seen[key]
            return trajectory, 'CYCLIC' if cycle_len <= 8 else 'METASTABLE'
        seen[key] = i
    
    return trajectory, 'CHAOTIC'
```

---

## 5. SUBIT-∞: Lazy Evaluation

For infinite S_∞, states are infinite trees. Use lazy/coinductive representation.

```python
from dataclasses import dataclass
from typing import Union, Callable

@dataclass
class State:
    """
    Lazy infinite state: either leaf (primitive) or triple (lazy children)
    """
    value: Union[str, Callable[[], tuple]]  # 'ME' | lambda: (State, State, State)
    
    def unfold(self, depth=0):
        """Force evaluation up to depth"""
        if isinstance(self.value, str):
            return self.value  # leaf
        if depth == 0:
            return '...'  # unevaluated
        w, x, y = self.value()
        return (
            w.unfold(depth - 1),
            x.unfold(depth - 1),
            y.unfold(depth - 1)
        )

def make_leaf(atom):
    return State(atom)

def make_node(f):
    """f: () -> (State, State, State)"""
    return State(f)
```

### Bisimilarity Check (Coinductive)

```python
def bisimilar(s, t, memo=None):
    """
    Check if two infinite states are bisimilar (equivalent under d_Omega = 0)
    """
    if memo is None:
        memo = set()
    
    if id(s) == id(t):
        return True
    
    if (id(s), id(t)) in memo:
        return True  # already checked, assume ok (coinduction)
    
    memo.add((id(s), id(t)))
    
    # Both leaves
    if isinstance(s.value, str) and isinstance(t.value, str):
        return s.value == t.value
    
    # Both nodes
    if callable(s.value) and callable(t.value):
        sw, sx, sy = s.value()
        tw, tx, ty = t.value()
        return (bisimilar(sw, tw, memo) and
                bisimilar(sx, tx, memo) and
                bisimilar(sy, ty, memo))
    
    return False
```

---

## 6. Ω-Algebra Operations

```python
# Ω lattice operations

OMEGA = ['CHAOTIC', 'CYCLIC', 'METASTABLE', 'STABLE']

def omega_leq(a, b):
    """Partial order: chaotic < cyclic < metastable < stable"""
    return OMEGA.index(a) <= OMEGA.index(b)

def omega_and(a, b):
    """Meet (conjunction)"""
    AND_TABLE = {
        ('STABLE', 'STABLE'): 'STABLE',
        ('STABLE', 'METASTABLE'): 'METASTABLE',
        ('STABLE', 'CYCLIC'): 'CYCLIC',
        ('METASTABLE', 'METASTABLE'): 'METASTABLE',
        ('METASTABLE', 'CYCLIC'): 'CYCLIC',
        ('CYCLIC', 'CYCLIC'): 'CYCLIC',
    }
    key = tuple(sorted([a, b], key=OMEGA.index))
    return AND_TABLE.get(key, 'CHAOTIC')

def omega_or(a, b):
    """Join (disjunction)"""
    OR_TABLE = {
        ('STABLE', 'STABLE'): 'STABLE',
        ('STABLE', 'METASTABLE'): 'STABLE',
        ('STABLE', 'CYCLIC'): 'STABLE',
        ('STABLE', 'CHAOTIC'): 'STABLE',
        ('METASTABLE', 'METASTABLE'): 'METASTABLE',
        ('METASTABLE', 'CYCLIC'): 'METASTABLE',
        ('METASTABLE', 'CHAOTIC'): 'METASTABLE',
        ('CYCLIC', 'CYCLIC'): 'CYCLIC',
        ('CYCLIC', 'CHAOTIC'): 'CYCLIC',
        ('CHAOTIC', 'CHAOTIC'): 'CHAOTIC',
    }
    key = tuple(sorted([a, b], key=OMEGA.index))
    return OR_TABLE.get(key, 'STABLE')

def omega_not(a):
    """Heyting negation: a -> CHAOTIC"""
    NOT_MAP = {
        'STABLE': 'CHAOTIC',
        'METASTABLE': 'CYCLIC',
        'CYCLIC': 'METASTABLE',
        'CHAOTIC': 'STABLE'
    }
    return NOT_MAP[a]
```

---

## 7. Testing Strategy

### 7.1 SUBIT-64 Exhaustive Tests

For finite space, verify by enumeration:

```python
def test_subit64_completeness():
    """Verify all axioms hold for SUBIT-64"""
    all_states = generate_all_64_states()
    all_rules = generate_restricted_rules()  # e.g., 1000 random rules
    
    for s in all_states:
        for rho in all_rules:
            s_hat = (s, rho)
            
            # A3: F is total
            result = F(s_hat)
            assert result is not None
            
            # A4: F returns extended state
            s_next, rho_next = result
            assert s_next in all_states
            assert rho_next in all_rules

def test_omega_consistency():
    """Verify Ω-classification is exhaustive and mutually exclusive"""
    for s in all_states:
        for rho in all_rules:
            cls = omega_class((s, rho))
            assert cls in OMEGA
            
            # Verify against definition
            if cls == 'STABLE':
                assert F((s, rho)) == (s, rho)
            elif cls == 'CYCLIC':
                # Find cycle
                pass  # implementation
```

### 7.2 Category Laws

```python
def test_category_laws():
    """Verify associativity and identity for SUBIT-64"""
    # Construct sample objects X, Y, Z
    # Construct morphisms φ: X→Y, ψ: Y→Z, χ: Z→W
    
    # Associativity
    assert compose(compose(φ, ψ), χ) == compose(φ, compose(ψ, χ))
    
    # Identity
    assert compose(id_X, φ) == φ
    assert compose(φ, id_Y) == φ
```

---

## 8. Open Implementation Problems

### P1. Efficient Rule Encoding
How to encode ℛ compactly for U? For SUBIT-64, rules are 64^64 — impossible to enumerate. Need canonical form or compression.

### P2. Meta-Evolution g
What is a natural choice for g? Options:
- **Fixed**: g(ρ, s) = ρ (no meta-evolution)
- **Periodic**: cycle through rule set
- **State-dependent**: g depends on Ω-class of current state
- **Self-modifying**: g can rewrite its own code

### P3. Approximating S_∞
Infinite trees require lazy evaluation. For numerical computation, truncate at depth D with error bound.

### P4. Visualization
How to visualize 64-state dynamics? Suggestions:
- 4×4×4 cube (WHO × WHERE × WHEN)
- Circular layout with hexagram glyphs
- Trajectory graph with Ω-class coloring

### P5. Performance
For |ℛ| = 1000 rules and |S| = 64 states, full pairwise distance matrix:
- 64,000 × 64,000 entries
- Each entry: K=20 steps × 2 F-evaluations
- Total: ~1.6 billion F-evaluations

Optimization: parallelize, cache F-results, use bit-parallel encoding.

---

## 9. Roadmap

| Phase | Goal | Deliverable |
|-------|------|-------------|
| 0 | SUBIT-64 core | Python module: State, Rule, F, omega_class |
| 1 | Trajectory analysis | Jupyter notebook: visualize 64-state dynamics |
| 2 | Category verification | Test suite: prove SUBIT-64 satisfies axioms A1–A10 |
| 3 | U prototype | Universal interpreter for restricted rule set |
| 4 | Metric computation | Distance matrix + clustering of states/rules |
| 5 | Type theory | Implement modal type checker (□, ◇, ◯) |
| 6 | S_∞ approximation | Lazy evaluation with bounded depth |
| 7 | Self-reference | U simulating U (fixed-point construction) |

---

## 10. Quick Reference: File Map

| File | What to implement |
|------|-----------------|
| `src/state.py` | `State` class, bit encoding, hexagram mapping |
| `src/rule.py` | `Rule` class, rule application f_rho |
| `src/evolution.py` | `F` operator, meta-evolution g |
| `src/classifier.py` | `omega_class()`, Ω-table operations |
| `src/metric.py` | `semantic_distance()`, ultrametric properties |
| `src/category.py` | `Object`, `Morphism`, composition, products |
| `src/universal.py` | `UniversalObject`, encode/decode, eval |
| `tests/test_axioms.py` | Verification of A1–A27 for SUBIT-64 |

---
