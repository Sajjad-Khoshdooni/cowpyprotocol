"""Solver logic — port of solver + solvers-dto + winner-selection."""

from cow_solver.dto import AuctionRequest, Solution
from cow_solver.winner_selection import select_winner

__all__ = ["AuctionRequest", "Solution", "select_winner"]
