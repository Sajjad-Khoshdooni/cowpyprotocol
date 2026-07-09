"""Unit tests for cow_solver winner selection."""

from cow_solver import Solution, select_winner


def test_select_winner_highest_score() -> None:
    solutions = [
        Solution(solver="a", score=1.0),
        Solution(solver="b", score=2.5),
        Solution(solver="c", score=0.5),
    ]
    winner = select_winner(solutions)
    assert winner is not None
    assert winner.solver == "b"


def test_select_winner_empty() -> None:
    assert select_winner([]) is None
