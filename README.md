# Clinical Trials Data Pipeline & Dashboard Suite

**Author:** Olguyne Fernandez-Fraga | Data Analyst

## Overview

This project builds an end-to-end pipeline that pulls industry-sponsored clinical trial
data from the [ClinicalTrials.gov v2 API](https://clinicaltrials.gov/data-api/api), classifies
trials by disease area, and surfaces the results in a set of interactive Tableau dashboards.
It was completed as part of an internship with a healthcare analytics client (sourced via Riipen), and later adapted
for my WGU Data Analytics capstone.

As a Registered Dietitian with six-plus years of clinical experience (oncology, community
health/WIC, and hospital settings), I built this project to bridge my clinical domain
knowledge with hands-on data engineering and analytics — the exact intersection I'm now
targeting in my career.

## Problem

The client needed a repeatable way to track industry-sponsored clinical trial activity
across multiple disease areas — who's sponsoring what, at what phase, and how sponsor
activity compares across therapeutic areas — without manually pulling and reclassifying data
from ClinicalTrials.gov for every disease area.

## What This Pipeline Does

- **Fetches** trial-level data from the ClinicalTrials.gov v2 API across 7 disease areas:
  cardiovascular, kidney, diabetes, liver disease, obesity, autoimmune, and rare disease
- **Classifies** trials into disease-area categories using a shared MeSH-term
  include/exclude dictionary
- **Normalizes** sponsor names via a maintained lookup table, so the same sponsor doesn't
  appear under multiple name variants
- **Feeds** cleaned, structured data into Tableau for cross-disease and single-disease
  visual analysis

## Tech Stack

- **Python** — `requests` (API calls), `pandas` (data wrangling)
- **Jupyter Notebooks** — one per disease area, importing shared logic
- **Tableau** — dashboard and visualization layer
- **ClinicalTrials.gov API v2**

## Repo Structure

```text
├── trials_pipeline.py                      # Shared pipeline logic
│   ├── fetch_trials()
│   ├── extract_fields()
│   ├── run_pipeline()
│   ├── build_include_exclude_patterns()
│   └── classify()
├── mesh_include_exclude_dictionary.csv     # Disease-area classification terms
├── industry_sponsor_normalization_USABLE_LOOKUP.csv
├── notebooks/
│   ├── fetch_trials.ipynb                  # Cardiovascular
│   ├── kidney_trials.ipynb                 # Kidney
│   └── ...                                 # Additional disease areas
├── data/
│   ├── sponsor_trial_count_by_disease_area.csv
│   └── all_disease_areas_combined_for_tableau.csv
└── dashboards/                             # Screenshots / links to published Tableau views
```


## Dashboards

- **Sponsor Breadth** — bar chart of sponsor activity across disease areas
- **Sponsor × Disease Area Heatmap** — cross-disease sponsor activity at a glance
- Single-disease dashboards for cardiovascular and kidney (fully classified)

## Key Technical Notes

- Cardiovascular and kidney disease areas are fully classified; diabetes, liver disease,
  obesity, autoimmune, and rare disease have been fetched and are pending classification
- Sponsor normalization is maintained in a single shared lookup to keep sponsor names
  consistent across all 7 disease-area datasets
- Tableau-specific handling: Top N filters require all other filters set to "Add to
  Context," and groups are rebuilt fresh per data source

## What's Next

Planned cross-disease views:
1. Total combined trial volume by sponsor across all 7 disease areas
2. Phase × Disease Area heatmap across the combined dataset
3. Observational vs. Interventional split by disease area

## About Me

I'm a Registered Dietitian transitioning into healthcare data analytics, with clinical
experience spanning oncology, WIC community health, and hospital settings across South
Florida. I hold a BS in Data Analytics (WGU) and a CompTIA Data+ certification. This
project reflects how I approach data work: grounded in real clinical and operational
questions, not just technical exercises.

[Full case study on my portfolio site →](#)
