# Do Type Designers See Text Differently?

[![Posterior draws on Zenodo](https://zenodo.org/badge/DOI/10.5281/zenodo.24152973.svg)](https://doi.org/10.5281/zenodo.24152973)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Analysis code and data for

> Mangas, H., Tashk, A., Bækgaard, P., & Beier, S. *Do Type Designers See Text Differently? Short-Exposure Text Recognition, an Expert vs. Novice Performance Study.*

![Graphical abstract: 17 type designers and 17 novices reported five-letter strings shown for 10 to 200 ms in Helvetica and Klimax Plus. Posterior TVA curves with 95% credible bands show no credible group difference in Helvetica and a credible expert advantage in Klimax Plus from 55 to 200 ms, +0.72 letters at 100 ms.](docs/graphical_abstract.png)

Seventeen professional type designers and seventeen novices reported briefly presented five-letter strings set in Helvetica and in the display typeface Klimax Plus. Performance is analysed with a hierarchical Bayesian version of the Theory of Visual Attention (TVA) whole-report model (capacity *K*, processing speed *C*, perceptual threshold *t0*), followed by frequentist, descriptive and sensitivity analyses. Everything reported in the Results section of the manuscript (Figures 2–12, Tables 2–5 and the statistics quoted in the text) is produced by the single notebook in this repository.

**Main findings**

- **The font effect is large and certain.** Klimax Plus lowers capacity and processing speed and raises the perceptual threshold for every reader.
- **Expertise matters only for the demanding face, and only for capacity.** Under Klimax Plus experts are predicted to report about 0.7 letters more than novices at exposures from 55 to 200 ms (95% CrI at 100 ms: 0.13–1.30); the capacity contrast has posterior probability .946 (independent per-participant fits: *d* = 0.98, *p* = .010, *p*<sub>Holm</sub> = .058). Under Helvetica the groups do not differ credibly, but that condition sits close to the five-letter ceiling.
- **Age neither confounds nor moderates the effect.**
- **Implication.** Type designers read a demanding display face better than the readers it is meant for, so legibility tests of such faces should rely on non-expert readers.

## Repository layout

```
.
├── TVA_ExpertNovice_Analysis.ipynb   # the complete analysis, run top to bottom
├── data/
│   ├── Data_Expert_Novice_Combined_Data.csv   # trial-level data (36 participants × 160 trials)
│   └── participant_info.csv                   # age, gender and vision per participant
├── docs/
│   ├── graphical_abstract.png                 # the figure above
│   └── make_graphical_abstract.py             # draws it from results/posterior_full.nc and the data
├── figures/        # written by the notebook, named by manuscript figure number
├── results/
│   ├── README.md   # where the posterior files come from
│   ├── *.nc        # posterior draws (NetCDF), downloaded from Zenodo, see "Posterior draws" below
│   └── tables/     # CSV versions of the manuscript tables, written by the notebook
├── requirements.txt
├── environment.yml
├── CITATION.cff
└── LICENSE
```

All paths inside the notebook are relative to the repository root, so the repository can be cloned to any location.

## How to reproduce the results

1. Clone the repository and create the environment (Python 3.11 or newer; the reported results were produced with Python 3.12.3):

   ```bash
   # with conda
   conda env create -f environment.yml
   conda activate tva-expert-novice

   # or with pip
   python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Download the three posterior files from Zenodo into `results/` (see [Posterior draws](#posterior-draws) below). If any file is missing, the notebook stops in its first section and names the missing file.

3. Start Jupyter **from the repository root** and run `TVA_ExpertNovice_Analysis.ipynb` from top to bottom (`Kernel → Restart & Run All`):

   ```bash
   jupyter lab TVA_ExpertNovice_Analysis.ipynb
   ```

   Figures appear in `figures/` and tables in `results/tables/`. Section 10 of the notebook lists, for every figure, table and statistic in the manuscript, the notebook section that produces it.

### Posterior draws

The posterior draws behind every Bayesian result in the manuscript are archived on Zenodo in a single record: **[doi:10.5281/zenodo.24152973](https://doi.org/10.5281/zenodo.24152973)**. They are not part of this git repository because two of the files exceed GitHub's 100 MB file-size limit. Download the three files into `results/` before running the notebook; the notebook then loads the draws instead of re-sampling.

| File | Size | Contents |
|------|------|----------|
| `posterior_baseline.nc` | 219 MB | Baseline model (participant random effects only), including the pointwise log-likelihood used for LOO-CV |
| `posterior_full.nc` | 289 MB | Full Font × Group model, including the pointwise log-likelihood |
| `posterior_full_with_R8.nc` | 49 MB | Full model refitted with Expert #8 reinstated (sensitivity analysis, notebook Section 9.4) |

Download them from the Zenodo page, or run one of the following from the repository root:

```bash
# Linux / macOS
for f in posterior_baseline.nc posterior_full.nc posterior_full_with_R8.nc; do
  curl -L -o "results/$f" "https://zenodo.org/records/24152973/files/$f?download=1"
done
```

```powershell
# Windows PowerShell
foreach ($f in "posterior_baseline.nc", "posterior_full.nc", "posterior_full_with_R8.nc") {
  curl.exe -L -o "results/$f" "https://zenodo.org/records/24152973/files/${f}?download=1"
}
```

MD5 checksums, to verify the downloads (`md5sum results/*.nc` on Linux, `md5 results/*.nc` on macOS, `Get-FileHash -Algorithm MD5 results\*.nc` on Windows):

```
102f6f3c9621b51455fac73b06856082  posterior_baseline.nc
3f451bb00c7b95d7626b6a47100d6898  posterior_full.nc
2a5687ab915c2b49bc98b6fada677c64  posterior_full_with_R8.nc
```

All three models were sampled with NUTS: 4 chains, 3,000 draws each after 1,000–1,500 tuning iterations, `target_accept = 0.99`, maximum tree depth 14, seed 1234. If a file is missing, the notebook stops in Section 1 instead of silently re-fitting the models. To re-fit them from scratch on purpose, set `RESAMPLE_MISSING_MODELS = True` in Section 1 of the notebook; re-sampling is slow at these settings, and the new draws are saved under the same file names.

Two levels of reproduction are therefore possible:

- **Exact.** With the Zenodo files in `results/`, the notebook uses the posterior draws behind the manuscript, so the posterior summaries are the reported ones: for example, the population-level capacities in Figure 6 (4.295, 4.409, 3.117, 3.676), every row of Table 2, and the window in which experts credibly outperform novices under Klimax Plus (55–200 ms).
- **Statistical.** With `RESAMPLE_MISSING_MODELS = True` and no files, the notebook re-fits the models. The reported posteriors were drawn with the `nutpie` sampler (JAX backend), which the notebook uses when it is installed; otherwise PyMC's own NUTS sampler is used with the same settings. Either way the posterior summaries agree with the reported values only up to Monte-Carlo error, while the data-dependent quantities listed below are exact.

Quantities that do not depend on the posterior draws, and are therefore reproduced exactly on any platform: the trial accounting and duplicate audit, demographics, the timing-discrepancy summary, the mixed ANOVA, linear mixed models and Tukey tests (Table 4), the duration-matched comparisons (Figure 8), the independent per-participant TVA fits (Table 3, Figure S9), the DTW distances, bootstrap intervals and temporal-lead estimates (Figure 10), and the sensitivity power analysis.

### Package versions

The reported results were produced with PyMC 5 and ArviZ 0.x, which `requirements.txt` and `environment.yml` pin (`pymc<6`, `arviz<1`); ArviZ 1.x changed the LOO and plotting interfaces and is not targeted. The notebook prints the versions of all packages it uses in its first cell. To pin an environment exactly, run `pip freeze > requirements-lock.txt` in the environment that produced the results.

## Data

### `data/Data_Expert_Novice_Combined_Data.csv`

One row per trial (5,760 rows: 36 participants × 160 trials). The file is the unmodified export of the experiment software.

| Column | Description |
|--------|-------------|
| `TrialID` | Trial number within the session (1–160) |
| `Font` | Typeface: `Helvetica` or `KlimaxStd-Plus` (PostScript name of Klimax Plus; renamed to `Klimax Plus` by the notebook) |
| `FontSize` | Rendered em size in pixels (152 for Helvetica, 160 for Klimax Plus) |
| `Letters` | The five-letter stimulus string |
| `Positions` | Stimulus position code (constant, 1) |
| `WordCondition` | Stimulus type (constant, `NonWord`: random letter strings) |
| `WaitingDisplay_ms`, `WaitingDisplay_chrono` | Intended and recorded duration of the pre-stimulus interval (ms) |
| `TargetDisplay_ms` | Intended exposure duration of the stimulus (10, 20, 30, 40, 50, 60, 90 or 200 ms) |
| `TargetDisplay_chrono` | Recorded exposure duration of the stimulus (ms) |
| `MaskDisplay_ms`, `MaskDisplay_chrono` | Intended (800 ms) and recorded duration of the pattern mask |
| `Responses` | Letters typed by the participant (`[]` if none) |
| `NumberResponses` | Number of letters typed |
| `NumberCorrect` | Number of typed letters scored as correct by the experiment software (re-scored by the notebook, see below) |
| `ItemsCorrect` | The letters scored as correct |
| `ExpectedScore`, `GuessCorrection` | Scoring fields produced by the experiment software; not used in the analysis |
| `ParticipantID` | Participant code within group (`R1`–`R18`) |
| `GroupCondition` | `Expert` or `Novice` |
| `Participants_ID` | Unique participant identifier, `<ParticipantID>_<GroupCondition>` |

### `data/participant_info.csv`

One row per recorded participant: `Participants_ID`, `ParticipantID`, `group`, `age` (years), `gender` (`F`/`M`), `vision` (`Normal` or `Corrected`). R17_Novice has no demographic fields and R8_Expert has age only; neither participant enters the main analysis (R17_Novice is excluded for an exposure-timing failure, R8_Expert for age matching), and R8_Expert's age is the only field needed for the sensitivity refit.

### Data-processing steps performed by the notebook

1. **Duplicate-response audit.** A letter typed twice but present only once in the stimulus had been scored twice; the notebook re-scores every trial so that each stimulus letter can be matched once (31 of 5,760 trials corrected downward by one).
2. **Participant exclusions.** R17_Novice (mean exposure-timing discrepancy of about 100 ms) and R8_Expert (age matching), leaving 17 participants per group. The exclusion of R8_Expert is revisited in the sensitivity refit.
3. **Novice exposure-time correction.** The novice display missed frames: recorded exposures are snapped to the 60 Hz frame grid and only trials whose snapped duration matches the dominant mapping for their intended duration are retained (159 of 2,720 novice trials removed). Expert exposures are used as recorded. The analysed dataset has 5,281 trials.

## Notebook outline

| Section | Content |
|---------|---------|
| 1 | Setup: imports, repository paths, sampler configuration |
| 2 | Data preparation: loading, demographics, duplicate audit, timing correction, model indices |
| 3 | Hierarchical Bayesian TVA models: baseline and full model, LOO-CV comparison, diagnostics |
| 4 | Primary analysis: posterior TVA curves (Fig. 2), posterior difference curves (Fig. 9), forest plot (Fig. 6), posterior contrasts (Table 2), difference distributions (Fig. 5), font effect (Fig. 7) |
| 5 | H1: participant-level tests, parameter box plots (Fig. 3), mixed ANOVA, mixed models and Tukey HSD (Table 4) |
| 6 | H3: age × expertise (Fig. 11) |
| 7 | H2: exposure-time comparisons, matched pairs (Fig. 8) |
| 8 | Dynamic time warping, age analyses, capacity vs. age (Fig. 12), age-extremes comparison (Table 5) |
| 9 | Supplementary and sensitivity analyses: trial accounting, ceiling/ROPE diagnostics, independent per-participant fits and shrinkage check (Fig. 4, Table 3), refit with Expert #8 reinstated, DTW bootstrap and temporal lead (Fig. 10), power analysis, estimand reconciliation |
| 10 | Map from every manuscript figure, table and quoted statistic to the notebook section that produces it |

## Citation

See `CITATION.cff`. Please cite the article when using the data or code, and the Zenodo record ([doi:10.5281/zenodo.24152973](https://doi.org/10.5281/zenodo.24152973)) when using the posterior draws.

## License

This repository is released under the [MIT License](LICENSE). Copyright (c) 2026 Héctor Mangas, Ashkan Tashk, Per Bækgaard and Sofie Beier.
