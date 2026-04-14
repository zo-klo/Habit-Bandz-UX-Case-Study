# Habit Bandz UX Case Study

This repository contains a public-safe portfolio version of a UX and product insight workflow for Habit Bandz, a behavioral health product spanning a wearable device, companion app, and clinician-facing dashboard.

The full write-up lives in [CASE_STUDY.md](./CASE_STUDY.md).

## What This Repository Shows

- how qualitative interview data can be normalized into an analysis-ready structure
- how lightweight NLP can support signal detection without overclaiming certainty
- how behavioral segmentation can inform product decisions
- how synthetic scenario simulation can be used to explore UX risk before further live testing

## Repository Contents

```text
Habit-Bandz-UX-Case-Study/
├── CASE_STUDY.md
├── README.md
├── requirements.txt
└── public_notebooks/
    ├── 01_habitbandz_user_insight_workflow.ipynb
    ├── 02_persona_simulation_exploration.ipynb
    ├── habitbandz_portfolio_utils.py
    ├── README.md
    └── data/
        └── habitbandz_synthetic_feedback.csv
```

## Recommended Reading Order

1. [CASE_STUDY.md](./CASE_STUDY.md) for the full narrative and product implications
2. [public_notebooks/01_habitbandz_user_insight_workflow.ipynb](./public_notebooks/01_habitbandz_user_insight_workflow.ipynb) for the cleaned insight workflow
3. [public_notebooks/02_persona_simulation_exploration.ipynb](./public_notebooks/02_persona_simulation_exploration.ipynb) for the exploratory persona simulation workflow

## Notes

- The public version uses synthetic data and redacted configuration.
- The simulation notebook is exploratory and is not a substitute for user research.
- Any API key should be supplied through an environment variable rather than committed to the repository.
