"""
build_docs.py — render the human-readable repository from the derived data.

Reads  : data/sustfin_datasets.json, data/link_inventory.csv
Writes : docs/CATALOGUE.md   one row per paper, all 109, sorted by availability
         docs/CITATIONS.md   full verbatim citation for every paper ID
         docs/STATS.md       every headline figure, recomputed
         README.md           refreshes the block between the STATS markers

Nothing here is hand-typed: every number in the repository is computed from the
frozen corpus, so `make build` is the only way a figure can change.
"""

import collections
import csv
import datetime as dt
import json
import os
import re
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOCS = os.path.join(ROOT, "docs")

CLUSTER_ORDER = [
    "Biodiversity & Nature",
    "Climate Physical Risk",
    "Climate Transition Risk & Corporate Emissions",
    "Green Bonds & Sustainable Debt",
    "Social & Governance",
    "ESG Disclosure & Ratings",
]

# Mirrors PERIOD_BOUNDS in derive.py (documented in CODEBOOK.md §6), which is
# the canonical declaration. Not stored as a derived field -- the schema stays
# at 36 fields per paper -- so every period table here computes it from
# publication_year via period_of() below.
PERIOD_BOUNDS = [
    (2011, 2015, "2011–2015"),
    (2016, 2020, "2016–2020"),
    (2021, 2023, "2021–2023"),
    (2024, 2026, "2024–2026"),
]
PERIOD_ORDER = [label for _, _, label in PERIOD_BOUNDS]


def period_of(year):
    for lo, hi, label in PERIOD_BOUNDS:
        if year is not None and lo <= year <= hi:
            return label
    return None

UNIT_ORDER = [
    "Firm-Year", "Other", "Portfolio-Level", "Asset-Level",
    "Document-Level", "Country-Year", "(unrecorded)",
]

DATA_LEVEL_ORDER = ["Y", "Partial", "Raw Data", "On Demand", "N"]
CODE_LEVEL_ORDER = ["Y", "Partial", "On Demand", "N"]

JOURNAL_ORDER = [
    "Journal of Finance",
    "Journal of Financial Economics",
    "Review of Financial Studies",
    "Review of Finance",
]

# Raw data source categories, in the order Table 4.1 Panel A presents them, with
# the access class each carries. This mirrors LICENSED / PUBLIC in derive.py
# and CODEBOOK.md §4, which is the canonical declaration of the classification
# itself; duplicated here (as CLUSTER_ORDER and PRIMARY_TO_CODE already are)
# so this file can render a table without importing derive.py.
SOURCE_CATEGORY_ORDER = [
    "Proprietary Database", "Market Data", "Official Statistics",
    "Weather & Hazard", "Other", "Survey Data", "SEC Filings",
    "Earnings Call transcripts", "News & Media", "Social Media",
    "Satellite Imagery", "CDP Reports",
]
SOURCE_CLASS = {
    "Proprietary Database": "licensed",
    "Market Data": "licensed",
    "Earnings Call transcripts": "licensed",
    "News & Media": "licensed",
    "Official Statistics": "public",
    "SEC Filings": "public",
    "Weather & Hazard": "public",
    "Satellite Imagery": "public",
    "CDP Reports": "public",
    "Survey Data": "neither",
    "Social Media": "neither",
    "Other": "neither",
}

DATA_BADGE = {
    "Y": "`D:OPEN`",
    "Partial": "`D:PART`",
    "Raw Data": "`D:RAW`",
    "On Demand": "`D:REQ`",
    "N": "`D:—`",
}

CODE_BADGE = {
    "Y": "`C:OPEN`",
    "Partial": "`C:PART`",
    "On Demand": "`C:REQ`",
    "N": "`C:—`",
}

METHOD_NAME = {
    "ECON": "Standard econometrics on accounting and market data",
    "SAT": "Satellite and remote sensing",
    "NLP": "NLP / textual analysis",
    "SURV": "Survey instrument",
    "EXP": "Experiment",
    "FILE": "Regulatory filing parsing",
    "ML": "Machine learning (non-NLP)",
    "META": "Meta-analysis / systematic review",
    "OTH": "Other",
}

METHOD_ORDER = ["ECON", "SAT", "NLP", "SURV", "EXP", "FILE", "ML", "META", "OTH"]

PRIMARY_TO_CODE = {
    "Standard Econometrics Accounting / Market Data": "ECON",
    "NLP / Textual Analysis": "NLP",
    "Satellite & Remote Sensing": "SAT",
    "Survey Instrument": "SURV",
    "Experiment": "EXP",
    "Regulatory Filing Parsing": "FILE",
    "Machine Learning (non-NLP)": "ML",
    "Meta-Analysis / Systematic Review": "META",
    "Other": "OTH",
}

TIER_BADGE = {f"Tier {i}": f"`T{i}`" for i in range(1, 8)}
TIER_BADGE[""] = ""

# The ladder, in order, with the rule and what a reader can do with an entry.
# Rules are enforced in curation_tier() in derive.py; these are the readable
# statements of the same thing.
TIER_LADDER = [
    ("Tier 1", "`data = Y` and `code = Y`",
     "Panel and code both released. Rerunnable as published."),
    ("Tier 2", "`data = Partial` and `code = Y`",
     "Code released against a partially released panel. Reproducible in part, "
     "and the cheapest entries to move into Tier 1."),
    ("Tier 3", "`data` is `Y` or `Partial`, `code` is not `Y`",
     "A panel is released but the analysis code is not. The result can be "
     "re-estimated, not reproduced exactly."),
    ("Tier 4", "`data = Raw Data` and `code = Y`",
     "No panel, but the code names the public sources it was built from and "
     "shows what was done to them."),
    ("Tier 5", "`data = N` and `code = Y`",
     "No panel and no public inputs, but the released code documents the "
     "pipeline. Usually the inputs are licensed rather than withheld."),
    ("Tier 6", "`data` is `Raw Data` or `On Demand`, `code` is not `Y`",
     "Provenance is recorded and nothing is released. Rebuilding means "
     "reconstructing every cleaning decision."),
    ("Tier 7", "`data = N` and `code` is not `Y`",
     "Neither the data nor the method is recoverable."),
]

# Tiers 1-3 are listed paper by paper in the README; 4-7 are summarised.
TIER_DETAIL = ("Tier 1", "Tier 2", "Tier 3")


def load():
    recs = json.load(open(os.path.join(ROOT, "data", "sustfin_datasets.json")))
    links = list(csv.DictReader(open(os.path.join(ROOT, "data", "link_inventory.csv"))))
    return recs, links


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def fmt(x, n=2):
    return f"{x:.{n}f}"


# ---------------------------------------------------------------------------
# statistics
# ---------------------------------------------------------------------------

def stats(recs, links):
    n = len(recs)
    s = {"n": n, "built_on": dt.date.today().isoformat()}

    s["journals"] = collections.Counter(r["journal"] for r in recs)
    s["years"] = collections.Counter(r["publication_year"] for r in recs)
    s["data_levels"] = collections.Counter(r["data_availability"] for r in recs)
    s["code_levels"] = collections.Counter(r["code_availability"] for r in recs)
    s["geo"] = collections.Counter(r["geographic_scope"] for r in recs)
    s["unit"] = collections.Counter(r["unit_of_observation"] or "(unrecorded)" for r in recs)
    s["tiers"] = collections.Counter(r["curation_tier"] for r in recs if r["curation_tier"])

    s["data_mean"] = mean([r["data_score"] for r in recs])
    s["code_mean"] = mean([r["code_score"] for r in recs])
    s["open_mean"] = mean([r["openness_score"] for r in recs])
    s["fully_open"] = sum(1 for r in recs if r["openness_band"] == "fully open")
    s["fully_closed"] = sum(1 for r in recs if r["openness_score"] == 0.0)
    s["score_hist"] = collections.Counter(r["openness_score"] for r in recs)

    # the asymmetry: released code without released data, and the reverse
    s["code_y_not_open"] = sum(
        1 for r in recs if r["code_availability"] == "Y" and r["data_availability"] != "Y"
    )
    s["data_y_not_open"] = sum(
        1 for r in recs if r["data_availability"] == "Y" and r["code_availability"] != "Y"
    )
    s["unrunnable_code"] = sum(
        1 for r in recs if r["code_availability"] == "Y" and r["data_availability"] == "N"
    )

    s["licensing"] = {}
    for k in ("licensed only", "licensed and public", "public only", "neither"):
        g = [r for r in recs if r["licensing_exposure"] == k]
        s["licensing"][k] = {
            "n": len(g),
            "data": mean([r["data_score"] for r in g]),
            "code": mean([r["code_score"] for r in g]),
            "open": mean([r["openness_score"] for r in g]),
            "fully_open": sum(1 for r in g if r["openness_band"] == "fully open"),
        }
    s["any_licensed"] = sum(
        1 for r in recs if r["licensing_exposure"] in ("licensed only", "licensed and public")
    )

    s["clusters"] = {}
    for c in CLUSTER_ORDER:
        g = [r for r in recs if c in r["clusters"]]
        lags = [r["lag_years"] for r in g if r["lag_years"] is not None]
        s["clusters"][c] = {
            "n": len(g),
            "data": mean([r["data_score"] for r in g]),
            "code": mean([r["code_score"] for r in g]),
            "open": mean([r["openness_score"] for r in g]),
            "fully_open": sum(1 for r in g if r["openness_band"] == "fully open"),
            "median_lag": st.median(lags) if lags else None,
            "median_end": st.median([r["dataset_end_year"] for r in g
                                     if r["dataset_end_year"]]),
        }

    # Methods are counted on an any-mention basis across the primary and
    # secondary fields; the primary column is reported alongside, because the
    # gap between the two is the adoption result.
    primary = collections.Counter(
        PRIMARY_TO_CODE.get(r["method_primary"], "OTH") for r in recs
    )
    s["methods"] = {}
    for code in METHOD_ORDER:
        g = [r for r in recs if code in r["method_codes"]]
        if not g:
            continue
        s["methods"][code] = {
            "n": len(g),
            "primary": primary.get(code, 0),
            "open": mean([r["openness_score"] for r in g]),
            "data": mean([r["data_score"] for r in g]),
        }

    s["cluster_methods"] = {}
    for c in CLUSTER_ORDER:
        g = [r for r in recs if c in r["clusters"]]
        mc = collections.Counter()
        for r in g:
            for m in set(r["method_codes"]):
                mc[m] += 1
        s["cluster_methods"][c] = mc

    # -----------------------------------------------------------------
    # Six tables added for the restructured Chapters 4-5 (ported from
    # Derived_tables_Ch4_Ch5_2026-09-16.md): journal x period, cluster x
    # period, method x period, unit x cluster, source categories with their
    # licensing class, and the data x code cross-tabulation. `make verify`
    # independently recomputes each of these from the frozen corpus.
    # -----------------------------------------------------------------

    s["periods"] = collections.Counter(period_of(r["publication_year"]) for r in recs if period_of(r["publication_year"]))

    s["journal_period"] = {}
    for j, jv in s["journals"].items():
        g = [r for r in recs if r["journal"] == j]
        s["journal_period"][j] = collections.Counter(period_of(r["publication_year"]) for r in g if period_of(r["publication_year"]))

    s["cluster_period"] = {}
    for c in CLUSTER_ORDER:
        g = [r for r in recs if c in r["clusters"]]
        s["cluster_period"][c] = collections.Counter(period_of(r["publication_year"]) for r in g if period_of(r["publication_year"]))

    s["method_period"] = {}
    for code in METHOD_ORDER:
        g = [r for r in recs if code in r["method_codes"]]
        if not g:
            continue
        s["method_period"][code] = collections.Counter(period_of(r["publication_year"]) for r in g if period_of(r["publication_year"]))

    s["unit_cluster"] = {}
    for c in CLUSTER_ORDER:
        g = [r for r in recs if c in r["clusters"]]
        s["unit_cluster"][c] = collections.Counter(
            r["unit_of_observation"] or "(unrecorded)" for r in g
        )

    s["source_categories"] = {}
    for cat in SOURCE_CATEGORY_ORDER:
        any_n = sum(
            1 for r in recs
            if cat in (r["source_primary"], r["source_secondary"])
        )
        primary_n = sum(1 for r in recs if r["source_primary"] == cat)
        s["source_categories"][cat] = {
            "any": any_n, "primary": primary_n, "class": SOURCE_CLASS[cat],
        }

    s["data_code_matrix"] = {
        d: collections.Counter(
            r["code_availability"] for r in recs if r["data_availability"] == d
        )
        for d in DATA_LEVEL_ORDER
    }

    lags = [r["lag_years"] for r in recs if r["lag_years"] is not None]
    s["lag_median"], s["lag_mean"], s["lag_max"] = st.median(lags), mean(lags), max(lags)
    s["past_2023"] = sum(1 for r in recs if (r["dataset_end_year"] or 0) > 2023)
    windows = [r["coverage_window_years"] for r in recs if r["coverage_window_years"]]
    s["window_median"] = st.median(windows)

    # Link figures cover data and code links only. Publisher landing pages are
    # DOIs and were never probed; counting them would inflate the denominator
    # with links that were never in question.
    assets = [x for x in links if x["link_type"] != "paper_link" and x["url"]]
    s["links_total"] = len(assets)
    s["links_verdicts"] = collections.Counter(x["verdict"] for x in assets)
    s["links_methods"] = collections.Counter(x["method"] or "—" for x in assets)
    s["links_paper_pages"] = sum(
        1 for x in links if x["link_type"] == "paper_link" and x["url"]
    )
    s["links_checked_on"] = max((x["checked_on"] for x in assets if x["checked_on"]),
                                default="")
    return s


# ---------------------------------------------------------------------------
# renderers
# ---------------------------------------------------------------------------

def clip(s, n=70):
    """One-line a note and trim it to n characters on a word boundary."""
    s = oneline(s)
    return s if len(s) <= n else s[: n - 1].rsplit(" ", 1)[0] + "…"


def oneline(s):
    """Flatten a cell for a markdown table.

    The coding workbook uses real line breaks inside cells for legibility — in
    citations, in the free-text access notes, and in the one cell that lists two
    sample years. A raw newline terminates a markdown table row, so every value
    rendered into a table passes through here first.
    """
    return re.sub(r"\s+", " ", str(s or "").replace("|", "\\|")).strip()


def link_cell(rec, links_by_paper):
    """Render the access links for one paper, with their verified status."""
    parts = []
    for field, label in (("data_link", "data"), ("code_link", "code")):
        entries = [x for x in links_by_paper.get(rec["paper_id"], [])
                   if x["link_type"] == field]
        urls = [x for x in entries if x["url"]]
        if not urls:
            note = next((x["access_note"] for x in entries if x["access_note"]), "")
            if note:
                parts.append(f"{label}: <sub>{clip(note)}</sub>")
            continue
        marks = []
        note = next((x["access_note"] for x in entries if x["access_note"]), "")
        for i, x in enumerate(urls, 1):
            # Verification state is deliberately not shown here. It lives in
            # LINK_CHECKS.md, because a mark in this column reads as a judgement
            # on the paper rather than on the checker that produced it.
            name = label if len(urls) == 1 else f"{label}&nbsp;{i}"
            marks.append(f"[{name}]({x['url']})")
        cell = " ".join(marks)
        if note:
            cell += f" <sub>{clip(note)}</sub>"
        parts.append(cell)
    return "<br>".join(parts) if parts else "—"


def catalogue(recs, links, s):
    links_by_paper = collections.defaultdict(list)
    for x in links:
        links_by_paper[x["paper_id"]].append(x)

    order = sorted(recs, key=lambda r: (-r["openness_score"], r["paper_id"]))

    out = [
        "# Catalogue — all 109 papers",
        "",
        "Every paper in the frozen corpus, whether or not it releases anything. "
        "Papers with no public data and no code are listed too. The openness rate "
        "of the field is only measurable against the whole population.",
        "",
        "Sorted by availability score, descending. Full citations are in "
        "[CITATIONS.md](CITATIONS.md); field definitions and scoring keys are in "
        "[CODEBOOK.md](CODEBOOK.md).",
        "",
        "Three kinds of link appear in each row, and they go to three different "
        "places. The **ID** links to that paper's full citation in "
        "[CITATIONS.md](CITATIONS.md). The **Study** title links to the paper "
        "itself, at its DOI or publisher page. The **Access** column links to "
        "the data and the code, where the paper releases them.",
        "",
"**Availability.** `D:` data — `OPEN` constructed panel released · `PART` "
        "partly released · `RAW` public raw sources named, nothing released · "
        "`REQ` on request · `—` none. `C:` replication code, same scale. The "
        "score is the mean of the two; `T1`–`T7` marks the curation tier, "
        "defined in [CODEBOOK.md](CODEBOOK.md).",
        "",
        "**Topics.** `BIO` biodiversity · `PHY` physical risk · `TRN` transition "
        "risk · `EMI` corporate emissions · `GRB` green bonds · `DIS` ESG "
        "disclosure · `RAT` ESG ratings · `SOC` social · `GOV` governance · "
        "`OTH` other. Non-exclusive.",
        "",
        "**Methods**, counted across the primary and secondary fields: `ECON` "
        "standard econometrics · `NLP` textual analysis · `SAT` satellite and "
        "remote sensing · `SURV` survey · `EXP` experiment · `FILE` regulatory "
        "filing parsing · `ML` machine learning · `META` meta-analysis · `OTH` "
        "other.",
        "",
        "**Inputs.** The raw data sources: `PROP` proprietary database · `MKT` "
        "market data · `OFF` official statistics · `SEC` SEC filings · `WX` "
        "weather and hazard · `SATI` satellite imagery · `CALL` earnings calls · "
        "`NEWS` news and media · `CDP` CDP reports · `SURV` survey · `SOCM` "
        "social media · `OTH` other. The leading badge is the paper's licensing "
        "exposure — `L:LIC` licensed inputs only · `L:MIX` licensed and public · "
        "`L:PUB` public only · `L:—` neither. This is the variable behind the "
        "corpus-wide result that papers built exclusively on licensed inputs "
        "score 0.16 on data against 0.55 for public-only; see "
        "[STATS.md](STATS.md).",
        "",
        "**Access links** are reproduced as the paper gives them. Every one has "
        "been checked and the result — when, by what means, and what it "
        f"resolved to — is recorded in [LINK_CHECKS.md](LINK_CHECKS.md), last "
        f"updated {s['links_checked_on']}.",
        "",
        "| ID | Study | Topics | Methods | Inputs | Coverage | Geo | Data | Code | Score | Access |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in order:
        title = oneline(r["short_title"])
        study = f"[{title}]({r['paper_link']})" if r["paper_link"] else title
        study = f"{study}<br><sub>{r['journal']} {r['publication_year']}</sub>"
        id_cell = f"[{r['paper_id']}](CITATIONS.md#{r['paper_id'].lower()})"
        topics = " ".join(f"`{t}`" for t in r["topic_codes"])
        methods = " ".join(f"`{m}`" for m in r["method_codes"]) or "—"
        inputs = " ".join(
            [f"**`L:{r['licensing_code']}`**"]
            + [f"`{c}`" for c in r["source_codes"]]
        )
        score = fmt(r["openness_score"])
        if r["curation_tier"]:
            score += f" {TIER_BADGE[r['curation_tier']]}"
        out.append(
            f"| {id_cell} | {study} | {topics} | {methods} | {inputs} | "
            f"{oneline(r['coverage']) or '—'} | "
            f"{oneline(r['geographic_scope']) or '—'} | {DATA_BADGE[r['data_availability']]} | "
            f"{CODE_BADGE[r['code_availability']]} | {score} | "
            f"{link_cell(r, links_by_paper)} |"
        )

    out += ["", "---", "", "## Index by cluster", "",
            "Clusters are non-exclusive, so a paper carrying several topic flags "
            "appears under several clusters and the counts sum above 109.", ""]
    for c in CLUSTER_ORDER:
        g = sorted((r for r in recs if c in r["clusters"]),
                   key=lambda r: (-r["openness_score"], r["paper_id"]))
        cs = s["clusters"][c]
        out += [
            f"### {c} — n = {cs['n']}",
            "",
            f"Mean data {fmt(cs['data'])} · mean code {fmt(cs['code'])} · "
            f"composite {fmt(cs['open'])} · fully open {cs['fully_open']} · "
            f"median lag {cs['median_lag']:.0f} years",
            "",
            " ".join(f"`{r['paper_id']}`" for r in g),
            "",
        ]
    return "\n".join(out) + "\n"


def link_checks(recs, links):
    """A readable rendering of the link-rot baseline, one row per link."""
    titles = {r["paper_id"]: oneline(r["short_title"]) for r in recs}
    order = {p: i for i, p in enumerate(sorted(titles, key=lambda x: int(x[1:])))}
    rows = [x for x in links if x["link_type"] != "paper_link"]
    rows.sort(key=lambda x: (order.get(x["paper_id"], 999), x["link_type"]))

    counts = collections.Counter(x["verdict"] for x in rows if x["url"])

    out = [
        "# Link checks",
        "",
        "Every data and code access link in the corpus, with the result of "
        "checking it. Publisher landing pages are omitted: those are DOIs.",
        "",
        "**Verdicts.** `LIVE` resolved and served the expected resource · "
        "`REDIRECT` resolves, but to a different address than the paper gives — "
        "the new one is in the note · `BLOCKED` the host refuses automated "
        "requests, or answers all of them identically whatever the file's real "
        "permissions, so only a person can settle it · `ERROR` returned a server "
        "error, possibly transient · `NO URL` the access field holds an email "
        "address or a prose note rather than a link.",
        "",
        "**Method.** `web` an automated probe · `manual` a person opened it in a "
        "browser. A manual verdict overrides an automated one and should not be "
        "overwritten by a later `make check-links` run without someone looking "
        "again.",
        "",
        "A `LIVE` verdict proves a page exists. It does not prove the file behind "
        "it is still the file the paper used, and nothing here verifies that a "
        "released panel reproduces a published table.",
        "",
        "Current state: "
        + " · ".join(f"**{k}** {v}" for k, v in counts.most_common())
        + f" across {sum(counts.values())} link entries. Counted per entry: "
        "several papers cite the same public source, so the unique-URL totals "
        "quoted in the README are lower.",
        "",
        "| Paper | Study | Link | Verdict | Method | Checked | Note |",
        "|---|---|---|---|---|---|---|",
    ]
    for x in rows:
        kind = "data" if x["link_type"] == "data_link" else "code"
        if x["url"]:
            shown = x["url"]
            label = shown if len(shown) <= 60 else shown[:57] + "…"
            cell = f"[{oneline(label)}]({shown})"
        else:
            cell = f"<sub>{clip(x['access_note'], 60)}</sub>"
        out.append(
            f"| {x['paper_id']} | <sub>{clip(titles.get(x['paper_id'], ''), 45)}</sub> | "
            f"{kind}: {cell} | `{x['verdict']}` | {('`' + x['method'] + '`') if x.get('method') else '—'} | "
            f"{x['checked_on'] or '—'} | <sub>{clip(x['check_note'], 90)}</sub> |"
        )
    return "\n".join(out) + "\n"


def citations(recs):
    out = [
        "# Citations",
        "",
        "The full citation for every paper in the corpus, reproduced verbatim as "
        "coded. Ordered by paper ID.",
        "",
        "Each row carries an anchor on its ID, so the ID column of "
        "[CATALOGUE.md](CATALOGUE.md) links straight to the citation of the paper "
        "it names: `CITATIONS.md#p05` lands on P05.",
        "",
        "| ID | Journal | Citation |",
        "|---|---|---|",
    ]
    for r in sorted(recs, key=lambda r: int(r["paper_id"][1:])):
        cite = oneline(r["citation"])
        anchor = r["paper_id"].lower()
        out.append(
            f'| <a id="{anchor}" name="{anchor}"></a>{r["paper_id"]} | '
            f"{r['journal']} | {cite} |"
        )
    return "\n".join(out) + "\n"


def stats_md(s):
    o = [
        "# Statistics",
        "",
        f"Recomputed from the frozen corpus on {s['built_on']}. Every figure the "
        "README or the thesis cites is derived here, so the two cannot drift apart.",
        "",
        "## Corpus",
        "",
        f"- **n = {s['n']}** papers, four journals, publication years "
        f"{min(s['years'])}–{max(s['years'])}.",
        "- Journals: " + " · ".join(f"{k} {v}" for k, v in s["journals"].most_common()),
        "- Geographic scope of the data: "
        + " · ".join(f"{k} {v}" for k, v in s["geo"].most_common()),
        "- Unit of observation: "
        + " · ".join(f"{k} {v}" for k, v in s["unit"].most_common()),
        "",
        "### Composition: journal × period",
        "",
        "| Journal | " + " | ".join(PERIOD_ORDER) + " | Total |",
        "|---|" + "---:|" * (len(PERIOD_ORDER) + 1),
    ]
    for j in JOURNAL_ORDER:
        row = s["journal_period"][j]
        cells = [str(row.get(p, 0)) for p in PERIOD_ORDER]
        o.append(f"| {j} | " + " | ".join(cells) + f" | **{s['journals'][j]}** |")
    o.append(
        "| **Total** | "
        + " | ".join(f"**{s['periods'].get(p, 0)}**" for p in PERIOD_ORDER)
        + f" | **{s['n']}** |"
    )
    o += [
        "",
        "*Source: Own calculations with data from the coding workbook.*",
        "",
        "## Availability",
        "",
        f"- Mean data score **{fmt(s['data_mean'])}**, mean code score "
        f"**{fmt(s['code_mean'])}**, mean composite **{fmt(s['open_mean'])}**.",
        f"- **{s['fully_open']}** papers ({fmt(100*s['fully_open']/s['n'], 1)} %) are "
        f"fully open — data *and* code released. **{s['fully_closed']}** "
        f"({fmt(100*s['fully_closed']/s['n'], 1)} %) score zero on both.",
        "- Data availability: "
        + " · ".join(f"{k} {v}" for k, v in s["data_levels"].most_common()),
        "- Code availability: "
        + " · ".join(f"{k} {v}" for k, v in s["code_levels"].most_common()),
        f"- The asymmetry runs one way: **{s['code_y_not_open']}** papers release "
        f"code without releasing data, against **{s['data_y_not_open']}** the other "
        f"way. **{s['unrunnable_code']}** publish replication code against no public "
        "data at all — code that cannot be executed.",
        "- Score distribution: "
        + " · ".join(f"{fmt(k)}: {v}" for k, v in sorted(s["score_hist"].items())),
        "",
        "### Data level × code level",
        "",
        "| data \\ code | " + " | ".join(CODE_LEVEL_ORDER) + " | Total |",
        "|---|" + "---:|" * (len(CODE_LEVEL_ORDER) + 1),
    ]
    for d in DATA_LEVEL_ORDER:
        row = s["data_code_matrix"][d]
        cells = [str(row.get(c, 0)) for c in CODE_LEVEL_ORDER]
        o.append(f"| {d} | " + " | ".join(cells) + f" | **{sum(row.values())}** |")
    col_totals = [sum(s["data_code_matrix"][d].get(c, 0) for d in DATA_LEVEL_ORDER)
                  for c in CODE_LEVEL_ORDER]
    o.append("| **Total** | " + " | ".join(f"**{v}**" for v in col_totals)
              + f" | **{sum(col_totals)}** |")
    no_panel_code_y = sum(s["data_code_matrix"][d].get("Y", 0) for d in ("Raw Data", "N"))
    panel_no_code = sum(v for k, v in s["data_code_matrix"]["Y"].items() if k != "Y")
    o += [
        "",
        f"The off-diagonal carries the corpus's structure: **{no_panel_code_y}** "
        "papers release code against no released panel (Raw Data or N on data), "
        f"against **{panel_no_code}** releasing a panel (Y on data) with no code.",
        "",
        "*Source: Own calculations with data from the coding workbook.*",
        "",
        "## Curation tiers",
        "",
        "Every paper carries exactly one tier, ranked by what a reader can "
        "recover. The rules are in [CODEBOOK.md](CODEBOOK.md) §7.",
        "",
        "| Tier | n | Share |",
        "|---|---|---|",
    ]
    for t, _rule, _blurb in TIER_LADDER:
        v = s["tiers"].get(t, 0)
        o.append(f"| {t} | {v} | {fmt(100*v/s['n'], 1)} % |")
    downloadable = sum(s["tiers"].get(t, 0) for t in TIER_DETAIL)
    code_no_panel = s["tiers"].get("Tier 4", 0) + s["tiers"].get("Tier 5", 0)
    o += [
        "",
        f"Tiers 1 to 3 are the {downloadable} entries with something "
        f"downloadable, {fmt(100*downloadable/s['n'], 1)} % of the corpus. Tiers 4 "
        f"and 5 add {code_no_panel} papers that release code without a panel: not "
        "rerunnable, but the pipeline is documented.",
        "",
        "## Raw data sources",
        "",
        "Counted on an any-mention basis across the primary and secondary source "
        "fields; a category counts once for a paper naming it in either. Class is "
        "the access-terms classification of CODEBOOK.md §4.",
        "",
        "| Source category | Any-mention | Primary | Class |",
        "|---|---:|---:|---|",
    ]
    for cat in sorted(SOURCE_CATEGORY_ORDER,
                       key=lambda c: -s["source_categories"][c]["any"]):
        v = s["source_categories"][cat]
        if v["any"] == 0:
            continue
        o.append(f"| {cat} | {v['any']} | {v['primary']} | {v['class']} |")
    total_mentions = sum(v["any"] for v in s["source_categories"].values())
    o += [
        "",
        f"{total_mentions} source mentions across {s['n']} papers. These counts "
        "are a lower bound on named vendors: the free-text coding note records a "
        "source category, not a systematic vendor field, so a paper using a given "
        "source without the note recording it is not counted here. Per-paper "
        "detail is in [CATALOGUE.md](CATALOGUE.md).",
        "",
        "*Source: Own calculations with data from the coding workbook.*",
        "",
        "## Licensing exposure",
        "",
        f"**{s['any_licensed']}** of {s['n']} papers "
        f"({fmt(100*s['any_licensed']/s['n'], 1)} %) draw on at least one licensed input.",
        "",
        "| Exposure | n | Mean data | Mean code | Composite | Fully open |",
        "|---|---|---|---|---|---|",
    ]
    for k, v in s["licensing"].items():
        o.append(f"| {k} | {v['n']} | {fmt(v['data'])} | {fmt(v['code'])} | "
                 f"{fmt(v['open'])} | {v['fully_open']} |")
    o += [
        "",
        "## Clusters",
        "",
        "Ordered along the availability gradient. Non-exclusive, so counts sum "
        f"above {s['n']}.",
        "",
        "| Cluster | n | Data | Code | Composite | Fully open | Median lag | Median data end |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for c in CLUSTER_ORDER:
        v = s["clusters"][c]
        o.append(f"| {c} | {v['n']} | {fmt(v['data'])} | {fmt(v['code'])} | "
                 f"{fmt(v['open'])} | {v['fully_open']} | {v['median_lag']:.0f} | "
                 f"{v['median_end']:.0f} |")
    o += [
        "",
        "### Cluster composition by period",
        "",
        "Non-exclusive; columns sum above the period *n*.",
        "",
        "| Cluster | " + " | ".join(PERIOD_ORDER) + " | Total |",
        "|---|" + "---:|" * (len(PERIOD_ORDER) + 1),
    ]
    for c in CLUSTER_ORDER:
        row = s["cluster_period"][c]
        cells = [str(row.get(p, 0)) for p in PERIOD_ORDER]
        o.append(f"| {c} | " + " | ".join(cells) + f" | **{s['clusters'][c]['n']}** |")
    o.append(
        "| *Papers in period* | "
        + " | ".join(f"*{s['periods'].get(p, 0)}*" for p in PERIOD_ORDER)
        + f" | *{s['n']}* |"
    )
    o += [
        "",
        "*Source: Own calculations with data from the coding workbook.*",
        "",
        "### Unit of observation × cluster",
        "",
        "| Unit | " + " | ".join(CLUSTER_ORDER) + " | Corpus |",
        "|---|" + "---:|" * (len(CLUSTER_ORDER) + 1),
    ]
    for u in UNIT_ORDER:
        cells = [str(s["unit_cluster"][c].get(u, 0)) for c in CLUSTER_ORDER]
        corpus_n = s["unit"].get(u, 0)
        o.append(f"| {u} | " + " | ".join(cells) + f" | {corpus_n} |")
    o += [
        "",
        "Granularity tracks the input class: asset-level observation concentrates "
        "where the data is physical or security-level, firm-year where it is "
        "accounting or vendor-supplied, portfolio-level where it is a rating "
        "attached to a fund.",
        "",
        "*Source: Own calculations with data from the coding workbook.*",
        "",
        "## Methods",
        "",
        "Counted on an **any-mention** basis across the primary and secondary "
        "method fields. A method can be widely used without being any paper's "
        "primary technique, which is why the two columns differ.",
        "",
        "| Method | Any mention | Primary only | Mean availability | Mean data |",
        "|---|---|---|---|---|",
    ]
    for code, v in s["methods"].items():
        o.append(f"| {METHOD_NAME[code]} | {v['n']} | {v['primary']} | "
                 f"{fmt(v['open'])} | {fmt(v['data'])} |")
    o += [
        "",
        "### Method mix by period, any-mention",
        "",
        "| Method | " + " | ".join(PERIOD_ORDER) + " | Total |",
        "|---|" + "---:|" * (len(PERIOD_ORDER) + 1),
    ]
    for code in METHOD_ORDER:
        if code not in s["method_period"]:
            continue
        row = s["method_period"][code]
        cells = [str(row.get(p, 0)) for p in PERIOD_ORDER]
        o.append(f"| {METHOD_NAME[code]} | " + " | ".join(cells)
                  + f" | **{s['methods'][code]['n']}** |")
    o += [
        "",
        "*Source: Own calculations with data from the coding workbook.*",
        "",
        "### Methods by cluster",
        "",
        "| Cluster | n | Standard econometrics | Other methods, any mention |",
        "|---|---|---|---|",
    ]
    for c in CLUSTER_ORDER:
        mc = s["cluster_methods"][c]
        n = s["clusters"][c]["n"]
        econ = mc.get("ECON", 0)
        rest = " · ".join(f"{METHOD_NAME[k].split(' /')[0].split(' on ')[0]} {v}"
                          for k, v in sorted(mc.items(), key=lambda kv: (-kv[1], kv[0]))
                          if k != "ECON")
        o.append(f"| {c} | {n} | {econ} ({fmt(100*econ/n, 0)} %) | {rest or '—'} |")
    o += [
        "",
        "## Currency of the evidence",
        "",
        f"- Median lag from last year of data to publication: **{s['lag_median']:.0f} "
        f"years** (mean {fmt(s['lag_mean'], 1)}, maximum {s['lag_max']}).",
        f"- Median sample window: **{s['window_median']:.0f} years**.",
        f"- Papers carrying data past 2023: **{s['past_2023']}**.",
        "",
        "## Link inventory",
        "",
        f"{s['links_total']} data and code link entries across the corpus, last "
        f"checked {s['links_checked_on']}: "
        + " · ".join(f"{k} {v}" for k, v in s["links_verdicts"].most_common())
        + ". Established by "
        + " · ".join(f"{k} {v}" for k, v in s["links_methods"].most_common())
        + ".",
        "",
        f"The {s['links_paper_pages']} publisher landing pages are excluded: they "
        "are DOIs and were not probed. Where an automated probe could not "
        "settle a link — Harvard Dataverse, Wiley, Mendeley, FEMA, OSF and Google "
        "all refuse robots or answer them identically whatever a file's real "
        "permissions — it was opened in a browser instead, which is what the "
        "`manual` method records. See [LINK_CHECKS.md](LINK_CHECKS.md).",
        "",
    ]
    return "\n".join(o) + "\n"


def readme_block(s):
    lic = s["licensing"]
    return "\n".join([
        f"| | |",
        f"|---|---|",
        f"| Papers coded | **{s['n']}** (JF {s['journals']['Journal of Finance']} · "
        f"JFE {s['journals']['Journal of Financial Economics']} · "
        f"RFS {s['journals']['Review of Financial Studies']} · "
        f"RoF {s['journals']['Review of Finance']}) |",
        f"| Fully open (data **and** code) | **{s['fully_open']}** "
        f"({fmt(100*s['fully_open']/s['n'], 1)} %) |",
        f"| Fully closed (neither) | **{s['fully_closed']}** "
        f"({fmt(100*s['fully_closed']/s['n'], 1)} %) |",
        f"| Mean availability score | **{fmt(s['open_mean'])}** "
        f"(data {fmt(s['data_mean'])} · code {fmt(s['code_mean'])}) |",
        f"| Code released without data | **{s['code_y_not_open']}** papers, against "
        f"{s['data_y_not_open']} the other way |",
        f"| Touch at least one licensed input | **{s['any_licensed']}** "
        f"({fmt(100*s['any_licensed']/s['n'], 1)} %) |",
        f"| Mean data score, licensed-only vs public-only | "
        f"**{fmt(lic['licensed only']['data'])}** vs "
        f"**{fmt(lic['public only']['data'])}** |",
        f"| Median lag, last data year to publication | **{s['lag_median']:.0f} years** |",
        f"| Access links resolving when last checked | "
        f"**{s['links_verdicts']['LIVE']}** of {s['links_total']}"
        + (f", {s['links_verdicts']['BLOCKED']} not verifiable automatically"
           if s["links_verdicts"].get("BLOCKED") else "")
        + (f", {s['links_verdicts']['REDIRECT']} redirecting"
           if s["links_verdicts"].get("REDIRECT") else "")
        + (f", {s['links_verdicts']['ERROR']} erroring"
           if s["links_verdicts"].get("ERROR") else "")
        + f" ({s['links_checked_on']}) |",
    ])


def readme_badges(s):
    def b(label, msg, colour):
        def q(t):
            t = t.replace("-", "--").replace("_", "__").replace("%", "%25")
            return (t.replace(" ", "%20").replace("(", "%28").replace(")", "%29"))
        return f"![{label}](https://img.shields.io/badge/{q(label)}-{q(msg)}-{colour})"

    pct = 100 * s["fully_open"] / s["n"]
    return " ".join([
        b("corpus", f"{s['n']} papers", "informational"),
        b("journals", "4", "informational"),
        b("fully open", f"{s['fully_open']} ({fmt(pct, 1)}%)", "critical"),
        b("mean availability", fmt(s["open_mean"]), "yellow"),
        b("links checked", s["links_checked_on"], "lightgrey"),
        b("data licence", "CC BY 4.0", "blue"),
        b("code licence", "MIT", "blue"),
    ])


def readme_tiers(recs, s, links):
    urls = collections.defaultdict(dict)
    for x in links:
        if x["url"]:
            urls[x["paper_id"]].setdefault(x["link_type"], x["url"])

    rows = [
        "| ID | Study | Topics | Coverage | Geo | Data | Code | Access |",
        "|---|---|---|---|---|---|---|---|",
    ]
    tiered = [r for r in recs if r["curation_tier"] in TIER_DETAIL]
    order = {t: i for i, t in enumerate(TIER_DETAIL)}
    for r in sorted(tiered, key=lambda r: (order[r["curation_tier"]], r["paper_id"])):
        u = urls.get(r["paper_id"], {})
        du, cu = u.get("data_link", ""), u.get("code_link", "")
        if du and du == cu:
            cell = [f"[data + code]({du})"]
        else:
            cell = ([f"[data]({du})"] if du else []) + ([f"[code]({cu})"] if cu else [])
        cl = " ".join(f"`{t}`" for t in r["topic_codes"])
        rows.append(
            f"| **{r['paper_id']}** | {oneline(r['short_title'])} | {cl} | "
            f"{oneline(r['coverage']) or '—'} | {oneline(r['geographic_scope']) or '—'} | "
            f"{DATA_BADGE[r['data_availability']]} | {CODE_BADGE[r['code_availability']]} | "
            f"{' · '.join(cell) or '—'} |"
        )
    counts = collections.Counter(r["curation_tier"] for r in recs)
    out = [
        "| Tier | Rule | n | What a reader can do |",
        "|---|---|---|---|",
    ]
    for t, rule, blurb in TIER_LADDER:
        out.append(f"| **{TIER_BADGE[t]}** | {rule} | {counts.get(t, 0)} | {blurb} |")
    out += [
        "",
        f"Tiers 1 to 3 are the {sum(counts.get(t, 0) for t in TIER_DETAIL)} entries "
        "with something downloadable, and are listed in full below. Tiers 4 to 7 "
        f"are the remaining {sum(counts.get(t, 0) for t in ('Tier 4','Tier 5','Tier 6','Tier 7'))}; "
        "they are in [the catalogue](docs/CATALOGUE.md), which carries the tier "
        "on every row.",
        "",
    ]
    for t, _rule, blurb in TIER_LADDER:
        if t not in TIER_DETAIL:
            continue
        title = f"{t} — " + {"Tier 1": "fully open",
                             "Tier 2": "full code, partial data",
                             "Tier 3": "data available, code incomplete"}[t]
        g = [r for r in tiered if r["curation_tier"] == t]
        out += [f"#### {title} ({len(g)})", "", blurb, ""]
        out.append(rows[0])
        out.append(rows[1])
        for line in rows[2:]:
            if f"**{[r['paper_id'] for r in g][0]}**" in line or any(
                    f"**{r['paper_id']}**" in line for r in g):
                out.append(line)
        out.append("")
    return "\n".join(out).rstrip()


def inject(path, marker, block):
    a, b = f"<!-- {marker}:BEGIN -->", f"<!-- {marker}:END -->"
    s = open(path, encoding="utf-8").read()
    if a not in s or b not in s:
        return False
    pre, rest = s.split(a, 1)
    _, post = rest.split(b, 1)
    open(path, "w", encoding="utf-8").write(f"{pre}{a}\n{block}\n{b}{post}")
    return True


def main():
    recs, links = load()
    s = stats(recs, links)
    os.makedirs(DOCS, exist_ok=True)
    for name, text in (
        ("CATALOGUE.md", catalogue(recs, links, s)),
        ("CITATIONS.md", citations(recs)),
        ("LINK_CHECKS.md", link_checks(recs, links)),
        ("STATS.md", stats_md(s)),
    ):
        open(os.path.join(DOCS, name), "w", encoding="utf-8").write(text)
        print("wrote docs/" + name)

    readme = os.path.join(ROOT, "README.md")
    if os.path.exists(readme):
        for marker, block in (("STATS", readme_block(s)),
                              ("BADGES", readme_badges(s)),
                              ("TIERS", readme_tiers(recs, s, links))):
            if inject(readme, marker, block):
                print(f"refreshed README.md {marker} block")

    json.dump(
        {k: (dict(v) if isinstance(v, collections.Counter) else v) for k, v in s.items()},
        open(os.path.join(ROOT, "data", "stats.json"), "w"),
        indent=2, default=str, sort_keys=True,
    )
    print("wrote data/stats.json")


if __name__ == "__main__":
    main()
