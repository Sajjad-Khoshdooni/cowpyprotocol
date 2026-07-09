"""Winner selection — port of winner-selection crate."""

from __future__ import annotations

from cow_solver.dto import Solution


def select_winner(solutions: list[Solution]) -> Solution | None:
    """Select the highest-scoring solution."""
    if not solutions:
        return None
    return max(solutions, key=lambda s: s.score)
