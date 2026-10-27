
from dataclasses import dataclass, field
from typing import Dict, Optional, Set, Tuple

Position = Tuple[int, int]
Owner = Optional[int]


@dataclass
class CompetitiveState:
    width: int
    height: int
    walls: Set[Position]
    goals: Set[Position]
    agents: Dict[int, Position]
    boxes: Dict[Position, Owner] = field(default_factory=dict)
    turn: int = 0

    @classmethod
    def from_text(cls, text: str):
        lines = text.splitlines()

        if not lines:
            raise ValueError("Map cannot be empty.")

        width = max(len(line) for line in lines)
        height = len(lines)

        walls = set()
        goals = set()
        agents = {}
        boxes = {}

        for y, line in enumerate(lines):
            for x in range(width):
                pos = (x, y)

                if x >= len(line):
                    walls.add(pos)
                    continue

                cell = line[x]

                if cell == "%":
                    walls.add(pos)
                elif cell == "A":
                    if 1 in agents:
                        raise ValueError("Map has multiple Agent 1 markers.")
                    agents[1] = pos
                elif cell == "X":
                    if 2 in agents:
                        raise ValueError("Map has multiple Agent 2 markers.")
                    agents[2] = pos
                elif cell == "B":
                    boxes[pos] = None
                elif cell == "D":
                    goals.add(pos)
                elif cell == "C":
                    goals.add(pos)
                    boxes[pos] = None
                elif cell == " ":
                    pass
                else:
                    raise ValueError(
                        f"Unknown map symbol {cell!r} at {pos}."
                    )

        if set(agents) != {1, 2}:
            raise ValueError("Map must contain exactly one A and one X.")

        if not boxes:
            raise ValueError("Map must contain at least one box.")

        if not goals:
            raise ValueError("Map must contain at least one goal.")

        for agent_id, pos in agents.items():
            if pos in walls or pos in boxes:
                raise ValueError(
                    f"Agent {agent_id} overlaps a wall or box."
                )

        return cls(
            width=width,
            height=height,
            walls=walls,
            goals=goals,
            agents=agents,
            boxes=boxes,
        )

    @classmethod
    def from_file(cls, path: str):
        with open(path, "r", encoding="utf-8") as file:
            return cls.from_text(file.read())

    def clone(self):
        # Tạo trạng thái độc lập
        return CompetitiveState(
            width=self.width,
            height=self.height,
            walls=set(self.walls),
            goals=set(self.goals),
            agents=dict(self.agents),
            boxes=dict(self.boxes),
            turn=self.turn,
        )

    def score(self, agent_id: int) -> int:
        # Đếm các ô chứa mục tiêu của agent
        return sum(
            1
            for pos, owner in self.boxes.items()
            if pos in self.goals and owner == agent_id
        )

    def total_completed(self) -> int:
        # Đếm tất cả box nằm trên target
        return sum(pos in self.goals for pos in self.boxes)

    def is_solved(self) -> bool:
        return bool(self.boxes) and all(
            pos in self.goals for pos in self.boxes
        )

    def winner(self):
        # Trả về 1, 2 nếu None là hòa
        score_1 = self.score(1)
        score_2 = self.score(2)

        if score_1 > score_2:
            return 1
        if score_2 > score_1:
            return 2
        return None
