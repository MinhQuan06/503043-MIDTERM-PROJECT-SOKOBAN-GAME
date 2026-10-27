import random
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from .competitive_state import CompetitiveState, Position


DIRECTIONS = {
    "North": (0, -1),
    "East": (1, 0),
    "South": (0, 1),
    "West": (-1, 0),
    "UP": (0, -1),
    "RIGHT": (1, 0),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "N": (0, -1),
    "E": (1, 0),
    "S": (0, 1),
    "W": (-1, 0),
    "WAIT": (0, 0),
    "STAY": (0, 0),
}


@dataclass
class MoveProposal:
    agent_id: int
    start: Position
    target: Position
    valid: bool = True
    box_from: Optional[Position] = None
    box_to: Optional[Position] = None


class CompetitiveEngine:
    """Rules engine for simultaneous two-agent Sokoban."""

    def __init__(self, state: CompetitiveState, max_turns: int):
        if max_turns < 1:
            raise ValueError("max_turns must be at least 1.")

        self.state = state
        self.max_turns = max_turns
        self.finished = False

    @staticmethod
    def _add(a: Position, b: Position) -> Position:
        return a[0] + b[0], a[1] + b[1]

    # Hàm dùng để giải quyết nếu như 2 agent cùng vào 1 vị trí, đẩy 1 hộp, đẩy 2 hộp cùng 1 chỗ/đích
    # p roll theo phân bố đều liên tục, p<0.5 agent 1 thắng lượt và agent 2 sẽ mất lượt, và ngược lại
    def _resolve_conflict(self, p1: MoveProposal, p2:MoveProposal):
        p = random.random()
        if p < 0.5:
            p2.valid = False
        else:
            p1.valid = False

    def _propose(self, agent_id: int, action: str) -> MoveProposal:
        start = self.state.agents[agent_id]
        direction = DIRECTIONS.get(action)

        if direction is None:
            raise ValueError(f"Unknown action: {action!r}")

        target = self._add(start, direction)
        proposal = MoveProposal(agent_id, start, target)

        # Waiting is always legal.
        if target == start:
            return proposal

        # Cannot move outside the map or into a wall.
        if (
            not self._is_inside(target)
            or target in self.state.walls
        ):
            proposal.valid = False
            return proposal

        # Ordinary movement.
        if target not in self.state.boxes:
            return proposal

        # Pushing a box.
        box_target = self._add(target, direction)

        if (
            not self._is_inside(box_target)
            or box_target in self.state.walls
            or box_target in self.state.boxes
            or box_target in self.state.agents.values()
        ):
            proposal.valid = False
            return proposal

        proposal.box_from = target
        proposal.box_to = box_target
        return proposal

    def step(self, actions: Dict[int, str]):
        """
        Apply one simultaneous game turn.

        actions example:
            {1: "East", 2: "North"}

        Returns a report describing the resolved turn.
        """
        if self.finished:
            raise RuntimeError("The game has already finished.")

        if set(actions) != {1, 2}:
            raise ValueError("Actions must be provided for agents 1 and 2.")

        proposals = {
            agent_id: self._propose(agent_id, action)
            for agent_id, action in actions.items()
        }

        p1 = proposals[1]
        p2 = proposals[2]

        # Both agents cannot occupy the same destination.
        if p1.target == p2.target:
            self._resolve_conflict(p1, p2)

        # Agents cannot pass through each other by swapping positions.
        if p1.target == p2.start and p2.target == p1.start:
            p1.valid = False
            p2.valid = False

        # Both agents cannot push the same box.
        # Two different boxes cannot be pushed into the same cell.
        if (
            p1.valid
            and p2.valid
            and p1.box_to is not None
            and p2.box_to is not None
            and p1.box_to == p2.box_to
        ):
            self._resolve_conflict(p1, p2)
        if (
            p1.box_from is not None
            and p1.box_from == p2.box_from
        ):
            self._resolve_conflict(p1, p2)

        # A box cannot be pushed into the other agent's destination.
        for pusher, other in ((p1, p2), (p2, p1)):
            if pusher.box_to is not None:
                if pusher.box_to == other.target:
                    pusher.valid = False
                    other.valid = False

                # Avoid entering the old cell of a box being pushed.
                if other.target == pusher.box_from:
                    pusher.valid = False
                    other.valid = False

        # An agent cannot enter a cell occupied by an agent
        # that is staying in place.
        for mover, other in ((p1, p2), (p2, p1)):
            if mover.target == other.start and other.target == other.start:
                mover.valid = False

        # Resolve dependencies when an agent tries to enter
        # the current position of the other agent.
        changed = True

        while changed:
            changed = False

            for mover, other in ((p1, p2), (p2, p1)):
                if not mover.valid:
                    continue

                if mover.target != other.start:
                    continue

                # The other agent is staying or cannot move.
                if not other.valid or other.target == other.start:
                    mover.valid = False
                    changed = True
        # Apply box pushes only after resolving conflicts.
        for proposal in (p1, p2):
            if proposal.valid and proposal.box_from is not None:
                owner = self.state.boxes.pop(proposal.box_from)
                self.state.boxes[proposal.box_to] = proposal.agent_id

        # Update both agent positions.
        for proposal in (p1, p2):
            if proposal.valid:
                self.state.agents[proposal.agent_id] = proposal.target

        self.state.turn += 1

        if self.state.turn >= self.max_turns:
            self.finished = True

        scores = {
            1: self.state.score(1),
            2: self.state.score(2),
        }

        winner = self.state.winner() if self.finished else None

        return {
            "turn": self.state.turn,
            "actions": dict(actions),
            "accepted": {
                1: p1.valid,
                2: p2.valid,
            },
            "scores": scores,
            "winner": winner,
            "finished": self.finished,
        }
        
    def _is_inside(self, position: Position) -> bool:
        x, y = position
        return (
            0 <= x < self.state.width
            and 0 <= y < self.state.height
        )
