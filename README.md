# Sustainable Finance Data

A catalogue of the data behind **109 empirical sustainable finance papers**
published in the *Journal of Finance*, *Journal of Financial Economics*,
*Review of Financial Studies* and *Review of Finance* through April 2026 —
what each study is built on: its raw sources, its methods, the coverage and
geographic scope of its evidence, and, for every entry, whether any of it can
be recovered and under what terms.

<!-- BADGES:BEGIN -->
![corpus](https://img.shields.io/badge/corpus-109%20papers-informational) ![journals](https://img.shields.io/badge/journals-4-informational) ![fully open](https://img.shields.io/badge/fully%20open-6%20%285.5%25%29-critical) ![mean availability](https://img.shields.io/badge/mean%20availability-0.33-yellow) ![links checked](https://img.shields.io/badge/links%20checked-2026--08--22-lightgrey) ![data licence](https://img.shields.io/badge/data%20licence-CC%20BY%204.0-blue) ![code licence](https://img.shields.io/badge/code%20licence-MIT-blue)
<!-- BADGES:END -->

Every paper in the frozen corpus is catalogued, whether or not it releases
anything: source, method, coverage window and geographic scope are coded for
all 109, and each paper's data and code availability is recorded alongside
them as one further coded field rather than a condition of entry. That is what
makes the availability rate of the field measurable rather than assumed, and
it is why papers that release nothing appear here beside those that do, each
with a scored availability level and, where one exists, a checked link.

## Headline figures

<!-- STATS:BEGIN -->
| | |
|---|---|
| Papers coded | **109** (JF 14 · JFE 42 · RFS 22 · RoF 31) |
| Fully open (data **and** code) | **6** (5.5 %) |
| Fully closed (neither) | **34** (31.2 %) |
| Mean availability score | **0.33** (data 0.31 · code 0.35) |
| Code released without data | **31** papers, against 3 the other way |
| Touch at least one licensed input | **92** (84.4 %) |
| Mean data score, licensed-only vs public-only | **0.16** vs **0.55** |
| Median lag, last data year to publication | **4 years** |
| Access links resolving when last checked | **106** of 109, 1 redirecting, 2 erroring (2026-08-22) |
<!-- STATS:END -->

Full breakdowns — by cluster, by licensing exposure, by journal and by year —
are in [`docs/STATS.md`](docs/STATS.md), recomputed from the frozen corpus on
every build.

## What is in here

| Path | What it is |
|---|---|
| [`docs/CATALOGUE.md`](docs/CATALOGUE.md) | **The catalogue.** All 109 papers, one row each, sorted by availability score: topic and method codes, raw inputs with their licensing exposure, coverage window, geographic scope, availability badges and access links. Each row's ID links to that paper's full citation, its title to the paper itself. Indexed by cluster at the foot. |
| [`docs/CITATIONS.md`](docs/CITATIONS.md) | Full verbatim citation for every paper ID, each row anchored so the catalogue can link straight to it. |
| [`docs/CODEBOOK.md`](docs/CODEBOOK.md) | Every field defined; the two scoring keys; the source-licensing classification; the topic-to-cluster mapping. Read this before citing any number. |
| [`docs/STATS.md`](docs/STATS.md) | All descriptive statistics, generated. |
| [`docs/LINK_CHECKS.md`](docs/LINK_CHECKS.md) | Every data and code link, with its verdict, whether a script or a person established it, and when. |
| [`data/Taxonomy_Coding_Sheet_FINAL.xlsx`](data/Taxonomy_Coding_Sheet_FINAL.xlsx) | **The coding workbook.** Where the hand-coding lives and where corrections are made. |
| [`data/SustFin_Corpus_FINAL.csv`](data/SustFin_Corpus_FINAL.csv) | **The frozen corpus.** Generated from the workbook's *Full Coding* sheet by `make import`; never hand-edited, never touched by the build. |
| [`data/sustfin_datasets.csv`](data/sustfin_datasets.csv) · [`.json`](data/sustfin_datasets.json) | The frozen fields plus every derived field (scores, clusters, licensing class, coverage window, lag, tier). Start here for analysis. |
| [`data/link_checks.csv`](data/link_checks.csv) | The recorded verdict for each unique URL — the link-rot baseline. |
| [`data/link_inventory.csv`](data/link_inventory.csv) | One row per paper × link, joining the baseline to the corpus. |
| [`scripts/`](scripts/) | `import_corpus.py` regenerates the frozen corpus from the coding workbook, `derive.py` builds the derived table, `check_links.py` re-verifies links, `build_docs.py` renders the docs, `verify.py` checks the lot. |

## How to use it

**Looking for data to reuse.** Start with Tiers 1 to 3 below, then the top
of [the catalogue](docs/CATALOGUE.md). Check the coverage column before the
availability column: the median study in this corpus stops collecting data four
years before it is published, so a great many open assets are already too old
for a question about the present.

**Assessing how reproducible a literature is.** Use
[`data/sustfin_datasets.csv`](data/sustfin_datasets.csv). The `openness_score`,
`licensing_exposure` and `curation_tier` fields are the ones built for that,
and [`docs/CODEBOOK.md`](docs/CODEBOOK.md) states exactly what each level means.

**Checking a claim in the thesis.** The statistics the thesis quotes are
regenerated by `make build` into [`docs/STATS.md`](docs/STATS.md), and
`make verify` re-derives them along an independent path. The seven printed
figures are redrawn by `make figures`, which also writes
[`figures/FIGURE_SERIES.md`](figures/FIGURE_SERIES.md) — every plotted value as
text, so a figure can be checked without rerunning it. Four appendix tables are
not generated here: named sources, licensing exposure by period, the pre- and
post-2023 journal split, and the nine topic flags shown beside the six clusters.
Those are computed in the thesis's analytical workbook, which this repository
does not ship. Where the thesis and the repository disagree on anything the
build produces, the build is correct.

## Tiers

Every paper carries a tier, ranking it by what a reader can recover — not by
the quality of the paper or of its data.

<!-- TIERS:BEGIN -->
| Tier | Rule | n | What a reader can do |
|---|---|---|---|
| **`T1`** | `data = Y` and `code = Y` | 6 | Panel and code both released. Rerunnable as published. |
| **`T2`** | `data = Partial` and `code = Y` | 6 | Code released against a partially released panel. Reproducible in part, and the cheapest entries to move into Tier 1. |
| **`T3`** | `data` is `Y` or `Partial`, `code` is not `Y` | 4 | A panel is released but the analysis code is not. The result can be re-estimated, not reproduced exactly. |
| **`T4`** | `data = Raw Data` and `code = Y` | 8 | No panel, but the code names the public sources it was built from and shows what was done to them. |
| **`T5`** | `data = N` and `code = Y` | 17 | No panel and no public inputs, but the released code documents the pipeline. Usually the inputs are licensed rather than withheld. |
| **`T6`** | `data` is `Raw Data` or `On Demand`, `code` is not `Y` | 33 | Provenance is recorded and nothing is released. Rebuilding means reconstructing every cleaning decision. |
| **`T7`** | `data = N` and `code` is not `Y` | 35 | Neither the data nor the method is recoverable. |

Tiers 1 to 3 are the 16 entries with something downloadable, and are listed in full below. Tiers 4 to 7 are the remaining 93; they are in [the catalogue](docs/CATALOGUE.md), which carries the tier on every row.

#### Tier 1 — fully open (6)

Panel and code both released. Rerunnable as published.

| ID | Study | Topics | Coverage | Geo | Data | Code | Access |
|---|---|---|---|---|---|---|---|
| **P05** | Firm-level climate exposure / earnings calls | `PHY` `TRN` `EMI` | 2002–2020 | Global | `D:OPEN` | `C:OPEN` | [data](https://osf.io/fd6jq/overview) · [code](https://onlinelibrary.wiley.com/action/downloadSupplement?doi=10.1111%2Fjofi.13219&file=jofi13219-sup-0002-ReplicationCode.zip) |
| **P101** | Regulator partisanship / ML text / SEC & Fed | `GOV` | 1930–2019 | US | `D:OPEN` | `C:OPEN` | [data + code](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/UTMICU) |
| **P43** | Risk & return of impact investing funds | `SOC` | 1999–2021 | Global | `D:OPEN` | `C:OPEN` | [data + code](https://zenodo.org/records/13282899) |
| **P45** | Moral preferences of investors (EXPERIMENT) | `DIS` `SOC` | 2019–2022 | Global | `D:OPEN` | `C:OPEN` | [data + code](https://data.mendeley.com/datasets/d5gxv5tc8b/2) |
| **P78** | EU biodiversity funding / Horizon programs / project-level | `BIO` | 2003–2023 | Europe | `D:OPEN` | `C:OPEN` | [data + code](https://researchbox.org/5014) |
| **P82** | Mangroves / coastal housing prices / climate resilience | `TRN` `BIO` | 1993–2019 | US | `D:OPEN` | `C:OPEN` | [data + code](https://github.com/tengtedliu/financial_value_of_nature_mangrove) |

#### Tier 2 — full code, partial data (6)

Code released against a partially released panel. Reproducible in part, and the cheapest entries to move into Tier 1.

| ID | Study | Topics | Coverage | Geo | Data | Code | Access |
|---|---|---|---|---|---|---|---|
| **P08** | Hurricanes / physical risk / options | `PHY` | 1996–2019 | US | `D:PART` | `C:OPEN` | [code](https://onlinelibrary.wiley.com/action/downloadSupplement?doi=10.1111%2Fjofi.13416&file=jofi13416-sup-0002-ReplicationCode.zip) |
| **P105** | Swedish CO2 tax / firm emissions elasticity | `TRN` `EMI` | 1990–2015 | Europe | `D:PART` | `C:OPEN` | [data + code](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/9NWRW8) |
| **P109** | Catastrophe bonds / natural disaster risk / intermediary asset pricing | `PHY` `GRB` | 1997–2018 | Global | `D:PART` | `C:OPEN` | [data + code](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/MBBSGV) |
| **P49** | CRISK — systemic climate risk of banks | `TRN` | 2000–2021 | Global | `D:PART` | `C:OPEN` | [data + code](https://data.mendeley.com/datasets/5pzr9t645v/2) |
| **P50** | Bank exit (coal divestment) policies & emissions | `TRN` `GRB` `EMI` | 2005–2021 | Global | `D:PART` | `C:OPEN` | [data + code](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/5LX4LD) |
| **P53** | Green tilts (institutional green portfolio tilts) | `TRN` `RAT` | 2023–2023 | US | `D:PART` | `C:OPEN` | [data + code](https://data.mendeley.com/datasets/y5p3vdzzwr/1) |

#### Tier 3 — data available, code incomplete (4)

A panel is released but the analysis code is not. The result can be re-estimated, not reproduced exactly.

| ID | Study | Topics | Coverage | Geo | Data | Code | Access |
|---|---|---|---|---|---|---|---|
| **P13** | Social impact / consumer surplus / impact investing | `SOC` | 2021–2021 | US | `D:PART` | `C:PART` | [data + code](https://onlinelibrary.wiley.com/action/downloadSupplement?doi=10.1111%2Fjofi.70004&file=jofi70004-sup-0002-ReplicationCode.zip) |
| **P80** | Protected areas / Kunming-Montreal / firm corporate behavior | `TRN` `BIO` | 1990–2021 | US | `D:OPEN` | `C:—` | [data](https://docs.google.com/spreadsheets/d/1Lz3FSaHMt36nuq82qmg9DWtWYxslPMYH/edit?pli=1&gid=1092822974#gid=1092822974) |
| **P81** | Biodiversity risk indices / news + 10-K + survey | `TRN` `BIO` | 2010–2023 | Global | `D:OPEN` | `C:—` | [data](https://www.biodiversityrisk.org/download/) |
| **P91** | Climate news index / hedge portfolios / textual analysis | `TRN` `DIS` | 1984–2018 | US | `D:OPEN` | `C:—` | [data](https://drive.google.com/file/d/1pCHmcebmOwrVCFim78ALhB51c3h1qt2T/view?pli=1) |
<!-- TIERS:END -->

Two of the six Tier 1 papers are 2026 biodiversity papers, and four of the six
were published after the 2023 journal replication mandates. None carries the ESG
ratings flag; the only Tier 1 paper in that cluster, `P45`, is coded on
disclosure.

## How openness is scored

Two levels are coded per paper and averaged, unweighted.

**Data availability** — `Y` 1.00 the constructed analysis panel is released ·
`Partial` 0.75 some of it is · `Raw Data` 0.50 the public raw sources are named
but nothing is released · `On Demand` 0.25 available from the authors on request
· `N` 0.00 no public pathway.

**Code availability** — `Y` 1.00 · `Partial` 0.50 · `On Demand` 0.25 · `N` 0.00.

Two distinctions matter. First, open is not the same as public: a paper that
names EPA emissions data and CRSP returns has documented its provenance without
releasing anything. That is the `Raw Data` level, and it is the largest single
category in the corpus. Second, `fully open` requires both data and code,
because code cannot be run without the data it operates on. The papers marked
`C:OPEN` alongside `D:—` are in that position.

The catalogue's badge legend is repeated at the top of
[`docs/CATALOGUE.md`](docs/CATALOGUE.md); the full definitions are in
[`docs/CODEBOOK.md`](docs/CODEBOOK.md).

## Known limitations

These are properties of the instrument, not defects to be fixed by a pull
request. They are stated here as a transparence mesure.

- **One coder.** The corpus was coded by a single reader with no second-coder
  agreement statistic. Borderline calls between `Partial` and `Raw Data`, in
  particular, are judgement.
- **Four journals.** A statement about the top of the field and the most influential papers in Finance, not the entire field.

- **Availability is coded as published, not as tested.** A paper coded `D:OPEN`
  released something; whether that something reproduces the paper's tables was
  not verified, and nothing here attempts that.
- **An automated probe cannot judge every host.** Harvard Dataverse, Wiley,
  Mendeley, FEMA and OSF refuse automated requests outright, and consumer
  file-sharing services serve a sign-in banner to every automated client
  whatever a file's real permissions. Thirty-one of the 81 unique access links
  could only be settled by opening them in a browser, and four more were read
  wrongly by the probe and corrected the same way — thirty-five manual verdicts
  in all, recorded as such in
  [`data/link_checks.csv`](data/link_checks.csv). That nearly two-fifths of this
  literature's deposited material resists automated verification is a fact about
  the infrastructure, not about the instrument.
- **The source-licensing classification is the author's judgement.** It is
  declared in one place, `LICENSED` and `PUBLIC` in
  [`scripts/derive.py`](scripts/derive.py), and changing it and rerunning the
  build is how you test whether a result depends on it.
- **The ordinal levels are treated as cardinal** when averaged. A 0/0.25/0.5/
  0.75/1 map is a convenience, not a measurement.
- **Clusters overlap.** Topic flags are non-exclusive, so cluster counts sum
  above 109 and cluster comparisons are not comparisons of disjoint samples.

## Maintenance

Links decay, and a catalogue of dead links is useless. The repository
therefore ships its own baseline: every URL has a
recorded state and a date in [`data/link_checks.csv`](data/link_checks.csv).

```bash
make check-links     # re-probe every URL and diff against the recorded baseline
```

`check_links.py` writes both the recorded verdict and a fresh probe result into
[`data/link_inventory.csv`](data/link_inventory.csv), so what has changed since
the baseline can be read off by comparing the two columns.

Two caveats worth knowing before reading the verdicts. A re-probe will report
`BLOCKED` for every link on a host that refuses robots — Harvard Dataverse,
Wiley, Mendeley, FEMA and OSF all do — and that is not evidence of rot; those
carry a `manual` verdict established in a browser, which a fresh probe cannot
reproduce and should not overwrite. And a `200` proves a page exists, not that
the file behind it is still the one the paper used.

Rebuilding everything else:

```bash
make build           # derive + render docs from the frozen corpus
make verify          # re-derive every headline figure and assert it independently
```

## Contributing

Additions are welcome, in a defined shape: see
[`CONTRIBUTING.md`](CONTRIBUTING.md). The short version is that the frozen
corpus does not change — it is the baseline the thesis is computed from — and
new entries arrive in a separate extension file so that both stay citable.

## Citation

If you use this catalogue, please cite it. [`CITATION.cff`](CITATION.cff) is
machine-readable and GitHub renders a "Cite this repository" button from it.

- Repository: <https://github.com/btogno/sustainable-finance-data>
- Archived version DOI: `10.5281/zenodo.XXXXXXX` — minted at release. Cite the
  version DOI rather than the concept DOI, so that a reader following it lands
  on exactly the corpus and figures reported, not on a later revision.

## Licence

The curated metadata in `data/`, `docs/` and this README is released under
**CC BY 4.0**; the scripts under **MIT**. See [`LICENSE`](LICENSE).

Neither licence extends to the underlying datasets. Those remain governed by
whatever terms their producers set, which for 92 of the 109 papers includes at
least one commercially licensed input. This repository links to the underlying
data and does not redistribute it.

## Provenance

Built from the corpus hand-coded for *Data in Sustainable Finance: Sources,
Methods and Availability in the Top Finance Journals, 2010–2026*, a master's
thesis at the University of Zurich (Department of Banking and Finance).
Version 1.0 corresponds to the frozen 109-paper corpus the thesis reports;
later additions extend the catalogue without altering that baseline. This
repository was named `open-sustainable-finance-data` through v1.0.0; GitHub
redirects the old name to `sustainable-finance-data`.
