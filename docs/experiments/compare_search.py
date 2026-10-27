import sys
import time
import tracemalloc
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.problem import SokobanProblem
from core.search import solve


MAPS = ["maps/map1.txt", "maps/map2.txt"]
ALGORITHMS = ["ucs", "astar"]

def plot_results(rows, out_dir):
    maps = sorted(set(row["map"] for row in rows))
    algorithms = ALGORITHMS

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    x = range(len(maps))
    width = 0.35

    for i, algorithm in enumerate(algorithms):
        times = [
            next(r["time_s"] for r in rows if r["map"] == m and r["algorithm"] == algorithm)
            for m in maps
        ]
        offset = [p + i * width for p in x]
        axes[0].bar(offset, times, width, label=algorithm)

    axes[0].set_xticks([p + width / 2 for p in x])
    axes[0].set_xticklabels(maps)
    axes[0].set_ylabel("Time (s)")
    axes[0].set_title("Execution time")
    axes[0].legend()

    for i, algorithm in enumerate(algorithms):
        peaks = [
            next(r["peak_kb"] for r in rows if r["map"] == m and r["algorithm"] == algorithm)
            for m in maps
        ]
        offset = [p + i * width for p in x]
        axes[1].bar(offset, peaks, width, label=algorithm)

    axes[1].set_xticks([p + width / 2 for p in x])
    axes[1].set_xticklabels(maps)
    axes[1].set_ylabel("Peak memory (KB)")
    axes[1].set_title("Peak memory")
    axes[1].legend()

    fig.tight_layout()
    fig.savefig(out_dir / "results.png")

def run_once(problem, algorithm):
    tracemalloc.start()
    start = time.perf_counter()

    actions, cost, metrics = solve(problem, algorithm)

    elapsed = time.perf_counter() - start
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "algorithm": algorithm,
        "time_s": elapsed,
        "peak_kb": peak_bytes / 1024,
        "cost": cost,
        "steps": len(actions) if actions else None,
        "expanded": metrics.expanded,
        "generated": metrics.generated,
        "frontier_peak": metrics.frontier_peak,
    }

def main():
    root = Path(__file__).resolve().parents[2]
    rows = []

    for map_name in MAPS:
        problem = SokobanProblem.from_file(root / map_name)

        for algorithm in ALGORITHMS:
            result = run_once(problem, algorithm)
            result["map"] = map_name
            rows.append(result)

    header = (
        "| Map | Algorithm | Time (s) | Peak (KB) | Cost | Steps "
        "| Expanded | Generated | Frontier peak |"
    )
    separator = "|---" * 9 + "|"
    lines = [header, separator]

    for row in rows:
        lines.append(
            f"| {row['map']} | {row['algorithm']} "
            f"| {row['time_s']:.4f} | {row['peak_kb']:.2f} "
            f"| {row['cost']} | {row['steps']} "
            f"| {row['expanded']} | {row['generated']} "
            f"| {row['frontier_peak']} |"
        )

    table = "\n".join(lines)
    print(table)

    out_path = root / "docs" / "experiments" / "results.csv"
    
    fieldnames = [
        "map", "algorithm", "time_s", "peak_kb", "cost",
        "steps", "expanded", "generated", "frontier_peak",
    ]

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    plot_results(rows, root / "docs" / "experiments")

if __name__ == "__main__":
    main()