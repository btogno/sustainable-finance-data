# Statistics

Recomputed from the frozen corpus on 2026-09-23. Every figure the README or the thesis cites is derived here, so the two cannot drift apart.

## Corpus

- **n = 109** papers, four journals, publication years 2011–2026.
- Journals: Journal of Financial Economics 42 · Review of Finance 31 · Review of Financial Studies 22 · Journal of Finance 14
- Geographic scope of the data: US 57 · Global 42 · Europe 7 · Asia-Pacific 2 · Other / Regional 1
- Unit of observation: Firm-Year 43 · Other 28 · Portfolio-Level 17 · Asset-Level 15 · Document-Level 3 · Country-Year 2 · (unrecorded) 1

### Composition: journal × period

| Journal | 2011–2015 | 2016–2020 | 2021–2023 | 2024–2026 | Total |
|---|---:|---:|---:|---:|---:|
| Journal of Finance | 0 | 4 | 2 | 8 | **14** |
| Journal of Financial Economics | 6 | 7 | 14 | 15 | **42** |
| Review of Financial Studies | 0 | 5 | 10 | 7 | **22** |
| Review of Finance | 0 | 0 | 7 | 24 | **31** |
| **Total** | **6** | **16** | **33** | **54** | **109** |

*Source: Own calculations with data from the coding workbook.*

## Availability

- Mean data score **0.31**, mean code score **0.35**, mean composite **0.33**.
- **6** papers (5.5 %) are fully open — data *and* code released. **34** (31.2 %) score zero on both.
- Data availability: N 52 · Raw Data 36 · Y 9 · Partial 7 · On Demand 5
- Code availability: N 69 · Y 37 · Partial 2 · On Demand 1
- The asymmetry runs one way: **31** papers release code without releasing data, against **3** the other way. **17** publish replication code against no public data at all — code that cannot be executed.
- Score distribution: 0.00: 34 · 0.12: 6 · 0.25: 27 · 0.50: 21 · 0.62: 1 · 0.75: 8 · 0.88: 6 · 1.00: 6

### Data level × code level

| data \ code | Y | Partial | On Demand | N | Total |
|---|---:|---:|---:|---:|---:|
| Y | 6 | 0 | 0 | 3 | **9** |
| Partial | 6 | 1 | 0 | 0 | **7** |
| Raw Data | 8 | 1 | 0 | 27 | **36** |
| On Demand | 0 | 0 | 0 | 5 | **5** |
| N | 17 | 0 | 1 | 34 | **52** |
| **Total** | **37** | **2** | **1** | **69** | **109** |

The off-diagonal carries the corpus's structure: **25** papers release code against no released panel (Raw Data or N on data), against **3** releasing a panel (Y on data) with no code.

*Source: Own calculations with data from the coding workbook.*

## Curation tiers

Every paper carries exactly one tier, ranked by what a reader can recover. The rules are in [CODEBOOK.md](CODEBOOK.md) §7.

| Tier | n | Share |
|---|---|---|
| Tier 1 | 6 | 5.5 % |
| Tier 2 | 6 | 5.5 % |
| Tier 3 | 4 | 3.7 % |
| Tier 4 | 8 | 7.3 % |
| Tier 5 | 17 | 15.6 % |
| Tier 6 | 33 | 30.3 % |
| Tier 7 | 35 | 32.1 % |

Tiers 1 to 3 are the 16 entries with something downloadable, 14.7 % of the corpus. Tiers 4 and 5 add 25 papers that release code without a panel: not rerunnable, but the pipeline is documented.

## Raw data sources

Counted on an any-mention basis across the primary and secondary source fields; a category counts once for a paper naming it in either. Class is the access-terms classification of CODEBOOK.md §4.

| Source category | Any-mention | Primary | Class |
|---|---:|---:|---|
| Proprietary Database | 69 | 41 | licensed |
| Market Data | 57 | 18 | licensed |
| Official Statistics | 22 | 15 | public |
| Weather & Hazard | 18 | 5 | public |
| Other | 14 | 9 | neither |
| Survey Data | 11 | 10 | neither |
| SEC Filings | 5 | 3 | public |
| Earnings Call transcripts | 4 | 4 | licensed |
| News & Media | 4 | 3 | licensed |
| Social Media | 1 | 0 | neither |
| Satellite Imagery | 1 | 1 | public |
| CDP Reports | 1 | 0 | public |

207 source mentions across 109 papers. These counts are a lower bound on named vendors: the free-text coding note records a source category, not a systematic vendor field, so a paper using a given source without the note recording it is not counted here. Per-paper detail is in [CATALOGUE.md](CATALOGUE.md).

*Source: Own calculations with data from the coding workbook.*

## Licensing exposure

**92** of 109 papers (84.4 %) draw on at least one licensed input.

| Exposure | n | Mean data | Mean code | Composite | Fully open |
|---|---|---|---|---|---|
| licensed only | 61 | 0.16 | 0.38 | 0.27 | 2 |
| licensed and public | 31 | 0.50 | 0.32 | 0.41 | 1 |
| public only | 11 | 0.55 | 0.27 | 0.41 | 1 |
| neither | 6 | 0.38 | 0.33 | 0.35 | 2 |

## Clusters

Ordered along the availability gradient. Non-exclusive, so counts sum above 109.

| Cluster | n | Data | Code | Composite | Fully open | Median lag | Median data end |
|---|---|---|---|---|---|---|---|
| Biodiversity & Nature | 14 | 0.46 | 0.21 | 0.34 | 2 | 3 | 2023 |
| Climate Physical Risk | 28 | 0.44 | 0.36 | 0.40 | 1 | 4 | 2018 |
| Climate Transition Risk & Corporate Emissions | 42 | 0.35 | 0.37 | 0.36 | 2 | 4 | 2020 |
| Green Bonds & Sustainable Debt | 13 | 0.25 | 0.69 | 0.47 | 0 | 4 | 2021 |
| Social & Governance | 40 | 0.24 | 0.24 | 0.24 | 3 | 5 | 2018 |
| ESG Disclosure & Ratings | 38 | 0.20 | 0.32 | 0.26 | 1 | 4 | 2019 |

### Cluster composition by period

Non-exclusive; columns sum above the period *n*.

| Cluster | 2011–2015 | 2016–2020 | 2021–2023 | 2024–2026 | Total |
|---|---:|---:|---:|---:|---:|
| Biodiversity & Nature | 0 | 0 | 0 | 14 | **14** |
| Climate Physical Risk | 1 | 6 | 10 | 11 | **28** |
| Climate Transition Risk & Corporate Emissions | 0 | 3 | 12 | 27 | **42** |
| Green Bonds & Sustainable Debt | 0 | 1 | 4 | 8 | **13** |
| Social & Governance | 6 | 8 | 13 | 13 | **40** |
| ESG Disclosure & Ratings | 0 | 7 | 14 | 17 | **38** |
| *Papers in period* | *6* | *16* | *33* | *54* | *109* |

*Source: Own calculations with data from the coding workbook.*

### Unit of observation × cluster

| Unit | Biodiversity & Nature | Climate Physical Risk | Climate Transition Risk & Corporate Emissions | Green Bonds & Sustainable Debt | Social & Governance | ESG Disclosure & Ratings | Corpus |
|---|---:|---:|---:|---:|---:|---:|---:|
| Firm-Year | 6 | 5 | 26 | 3 | 17 | 15 | 43 |
| Other | 5 | 11 | 6 | 3 | 13 | 7 | 28 |
| Portfolio-Level | 0 | 1 | 3 | 0 | 6 | 14 | 17 |
| Asset-Level | 3 | 10 | 3 | 6 | 1 | 0 | 15 |
| Document-Level | 0 | 1 | 1 | 0 | 2 | 1 | 3 |
| Country-Year | 0 | 0 | 2 | 1 | 0 | 0 | 2 |
| (unrecorded) | 0 | 0 | 1 | 0 | 1 | 1 | 1 |

Granularity tracks the input class: asset-level observation concentrates where the data is physical or security-level, firm-year where it is accounting or vendor-supplied, portfolio-level where it is a rating attached to a fund.

*Source: Own calculations with data from the coding workbook.*

## Methods

Counted on an **any-mention** basis across the primary and secondary method fields. A method can be widely used without being any paper's primary technique, which is why the two columns differ.

| Method | Any mention | Primary only | Mean availability | Mean data |
|---|---|---|---|---|
| Standard econometrics on accounting and market data | 99 | 84 | 0.33 | 0.30 |
| Satellite and remote sensing | 14 | 3 | 0.43 | 0.50 |
| NLP / textual analysis | 10 | 8 | 0.56 | 0.57 |
| Survey instrument | 9 | 4 | 0.25 | 0.33 |
| Experiment | 6 | 3 | 0.19 | 0.21 |
| Regulatory filing parsing | 4 | 0 | 0.47 | 0.44 |
| Machine learning (non-NLP) | 1 | 0 | 0.00 | 0.00 |
| Meta-analysis / systematic review | 1 | 0 | 0.00 | 0.00 |
| Other | 10 | 7 | 0.20 | 0.10 |

### Method mix by period, any-mention

| Method | 2011–2015 | 2016–2020 | 2021–2023 | 2024–2026 | Total |
|---|---:|---:|---:|---:|---:|
| Standard econometrics on accounting and market data | 6 | 15 | 30 | 48 | **99** |
| Satellite and remote sensing | 0 | 2 | 8 | 4 | **14** |
| NLP / textual analysis | 0 | 1 | 2 | 7 | **10** |
| Survey instrument | 1 | 1 | 3 | 4 | **9** |
| Experiment | 0 | 3 | 1 | 2 | **6** |
| Regulatory filing parsing | 1 | 0 | 1 | 2 | **4** |
| Machine learning (non-NLP) | 0 | 0 | 0 | 1 | **1** |
| Meta-analysis / systematic review | 0 | 0 | 1 | 0 | **1** |
| Other | 0 | 1 | 4 | 5 | **10** |

*Source: Own calculations with data from the coding workbook.*

### Methods by cluster

| Cluster | n | Standard econometrics | Other methods, any mention |
|---|---|---|---|
| Biodiversity & Nature | 14 | 10 (71 %) | NLP 3 · Satellite and remote sensing 2 · Survey instrument 2 · Experiment 1 · Machine learning (non-NLP) 1 · Other 1 |
| Climate Physical Risk | 28 | 26 (93 %) | Satellite and remote sensing 12 · NLP 4 · Other 1 · Survey instrument 1 |
| Climate Transition Risk & Corporate Emissions | 42 | 39 (93 %) | NLP 7 · Other 5 · Survey instrument 3 · Satellite and remote sensing 2 · Experiment 1 · Regulatory filing parsing 1 |
| Green Bonds & Sustainable Debt | 13 | 12 (92 %) | Other 2 · Satellite and remote sensing 2 · Experiment 1 · Survey instrument 1 |
| Social & Governance | 40 | 35 (88 %) | Experiment 4 · Satellite and remote sensing 4 · Survey instrument 4 · Regulatory filing parsing 2 · Other 2 · NLP 1 |
| ESG Disclosure & Ratings | 38 | 34 (89 %) | Experiment 5 · Other 4 · Survey instrument 4 · Regulatory filing parsing 2 · NLP 2 · Meta-analysis 1 |

## Currency of the evidence

- Median lag from last year of data to publication: **4 years** (mean 4.4, maximum 14).
- Median sample window: **13 years**.
- Papers carrying data past 2023: **5**.

## Link inventory

109 data and code link entries across the corpus, last checked 2026-08-22: LIVE 106 · ERROR 2 · REDIRECT 1. Established by web 65 · manual 44.

The 109 publisher landing pages are excluded: they are DOIs and were not probed. Where an automated probe could not settle a link — Harvard Dataverse, Wiley, Mendeley, FEMA, OSF and Google all refuse robots or answer them identically whatever a file's real permissions — it was opened in a browser instead, which is what the `manual` method records. See [LINK_CHECKS.md](LINK_CHECKS.md).

