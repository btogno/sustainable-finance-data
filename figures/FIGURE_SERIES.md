# Figure series

Every value plotted in `fig4_1.png` … `figD_3.png`, written out by `scripts/make_figures.py` from the same derived table the figures are drawn from. Compare against [STATS.md](../docs/STATS.md).


## Figure 4.1 — cluster composition by period

| Cluster | 2011–2015 | 2016–2020 | 2021–2023 | 2024–2026 | Total |
|---|---:|---:|---:|---:|---:|
| Climate Transition Risk & Corporate Emissions | 0 | 3 | 12 | 27 | **42** |
| Social & Governance | 6 | 8 | 13 | 13 | **40** |
| ESG Disclosure & Ratings | 0 | 7 | 14 | 17 | **38** |
| Climate Physical Risk | 1 | 6 | 10 | 11 | **28** |
| Biodiversity & Nature | 0 | 0 | 0 | 14 | **14** |
| Green Bonds & Sustainable Debt | 0 | 1 | 4 | 8 | **13** |
| *Papers in period* | 6 | 16 | 33 | 54 | *109* |

## Figure 4.2 — geographic scope by period (shares)

| Scope | 2011–2015 (n = 6) | 2016–2020 (n = 16) | 2021–2023 (n = 33) | 2024–2026 (n = 54) |
|---|---:|---:|---:|---:|
| United States | 1.0000 | 0.6875 | 0.5758 | 0.3889 |
| Global | 0.0000 | 0.2500 | 0.3636 | 0.4815 |
| Europe and other | 0.0000 | 0.0625 | 0.0606 | 0.1296 |

## Figure 4.3 — mean scores by licensing exposure

| Exposure | n | Mean data | Mean code |
|---|---:|---:|---:|
| Licensed only | 61 | 0.1598 | 0.3811 |
| Licensed and public | 31 | 0.5000 | 0.3226 |
| Public only | 11 | 0.5455 | 0.2727 |
| Neither | 6 | 0.3750 | 0.3333 |

## Figure 4.4 — availability by publication year

Both series are **shares of the year's papers**, not mean scores. A paper coded
`On Demand` on code scores 0.25 and is not posting code.

| Year | Papers | Share posting code | Share releasing the panel |
|---:|---:|---:|---:|
| 2011 | 2 | 0.0000 | 0.0000 |
| 2012 | 1 | 0.0000 | 0.0000 |
| 2013 | 1 | 0.0000 | 0.0000 |
| 2014 | 1 | 0.0000 | 0.0000 |
| 2015 | 1 | 0.0000 | 0.0000 |
| 2016 | 1 | 0.0000 | 0.0000 |
| 2017 | 5 | 0.0000 | 0.0000 |
| 2018 | 0 | — | — |
| 2019 | 3 | 0.0000 | 0.0000 |
| 2020 | 7 | 0.0000 | 0.1429 |
| 2021 | 11 | 0.0909 | 0.0000 |
| 2022 | 15 | 0.0667 | 0.0000 |
| 2023 | 7 | 0.7143 | 0.2857 |
| 2024 | 15 | 0.5333 | 0.0667 |
| 2025 | 19 | 0.7895 | 0.0526 |
| 2026 | 20 | 0.3500 | 0.2000 |

## Figure D.1 — distribution of the publication lag

| Lag (years) | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Papers | 1 | 5 | 10 | 28 | 16 | 20 | 11 | 8 | 6 | 3 | 0 | 0 | 0 | 0 | 1 |

Median 4 · mean 4.4404 · maximum 14 · n = 109


## Figure D.2 — reference lines

| Line | From | To |
|---|---|---|
| No lag | (2010, 2010) | (2026, 2026) |
| Median lag of 4 years | (2010, 2006) | (2026, 2022) |

109 points plotted, one per paper. Horizontal offsets are cosmetic and deterministic; the vertical coordinate is the paper's `dataset_end_year`.


## Figure D.3 — distribution of the composite availability score

| Score | 0 | 0.125 | 0.25 | 0.375 | 0.5 | 0.625 | 0.75 | 0.875 | 1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Papers | 34 | 6 | 27 | 0 | 21 | 1 | 8 | 6 | 6 |
