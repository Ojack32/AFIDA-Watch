"""
AFIDA Watch - Script 02
Cleans and enriches the holdings data with proper labels
Uses reference data from AFIDA data field PDFs
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
OUTPUT_DIR = Path("/home/afida/apps/AFIDA-Watch/output")
REPORTS_DIR = Path("/home/afida/apps/AFIDA-Watch/reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# ── Code Mappings from Reference PDFs ─────────────────────────────────────

# National Security Countries of Concern
SECURITY_COUNTRIES = {
    "CHINA": "🇨🇳 China",
    "RUSSIAN FEDERATION": "🇷🇺 Russia",
    "IRAN (ISLAMIC REPUBLIC OF)": "🇮🇷 Iran",
    "KOREA, D.P.R.O.": "🇰🇵 North Korea",
}

# Owner Type codes (2015 and prior)
OWNER_TYPE_PRE2016 = {
    "A": "Individual",
    "B": "Government",
    "C": "Corporation",
    "D": "Partnership",
    "E": "Estate",
    "F": "Trust",
    "G": "Institution",
    "H": "Association",
    "K": "Other (LLC)",
}

# Acquisition Method codes (2016+)
ACQUISITION_METHOD = {
    1: "Cash Transaction",
    2: "Check or Installment",
    3: "Trade",
    4: "Gift or Inheritance",
    5: "Foreclosure",
    6: "Other",
}

# Type of Interest codes (2016+)
TYPE_OF_INTEREST = {
    1: "Fee Interest (Whole)",
    2: "Fee Interest (Partial)",
    3: "Life Estate",
    4: "Trust Beneficiary",
    5: "Purchase Contract",
    6: "Other/Long Term Lease",
}

# Citizenship codes
CITIZENSHIP = {
    1: "US",
    2: "Foreign",
    3: "Unknown",
    0: "Blank",
}

# ── Clean a single year's dataframe ───────────────────────────────────────
def clean_dataframe(df):
    # Strip whitespace from string columns
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].apply(lambda x: x.str.strip())

    # Flag national security countries
    df["Is_Security_Country"] = df["Country"].isin(SECURITY_COUNTRIES.keys())

    # Flag unknown/no investor entries
    df["Is_Unknown_Country"] = df["Country Code"].astype(str).isin(["999", "998"])

    # Map acquisition method
    if "Acquisition Method" in df.columns:
        df["Acquisition_Method_Label"] = df["Acquisition Method"].map(
            ACQUISITION_METHOD
        ).fillna("Unknown")

    # Map type of interest
    if "Type of Interest" in df.columns:
        df["Type_of_Interest_Label"] = df["Type of Interest"].map(
            TYPE_OF_INTEREST
        ).fillna("Unknown")

    # Map citizenship
    if "Citizenship" in df.columns:
        df["Citizenship_Label"] = df["Citizenship"].map(
            CITIZENSHIP
        ).fillna("Unknown")

    # Clean numeric columns
    numeric_cols = [
        "Number of Acres", "Purchase Price",
        "Estimated Value", "Current Value", "Debt"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df

# ── Generate enriched summary ──────────────────────────────────────────────
def generate_enriched_summary(df):
    print("\n=== ENRICHED ANALYSIS ===")

    # Security countries over time
    print("\n-- National Security Countries Acreage by Year --")
    security_df = df[df["Is_Security_Country"]]
    sec_by_year = security_df.groupby(
        ["ReportYear", "Country"]
    )["Number of Acres"].sum().reset_index()
    sec_by_year.columns = ["Year", "Country", "Total_Acres"]
    sec_by_year["Total_Acres"] = sec_by_year["Total_Acres"].round(2)
    print(sec_by_year.to_string(index=False))
    sec_by_year.to_csv(REPORTS_DIR / "security_countries_by_year.csv", index=False)

    # Acquisition method breakdown (2024)
    print("\n-- Acquisition Methods (2024) --")
    df_2024 = df[df["ReportYear"] == 2024]
    if "Acquisition_Method_Label" in df_2024.columns:
        acq = df_2024.groupby("Acquisition_Method_Label")["Number of Acres"].sum()
        acq = acq.sort_values(ascending=False).reset_index()
        acq.columns = ["Acquisition_Method", "Total_Acres"]
        acq["Total_Acres"] = acq["Total_Acres"].round(2)
        print(acq.to_string(index=False))
        acq.to_csv(REPORTS_DIR / "acquisition_methods_2024.csv", index=False)

    # Land use breakdown (2024)
    print("\n-- Land Use Breakdown (2024) --")
    land_use = {
        "Crop": df_2024["Crop"].sum(),
        "Pasture": df_2024["Pasture"].sum(),
        "Forest": df_2024["Forest"].sum(),
        "Other Agriculture": df_2024["Other Agriculture"].sum(),
        "Non-Agriculture": df_2024["Non-Agriculture"].sum(),
    }
    land_use_df = pd.DataFrame(
        list(land_use.items()), columns=["Land_Use", "Total_Acres"]
    )
    land_use_df["Total_Acres"] = land_use_df["Total_Acres"].round(2)
    land_use_df["Percentage"] = (
        land_use_df["Total_Acres"] / land_use_df["Total_Acres"].sum() * 100
    ).round(2)
    print(land_use_df.to_string(index=False))
    land_use_df.to_csv(REPORTS_DIR / "land_use_2024.csv", index=False)

    # Top owners by country and state (2024)
    print("\n-- Foreign Ownership by Country and State (2024) --")
    country_state = df_2024.groupby(
        ["Country", "State"]
    )["Number of Acres"].sum().reset_index()
    country_state = country_state.sort_values(
        "Number of Acres", ascending=False
    ).head(30)
    country_state.columns = ["Country", "State", "Total_Acres"]
    country_state["Total_Acres"] = country_state["Total_Acres"].round(2)
    print(country_state.to_string(index=False))
    country_state.to_csv(
        REPORTS_DIR / "country_state_breakdown_2024.csv", index=False
    )

    return sec_by_year, land_use_df

# ── Main ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Loading all AFIDA holdings data...")
    frames = []
    for year in range(2010, 2025):
        file = OUTPUT_DIR / f"afida_current_holdings_yr{year}_clean.csv"
        if file.exists():
            print(f"  Loading {year}...")
            df = pd.read_csv(file, low_memory=False)
            df = clean_dataframe(df)
            frames.append(df)

    combined = pd.concat(frames, ignore_index=True)
    print(f"\nTotal records loaded: {len(combined):,}")

    generate_enriched_summary(combined)
    print("\n✅ Enriched analysis complete! Results saved to:", REPORTS_DIR)
