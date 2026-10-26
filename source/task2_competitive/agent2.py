
import heapq
import itertools
import time

from .competitive_state import CompetitiveState


MOVES = {
    "North": (0, -1),
    "East": (1, 0),
    "South": (0, 1),
    "West": (-1, 0),
}


class Agent2:
    def __init__(self):
        self.agent_id = 2

    @staticmethod
    def distance(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def is_free(self, state, position):
        x, y = position
        return (
            0 <= x < state.width
            and 0 <= y < state.height
            and position not in state.walls
        )

    def get_successors(self, state, player, boxes):
        successors = []
        opponent = state.agents[1]
        current_boxes = dict(boxes)

        for action, (dx, dy) in MOVES.items():
            target = (player[0] + dx, player[1] + dy)

            if not self.is_free(state, target):
                continue

            if target == opponent:
                continue

            new_boxes = current_boxes.copy()

            if target in current_boxes:
                box_target = (
                    target[0] + dx,
                    target[1] + dy
                )

                if not self.is_free(state, box_target):
                    continue

                if box_target in current_boxes:
                    continue

                if box_target == opponent:
                    continue

                # Agent 2 gains ownership when pushing.
                del new_boxes[target]
                new_boxes[box_target] = self.agent_id

            successors.append((
                action,
                target,
                tuple(sorted(new_boxes.items()))
            ))

        return successors

    def score(self, boxes, goals):
        return sum(
            1
            for position, owner in boxes
            if position in goals and owner == self.agent_id
        )

    def heuristic(self, player, boxes, goals, state):
        box_dict = dict(boxes)
        opponent = state.agents[1]
        candidates = []

        for position, owner in boxes:
            if position in goals and owner == self.agent_id:
                continue

            bx, by = position

            for dx, dy in MOVES.values():
                behind = (bx - dx, by - dy)
                destination = (bx + dx, by + dy)

                if not self.is_free(state, behind):
                    continue

                if not self.is_free(state, destination):
                    continue

                if behind in box_dict:
                    continue

                if destination in box_dict:
                    continue

                if behind == opponent:
                    continue

                if destination == opponent:
                    continue

                approach = self.distance(player, behind)

                # Approximate distance to a goal after pushing.
                goal_distance = min(
                    (
                        self.distance(destination, goal)
                        for goal in goals
                    ),
                    default=0
                )

                candidates.append(
                    approach + goal_distance + 1
                )

        if not candidates:
            return 100000

        return min(candidates)

    def choose_action(
        self,
        state: CompetitiveState,
        time_limit=0.9
    ):
        start_time = time.perf_counter()

        player = state.agents[self.agent_id]
        boxes = tuple(sorted(state.boxes.items()))
        start = (player, boxes)

        initial_score = self.score(boxes, state.goals)

        counter = itertools.count()
        frontier = []

        initial_h = self.heuristic(
            player, boxes, state.goals, state
        )

        heapq.heappush(
            frontier,
            (initial_h, next(counter), start, None)
        )

        visited = set()
        discovered = {start}

        fallback_action = "WAIT"
        fallback_rank = None

        while frontier:
            if time.perf_counter() - start_time >= time_limit:
                break

            h, _, current, first_action = heapq.heappop(
                frontier
            )

            if current in visited:
                continue

            visited.add(current)

            current_player, current_boxes = current

            current_score = self.score(
                current_boxes, state.goals
            )

            # A scoring plan has been found.
            if current_score > initial_score:
                return first_action or "WAIT"

            if first_action is not None:
                rank = (
                    -current_score,
                    h
                )

                if (
                    fallback_rank is None
                    or rank < fallback_rank
                ):
                    fallback_rank = rank
                    fallback_action = first_action

            for action, new_player, new_boxes in (
                self.get_successors(
                    state,
                    current_player,
                    current_boxes
                )
            ):
                new_state = (new_player, new_boxes)

                if new_state in discovered:
                    continue

                discovered.add(new_state)

                new_h = self.heuristic(
                    new_player,
                    new_boxes,
                    state.goals,
                    state
                )

                first = first_action or action

                heapq.heappush(
                    frontier,
                    (
                        new_h,
                        next(counter),
                        new_state,
                        first
                    )
                )

        return fallback_action
