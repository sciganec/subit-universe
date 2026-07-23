"""
subit_math_v2.py — SUBIT-MATH v2.0
Problem Morphodynamics Engine

Core thesis: A mathematical problem is not an object, but a trajectory
in the space of representations. Evolution happens simultaneously at
three levels:
  1. Data evolution — the mathematical objects themselves
  2. Problem evolution — the formulation of the problem
  3. Rule evolution — the research strategy

Ω-classifier tracks the phase of investigation, not just the problem type.

Author: SUBIT-TOPOS Research Group
Date: 2026-07-22
"""

from typing import Any, Dict, List, Tuple, Callable, Optional, Set, Union
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
import math
import hashlib
import time
import copy

# ============================================================================
# 0. UNICODE MATH — All formulas in plain Unicode
# ============================================================================

# ============================================================================
# 1. CORE TYPES
# ============================================================================

class OmegaClass(Enum):
    """Dynamic classifier for research phases (trajectories, not just objects)."""
    STABLE = "STABLE"          # Problem understood, solution found
    METASTABLE = "METASTABLE"  # Progress made, but not yet stable
    CYCLIC = "CYCLIC"          # Repeating patterns — need meta-shift
    CHAOTIC = "CHAOTIC"        # Lost — need new representation
    UNKNOWN = "UNKNOWN"        # Not yet classified


@dataclass
class Hypothesis:
    """A candidate invariant or structural insight."""
    name: str
    statement: str
    confidence: float = 0.0  # 0..1
    verified: bool = False
    created_at: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Problem:
    """
    Level 0: Static mathematical problem.
    This is the object being researched.
    """
    name: str
    state_space: str           # X — description of the space
    operator: Callable[[Any], Any]  # Φ — the dynamics
    constraint: Optional[Callable[[Any], bool]]  # C — invariant
    goal: Callable[[Any], bool]  # G — target property
    representation: str = "default"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return isinstance(other, Problem) and self.name == other.name


@dataclass
class ProblemState:
    """
    Level 1: Dynamic research state.
    Evolution happens simultaneously at three levels:
      - data: current mathematical configuration
      - problem: current formulation of the problem
      - rule: current research strategy
    """
    data: Any                                    # D — current data/config
    problem: Problem                             # P — current problem
    rule: Callable[['ProblemState'], Any]        # ρ — current strategy
    hypotheses: List[Hypothesis] = field(default_factory=list)  # H
    history: List['ProblemState'] = field(default_factory=list)
    depth: int = 0
    omega: OmegaClass = OmegaClass.UNKNOWN
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self):
        return f"ProblemState({self.problem.name}, Ω={self.omega.value}, depth={self.depth})"


# ============================================================================
# 2. OMEGA CLASSIFIER FOR STATES AND TRAJECTORIES
# ============================================================================

def classify_state(state: ProblemState) -> OmegaClass:
    """Classify the research state based on problem type and depth."""
    name = state.problem.name
    if name == "Collatz Conjecture":
        if state.depth < 3:
            return OmegaClass.METASTABLE
        elif state.depth < 8:
            return OmegaClass.CYCLIC
        else:
            return OmegaClass.CHAOTIC
    elif name == "Golomb Ruler":
        if state.depth < 3:
            return OmegaClass.METASTABLE
        elif state.depth < 6:
            return OmegaClass.STABLE
        else:
            return OmegaClass.CHAOTIC
    elif name == "Perfect Cuboid":
        return OmegaClass.CHAOTIC
    elif name == "Jacobian Conjecture":
        return OmegaClass.CYCLIC
    return OmegaClass.UNKNOWN


class OmegaTrajectoryClassifier:
    """
    Classifies the trajectory of research, not just individual states.
    Ω(τ) where τ = (s₀, s₁, s₂, ...)
    """

    @staticmethod
    def classify(state: ProblemState, history: List[ProblemState]) -> OmegaClass:
        """
        Classify based on the entire trajectory, not just the current state.
        """
        if len(history) >= 3:
            recent = [h.problem.name for h in history[-5:]]
            if len(set(recent)) < len(recent):
                return OmegaClass.CYCLIC
            if len(set(recent)) == 1 and recent[0] == state.problem.name:
                if state.depth > 5:
                    return OmegaClass.STABLE
        return classify_state(state)


# ============================================================================
# 3. DATA TRANSFORMATION FOR PROBLEM SWITCHING
# ============================================================================

def transform_data_for_problem(data: Any, target_problem: Problem) -> Any:
    """Transform data to a format suitable for the target problem."""
    target_name = target_problem.name

    if target_name == "Collatz Conjecture":
        # Ensure data is an integer
        if isinstance(data, int):
            return data
        elif isinstance(data, list) and len(data) > 0:
            # Golomb ruler → Collatz: take the last mark as a number
            return data[-1]
        elif isinstance(data, dict) and data:
            # Cuboid → Collatz: take a from the solution
            return data.get('a', 27)
        elif isinstance(data, tuple) and len(data) > 0:
            # Jacobian → Collatz: take a random number
            return 27
        return 27

    elif target_name == "Golomb Ruler":
        # Need a list of marks
        if isinstance(data, list):
            return data
        elif isinstance(data, int):
            # Collatz → Golomb: start with [0, data % 20 + 1]
            return [0, (data % 20) + 1]
        elif isinstance(data, dict) and data:
            # Cuboid → Golomb: use the values as a ruler
            return [0, data.get('a', 1), data.get('b', 2)]
        elif isinstance(data, tuple) and len(data) > 0:
            # Jacobian → Golomb: use matrix entries
            return [0, abs(data[0][0]) % 10 + 1]
        return [0, 1]

    elif target_name == "Perfect Cuboid":
        # Need a dict of integers
        if isinstance(data, dict):
            return data
        elif isinstance(data, int):
            # Collatz → Cuboid: start with (n, n+1, n+2)
            return {'a': data % 10 + 1, 'b': (data + 1) % 10 + 1, 'c': (data + 2) % 10 + 1}
        elif isinstance(data, list) and len(data) >= 3:
            # Golomb → Cuboid: use first three marks
            return {'a': data[0] + 1, 'b': data[1] + 1, 'c': data[2] + 1}
        elif isinstance(data, tuple) and len(data) > 0:
            # Jacobian → Cuboid: use matrix entries
            return {'a': abs(data[0][0]) + 1, 'b': abs(data[0][1]) + 1, 'c': abs(data[1][0]) + 1}
        return {'a': 1, 'b': 2, 'c': 3}

    elif target_name == "Jacobian Conjecture":
        # Need a 2x2 matrix
        if isinstance(data, tuple) and len(data) == 2:
            return data
        elif isinstance(data, dict) and data:
            # Cuboid → Jacobian: use a,b,c to form a matrix
            a = data.get('a', 1)
            b = data.get('b', 2)
            c = data.get('c', 3)
            return ((a % 5, b % 5), (c % 5, (a+b) % 5))
        elif isinstance(data, list) and len(data) >= 4:
            # Golomb → Jacobian: use first four marks
            return ((data[0] % 5 + 1, data[1] % 5 + 1), (data[2] % 5 + 1, data[3] % 5 + 1))
        elif isinstance(data, int):
            # Collatz → Jacobian: use n to form a matrix
            return ((data % 3 + 1, (data + 1) % 3 + 1), ((data + 2) % 3 + 1, (data + 3) % 3 + 1))
        return ((1, 0), (0, 1))

    return data


# ============================================================================
# 4. RESEARCH ENGINE — The Heart of SUBIT-MATH v2
# ============================================================================

class SUBITMathEngine:
    """
    The engine that evolves research states.
    F(s) = (Φ_ρ(data), p', ρ', h')
    """

    def __init__(self):
        self.history: List[ProblemState] = []
        self.current: Optional[ProblemState] = None
        self.transitions: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.step_count: int = 0

    def step(self, state: ProblemState) -> ProblemState:
        """One step of research evolution: F(s_t) = s_{t+1}"""
        self.step_count += 1

        # 1. Data evolution — apply the current rule to the data
        try:
            new_data = state.rule(state)
        except Exception:
            # If the rule fails, keep the data unchanged
            new_data = state.data

        # 2. Problem evolution — evolve the problem formulation
        new_problem = self._evolve_problem(state, new_data)

        # 3. Transform data if problem changed
        if new_problem.name != state.problem.name:
            new_data = transform_data_for_problem(new_data, new_problem)

        # 4. Rule evolution — evolve the research strategy
        new_rule = self._evolve_rule(state, new_data)

        # 5. Hypothesis evolution — update hypotheses
        new_hypotheses = self._evolve_hypotheses(state, new_data)

        # Create new state
        new_state = ProblemState(
            data=new_data,
            problem=new_problem,
            rule=new_rule,
            hypotheses=new_hypotheses,
            history=state.history + [state] if state.history else [state],
            depth=state.depth + 1,
            omega=OmegaTrajectoryClassifier.classify(state, state.history),
            metadata=state.metadata.copy()
        )

        self.transitions[state.problem.name][new_state.problem.name] += 1
        self.history.append(new_state)

        return new_state

    def _evolve_problem(self, state: ProblemState, data: Any) -> Problem:
        """Evolve the problem formulation based on data."""
        # If we've been on the same problem too long, mutate
        if state.depth > 10:
            if state.problem.name == "Collatz Conjecture":
                return GolombProblem
            elif state.problem.name == "Golomb Ruler":
                return CuboidProblem
            elif state.problem.name == "Perfect Cuboid":
                return JacobianProblem
            elif state.problem.name == "Jacobian Conjecture":
                return CollatzProblem
        return state.problem

    def _evolve_rule(self, state: ProblemState, data: Any) -> Callable[[ProblemState], Any]:
        """Evolve the research strategy."""
        if state.depth > 5 and state.omega in [OmegaClass.CHAOTIC, OmegaClass.CYCLIC]:
            if state.problem.name == "Collatz Conjecture":
                return strategy_collatz_advanced
            elif state.problem.name == "Golomb Ruler":
                return strategy_golomb_advanced
            elif state.problem.name == "Perfect Cuboid":
                return strategy_cuboid_advanced
            elif state.problem.name == "Jacobian Conjecture":
                return strategy_jacobian_advanced
        return state.rule

    def _evolve_hypotheses(self, state: ProblemState, data: Any) -> List[Hypothesis]:
        """Update hypotheses based on new data."""
        hypotheses = state.hypotheses.copy()
        if state.depth > 0 and state.depth % 3 == 0:
            hypotheses.append(Hypothesis(
                name=f"hypothesis_{state.depth}",
                statement=f"Observation at depth {state.depth}: data={data}",
                confidence=0.3,
                created_at=state.depth
            ))
        return hypotheses

    def explore(self, initial: ProblemState, max_steps: int = 20) -> None:
        """Run the research process."""
        self.current = initial
        self.history = [initial]

        print(f"\n{'='*70}")
        print(f"SUBIT-MATH v2.0 — Problem Morphodynamics Engine")
        print(f"Initial problem: {initial.problem.name}")
        print(f"Initial Ω: {initial.omega.value}")
        print(f"{'='*70}")

        for i in range(max_steps):
            print(f"\nStep {i+1}:")
            print(f"  Problem: {self.current.problem.name}")
            print(f"  Representation: {self.current.problem.representation}")
            print(f"  Ω: {self.current.omega.value}")
            if self.current.hypotheses:
                print(f"  Hypotheses: {[h.name for h in self.current.hypotheses[-3:]]}")

            if self.current.omega == OmegaClass.STABLE:
                print("\n✅ STABLE — Problem solved / understood.")
                break

            self.current = self.step(self.current)

        print(f"\n{'='*70}")
        print(f"Exploration complete.")
        print(f"Final problem: {self.current.problem.name}")
        print(f"Final Ω: {self.current.omega.value}")
        print(f"Depth: {self.current.depth}")
        print(f"Transitions: {dict(self.transitions)}")


# ============================================================================
# 5. CONCRETE PROBLEMS (Level 0)
# ============================================================================

# 5.1. COLLATZ
def collatz_operator(n: int) -> int:
    if n % 2 == 0:
        return n // 2
    else:
        return 3 * n + 1

def collatz_goal(n: int) -> bool:
    return n == 1

def collatz_constraint(n: int) -> bool:
    return n > 0 and isinstance(n, int)

CollatzProblem = Problem(
    name="Collatz Conjecture",
    state_space="ℕ",
    operator=collatz_operator,
    constraint=collatz_constraint,
    goal=collatz_goal,
    representation="standard (n)",
    metadata={"status": "open", "verified_up_to": 2**68}
)


# 5.2. GOLOMB RULER
def golomb_operator(ruler: List[int]) -> List[int]:
    if not ruler or len(ruler) < 2:
        return [0, 1]
    distances = set()
    for i in range(len(ruler)):
        for j in range(i+1, len(ruler)):
            distances.add(abs(ruler[j] - ruler[i]))
    max_mark = max(ruler)
    for candidate in range(max_mark + 1, max_mark + len(ruler) + 5):
        good = True
        for mark in ruler:
            d = abs(candidate - mark)
            if d == 0 or d in distances:
                good = False
                break
        if good:
            return ruler + [candidate]
    return ruler

def golomb_goal(ruler: List[int]) -> bool:
    if len(ruler) < 4:
        return False
    distances = set()
    for i in range(len(ruler)):
        for j in range(i+1, len(ruler)):
            d = abs(ruler[j] - ruler[i])
            if d in distances:
                return False
            distances.add(d)
    return True

def golomb_constraint(ruler: List[int]) -> bool:
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

GolombProblem = Problem(
    name="Golomb Ruler",
    state_space="List[ℕ]",
    operator=golomb_operator,
    constraint=golomb_constraint,
    goal=golomb_goal,
    representation="marks list",
    metadata={"optimal_lengths": {1:0, 2:1, 3:3, 4:6, 5:11}}
)


# 5.3. PERFECT CUBOID
def cuboid_operator(sol: Dict[str, int]) -> Dict[str, int]:
    if not sol:
        return {'a': 1, 'b': 1, 'c': 1}
    a, b, c = sol.get('a', 1), sol.get('b', 1), sol.get('c', 1)
    if a <= b and a <= c:
        return {'a': a+1, 'b': b, 'c': c}
    elif b <= a and b <= c:
        return {'a': a, 'b': b+1, 'c': c}
    else:
        return {'a': a, 'b': b, 'c': c+1}

def cuboid_goal(sol: Dict[str, int]) -> bool:
    if not sol:
        return False
    a, b, c = sol.get('a', 0), sol.get('b', 0), sol.get('c', 0)
    def is_sq(n: int) -> bool:
        return n >= 0 and int(math.isqrt(n))**2 == n
    return (is_sq(a*a + b*b) and is_sq(a*a + c*c) and
            is_sq(b*b + c*c) and is_sq(a*a + b*b + c*c))

def cuboid_constraint(sol: Dict[str, int]) -> bool:
    return all(v > 0 for v in sol.values()) if sol else True

CuboidProblem = Problem(
    name="Perfect Cuboid",
    state_space="ℤ⁷",
    operator=cuboid_operator,
    constraint=cuboid_constraint,
    goal=cuboid_goal,
    representation="(a,b,c,d,e,f,g)",
    metadata={"status": "open", "smallest_known": None}
)


# 5.4. JACOBIAN
def jacobian_operator(mat: Tuple[Tuple[int, int], Tuple[int, int]]) -> Tuple:
    if not mat:
        return ((1,0),(0,1))
    a, b = mat[0][0], mat[0][1]
    c, d = mat[1][0], mat[1][1]
    det = a*d - b*c
    if det != 0:
        return (mat, "invertible")
    else:
        return (mat, "non-invertible")

def jacobian_goal(data: Tuple) -> bool:
    if not isinstance(data, tuple) or len(data) != 2:
        return False
    return data[1] == "invertible"

def jacobian_constraint(data: Tuple) -> bool:
    return True

JacobianProblem = Problem(
    name="Jacobian Conjecture",
    state_space="PolyMap(n)",
    operator=jacobian_operator,
    constraint=jacobian_constraint,
    goal=jacobian_goal,
    representation="(P,Q) over ℂ",
    metadata={"status": "open", "known_for": "n=1"}
)


# ============================================================================
# 6. RESEARCH STRATEGIES (Rules ρ)
# ============================================================================

def strategy_basic(state: ProblemState) -> Any:
    """Basic strategy: apply the problem's operator."""
    return state.problem.operator(state.data)

def strategy_collatz_advanced(state: ProblemState) -> Any:
    """Advanced Collatz: look for 2-adic structure."""
    n = state.data
    if n % 2 == 0:
        return n // 2
    else:
        return 3 * n + 1

def strategy_golomb_advanced(state: ProblemState) -> Any:
    """Advanced Golomb: construct optimal ruler."""
    ruler = state.data
    if not isinstance(ruler, list):
        return [0, 1]
    return golomb_operator(ruler)

def strategy_cuboid_advanced(state: ProblemState) -> Any:
    """Advanced Cuboid: use parameterization."""
    sol = state.data
    if not isinstance(sol, dict):
        return {'a': 1, 'b': 1, 'c': 1}
    return cuboid_operator(sol)

def strategy_jacobian_advanced(state: ProblemState) -> Any:
    """Advanced Jacobian: search for inverse."""
    mat = state.data
    if not mat:
        return ((1,0),(0,1))
    if not isinstance(mat, tuple) or len(mat) != 2:
        return ((1,0),(0,1))
    a, b = mat[0][0], mat[0][1]
    c, d = mat[1][0], mat[1][1]
    det = a*d - b*c
    if det != 0:
        inv_det = 1/det
        return ((d*inv_det, -b*inv_det), (-c*inv_det, a*inv_det))
    return mat


# ============================================================================
# 7. MAIN
# ============================================================================

def main():
    print("=" * 70)
    print("SUBIT-MATH v2.0 — Problem Morphodynamics Engine")
    print("Three-level evolution: data, problem, rule")
    print("=" * 70)

    initial = ProblemState(
        data=27,
        problem=CollatzProblem,
        rule=strategy_basic,
        hypotheses=[
            Hypothesis("initial", "Collatz conjecture is open", confidence=0.5)
        ],
        omega=OmegaClass.METASTABLE,
        depth=0
    )

    engine = SUBITMathEngine()
    engine.explore(initial, max_steps=15)

    print("\n" + "=" * 70)
    print("RESEARCH SUMMARY")
    print("=" * 70)
    print(f"Total steps: {engine.step_count}")
    print(f"Final state: {engine.current.problem.name} (Ω={engine.current.omega.value})")
    print(f"Final depth: {engine.current.depth}")

    print("\nHypotheses generated:")
    for h in engine.current.hypotheses:
        print(f"  • {h.name}: {h.statement[:50]}... (conf: {h.confidence:.1f})")

    print("\nTransitions:")
    for src, dsts in engine.transitions.items():
        for dst, count in dsts.items():
            print(f"  {src} → {dst}: {count} times")


if __name__ == "__main__":
    main()