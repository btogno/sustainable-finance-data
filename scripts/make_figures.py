"""
make_figures.py — draw the seven figures printed in the thesis.

Input : data/sustfin_datasets.json   (the derived table written by derive.py)
Output: figures/fig4_1.png … figD_3.png

Every series is computed here from the derived table and nowhere else, so a
recoded paper moves the figures exactly as it moves docs/STATS.md. The only
third-party requirement is matplotlib; the rest of the build stays
standard-library only, which is why this runs from its own target rather than
from `make build`.

    python3 scripts/make_figures.py [--out DIR] [--dpi N]

Figures:
    4.1  cluster composition by publication period      (§4.1)
    4.2  geographic scope of the data by period         (§4.2)
    4.3  mean data and code scores by licensing exposure(§4.5)
    4.4  availability by publication year               (§4.6)
    D.1  distribution of the publication lag
    D.2  publication year against last year of data
    D.3  distribution of the composite availability score
"""

import argparse
import json
import os
import statistics
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "data", "sustfin_datasets.json")

# ---------------------------------------------------------------------------
# Palette. Sampled from the figures printed in the submitted thesis; the
# workbook's charts use the same values, so the two cannot drift apart.
# ---------------------------------------------------------------------------

PRIMARY = "#1F4FB8"      # first series
SECOND = "#C87A00"       # second series
THIRD = "#8E44AD"        # third series (Figure 4.2 only)
RAMP = ["#CBD6EE", "#7E9AD9", "#3357B5", "#001C6E"]   # period ramp, old -> new
RAMP_DARK_TEXT = 2       # ramp steps at this index and above take white labels
GRID = "#E1E5EA"
TICK = "#55606E"
LABEL = "#1A1A1A"
CANVAS = "#FBFBFC"

# Segment and share labels are suppressed below these values, because a label
# wider than its segment is worse than no label.
MIN_COUNT_LABEL = 5
MIN_SHARE_LABEL = 0.10

PERIODS = ["2011–2015", "2016–2020", "2021–2023", "2024–2026"]
PERIOD_BOUNDS = [(2011, 2015), (2016, 2020), (2021, 2023), (2024, 2026)]

CLUSTER_ORDER = [
    "Biodiversity & Nature",
    "Climate Physical Risk",
    "Climate Transition Risk & Corporate Emissions",
    "Green Bonds & Sustainable Debt",
    "Social & Governance",
    "ESG Disclosure & Ratings",
]

# Two-line labels for the figure axes, where the full cluster name will not fit.
CLUSTER_LABEL = {
    "Biodiversity & Nature": "Biodiversity & nature",
    "Climate Physical Risk": "Climate physical risk",
    "Climate Transition Risk & Corporate Emissions":
        "Climate transition risk\n& corporate emissions",
    "Green Bonds & Sustainable Debt": "Green bonds &\nsustainable debt",
    "Social & Governance": "Social & governance",
    "ESG Disclosure & Ratings": "ESG disclosure & ratings",
}

EXPOSURE_ORDER = ["licensed only", "licensed and public", "public only", "neither"]
EXPOSURE_LABEL = {
    "licensed only": "Licensed only",
    "licensed and public": "Licensed and public",
    "public only": "Public only",
    "neither": "Neither",
}

YEARS = list(range(2011, 2027))


# ---------------------------------------------------------------------------
# Shared chart furniture
# ---------------------------------------------------------------------------

def new_fig(w_px, h_px, dpi):
    fig, ax = plt.subplots(figsize=(w_px / dpi, h_px / dpi), dpi=dpi)
    fig.patch.set_facecolor(CANVAS)
    ax.set_facecolor(CANVAS)
    for side in ("top", "right", "bottom", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(colors=TICK, length=0, labelsize=9)
    for lbl in list(ax.get_xticklabels()) + list(ax.get_yticklabels()):
        lbl.set_color(TICK)
    return fig, ax


def gridlines(ax, axis="y"):
    ax.grid(axis=axis, color=GRID, linewidth=0.9, zorder=0)
    ax.set_axisbelow(True)


def save(fig, ax, out, name, dpi):
    for lbl in list(ax.get_xticklabels()) + list(ax.get_yticklabels()):
        lbl.set_color(TICK)
    ax.xaxis.label.set_color(TICK)
    ax.yaxis.label.set_color(TICK)
    path = os.path.join(out, name)
    fig.savefig(path, dpi=dpi, facecolor=CANVAS, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    print("wrote", os.path.relpath(path, ROOT))


def period_of(year):
    for (lo, hi), label in zip(PERIOD_BOUNDS, PERIODS):
        if lo <= year <= hi:
            return label
    raise ValueError("publication year %r outside the corpus window" % year)


# ---------------------------------------------------------------------------
# Figure 4.1 — cluster composition by publication period
# ---------------------------------------------------------------------------

def fig_4_1(rows, out, dpi):
    counts = {
        c: [sum(1 for r in rows if c in r["clusters"] and period_of(r["publication_year"]) == p)
            for p in PERIODS]
        for c in CLUSTER_ORDER
    }
    order = sorted(CLUSTER_ORDER, key=lambda c: sum(counts[c]))   # smallest at the bottom

    fig, ax = new_fig(1315, 669, dpi)
    gridlines(ax, "x")
    ypos = range(len(order))
    left = [0.0] * len(order)
    for i, period in enumerate(PERIODS):
        vals = [counts[c][i] for c in order]
        ax.barh(list(ypos), vals, left=left, height=0.62, color=RAMP[i],
                label=period, zorder=3)
        for y, (v, l) in enumerate(zip(vals, left)):
            if v >= MIN_COUNT_LABEL:
                ax.text(l + v / 2, y, str(v), ha="center", va="center", fontsize=10,
                        color="white" if i >= RAMP_DARK_TEXT else LABEL, zorder=4)
        left = [l + v for l, v in zip(left, vals)]
    for y, total in enumerate(left):
        ax.text(total + 0.6, y, str(int(total)), ha="left", va="center",
                fontsize=11, fontweight="bold", color=LABEL, zorder=4)

    ax.set_yticks(list(ypos))
    ax.set_yticklabels([CLUSTER_LABEL[c] for c in order], fontsize=11)
    ax.set_xlabel("Papers", fontsize=11)
    ax.set_xlim(0, max(left) * 1.10)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=4,
              frameon=False, fontsize=10, labelcolor=TICK, handlelength=1.2)
    save(fig, ax, out, "fig4_1.png", dpi)


# ---------------------------------------------------------------------------
# Figure 4.2 — geographic scope of the data by period
# ---------------------------------------------------------------------------

def fig_4_2(rows, out, dpi):
    groups = [("United States", ["US"]),
              ("Global", ["Global"]),
              ("Europe and other", ["Europe", "Asia-Pacific", "Other / Regional"])]
    n = [sum(1 for r in rows if period_of(r["publication_year"]) == p) for p in PERIODS]
    shares = {
        name: [sum(1 for r in rows
                   if period_of(r["publication_year"]) == p
                   and r["geographic_scope"] in scopes) / n[i]
               for i, p in enumerate(PERIODS)]
        for name, scopes in groups
    }

    fig, ax = new_fig(958, 657, dpi)
    gridlines(ax, "y")
    x = range(len(PERIODS))
    bottom = [0.0] * len(PERIODS)
    for (name, _), colour in zip(groups, (PRIMARY, SECOND, THIRD)):
        vals = shares[name]
        ax.bar(list(x), vals, bottom=bottom, width=0.62, color=colour,
               label=name, zorder=3)
        for xi, (v, b) in enumerate(zip(vals, bottom)):
            if v >= MIN_SHARE_LABEL:
                ax.text(xi, b + v / 2, "%d%%" % round(v * 100), ha="center",
                        va="center", fontsize=11, color="white", zorder=4)
        bottom = [b + v for b, v in zip(bottom, vals)]

    ax.set_xticks(list(x))
    ax.set_xticklabels(["%s\n(n = %d)" % (p, k) for p, k in zip(PERIODS, n)], fontsize=10)
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0))
    ax.set_ylabel("Share of papers in the period", fontsize=11)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.20), ncol=3,
              frameon=False, fontsize=10, labelcolor=TICK, handlelength=1.2)
    save(fig, ax, out, "fig4_2.png", dpi)


# ---------------------------------------------------------------------------
# Figure 4.3 — mean data and code scores by licensing exposure
# ---------------------------------------------------------------------------

def fig_4_3(rows, out, dpi):
    grp = {e: [r for r in rows if r["licensing_exposure"] == e] for e in EXPOSURE_ORDER}
    data = [statistics.fmean(r["data_score"] for r in grp[e]) for e in EXPOSURE_ORDER]
    code = [statistics.fmean(r["code_score"] for r in grp[e]) for e in EXPOSURE_ORDER]

    fig, ax = new_fig(1080, 539, dpi)
    gridlines(ax, "y")
    x = list(range(len(EXPOSURE_ORDER)))
    w = 0.36
    for off, vals, colour, lab in ((-w / 2, data, PRIMARY, "Mean data score"),
                                   (w / 2, code, SECOND, "Mean code score")):
        ax.bar([xi + off for xi in x], vals, width=w, color=colour, label=lab, zorder=3)
        for xi, v in zip(x, vals):
            ax.text(xi + off, v + 0.012, "%.2f" % v, ha="center", va="bottom",
                    fontsize=10, color=LABEL, zorder=4)

    ax.set_xticks(x)
    ax.set_xticklabels(["%s\n(n = %d)" % (EXPOSURE_LABEL[e], len(grp[e]))
                        for e in EXPOSURE_ORDER], fontsize=9)
    ax.set_ylabel("Mean score, [0, 1]", fontsize=11)
    ax.set_ylim(0, max(data + code) * 1.20)
    ax.legend(loc="upper center", bbox_to_anchor=(0.62, 1.06), ncol=2,
              frameon=False, fontsize=10, labelcolor=TICK, handlelength=1.2)
    save(fig, ax, out, "fig4_3.png", dpi)


# ---------------------------------------------------------------------------
# Figure 4.4 — availability by publication year
#
# The two series are SHARES of the year's papers, not mean scores. A paper
# coded `On Demand` on code scores 0.25 and is not posting code; reading the
# mean code score into this figure is the error the 22 September reconciliation
# found in the previously printed version at 2013.
# ---------------------------------------------------------------------------

def fig_4_4(rows, out, dpi):
    by_year = {y: [r for r in rows if r["publication_year"] == y] for y in YEARS}
    share_code, share_panel, counts = [], [], []
    for y in YEARS:
        rs = by_year[y]
        counts.append(len(rs))
        if not rs:
            share_code.append(float("nan"))
            share_panel.append(float("nan"))
            continue
        share_code.append(sum(1 for r in rs if r["code_availability"] == "Y") / len(rs))
        share_panel.append(sum(1 for r in rs if r["data_availability"] == "Y") / len(rs))

    fig, ax = new_fig(1260, 568, dpi)
    gridlines(ax, "y")
    x = list(range(len(YEARS)))
    ax.plot(x, share_code, marker="o", markersize=6, linewidth=2.2, color=PRIMARY,
            label="Share posting replication code", zorder=3)
    ax.plot(x, share_panel, marker="s", markersize=6, linewidth=2.2, color=SECOND,
            label="Share releasing the analysis panel", zorder=3)

    cut = YEARS.index(2023) - 0.5
    ax.axvline(cut, color=TICK, linestyle="--", linewidth=1.3, zorder=2)
    ax.text(cut + 0.15, 0.44, "2023", fontsize=10, color=TICK, zorder=4)

    ax.set_xticks(x)
    ax.set_xticklabels(["%d\n%s" % (y, c if c else "–") for y, c in zip(YEARS, counts)],
                       fontsize=7.5)
    ax.set_xlim(-0.6, len(YEARS) - 0.4)
    ax.set_xlabel("Publication year, with the number of papers beneath", fontsize=10)
    ax.set_ylabel("Share of the year's papers", fontsize=10)
    ax.set_ylim(-0.03, 0.95)
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0))
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.14), ncol=2, frameon=False,
              fontsize=9.5, labelcolor=TICK, handlelength=1.6)
    save(fig, ax, out, "fig4_4.png", dpi)


# ---------------------------------------------------------------------------
# Figure D.1 — distribution of the publication lag
# ---------------------------------------------------------------------------

def fig_D_1(rows, out, dpi):
    lags = [r["lag_years"] for r in rows]
    hi = max(lags)
    bins = list(range(0, hi + 1))
    counts = [sum(1 for l in lags if l == b) for b in bins]
    mean = statistics.fmean(lags)

    fig, ax = new_fig(983, 493, dpi)
    gridlines(ax, "y")
    ax.bar(bins, counts, width=0.72, color=PRIMARY, zorder=3)
    for b, c in zip(bins, counts):
        if c:
            ax.text(b, c + 0.5, str(c), ha="center", va="bottom", fontsize=10,
                    color=LABEL, zorder=4)
    ax.axvline(mean, color=TICK, linestyle="--", linewidth=1.3, zorder=2)
    ax.text(mean + 0.18, max(counts) * 0.94, "mean %.2f" % mean, fontsize=10,
            color=TICK, zorder=4)

    ax.set_xticks(bins)
    ax.set_xticklabels([str(b) for b in bins], fontsize=10)
    ax.set_xlabel("Years from last year of data to publication", fontsize=11)
    ax.set_ylabel("Papers", fontsize=11)
    ax.set_ylim(0, max(counts) * 1.14)
    save(fig, ax, out, "figD_1.png", dpi)


# ---------------------------------------------------------------------------
# Figure D.2 — publication year against the last year of the paper's data
# ---------------------------------------------------------------------------

def fig_D_2(rows, out, dpi):
    # Deterministic horizontal offset: points sharing a coordinate are fanned
    # out in a fixed order, so the figure is reproducible run to run.
    seen = Counter()
    xs, ys = [], []
    for r in sorted(rows, key=lambda r: r["paper_id"]):
        key = (r["publication_year"], r["dataset_end_year"])
        k = seen[key]
        seen[key] += 1
        step = 0.085
        offset = ((k + 1) // 2) * step * (1 if k % 2 else -1)
        xs.append(r["publication_year"] + offset)
        ys.append(r["dataset_end_year"])

    lo, hi = 2010, 2026
    median_lag = statistics.median(r["lag_years"] for r in rows)

    fig, ax = new_fig(982, 601, dpi)
    gridlines(ax, "both")
    ax.plot([lo, hi], [lo, hi], linestyle=":", linewidth=1.6, color=TICK,
            label="No lag: data current at publication", zorder=2)
    ax.plot([lo, hi], [lo - median_lag, hi - median_lag], linewidth=2.2, color=SECOND,
            label="Median lag of %s years" % _spell(median_lag), zorder=2)
    ax.scatter(xs, ys, s=52, color=PRIMARY, alpha=0.72, linewidths=0, zorder=3)

    ax.set_xlabel("Publication year", fontsize=11)
    ax.set_ylabel("Last year of the paper's data", fontsize=11)
    ax.set_xticks(list(range(2010, 2027, 2)))
    ax.legend(loc="lower right", bbox_to_anchor=(1.0, 0.0), frameon=False,
              fontsize=9, labelcolor=TICK, handlelength=2.0)
    save(fig, ax, out, "figD_2.png", dpi)


def _spell(n):
    words = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}
    return words.get(int(n), str(int(n)))


# ---------------------------------------------------------------------------
# Figure D.3 — distribution of the composite availability score
# ---------------------------------------------------------------------------

def fig_D_3(rows, out, dpi):
    bins = [i / 8 for i in range(9)]
    counts = [sum(1 for r in rows if abs(r["openness_score"] - b) < 1e-9) for b in bins]

    fig, ax = new_fig(952, 489, dpi)
    gridlines(ax, "y")
    x = list(range(len(bins)))
    ax.bar(x, counts, width=0.72, color=PRIMARY, zorder=3)
    for xi, c in zip(x, counts):
        if c:
            ax.text(xi, c + 0.6, str(c), ha="center", va="bottom", fontsize=10,
                    color=LABEL, zorder=4)
    ax.set_xticks(x)
    ax.set_xticklabels([("%g" % b) for b in bins], fontsize=10)
    ax.set_xlabel("Composite availability score", fontsize=11)
    ax.set_ylabel("Papers", fontsize=11)
    ax.set_ylim(0, max(counts) * 1.14)
    save(fig, ax, out, "figD_3.png", dpi)


# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Every value plotted, written out as text.
#
# A figure cannot be checked against STATS.md by looking at it. This writes the
# series behind each figure so that every printed point has a number a reader
# can compare, which is what makes the figures auditable rather than merely
# reproducible.
# ---------------------------------------------------------------------------

def write_series(rows, out):
    L = []
    w = L.append
    w("# Figure series\n")
    w("Every value plotted in `fig4_1.png` … `figD_3.png`, written out by "
      "`scripts/make_figures.py` from the same derived table the figures are drawn "
      "from. Compare against [STATS.md](../docs/STATS.md).\n")

    w("\n## Figure 4.1 — cluster composition by period\n")
    counts = {c: [sum(1 for r in rows if c in r["clusters"]
                      and period_of(r["publication_year"]) == p) for p in PERIODS]
              for c in CLUSTER_ORDER}
    w("| Cluster | " + " | ".join(PERIODS) + " | Total |")
    w("|---|" + "---:|" * (len(PERIODS) + 1))
    for c in sorted(CLUSTER_ORDER, key=lambda c: -sum(counts[c])):
        w("| %s | %s | **%d** |" % (c, " | ".join(str(v) for v in counts[c]), sum(counts[c])))
    w("| *Papers in period* | %s | *%d* |" %
      (" | ".join(str(sum(1 for r in rows if period_of(r["publication_year"]) == p))
                  for p in PERIODS), len(rows)))

    w("\n## Figure 4.2 — geographic scope by period (shares)\n")
    groups = [("United States", ["US"]), ("Global", ["Global"]),
              ("Europe and other", ["Europe", "Asia-Pacific", "Other / Regional"])]
    n = [sum(1 for r in rows if period_of(r["publication_year"]) == p) for p in PERIODS]
    w("| Scope | " + " | ".join("%s (n = %d)" % (p, k) for p, k in zip(PERIODS, n)) + " |")
    w("|---|" + "---:|" * len(PERIODS))
    for name, scopes in groups:
        vals = [sum(1 for r in rows if period_of(r["publication_year"]) == p
                    and r["geographic_scope"] in scopes) / n[i]
                for i, p in enumerate(PERIODS)]
        w("| %s | %s |" % (name, " | ".join("%.4f" % v for v in vals)))

    w("\n## Figure 4.3 — mean scores by licensing exposure\n")
    w("| Exposure | n | Mean data | Mean code |")
    w("|---|---:|---:|---:|")
    for e in EXPOSURE_ORDER:
        g = [r for r in rows if r["licensing_exposure"] == e]
        w("| %s | %d | %.4f | %.4f |" % (EXPOSURE_LABEL[e], len(g),
                                         statistics.fmean(r["data_score"] for r in g),
                                         statistics.fmean(r["code_score"] for r in g)))

    w("\n## Figure 4.4 — availability by publication year\n")
    w("Both series are **shares of the year's papers**, not mean scores. A paper coded")
    w("`On Demand` on code scores 0.25 and is not posting code.\n")
    w("| Year | Papers | Share posting code | Share releasing the panel |")
    w("|---:|---:|---:|---:|")
    for y in YEARS:
        rs = [r for r in rows if r["publication_year"] == y]
        if not rs:
            w("| %d | 0 | — | — |" % y)
            continue
        w("| %d | %d | %.4f | %.4f |" %
          (y, len(rs),
           sum(1 for r in rs if r["code_availability"] == "Y") / len(rs),
           sum(1 for r in rs if r["data_availability"] == "Y") / len(rs)))

    lags = [r["lag_years"] for r in rows]
    w("\n## Figure D.1 — distribution of the publication lag\n")
    w("| Lag (years) | " + " | ".join(str(b) for b in range(max(lags) + 1)) + " |")
    w("|---|" + "---:|" * (max(lags) + 1))
    w("| Papers | " + " | ".join(str(sum(1 for l in lags if l == b))
                                 for b in range(max(lags) + 1)) + " |")
    w("\nMedian %g · mean %.4f · maximum %d · n = %d\n" %
      (statistics.median(lags), statistics.fmean(lags), max(lags), len(lags)))

    w("\n## Figure D.2 — reference lines\n")
    med = statistics.median(lags)
    w("| Line | From | To |")
    w("|---|---|---|")
    w("| No lag | (2010, 2010) | (2026, 2026) |")
    w("| Median lag of %g years | (2010, %d) | (2026, %d) |" % (med, 2010 - med, 2026 - med))
    w("\n%d points plotted, one per paper. Horizontal offsets are cosmetic and "
      "deterministic; the vertical coordinate is the paper's `dataset_end_year`.\n" % len(rows))

    w("\n## Figure D.3 — distribution of the composite availability score\n")
    bins = [i / 8 for i in range(9)]
    w("| Score | " + " | ".join("%g" % b for b in bins) + " |")
    w("|---|" + "---:|" * len(bins))
    w("| Papers | " + " | ".join(
        str(sum(1 for r in rows if abs(r["openness_score"] - b) < 1e-9)) for b in bins) + " |")

    path = os.path.join(out, "FIGURE_SERIES.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print("wrote", os.path.relpath(path, ROOT))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=os.path.join(ROOT, "figures"),
                    help="output directory (default: figures/)")
    ap.add_argument("--dpi", type=int, default=200)
    args = ap.parse_args()

    with open(SRC, encoding="utf-8") as fh:
        rows = json.load(fh)
    if len(rows) != 109:
        print("warning: derived table holds %d rows, not the frozen 109" % len(rows))

    os.makedirs(args.out, exist_ok=True)
    for fn in (fig_4_1, fig_4_2, fig_4_3, fig_4_4, fig_D_1, fig_D_2, fig_D_3):
        fn(rows, args.out, args.dpi)
    write_series(rows, args.out)


if __name__ == "__main__":
    main()
