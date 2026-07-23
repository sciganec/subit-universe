"""
subit_math.py — SUBIT-MATH v1.0
A dynamic framework for mathematical problem exploration.

Unifies four mathematical problems (Collatz, Golomb, Perfect Cuboid, Jacobian)
under a single dynamic system where:
- Problem = (State, Operator, Constraint, Goal)
- Meta-evolution g can switch between problem types
- Ω-classifier characterizes the phase of investigation

Author: SUBIT-TOPOS Research Group
Date: 2026-07-22
"""

import numpy as np
from typing import Any, Dict, List, Tuple, Callable, Optional, Set
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
import math
import itertools
import hashlib
import time

# ============================================================================
# 1. CORE TYPES
# ============================================================================

@dataclass
class State:
    """Abstract state in any mathematical problem."""
    data: Any

@dataclass
class Operator:
    """Abstract operator mapping states to states."""
    name: str
    apply: Callable[[State], State]
    inverse: Optional[Callable[[State], State]] = None

@dataclass
class Constraint:
    """Invariant or restriction on states."""
    name: str
    check: Callable[[State], bool]

@dataclass
class Goal:
    """Target property of a solution."""
    name: str
    check: Callable[[State], bool]

class OmegaClass(Enum):
    """Dynamic classifier from SUBIT-TOPOS."""
    STABLE = "STABLE"
    METASTABLE = "METASTABLE"
    CYCLIC = "CYCLIC"
    CHAOTIC = "CHAOTIC"
    UNKNOWN = "UNKNOWN"  # added for default

@dataclass
class Problem:
    """A formal mathematical problem."""
    name: str
    state_space: str          # description of X
    operator: Operator
    constraint: Optional[Constraint]
    goal: Goal
    # SUBIT-TOPOS dynamics extension
    meta_evolution: Optional[Callable[[State, 'Problem'], 'Problem']] = None
    omega: OmegaClass = OmegaClass.UNKNOWN
    
    def __repr__(self):
        return f"Problem({self.name}, Ω={self.omega.value})"


# ============================================================================
# 2. SUBIT PROBLEM SPACE — The Universe of Problems
# ============================================================================

class SUBITMathSpace:
    """
    A recursive space of problems.
    Just as SUBIT-TOPOS has S∞ = νX.(X×X×X),
    SUBIT-MATH has P∞ = νP.(State × Operator × Constraint × Goal).
    """
    
    def __init__(self):
        self.problems: Dict[str, Problem] = {}
        self.history: List[Tuple[Problem, OmegaClass]] = []
        self.transitions: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.current_problem: Optional[Problem] = None
        
    def register(self, problem: Problem) -> None:
        """Register a problem in the space."""
        self.problems[problem.name] = problem
    
    def classify(self, problem: Problem) -> OmegaClass:
        """
        Ω-classification based on problem structure.
        - STABLE: single known solution / proven
        - METASTABLE: known but complex
        - CYCLIC: self-referential / recursive structure
        - CHAOTIC: open / unknown / computationally hard
        """
        # Simple heuristic based on goal name
        if problem.goal.name == "reach_1":
            return OmegaClass.STABLE
        elif problem.goal.name == "valid_ruler":
            return OmegaClass.METASTABLE
        elif problem.goal.name == "solution_exists":
            return OmegaClass.CHAOTIC
        elif problem.goal.name == "inverse_exists":
            return OmegaClass.CYCLIC
        return OmegaClass.CHAOTIC
    
    def step(self, problem: Problem) -> Tuple[Problem, OmegaClass]:
        """
        Apply meta-evolution: explore the problem space.
        If the problem has a meta-evolution operator, apply it.
        Otherwise, return the problem unchanged.
        """
        if problem.meta_evolution is not None:
            new_problem = problem.meta_evolution(State(problem.name), problem)
            omega = self.classify(new_problem)
            self.history.append((new_problem, omega))
            self.transitions[problem.name][new_problem.name] += 1
            self.current_problem = new_problem
            return new_problem, omega
        else:
            omega = self.classify(problem)
            return problem, omega
    
    def explore(self, start: Problem, steps: int = 10) -> None:
        """Explore the problem space through meta-evolution."""
        self.current_problem = start
        print(f"\n{'='*60}")
        print(f"SUBIT-MATH EXPLORATION: {start.name}")
        print(f"{'='*60}")
        
        for i in range(steps):
            problem, omega = self.step(self.current_problem)
            print(f"Step {i+1}: {problem.name} → Ω = {omega.value}")
            if problem.name == start.name and i > 0:
                print("  → Reached a fixed point in problem space.")
                break
    
    def get_landscape(self) -> Dict[str, Dict[str, int]]:
        """Return the transition landscape of problems."""
        return dict(self.transitions)


# ============================================================================
# 3. CONCRETE PROBLEMS
# ============================================================================

# 3.1. COLLATZ — Dynamical / Orbit Problem
# ============================================================================

def collatz_operator(n: int) -> int:
    if n % 2 == 0:
        return n // 2
    else:
        return 3 * n + 1

collatz_goal = Goal(
    name="reach_1",
    check=lambda state: state.data == 1
)

collatz_constraint = Constraint(
    name="natural",
    check=lambda state: state.data >= 1 and isinstance(state.data, int)
)

collatz_op = Operator(
    name="Collatz_T",
    apply=lambda s: State(collatz_operator(s.data))
)

CollatzProblem = Problem(
    name="Collatz Conjecture",
    state_space="ℕ (natural numbers)",
    operator=collatz_op,
    constraint=collatz_constraint,
    goal=collatz_goal,
    meta_evolution=None,
    omega=OmegaClass.STABLE
)


# 3.2. GOLOMB RULER — Configuration / Combinatorial Problem
# ============================================================================

def golomb_operator(ruler: List[int]) -> List[int]:
    """Add a new mark to the ruler at the smallest possible position."""
    if not ruler:
        return [0, 1]
    
    # Find all pairwise distances
    distances = set()
    for i in range(len(ruler)):
        for j in range(i+1, len(ruler)):
            distances.add(abs(ruler[j] - ruler[i]))
    
    # Find the smallest mark that doesn't duplicate a distance
    max_mark = max(ruler)
    for candidate in range(max_mark + 1, max_mark + len(ruler) + 1):
        new_distances = set()
        for mark in ruler:
            d = abs(candidate - mark)
            if d == 0 or d in distances:
                break
            new_distances.add(d)
        else:
            # All new distances are unique
            return ruler + [candidate]
    return ruler

def golomb_goal_check(state: State) -> bool:
    ruler = state.data
    if len(ruler) < 2:
        return False
    distances = set()
    for i in range(len(ruler)):
        for j in range(i+1, len(ruler)):
            d = abs(ruler[j] - ruler[i])
            if d in distances:
                return False
            distances.add(d)
    return True

def golomb_constraint_check(state: State) -> bool:
    ruler = state.data
    if len(ruler) < 2:
        return True
    distances = set()
    for i in range(len(ruler)):
        for j in range(i+1, len(ruler)):
            d = abs(ruler[j] - ruler[i])
            if d in distances:
                return False
            distances.add(d)
    return True

golomb_op = Operator(
    name="Golomb_AddMark",
    apply=lambda s: State(golomb_operator(s.data)),
    inverse=lambda s: State(s.data[:-1]) if len(s.data) > 2 else State([0,1])
)

golomb_goal = Goal(
    name="valid_ruler",
    check=golomb_goal_check
)

golomb_constraint = Constraint(
    name="unique_distances",
    check=golomb_constraint_check
)

GolombProblem = Problem(
    name="Golomb Ruler",
    state_space="List[int] (ordered marks)",
    operator=golomb_op,
    constraint=golomb_constraint,
    goal=golomb_goal,
    meta_evolution=None,
    omega=OmegaClass.METASTABLE
)


# 3.3. PERFECT CUBOID — Diophantine / Constraint Problem
# ============================================================================

def cuboid_operator(solution: Dict[str, int]) -> Dict[str, int]:
    """Simple search: increment variables."""
    if not solution:
        return {'a': 1, 'b': 1, 'c': 1}
    
    # Simple heuristic: increment the smallest variable
    a, b, c = solution.get('a', 1), solution.get('b', 1), solution.get('c', 1)
    if a <= b and a <= c:
        return {'a': a+1, 'b': b, 'c': c}
    elif b <= a and b <= c:
        return {'a': a, 'b': b+1, 'c': c}
    else:
        return {'a': a, 'b': b, 'c': c+1}

def cuboid_goal_check(state: State) -> bool:
    solution = state.data
    if not solution:
        return False
    a, b, c = solution.get('a', 0), solution.get('b', 0), solution.get('c', 0)
    
    # Perfect cuboid equations:
    # a² + b² = d², a² + c² = e², b² + c² = f², a² + b² + c² = g²
    def is_square(n: int) -> bool:
        if n < 0:
            return False
        root = int(math.isqrt(n))
        return root * root == n
    
    d2 = a*a + b*b
    e2 = a*a + c*c
    f2 = b*b + c*c
    g2 = a*a + b*b + c*c
    
    return is_square(d2) and is_square(e2) and is_square(f2) and is_square(g2) and a > 0 and b > 0 and c > 0

cuboid_op = Operator(
    name="Cuboid_Search",
    apply=lambda s: State(cuboid_operator(s.data))
)

cuboid_goal = Goal(
    name="solution_exists",
    check=cuboid_goal_check
)

cuboid_constraint = Constraint(
    name="diophantine",
    check=lambda s: all(v > 0 for v in s.data.values()) if s.data else True
)

CuboidProblem = Problem(
    name="Perfect Cuboid",
    state_space="ℤ⁷ (integer equations)",
    operator=cuboid_op,
    constraint=cuboid_constraint,
    goal=cuboid_goal,
    meta_evolution=None,
    omega=OmegaClass.CHAOTIC
)


# 3.4. JACOBIAN CONJECTURE — Algebraic / Morphism Problem
# ============================================================================

def jacobian_operator(map_coeffs: Tuple[Tuple[int, int], Tuple[int, int]]) -> Tuple:
    """Compose map with a linear transformation to test invertibility."""
    # Simple: try to find inverse via linear algebra over GF(2)
    # For demonstration, just return the map unchanged
    return map_coeffs

def jacobian_goal_check(state: State) -> bool:
    """Check if the map is invertible (det J ≠ 0 and injective)."""
    # For simplicity: check if determinant is non-zero
    coeffs = state.data
    if not coeffs:
        return False
    # For a 2x2 linear map: [[a,b],[c,d]], det = ad - bc
    # In characteristic 0, det != 0 implies invertibility (for linear maps)
    # In characteristic 2, this fails (Frobenius)
    a, b = coeffs[0][0], coeffs[0][1]
    c, d = coeffs[1][0], coeffs[1][1]
    det = a * d - b * c
    return det != 0

jacobian_constraint = Constraint(
    name="polynomial",
    check=lambda s: True
)

jacobian_op = Operator(
    name="Jacobian_Compose",
    apply=lambda s: State(jacobian_operator(s.data))
)

jacobian_goal = Goal(
    name="inverse_exists",
    check=jacobian_goal_check
)

JacobianProblem = Problem(
    name="Jacobian Conjecture",
    state_space="Polynomial Map",
    operator=jacobian_op,
    constraint=jacobian_constraint,
    goal=jacobian_goal,
    meta_evolution=None,
    omega=OmegaClass.CYCLIC
)


# ============================================================================
# 4. META-EVOLUTION: DYNAMICS BETWEEN PROBLEMS
# ============================================================================

def meta_evolve_from_collatz(state: State, problem: Problem) -> Problem:
    """
    From Collatz (dynamical), move to:
    - Golomb if Collatz proves too complex (configuration view)
    - Cuboid if we need algebraic constraints
    - Jacobian if we need a morphism perspective
    """
    # Based on state (e.g., how many steps in Collatz)
    # If the state is small, stay in Collatz
    n = state.data if isinstance(state.data, int) else 0
    
    if n < 10:
        return CollatzProblem
    elif n < 50:
        return GolombProblem
    elif n < 100:
        return CuboidProblem
    else:
        return JacobianProblem

def meta_evolve_from_golomb(state: State, problem: Problem) -> Problem:
    """
    From Golomb (configuration), move to:
    - Cuboid if configuration search fails (need equations)
    - Collatz if we want to see dynamics
    """
    ruler = state.data if isinstance(state.data, list) else []
    length = len(ruler)
    
    if length < 5:
        return GolombProblem
    elif length < 10:
        return CuboidProblem
    else:
        return CollatzProblem

def meta_evolve_from_cuboid(state: State, problem: Problem) -> Problem:
    """
    From Cuboid (diophantine), move to:
    - Jacobian if we need algebraic structure
    - Golomb if we need combinatorial search
    """
    solution = state.data if isinstance(state.data, dict) else {}
    if not solution:
        return CuboidProblem
    a, b, c = solution.get('a', 0), solution.get('b', 0), solution.get('c', 0)
    
    if a + b + c < 10:
        return CuboidProblem
    elif a + b + c < 50:
        return JacobianProblem
    else:
        return GolombProblem

def meta_evolve_from_jacobian(state: State, problem: Problem) -> Problem:
    """
    From Jacobian (algebraic), move to:
    - Collatz if we need dynamics again
    - Cuboid if we need equations
    """
    # Just cycle back
    return CollatzProblem


# ============================================================================
# 5. MAIN DEMONSTRATION
# ============================================================================

def main():
    print("=" * 70)
    print("SUBIT-MATH v1.0: Dynamic Problem Space")
    print("Unifying Collatz, Golomb, Perfect Cuboid, Jacobian")
    print("=" * 70)
    
    # Create the problem space
    space = SUBITMathSpace()
    
    # Register problems
    space.register(CollatzProblem)
    space.register(GolombProblem)
    space.register(CuboidProblem)
    space.register(JacobianProblem)
    
    print("\nRegistered problems:")
    for name, p in space.problems.items():
        print(f"  {name}: Ω = {p.omega.value}")
    
    # === Define a meta-evolution path ===
    print("\n" + "=" * 70)
    print("META-EVOLUTION: Collatz → Golomb → Cuboid → Jacobian → Collatz")
    print("=" * 70)
    
    # Create a unified meta-evolution that traverses the problem space
    def unified_meta_evolution(state: State, problem: Problem) -> Problem:
        """Navigate through the problem space based on the current problem."""
        if problem.name == "Collatz Conjecture":
            # After Collatz, go to Golomb
            return GolombProblem
        elif problem.name == "Golomb Ruler":
            # After Golomb, go to Cuboid
            return CuboidProblem
        elif problem.name == "Perfect Cuboid":
            # After Cuboid, go to Jacobian
            return JacobianProblem
        elif problem.name == "Jacobian Conjecture":
            # After Jacobian, go back to Collatz
            return CollatzProblem
        return problem
    
    # Create a chain of problems with meta-evolution
    chain = [
        CollatzProblem,
        GolombProblem,
        CuboidProblem,
        JacobianProblem,
        CollatzProblem
    ]
    
    # Start with Collatz
    current = CollatzProblem
    print(f"\nStart: {current.name}")
    print(f"  Ω: {current.omega.value}")
    
    # Explore with meta-evolution
    for i in range(4):
        next_problem = unified_meta_evolution(State(0), current)
        omega = space.classify(next_problem)
        print(f"\n→ Step {i+1}: {next_problem.name}")
        print(f"  Ω: {omega.value}")
        current = next_problem
    
    print("\n" + "=" * 70)
    print("META-EVOLUTION BASED ON STATE (Dynamic Navigation)")
    print("=" * 70)
    
    # Dynamic meta-evolution based on state
    # Start with Collatz and a small number
    state = State(5)
    current = CollatzProblem
    print(f"\nStart: {current.name}, state={state.data}")
    print(f"  Ω: {current.omega.value}")
    
    # Define meta-evolution based on state
    def state_based_meta_evolution(s: State, p: Problem) -> Problem:
        if isinstance(s.data, int):
            n = s.data
            if n < 20:
                return GolombProblem
            elif n < 50:
                return CuboidProblem
            else:
                return JacobianProblem
        return p
    
    for i in range(5):
        state = State(state.data * 2 + 1)  # grow the state
        next_problem = state_based_meta_evolution(state, current)
        omega = space.classify(next_problem)
        print(f"\n→ Step {i+1}: state={state.data}")
        print(f"  Problem: {next_problem.name} → Ω = {omega.value}")
        current = next_problem
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY: SUBIT-MATH SPACE")
    print("=" * 70)
    print(f"Problems in space: {len(space.problems)}")
    print("Problem transition landscape:")
    landscape = space.get_landscape()
    for src, dsts in landscape.items():
        for dst, count in dsts.items():
            print(f"  {src} → {dst}: {count}")


if __name__ == "__main__":
    main()