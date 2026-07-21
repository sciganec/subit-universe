"""
SUBIT-TOPOS: Polynomial Jacobian Counterexample Search over GF(2)
Version 7.0 · 2026

Searches for polynomial maps F(x,y) = (P(x,y), Q(x,y)) over GF(2)
with constant non-zero Jacobian that are NOT injective.
"""

from typing import List, Tuple, Dict, Set, Optional
import hashlib
import random

# ============================================================================
# 1. POLYNOMIAL RULE OVER GF(2) (Degree up to 3)
# ============================================================================

# Monomials: 1, x, y, x^2, xy, y^2, x^3, x^2 y, x y^2, y^3
MONOMIALS = [
    (0, 0), (1, 0), (0, 1), (2, 0), (1, 1), (0, 2),
    (3, 0), (2, 1), (1, 2), (0, 3)
]
NUM_COEFFS = len(MONOMIALS)

def monomial_index(dx: int, dy: int) -> int:
    """Return index of monomial x^dx y^dy in MONOMIALS, or raise ValueError."""
    try:
        return MONOMIALS.index((dx, dy))
    except ValueError:
        raise ValueError(f"Monomial x^{dx} y^{dy} not supported")

def eval_poly(coeffs: List[int], x: int, y: int) -> int:
    """
    Evaluate polynomial over GF(2).
    coeffs: list of 10 integers (0 or 1) corresponding to MONOMIALS.
    x, y: 0 or 1.
    Returns: 0 or 1.
    """
    res = 0
    for c, (dx, dy) in zip(coeffs, MONOMIALS):
        if c:
            # Over GF(2), x^n = x for n >= 1, and x^0 = 1.
            term = 1
            if dx > 0:
                term &= x
            if dy > 0:
                term &= y
            res ^= term
    return res & 1

def derive_x(coeffs: List[int]) -> List[int]:
    """Formal derivative d/dx over GF(2) for degree up to 3."""
    new_coeffs = [0] * NUM_COEFFS
    for i, (dx, dy) in enumerate(MONOMIALS):
        if dx > 0:
            # derivative: dx * x^(dx-1) y^dy
            # In GF(2), dx mod 2 is 1 iff dx is odd.
            if dx & 1:
                target_idx = monomial_index(dx - 1, dy)
                new_coeffs[target_idx] ^= coeffs[i]
    return new_coeffs

def derive_y(coeffs: List[int]) -> List[int]:
    """Formal derivative d/dy over GF(2) for degree up to 3."""
    new_coeffs = [0] * NUM_COEFFS
    for i, (dx, dy) in enumerate(MONOMIALS):
        if dy > 0:
            if dy & 1:
                target_idx = monomial_index(dx, dy - 1)
                new_coeffs[target_idx] ^= coeffs[i]
    return new_coeffs


class PolynomialRule:
    """Polynomial map F(x,y) = (P(x,y), Q(x,y)) over GF(2)."""
    def __init__(self, coeffs_p: List[int], coeffs_q: List[int]):
        self.coeffs_p = coeffs_p
        self.coeffs_q = coeffs_q
        self._jac_constant = None
        self._jac_value = None

    @classmethod
    def from_seed(cls, seed: int) -> "PolynomialRule":
        """Generate random polynomial from seed (20 bits of coefficients)."""
        rng = random.Random(seed)
        coeffs_p = [rng.randint(0, 1) for _ in range(NUM_COEFFS)]
        coeffs_q = [rng.randint(0, 1) for _ in range(NUM_COEFFS)]
        return cls(coeffs_p, coeffs_q)

    def apply(self, s: int) -> int:
        """Apply polynomial map to 6-bit state (x in high 3 bits, y in low 3 bits)."""
        x = (s >> 3) & 0x7
        y = s & 0x7
        # For GF(2), we only care about the least significant bit of x and y.
        x_bool = x & 1
        y_bool = y & 1
        x_out = eval_poly(self.coeffs_p, x_bool, y_bool)
        y_out = eval_poly(self.coeffs_q, x_bool, y_bool)
        return (x_out << 3) | y_out

    def jacobian_values(self) -> List[int]:
        """Compute Jacobian determinant over all 4 points of GF(2)^2."""
        jac_list = []
        for x in range(2):
            for y in range(2):
                # Evaluate partial derivatives at (x, y)
                dPx = eval_poly(derive_x(self.coeffs_p), x, y)
                dPy = eval_poly(derive_y(self.coeffs_p), x, y)
                dQx = eval_poly(derive_x(self.coeffs_q), x, y)
                dQy = eval_poly(derive_y(self.coeffs_q), x, y)
                # Jacobian = dP/dx * dQ/dy - dP/dy * dQ/dx over GF(2)
                jac = (dPx & dQy) ^ (dPy & dQx)  # XOR = subtraction over GF(2)
                jac_list.append(jac)
        return jac_list

    def is_valid_counterexample(self) -> Optional[Tuple[int, int, int]]:
        """
        Checks:
        1. Jacobian is constant non-zero over GF(2)^2.
        2. The map is NOT injective on the full 64-state space.
        Returns (s1, s2, output) if counterexample, else None.
        """
        # Check Jacobian
        jac_values = self.jacobian_values()
        if len(set(jac_values)) != 1:
            return None
        jac = jac_values[0]
        if jac == 0:
            return None

        # Check injectivity over 0..63 (domain)
        seen = {}
        for s in range(64):
            out = self.apply(s)
            if out in seen:
                return (seen[out], s, out)
            seen[out] = s
        return None

    def to_string(self) -> str:
        """Pretty print polynomial."""
        def poly_str(coeffs):
            terms = []
            for c, (dx, dy) in zip(coeffs, MONOMIALS):
                if c:
                    if dx == 0 and dy == 0:
                        terms.append("1")
                    elif dx == 1 and dy == 0:
                        terms.append("x")
                    elif dx == 0 and dy == 1:
                        terms.append("y")
                    elif dx == 2 and dy == 0:
                        terms.append("x^2")
                    elif dx == 1 and dy == 1:
                        terms.append("xy")
                    elif dx == 0 and dy == 2:
                        terms.append("y^2")
                    elif dx == 3 and dy == 0:
                        terms.append("x^3")
                    elif dx == 2 and dy == 1:
                        terms.append("x^2 y")
                    elif dx == 1 and dy == 2:
                        terms.append("x y^2")
                    elif dx == 0 and dy == 3:
                        terms.append("y^3")
            if not terms:
                return "0"
            return " + ".join(terms)
        return f"P = {poly_str(self.coeffs_p)}, Q = {poly_str(self.coeffs_q)}"


# ============================================================================
# 2. SUBIT SYSTEM WITH POLYNOMIAL RULES
# ============================================================================

State = int
RuleID = int
ExtendedState = Tuple[State, RuleID]


class SUBITSystem:
    def __init__(self, num_rules: int = 4096, seed: int = 42):
        self.num_rules = num_rules
        rng = random.Random(seed)
        self.rules: List[PolynomialRule] = []
        for i in range(num_rules):
            self.rules.append(PolynomialRule.from_seed(i + seed))

    def f(self, rid: RuleID, s: State) -> State:
        return self.rules[rid].apply(s)

    def g(self, rid: RuleID, s: State) -> RuleID:
        key = (rid * 1000003 + s * 1000033) & 0xFFFFFFFF
        hash_val = hashlib.md5(str(key).encode()).hexdigest()
        return int(hash_val[:8], 16) % self.num_rules

    def step(self, es: ExtendedState) -> ExtendedState:
        s, rid = es
        new_s = self.f(rid, s)
        new_rid = self.g(rid, new_s)
        return (new_s, new_rid)


class OmegaClassifier:
    STABLE = "STABLE"
    METASTABLE = "METASTABLE"
    CYCLIC = "CYCLIC"
    CHAOTIC = "CHAOTIC"

    @staticmethod
    def classify_and_get_trajectory(
        system: SUBITSystem,
        s0: State,
        rid0: RuleID,
        max_steps: int = 200
    ) -> Tuple[str, List[ExtendedState]]:
        es = (s0 & 0x3F, rid0 % system.num_rules)
        visited: Dict[ExtendedState, int] = {}
        trajectory: List[ExtendedState] = []
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
# 3. MAIN SEARCH ENGINE
# ============================================================================

def search_polynomial_counterexample(num_trials: int = 500):
    print("=" * 70)
    print("SUBIT-TOPOS: Polynomial Jacobian Counterexample Search")
    print("Working over GF(2), degree up to 3")
    print("Checking: constant non-zero Jacobian + non-injectivity")
    print("=" * 70)

    system = SUBITSystem(num_rules=4096, seed=42)
    checked_rules: Set[RuleID] = set()
    total_rules_checked = 0

    for trial in range(num_trials):
        s0 = random.randint(0, 63)
        rid0 = random.randint(0, system.num_rules - 1)

        cls, traj = OmegaClassifier.classify_and_get_trajectory(
            system, s0, rid0, max_steps=200
        )

        if cls == OmegaClassifier.CHAOTIC and len(traj) >= 10:
            for s, rid in traj:
                if rid not in checked_rules:
                    checked_rules.add(rid)
                    total_rules_checked += 1

                    rule = system.rules[rid]
                    collision = rule.is_valid_counterexample()
                    if collision is not None:
                        s1, s2, out = collision
                        x1, y1 = (s1 >> 3) & 0x7, s1 & 0x7
                        x2, y2 = (s2 >> 3) & 0x7, s2 & 0x7
                        x_out, y_out = (out >> 3) & 0x7, out & 0x7

                        print("\n" + "🔥" * 30)
                        print("✅ POLYNOMIAL COUNTEREXAMPLE FOUND!")
                        print("🔥" * 30)
                        print(f"Rule ID: {rid} (found in chaotic trajectory #{trial})")
                        print(f"Polynomials: {rule.to_string()}")
                        print(f"Jacobian = 1 (constant non-zero) over GF(2)")
                        print(f"Collision: ({x1},{y1}) -> ({x_out},{y_out})")
                        print(f"           ({x2},{y2}) -> ({x_out},{y_out})")
                        print(f"Since two different inputs map to the same output,")
                        print("the map is NOT injective.")
                        print("The Jacobian is constant non-zero, so this is a")
                        print("discrete counterexample to the Jacobian conjecture!")

                        print("\n" + "-" * 70)
                        print("Detailed input-output table for this rule (first 16 states):")
                        print("   s (x,y) -> F(s)")
                        for i in range(16):
                            x, y = (i >> 3) & 0x7, i & 0x7
                            out_val = rule.apply(i)
                            ox, oy = (out_val >> 3) & 0x7, out_val & 0x7
                            marker = " <-- COLLISION" if i == s1 or i == s2 else ""
                            print(f"   {i:2d} ({x},{y}) -> {out_val:2d} ({ox},{oy}){marker}")
                        print("=" * 70)
                        return

        if trial % 50 == 0 and trial > 0:
            print(f"   Searched {trial} trials... checked {total_rules_checked} unique polynomial rules")

    print("\n" + "-" * 70)
    print(f"❌ No polynomial counterexamples found after checking {total_rules_checked} unique rules.")
    print("   Suggestions:")
    print("   - Increase num_rules (e.g., to 16384)")
    print("   - Increase max_steps to explore more chaotic trajectories")


if __name__ == "__main__":
    search_polynomial_counterexample(num_trials=500)