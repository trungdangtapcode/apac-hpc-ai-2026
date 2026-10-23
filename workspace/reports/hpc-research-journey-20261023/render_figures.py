"""Render presentation figures from reviewed native CPU evidence, never estimates."""
from pathlib import Path
import hashlib
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[2]
RESEARCH = PROJECT_ROOT / "2026-APAC-HPC-AI/hpc-experiments"
FOUR = RESEARCH / "four-node-review-20261023/review.json"
EARLIER = RESEARCH / "shared-cpu-density-review-20261022/review.json"
CONFIRMATION = RESEARCH / "nscc-cpu-four-node-confirm-20261023/submission.json"
OUT = HERE / "figures"
COLORS = {"hierarchical": "#2563a6", "scotch": "#d55e00"}


def save(fig, name):
    for suffix in ("svg", "png"):
        fig.savefig(OUT / (name + "." + suffix), dpi=170, facecolor="white")
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    four = json.loads(FOUR.read_text())
    earlier = json.loads(EARLIER.read_text())
    assert not four["per_run_gate_failures"]
    runs = list(four["runs"].values())
    assert len(runs) == 6 and all(r["timed_steps"] == 149 for r in runs)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "svg.fonttype": "none"})

    ordered = sorted(runs, key=lambda r: (r["per_node_mpi_ranks"], r["method"]))
    fig, ax = plt.subplots(figsize=(11.8, 6.1))
    fig.subplots_adjust(left=.29, right=.96, top=.84, bottom=.20)
    values = [r["native_simplefoam"]["average_step_seconds"] for r in ordered]
    ax.barh(range(6), values, color=[COLORS[r["method"]] for r in ordered], height=.65)
    labels = [r["method"].capitalize() + "  |  " + str(r["per_node_mpi_ranks"]) + " ranks/node" for r in ordered]
    ax.set_yticks(range(6), labels)
    ax.invert_yaxis()
    ax.set_xlim(0, max(values) * 1.13)
    ax.set_xlabel("Native mean seconds per solver iteration — lower is better")
    ax.set_axisbelow(True)
    ax.grid(axis="x", alpha=.16)
    for row, value in enumerate(values):
        ax.text(value + .09, row, f"{value:.3f}", va="center", weight="bold")
    fig.suptitle("Four-node choice depends on rank count and decomposition", x=.04, ha="left", fontsize=17, weight="bold")
    fig.text(.04, .895, "150 solver iterations; 149 native timed samples in each run", color="#444444")
    fig.text(.04, .06, "Separate allocations; these are candidate native records, not accepted scores.\nRequested CPUs: Scotch64/96 = 256/384; other configurations = 512. Final PBS accounting is unavailable.", fontsize=9, color="#555555")
    save(fig, "four-node-means")

    ids = {"hierarchical": ["25921831.pbs101", "25921809.pbs101", "25921692.pbs101"],
           "scotch": ["25921487.pbs101", "25921492.pbs101", "25921488.pbs101"]}
    series = {}
    fig, ax = plt.subplots(figsize=(11.8, 6.0))
    fig.subplots_adjust(left=.10, right=.94, top=.84, bottom=.23)
    for method, job_ids in ids.items():
        means = []
        for job in job_ids:
            result = four["runs"].get(job) or earlier["runs"][job]
            means.append(result["native_simplefoam"]["average_step_seconds"])
        series[method] = means
        ax.plot([1, 2, 4], means, "o-", color=COLORS[method], lw=2.3, ms=7, label=method.capitalize())
        for n, value in zip([1, 2, 4], means):
            ax.annotate(f"{value:.3f}", (n, value), xytext=(9, 10 if method == "hierarchical" else -18),
                        textcoords="offset points", color=COLORS[method], fontsize=10)
    ax.set_xticks([1, 2, 4], ["1 node\n40 iterations", "2 nodes\n80 iterations", "4 nodes\n150 iterations"])
    ax.set_ylim(0, 16.5)
    ax.set_ylabel("Native mean seconds per iteration")
    ax.grid(alpha=.17)
    ax.legend(loc="upper right", frameon=False)
    fig.suptitle("Observed scaling at 128 MPI ranks per node", x=.04, ha="left", fontsize=17, weight="bold")
    fig.text(.04, .895, "Hierarchical leads the two-node observation; Scotch leads at four nodes", color="#444444")
    fig.text(.04, .045, "Prescribed endpoints differ and every point uses a separate allocation.\nThese curves show observations, not a controlled same-work speedup or causal effect.", fontsize=9, color="#555555")
    save(fig, "observed-scaling")

    fig, ax = plt.subplots(figsize=(11.8, 6.0))
    fig.subplots_adjust(left=.09, right=.96, top=.84, bottom=.21)
    for method, job in (("hierarchical", "25921692.pbs101"), ("scotch", "25921488.pbs101")):
        result = four["runs"][job]["native_simplefoam"]
        samples = result["step_time_samples"]
        x = [s["time"] for s in samples]
        y = [s["wallClockTime_dat_seconds"] for s in samples]
        assert len(x) == len(y) == 149 and x == list(range(2, 151))
        ax.plot(x, y, color=COLORS[method], lw=1.15, alpha=.9,
                label=f"{method.capitalize()} — native mean {result['average_step_seconds']:.3f} s")
    peak = four["runs"]["25921488.pbs101"]["native_simplefoam"]
    ax.annotate(f"Time {peak['max_time']}: {peak['max_seconds']:.2f} s\nRetained in the native mean",
                (peak["max_time"], peak["max_seconds"]), xytext=(35, 29),
                arrowprops={"arrowstyle": "->", "color": COLORS["scotch"]}, fontsize=10)
    ax.set_xlim(1, 151)
    ax.set_ylim(0, 40)
    ax.set_xlabel("Solver iteration index (Time)")
    ax.set_ylabel("Seconds in that iteration")
    ax.grid(alpha=.16)
    ax.legend(frameon=False, loc="upper left")
    fig.suptitle("The mean alone hides slow iterations", x=.04, ha="left", fontsize=17, weight="bold")
    fig.text(.04, .895, "All 149 measured iterations shown, for the two 128-rank/node runs", color="#444444")
    fig.text(.04, .055, "No samples removed. Both native loggers emit short-sample warnings.\nThe traces identify when slow steps occurred; no hardware/MPI measurement establishes their cause.", fontsize=9, color="#555555")
    save(fig, "iteration-spikes")

    fig, ax = plt.subplots(figsize=(14, 7.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    boxes = [
        (.13, .73, "21 Oct — establish the task", "Official case + source checks\nFull required work and precision", "#e8f0fb"),
        (.38, .73, "21 Oct — native baseline", "Hierarchical, 1 node / 128 ranks\n14.922 seconds per step", "#e8f0fb"),
        (.63, .73, "21 Oct — compare methods", "Same-node H then Scotch\n0.994% observed gain, noisy", "#e8f0fb"),
        (.88, .73, "21 Oct — locality hypothesis", "NUMA-aware Scotch graph\n10.63% fewer crossing faces", "#fff1d6"),
        (.88, .32, "22 Oct — hypothesis loses", "3.44% slower in the solve\nClose this unchanged candidate", "#fbe9e7"),
        (.63, .32, "22 Oct — scale and density", "Keep 40 / 80-step endpoints\nHierarchical leads at 2 nodes", "#e8f0fb"),
        (.38, .32, "23 Oct — scored-size logs", "Scotch 128 ranks/node, 4 nodes\n3.678 s/step native observation", "#e6f2ee"),
        (.13, .32, "23 Oct — repeat submitted", "Independent frozen S128 run\nNew result not reviewed yet", "#f1f3f5"),
    ]
    width, height = .215, .24
    for x, y, title, body, color in boxes:
        ax.add_patch(FancyBboxPatch((x-width/2, y-height/2), width, height,
                                   boxstyle="round,pad=0.009", facecolor=color,
                                   edgecolor="#9da9b7", linewidth=1))
        ax.text(x, y+.055, title, ha="center", va="center", fontsize=10, weight="bold")
        ax.text(x, y-.025, body, ha="center", va="center", fontsize=9.6, linespacing=1.5)
    for i in range(len(boxes)-1):
        x1, y1 = boxes[i][:2]
        x2, y2 = boxes[i+1][:2]
        if y1 == y2:
            sign = 1 if x2 > x1 else -1
            start, end = (x1+sign*(width/2+.012), y1), (x2-sign*(width/2+.012), y2)
        else:
            start, end = (x1, y1-height/2-.012), (x2, y2+height/2+.012)
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=15, color="#526477"))
    fig.suptitle("The research journey: test an idea, keep the result, change direction", x=.035, ha="left", fontsize=17, weight="bold")
    fig.text(.035, .045, "Native observations are not accepted scores. No samples were discarded.\nA separate CPU-placement candidate reduces graph cut by 4.57%; its solve remains unsubmitted and unmeasured.", fontsize=10, color="#555555")
    save(fig, "research-journey")

    lineage = {"matplotlib_version": matplotlib.__version__,
               "inputs": {str(p.relative_to(PROJECT_ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (FOUR, EARLIER, CONFIRMATION)},
               "scaling_series_seconds_per_iteration": series,
               "notes": "All displayed values come from reviewed native records. No trimmed mean, causal speedup or confidence bands.",
               "files": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.suffix in ("svg", "png")}}
    (OUT / "provenance.json").write_text(json.dumps(lineage, indent=2) + "\n")


if __name__ == "__main__":
    main()
