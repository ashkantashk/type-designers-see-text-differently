# Do Type Designers See Text Differently?

Analysis code and data for

> Mangas, H., Tashk, A., Bækgaard, P., & Beier, S. *Do Type Designers See Text Differently? Short-Exposure Text Recognition, an Expert vs. Novice Performance Study.*

![Graphical abstract: 17 type designers and 17 novices reported briefly shown five-letter strings in Helvetica and Klimax Plus; TVA curves show no credible group difference in Helvetica but an expert advantage of about 0.7 letters in Klimax Plus from 55 to 200 ms](docs/graphical_abstract.png)

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
│   └── make_graphical_abstract.py             # script that draws it
├── figures/        # written by the notebook, named by manuscript figure number
├── results/
│   ├── *.nc        # cached posterior draws (NetCDF), see "Posterior draws" below
│   └── tables/     # CSV versions of the manuscript tables, written by the notebook
├── requirements.txt
├── environment.yml
└── CITATION.cff
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

2. Start Jupyter **from the repository root** and run `TVA_ExpertNovice_Analysis.ipynb` from top to bottom (`Kernel → Restart & Run All`):

   ```bash
   jupyter lab TVA_ExpertNovice_Analysis.ipynb
   ```

   Figures appear in `figures/` and tables in `results/tables/`. Section 10 of the notebook lists, for every figure, table and statistic in the manuscript, the notebook section that produces it.

### Posterior draws

The three hierarchical models (baseline, full model, and the sensitivity refit with Expert #8 reinstated) are sampled with NUTS: 4 chains, 3,000 draws each after 1,000–1,500 tuning iterations, `target_accept = 0.99`, maximum tree depth 14, seed 1234. On a laptop each model takes on the order of one hour. The notebook saves the draws as `results/posterior_baseline.nc`, `results/posterior_full.nc` and `results/posterior_full_with_R8.nc`, and loads them instead of re-sampling whenever they are present.

Two levels of reproduction are therefore possible:

- **Exact.** Place the NetCDF files used for the manuscript in `results/` before running the notebook. They are too large for git (several hundred MB each, because they include the pointwise log-likelihood needed for LOO-CV) and are distributed separately; see the "Data and code availability" statement of the manuscript. With these files every number in the manuscript is reproduced digit for digit.
- **Statistical.** Without the files, the notebook re-samples. The reported posteriors were drawn with the `nutpie` sampler (JAX backend), which the notebook uses when it is installed; otherwise PyMC's own NUTS sampler is used with the same settings. Either way the posterior summaries agree with the reported values up to Monte-Carlo error (the reported credible-interval limits are stable to about two decimals), while the data-dependent quantities listed below are exact.

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

See `CITATION.cff`. Please cite the article when using the data or code.

## License

This repository is released under the [MIT License](LICENSE). Copyright (c) 2026 Héctor Mangas, Ashkan Tashk, Per Bækgaard and Sofie Beier.
