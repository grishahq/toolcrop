"""Plot exported counts without invented measurements."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parents[1]
report = json.loads((root / "evidence/inventory-v1/report.json").read_text())
fig, ax = plt.subplots(figsize=(12, 6.75), facecolor="#0c1720")
ax.set_facecolor("#0c1720")
labels = ["Schema checks", "Executes without error", "Execution + goal checks"]
values = [report["overall"]["schema_valid"], report["overall"]["executable"], report["overall"]["accepted"]]
bars = ax.barh(labels[::-1], values[::-1], color=["#7ce3ba", "#e9bd70", "#8cacc5"], height=.55)
for bar, value in zip(bars, values[::-1], strict=True):
    ax.text(value + 8, bar.get_y() + bar.get_height() / 2, str(value), va="center", color="white", fontsize=20)
ax.set_xlim(0, 620)
ax.set_xlabel("Candidates admitted from the same 620 trajectories", color="#bdccd5", labelpad=15)
ax.tick_params(colors="#e7eef3", labelsize=13)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.set_title("A valid call can still miss the task", color="white", fontsize=25, pad=30, loc="left")
fig.text(.035, .065, "TOOLCROP · CONTROLLED OFFLINE FIXTURES\n124 reference plans + 496 predefined corruptions · one inventory environment\nDescriptive counts, not measured model performance or a training-quality gain.", color="#bdccd5", fontsize=11)
fig.subplots_adjust(left=.27, right=.94, bottom=.25, top=.8)
fig.savefig(root / "campaign/assets/filter-comparison.png", dpi=180, facecolor=fig.get_facecolor())
print("Chart plotted from evidence/inventory-v1/report.json")
