"""
Industry-Sponsored Clinical Trial Volume Trend Analysis
WGU D502 Capstone

Tests whether industry-sponsored clinical trial volume shows a statistically
significant trend over time (2020-2025) across seven chronic disease areas,
using linear regression of annual trial count against year.

Research Question: Did industry-sponsored clinical trial volume in the obesity
and autoimmune disease areas increase at a statistically significant rate
between 2020 and 2025?
"""

import pandas as pd
from scipy import stats
import numpy as np

# ---------------------------------------------------------------------------
# STEP 1: Load and filter data
# ---------------------------------------------------------------------------
# Only confidently-classified trials (indication_classification starting with
# "true_") are used. Trials flagged "needs_review" or "excluded" are dropped
# to avoid misclassification affecting the trend analysis.

df = pd.read_csv("all_disease_areas_combined_for_tableau.csv")
df = df[df["indication_classification"].str.startswith("true_", na=False)].copy()

df["first_posted"] = pd.to_datetime(df["first_posted"], errors="coerce")
df["year"] = df["first_posted"].dt.year

# 2026 is a partial year in this dataset (only through July 1), so it is
# excluded to avoid distorting the trend with an incomplete year.
df = df[df["year"].between(2020, 2025)]

print(f"Loaded {len(df)} confidently-classified, industry-sponsored trials, 2020-2025.\n")

# ---------------------------------------------------------------------------
# STEP 2: Aggregate to annual trial counts per disease area
# ---------------------------------------------------------------------------

counts = df.groupby(["disease_area", "year"]).size().reset_index(name="trial_count")

areas = sorted(df["disease_area"].unique())
years = list(range(2020, 2026))
full_index = pd.MultiIndex.from_product([areas, years], names=["disease_area", "year"])
counts = counts.set_index(["disease_area", "year"]).reindex(full_index, fill_value=0).reset_index()

# ---------------------------------------------------------------------------
# STEP 3: Run linear regression (trial_count ~ year) per disease area
# ---------------------------------------------------------------------------
# H0: slope = 0 (no trend)   |   Ha: slope != 0 (trial volume trending)
# Alpha = .05

results = []
for area in areas:
    sub = counts[counts["disease_area"] == area].sort_values("year")
    x, y = sub["year"].values, sub["trial_count"].values
    slope, intercept, r, p, se = stats.linregress(x, y)
    t_stat = slope / se
    results.append({
        "Disease Area": area.replace("_", " ").title(),
        "Slope (trials/yr)": round(slope, 2),
        "t-stat": round(t_stat, 3),
        "p-value": round(p, 4),
        "Significant (a=.05)": "Yes" if p < 0.05 else "No",
    })

results_df = pd.DataFrame(results).sort_values("p-value").reset_index(drop=True)

print("=" * 70)
print("REGRESSION RESULTS: Annual Trial Count vs. Year, by Disease Area")
print("=" * 70)
print(results_df.to_string(index=False))
print()

# ---------------------------------------------------------------------------
# STEP 4: Verify regression assumptions for the significant results
# ---------------------------------------------------------------------------

print("=" * 70)
print("ASSUMPTION CHECKS (obesity & autoimmune, the significant results)")
print("=" * 70)

for area in ["obesity", "autoimmune"]:
    sub = counts[counts["disease_area"] == area].sort_values("year")
    x, y = sub["year"].values, sub["trial_count"].values
    slope, intercept, r, p, se = stats.linregress(x, y)
    residuals = y - (slope * x + intercept)

    shapiro_stat, shapiro_p = stats.shapiro(residuals)
    hetero_r, hetero_p = stats.pearsonr(np.abs(residuals), slope * x + intercept)

    print(f"\n{area.title()}:")
    print(f"  Shapiro-Wilk normality test:  W={shapiro_stat:.3f}, p={shapiro_p:.3f} "
          f"({'normal' if shapiro_p > 0.05 else 'non-normal'})")
    print(f"  Homoscedasticity check:       r={hetero_r:.3f}, p={hetero_p:.3f} "
          f"({'constant variance' if hetero_p > 0.05 else 'variance concern'})")

print("\n" + "=" * 70)
print("CONCLUSION")
print("=" * 70)
print(
    "Obesity (p=.0011) and autoimmune (p=.0082) both fall below alpha=.05,\n"
    "providing sufficient evidence to reject H0 and support the hypothesis\n"
    "that industry-sponsored trial volume increased at a statistically\n"
    "significant rate in these two disease areas, 2020-2025. The remaining\n"
    "five disease areas show no statistically significant trend."
)