"""
Shared ClinicalTrials.gov pipeline logic for the Pensieve Health internship project.
Import from this file in each disease-area notebook (fetch_trials.ipynb, kidney_trials.ipynb, etc.)
rather than redefining these functions per notebook.
"""

import requests
import time
import re

CTGOV_BASE_URL = "https://clinicaltrials.gov/api/v2/studies"


def fetch_trials(term, start_date="2020-01-01", end_date="MAX"):
    date_filter = f'AREA[StudyFirstPostDate]RANGE[{start_date},{end_date}]'
    funding_filter = 'AREA[LeadSponsorClass]INDUSTRY'
    combined_filter = f'{date_filter} AND {funding_filter}'
    all_studies = []
    page_token = None
    while True:
        params = {
            "query.cond": term,
            "filter.advanced": combined_filter,
            "pageSize": 1000
        }
        if page_token:
            params["pageToken"] = page_token
        r = requests.get(CTGOV_BASE_URL, params=params, timeout=15)
        if r.status_code != 200:
            print(f"Error {r.status_code}, stopping.")
            break
        data = r.json()
        all_studies.extend(data.get("studies", []))
        page_token = data.get("nextPageToken")
        if not page_token:
            break
        time.sleep(0.3)
    return all_studies


def extract_fields(study, seed_term):
    """Pulls the fields needed now AND the ones the diversity scoring will need later."""
    protocol = study.get("protocolSection", {})
    ident = protocol.get("identificationModule", {})
    status_mod = protocol.get("statusModule", {})
    design = protocol.get("designModule", {})
    sponsor_mod = protocol.get("sponsorCollaboratorsModule", {})
    cond_mod = protocol.get("conditionsModule", {})
    conditions_list = cond_mod.get("conditions", [])
    armsMod = protocol.get("armsInterventionsModule", {})
    interventions = armsMod.get("interventions", [])
    drug_names = [
        i.get("name", "") for i in interventions
        if i.get("type") in ("DRUG", "BIOLOGICAL")
    ]
    phases_list = design.get("phases", [])
    if not phases_list:
        phase_value = "BLANK"
    elif phases_list == ["NA"]:
        phase_value = "NA"
    else:
        phase_value = ",".join(phases_list)
    return {
        "nct_id": ident.get("nctId"),
        "title": ident.get("briefTitle"),
        "seed_term": seed_term,
        "study_type": design.get("studyType"),
        "phase": phase_value,
        "status": status_mod.get("overallStatus"),
        "first_posted": status_mod.get("studyFirstPostDateStruct", {}).get("date"),
        "last_update_posted": status_mod.get("lastUpdatePostDateStruct", {}).get("date"),
        "lead_sponsor": sponsor_mod.get("leadSponsor", {}).get("name"),
        "lead_sponsor_class": sponsor_mod.get("leadSponsor", {}).get("class"),
        "conditions": "|".join(conditions_list) if conditions_list else "NA",
        "collaborators": "|".join(
            c.get("name", "") for c in sponsor_mod.get("collaborators", [])
        ),
        "drug_names": "|".join(drug_names) if drug_names else "NA",
        "intervention_types": "|".join(set(i.get("type", "") for i in interventions)) or "NA",
    }


def run_pipeline(seed_term, start_date="2020-01-01", end_date="MAX"):
    import csv  # local import keeps the module's top-level dependencies minimal

    print(f"Fetching (MeSH/native query.cond): {seed_term}")
    seen_nct_ids = set()
    rows = []
    studies = fetch_trials(seed_term, start_date=start_date, end_date=end_date)
    for study in studies:
        row = extract_fields(study, seed_term)
        if row["nct_id"] and row["nct_id"] not in seen_nct_ids:
            seen_nct_ids.add(row["nct_id"])
            rows.append(row)
    print(f"  {len(rows)} unique studies found")
    filename = f"{seed_term.replace(' ', '_')}_{start_date}_to_{end_date}_trials.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Saved to {filename}")
    return rows


def build_include_exclude_patterns(mesh_dict_df, extra_include_keywords=None):
    """
    mesh_dict_df: a pandas DataFrame with columns Term, Section ("Include"/"Exclude").
    Pass in the full shared dictionary already filtered to the relevant Disease Area,
    e.g. mesh_dict_df[mesh_dict_df["Disease Area"] == "kidney"].

    extra_include_keywords: optional dict of {category_name: [keyword, ...]} for
    disease-specific synonym expansion, the same pattern used for cardiovascular
    (e.g. category labels like "Arrhythmias" expanded into "atrial fibrillation", etc.)
    since raw category names rarely match literal trial condition strings.
    """
    exclude_terms = mesh_dict_df[mesh_dict_df["Section"] == "Exclude"]["Term"].str.lower().tolist()
    include_terms_csv = mesh_dict_df[mesh_dict_df["Section"] == "Include"]["Term"].str.lower().tolist()

    extra_terms = []
    if extra_include_keywords:
        for kws in extra_include_keywords.values():
            extra_terms.extend(kws)

    include_pattern = re.compile(
        "|".join([re.escape(t) for t in include_terms_csv] + extra_terms),
        re.IGNORECASE
    )
    exclude_pattern = re.compile(
        "|".join(re.escape(t) for t in exclude_terms),
        re.IGNORECASE
    )
    return include_pattern, exclude_pattern


def classify(conditions_str, include_pattern, exclude_pattern, match_label="true_match"):
    """
    match_label: what to call a positive match, e.g. "true_cv" or "true_kidney".
    Keeps the label disease-specific while the matching logic itself stays shared.
    """
    if not conditions_str or conditions_str == "NA":
        return "needs_review"
    conds = conditions_str.split("|")
    if any(exclude_pattern.search(c) for c in conds):
        return "excluded"
    if any(include_pattern.search(c) for c in conds):
        return match_label
    return "needs_review"
