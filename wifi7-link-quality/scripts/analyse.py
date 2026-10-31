"""Reproduce the tables and figures of the Wi-Fi 7 link-quality study.

Reads the CSV files in ../data and writes figures to ../figures.
Run from the repository root:  python scripts/analyse.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)

BANDS = ["2.4 GHz", "5 GHz", "6 GHz", "MLO"]
COLOURS = {"2.4 GHz": "#1f77b4", "5 GHz": "#ff7f0e", "6 GHz": "#2ca02c", "MLO": "#d62728"}

out = pd.read_csv(ROOT / "data" / "outdoor_measurements.csv")
ind = pd.read_csv(ROOT / "data" / "indoor_measurements.csv")


def pivot(metric):
    return out.pivot(index="distance_m", columns="band", values=metric)[BANDS]


# ---- MLO gain over the best single band (descriptive, per distance) ----
dl = pivot("download_mbps")
best_single = dl[["2.4 GHz", "5 GHz", "6 GHz"]].max(axis=1)
gain = 100 * (dl["MLO"] - best_single) / best_single
summary = pd.DataFrame({"best_single_mbps": best_single, "mlo_mbps": dl["MLO"], "mlo_gain_pct": gain.round(1)})
summary.to_csv(ROOT / "data" / "mlo_gain_summary.csv")
print(summary.to_string())
print(f"\nPeak MLO gain: {gain.max():.1f}% at {int(gain.idxmax())} m")

# ---- Figure 1: download vs distance ----
fig, ax = plt.subplots(figsize=(8, 4.5))
for b in BANDS:
    ax.plot(dl.index, dl[b], marker="o", label=b, color=COLOURS[b], lw=2.5 if b == "MLO" else 1.8)
ax.set_xlabel("Distance from access point (m)")
ax.set_ylabel("Download throughput (Mbps)")
ax.set_title("Outdoor download throughput by distance and band")
ax.grid(alpha=.3)
ax.legend()
fig.tight_layout()
fig.savefig(FIG / "outdoor_download_vs_distance.png", dpi=160)
plt.close(fig)

# ---- Figure 2: MLO gain ----
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.bar(gain.index, gain.values, width=6, color="#1f77b4")
ax.set_xlabel("Distance from access point (m)")
ax.set_ylabel("MLO gain vs best single band (%)")
ax.set_title("MLO download gain over the best single band")
ax.grid(axis="y", alpha=.3)
fig.tight_layout()
fig.savefig(FIG / "mlo_gain.png", dpi=160)
plt.close(fig)

# ---- Figure 3: RSSI decay ----
rssi = pivot("rssi_dbm")
fig, ax = plt.subplots(figsize=(8, 4.5))
for b in BANDS:
    ax.plot(rssi.index, rssi[b], marker="o", label=b, color=COLOURS[b])
ax.axhline(-85, ls="--", lw=1, color="#1f77b4", label="Illustrative -85 dBm reference")
ax.set_xlabel("Distance from access point (m)")
ax.set_ylabel("RSSI (dBm)")
ax.set_title("Outdoor signal-strength decay")
ax.grid(alpha=.3)
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(FIG / "outdoor_rssi_decay.png", dpi=160)
plt.close(fig)

# ---- Figure 4: indoor walls ----
walls = ind[ind["scenario"].str.contains("wall")].copy()
walls["n"] = walls["scenario"].str.extract(r"(\d)").astype(int)
fig, ax = plt.subplots(figsize=(8, 4.5))
for b in ["2.4 GHz", "5 GHz", "6 GHz"]:
    d = walls[walls["band"] == b].sort_values("n")
    ax.plot(d["n"], d["rssi_dbm"], marker="o", label=b, color=COLOURS[b])
ax.set_xticks([1, 2, 3])
ax.set_xlabel("Number of intervening walls")
ax.set_ylabel("RSSI (dBm)")
ax.set_title("Indoor wall-penetration signal profile (AUT building)")
ax.grid(alpha=.3)
ax.legend()
fig.tight_layout()
fig.savefig(FIG / "indoor_wall_penetration.png", dpi=160)
plt.close(fig)
print("\nFigures written to", FIG)
