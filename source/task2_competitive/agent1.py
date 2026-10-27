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


class Agent1:
    def __init__(self):
        self.agent_id = 1

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
        opponent = state.agents[2]

        current_boxes = dict(boxes)

        for action, (dx, dy) in MOVES.items():
            target = (
                player[0] + dx,
                player[1] + dy
            )

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

                # The pushing agent becomes the owner.
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

    def heuristic(self, player, boxes, goals):
        box_dict = dict(boxes)
        candidates = []

        for position, owner in boxes:
            # Already scored by this agent.
            if position in goals and owner == self.agent_id:
                continue

            bx, by = position

            for dx, dy in MOVES.values():
                behind = (bx - dx, by - dy)
                destination = (bx + dx, by + dy)

                if destination in box_dict:
                    continue

                if behind == player:
                    approach = 0
                else:
                    approach = self.distance(player, behind)

                goal_distance = min(
                    (
                        self.distance(position, goal)
                        for goal in goals
                    ),
                    default=0
                )

                candidates.append(
                    approach + goal_distance + 1
                )

        return min(candidates, default=0)

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
            player, boxes, state.goals
        )

        heapq.heappush(
            frontier,
            (initial_h, 0, next(counter), start, None)
        )

        best_cost = {start: 0}

        # A fallback action is selected from explored states.
        fallback_action = "WAIT"
        fallback_rank = None

        while frontier:
            if time.perf_counter() - start_time >= time_limit:
                break

            _, cost, _, current, first_action = (
                heapq.heappop(frontier)
            )

            if cost != best_cost.get(current):
                continue

            current_player, current_boxes = current

            current_score = self.score(
                current_boxes, state.goals
            )

            if current_score > initial_score:
                return first_action or "WAIT"

            h = self.heuristic(
                current_player,
                current_boxes,
                state.goals
            )

            # Prefer progress toward scoring.
            if first_action is not None:
                rank = (
                    -current_score,
                    h,
                    cost
                )

                if (
                    fallback_rank is None
                    or rank < fallback_rank
                ):
                    fallback_rank = rank
                    fallback_action = first_action

            for action, new_player, new_boxes in (
                self.get_successors(
                    state, current_player, current_boxes
                )
            ):
                new_state = (new_player, new_boxes)
                new_cost = cost + 1

                if new_cost >= best_cost.get(
                    new_state, float("inf")
                ):
                    continue

                best_cost[new_state] = new_cost

                first = first_action or action

                new_h = self.heuristic(
                    new_player, new_boxes, state.goals
                )

                heapq.heappush(
                    frontier,
                    (
                        new_cost + new_h,
                        new_cost,
                        next(counter),
                        new_state,
                        first
                    )
                )

        return fallback_action