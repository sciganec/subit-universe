"""
SUBIT-JACOBIAN LAB: Polynomial Map Atlas
Version 8.0 · 2026

Systematically explores polynomial maps across different characteristics
and builds a dependency atlas: char -> injectivity -> Ω-class.
"""

from typing import List, Tuple, Dict, Optional, Set
import random
import hashlib
from dataclasses import dataclass
from collections import defaultdict
import sys


# ============================================================================
# 1. POLYNOMIAL MAP OVER ARBITRARY RING
# ============================================================================

@dataclass
class Monomial:
    """A monomial c * x^dx * y^dy over a ring."""
    c: int          # coefficient (integer)
    dx: int         # degree in x
    dy: int         # degree in y

    def __repr__(self):
        if self.dx == 0 and self.dy == 0:
            return str(self.c)
        parts = []
        if self.c != 1:
            parts.append(str(self.c))
        if self.dx > 0:
            parts.append(f"x^{self.dx}" if self.dx > 1 else "x")
        if self.dy > 0:
            parts.append(f"y^{self.dy}" if self.dy > 1 else "y")
        return "*".join(parts)


class Polynomial:
    """Polynomial P(x,y) over a ring (coefficients mod modulus)."""
    def __init__(self, monomials: List[Monomial], modulus: Optional[int] = None):
        self.monomials = monomials
        self.modulus = modulus
        self._normalize()

    def _normalize(self):
        """Combine monomials with same (dx, dy)."""
        combined: Dict[Tuple[int, int], int] = {}
        for m in self.monomials:
            key = (m.dx, m.dy)
            val = m.c
            if self.modulus:
                val = val % self.modulus
            if key in combined:
                combined[key] = (combined[key] + val) % self.modulus if self.modulus else combined[key] + val
            else:
                combined[key] = val
        # Remove zero coefficients
        self.monomials = [
            Monomial(c, dx, dy) for (dx, dy), c in combined.items() if c != 0
        ]
        if not self.monomials:
            self.monomials = [Monomial(0, 0, 0)]

    def eval(self, x: int, y: int) -> int:
        """Evaluate polynomial at (x, y)."""
        total = 0
        for m in self.monomials:
            term = m.c
            if m.dx > 0:
                term *= pow(x, m.dx)
            if m.dy > 0:
                term *= pow(y, m.dy)
            total += term
        if self.modulus:
            total = total % self.modulus
        return total

    def derivative_x(self) -> "Polynomial":
        """Formal derivative d/dx."""
        new_monomials = []
        for m in self.monomials:
            if m.dx > 0:
                new_c = m.c * m.dx
                if self.modulus:
                    new_c = new_c % self.modulus
                if new_c != 0:
                    new_monomials.append(Monomial(new_c, m.dx - 1, m.dy))
        return Polynomial(new_monomials, self.modulus)

    def derivative_y(self) -> "Polynomial":
        """Formal derivative d/dy."""
        new_monomials = []
        for m in self.monomials:
            if m.dy > 0:
                new_c = m.c * m.dy
                if self.modulus:
                    new_c = new_c % self.modulus
                if new_c != 0:
                    new_monomials.append(Monomial(new_c, m.dx, m.dy - 1))
        return Polynomial(new_monomials, self.modulus)

    @classmethod
    def random(cls, max_degree: int = 3, max_coeff: int = 2,
               num_terms: int = 5, modulus: Optional[int] = None,
               rng: Optional[random.Random] = None):
        """Generate random polynomial."""
        if rng is None:
            rng = random.Random()
        monomials = []
        for _ in range(num_terms):
            dx = rng.randint(0, max_degree)
            dy = rng.randint(0, max_degree - dx) if max_degree > 0 else 0
            c = rng.randint(-max_coeff, max_coeff)
            if c != 0:
                monomials.append(Monomial(c, dx, dy))
        if not monomials:
            monomials = [Monomial(rng.randint(1, max_coeff), 0, 0)]
        return cls(monomials, modulus)

    def __repr__(self):
        if not self.monomials or (len(self.monomials) == 1 and self.monomials[0].c == 0):
            return "0"
        return " + ".join(repr(m) for m in self.monomials)


class PolynomialMap:
    """F(x,y) = (P(x,y), Q(x,y))."""
    def __init__(self, P: Polynomial, Q: Polynomial):
        self.P = P
        self.Q = Q
        self.modulus = P.modulus if P.modulus is not None else Q.modulus

    def apply(self, x: int, y: int) -> Tuple[int, int]:
        return self.P.eval(x, y), self.Q.eval(x, y)

    def jacobian(self, x: int, y: int) -> int:
        """Compute Jacobian determinant at (x, y)."""
        dPx = self.P.derivative_x().eval(x, y)
        dPy = self.P.derivative_y().eval(x, y)
        dQx = self.Q.derivative_x().eval(x, y)
        dQy = self.Q.derivative_y().eval(x, y)
        return dPx * dQy - dPy * dQx

    def is_constant_jacobian(self, points: List[Tuple[int, int]]) -> Tuple[bool, Optional[int]]:
        """Check if Jacobian is constant over given points."""
        if not points:
            return True, None
        values = [self.jacobian(x, y) for x, y in points]
        if len(set(values)) == 1:
            return True, values[0]
        return False, None

    def is_injective_on(self, points: List[Tuple[int, int]]) -> bool:
        """Check injectivity on a finite set of points."""
        seen = set()
        for x, y in points:
            out = self.apply(x, y)
            if out in seen:
                return False
            seen.add(out)
        return True

    def get_collision(self, points: List[Tuple[int, int]]) -> Optional[Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]]:
        """Return (p1, p2, output) if collision found."""
        seen = {}
        for x, y in points:
            out = self.apply(x, y)
            if out in seen:
                return (seen[out], (x, y), out)
            seen[out] = (x, y)
        return None

    def __repr__(self):
        return f"P = {self.P}\nQ = {self.Q}"


# ============================================================================
# 2. SUBIT SYSTEM FOR POLYNOMIAL MAPS
# ============================================================================

State = int          # encodes (x, y) in low/high bits
RuleID = int


class SUBITPolynomialSystem:
    def __init__(self, num_rules: int = 2048, modulus: Optional[int] = None,
                 max_degree: int = 3, max_coeff: int = 2, seed: int = 42):
        self.num_rules = num_rules
        self.modulus = modulus
        self.max_degree = max_degree
        self.max_coeff = max_coeff
        self.rng = random.Random(seed)

        self.rules: List[PolynomialMap] = []
        for i in range(num_rules):
            P = Polynomial.random(max_degree, max_coeff, 5, modulus, self.rng)
            Q = Polynomial.random(max_degree, max_coeff, 5, modulus, self.rng)
            self.rules.append(PolynomialMap(P, Q))

    def f(self, rid: RuleID, s: State) -> State:
        """Apply polynomial map to state (x in high bits, y in low bits)."""
        x = (s >> 3) & 0x7
        y = s & 0x7
        out_x, out_y = self.rules[rid].apply(x, y)
        if self.modulus:
            out_x = out_x % self.modulus
            out_y = out_y % self.modulus
        return ((out_x & 0x7) << 3) | (out_y & 0x7)

    def g(self, rid: RuleID, s: State) -> RuleID:
        """Meta-evolution: jump to a new rule based on state."""
        key = (rid * 1000003 + s * 1000033) & 0xFFFFFFFF
        hash_val = hashlib.md5(str(key).encode()).hexdigest()
        return int(hash_val[:8], 16) % self.num_rules

    def step(self, es: Tuple[State, RuleID]) -> Tuple[State, RuleID]:
        s, rid = es
        new_s = self.f(rid, s)
        new_rid = self.g(rid, new_s)
        return (new_s, new_rid)


# ============================================================================
# 3. Ω-CLASSIFIER FOR POLYNOMIAL MAPS
# ============================================================================

class OmegaClassifier:
    STABLE = "STABLE"
    METASTABLE = "METASTABLE"
    CYCLIC = "CYCLIC"
    CHAOTIC = "CHAOTIC"

    @staticmethod
    def classify_and_get_trajectory(system: SUBITPolynomialSystem,
                                    s0: State, rid0: RuleID,
                                    max_steps: int = 200) -> Tuple[str, List[Tuple[State, RuleID]]]:
        es = (s0 & 0x3F, rid0 % system.num_rules)
        visited: Dict[Tuple[State, RuleID], int] = {}
        trajectory: List[Tuple[State, RuleID]] = []
        step = 0
        while es not in visited:
            visited[es] = step
            trajectory.append(es)
            es = system.step(es)
            step += 1
            if step > max_steps:
                return OmegaClassifier.CHAOTIC, trajectory
        cycle_start = visited[es]
        cycle_len = step - cycle_start
        if cycle_start == 0 and cycle_len == 1:
            return OmegaClassifier.STABLE, trajectory
        elif cycle_start > 0 and cycle_len == 1:
            return OmegaClassifier.METASTABLE, trajectory
        elif cycle_len > 1:
            return OmegaClassifier.CYCLIC, trajectory
        return OmegaClassifier.CHAOTIC, trajectory


# ============================================================================
# 4. EXPERIMENT: CHARACTERISTIC ATLAS
# ============================================================================

def build_characteristic_atlas(num_rules: int = 1024, max_degree: int = 3, max_coeff: int = 2):
    print("=" * 80)
    print("SUBIT-JACOBIAN LAB: Characteristic Atlas")
    print(f"Rules per experiment: {num_rules}, max degree: {max_degree}, max coeff: {max_coeff}")
    print("=" * 80)

    # Define experiments: (modulus, description, point grid)
    experiments = [
        (None, "ℤ (char 0, finite sample)", list(range(4))),
        (2, "𝔽₂", list(range(2))),
        (3, "𝔽₃", list(range(3))),
        (4, "ℤ/4ℤ (nilpotents)", list(range(4))),
        (5, "𝔽₅", list(range(5))),
        (7, "𝔽₇", list(range(7))),
    ]

    results = []
    detailed_results: Dict[str, List[Tuple[int, int, int]]] = {}  # name -> [(rid, jac_val, collision_count)]

    for modulus, name, domain in experiments:
        print(f"\n▶ Experiment: {name} (modulus {modulus})")
        print(f"   Domain size: {len(domain)}x{len(domain)} = {len(domain)**2} points")

        # Build SUBIT system for this modulus
        system = SUBITPolynomialSystem(num_rules=num_rules, modulus=modulus,
                                       max_degree=max_degree, max_coeff=max_coeff, seed=42)

        # Generate all points in the grid
        points = [(x, y) for x in domain for y in domain]

        # Search for maps with constant non-zero Jacobian and non-injectivity
        counterexamples: List[Tuple[int, int, int]] = []  # (rid, jac_val, num_collisions)
        jacobian_distribution: Dict[int, int] = defaultdict(int)  # jac_val -> count

        for rid in range(system.num_rules):
            map_obj = system.rules[rid]

            # Check Jacobian constant on grid
            is_const, jac_val = map_obj.is_constant_jacobian(points)
            if not is_const or jac_val == 0:
                continue

            jacobian_distribution[jac_val] += 1

            # Check injectivity
            if not map_obj.is_injective_on(points):
                collision = map_obj.get_collision(points)
                if collision:
                    p1, p2, out = collision
                    counterexamples.append((rid, jac_val, len(points)))  # store rid, jac value, point count
                    if len(counterexamples) <= 5:
                        print(f"   Found: rule {rid} -> non-injective, Jacobian={jac_val}")
                        print(f"     Collision: {p1} -> {out}, {p2} -> {out}")

        results.append((name, modulus, len(domain), len(counterexamples)))
        detailed_results[name] = counterexamples

        print(f"   Total non-injective maps with const non-zero Jacobian: {len(counterexamples)}")
        if jacobian_distribution:
            print(f"   Jacobian value distribution: {dict(jacobian_distribution)}")

    # Summary table
    print("\n" + "=" * 80)
    print("SUMMARY ATLAS")
    print("=" * 80)
    print(f"{'Field/Ring':<20} {'|Domain|':<10} {'Non-injective maps':<20}")
    print("-" * 60)
    for name, _, domain_size, count in results:
        print(f"{name:<20} {domain_size**2:<10} {count:<20}")
    print("=" * 80)

    # Detailed counterexample listing (if any)
    print("\n" + "=" * 80)
    print("DETAILED COUNTEREXAMPLES")
    print("=" * 80)
    any_found = False
    for name, examples in detailed_results.items():
        if examples:
            any_found = True
            print(f"\n{name}:")
            for rid, jac_val, _ in examples[:5]:  # show first 5 per field
                print(f"  Rule {rid}: Jacobian = {jac_val}")
    if not any_found:
        print("\nNo counterexamples found in any field.")
    print("=" * 80)

    return results, detailed_results


# ============================================================================
# 5. MAIN
# ============================================================================

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SUBIT-JACOBIAN LAB: Polynomial Map Atlas")
    parser.add_argument("--rules", type=int, default=1024, help="Number of rules per experiment")
    parser.add_argument("--degree", type=int, default=3, help="Maximum polynomial degree")
    parser.add_argument("--coeff", type=int, default=2, help="Maximum coefficient value")
    args = parser.parse_args()

    build_characteristic_atlas(num_rules=args.rules, max_degree=args.degree, max_coeff=args.coeff)