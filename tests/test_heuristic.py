import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.problem import SokobanProblem
from core.heuristic import make_heuristic
from core.search import ucs


def test_admissible_and_consistent():
    root = Path(__file__).resolve().parents[1]
    problem = SokobanProblem.from_file(root / "maps" / "map1.txt")
    heuristic = make_heuristic(problem)

    _, optimal_cost, _ = ucs(problem)
    assert heuristic(problem.initial) <= optimal_cost

    visited = {problem.initial}
    frontier = [problem.initial]
    checked = 0

    while frontier and checked < 500:
        state = frontier.pop()
        h_state = heuristic(state)

        for action, next_state, cost in problem.successors(state):
                h_next = heuristic(next_state)
                assert h_state <= cost + h_next, (
                    f"Consistency violation at {state} -> {next_state}"
                )
                checked += 1

                if next_state not in visited:
                    visited.add(next_state)
                    frontier.append(next_state)

    assert checked > 0