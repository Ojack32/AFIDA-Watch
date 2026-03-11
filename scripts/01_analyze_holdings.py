"""
AFIDA Watch - Script 01
Analyzes all AFIDA holdings CSV files (2010-2024)
Generates summary statistics for report generation
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
OUTPUT_DIR = Path("/home/afida/apps/AFIDA-Watch/output")
REPORTS_DIR = Path("/home/afida/apps/AFIDA-Watch/reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# ── Load all CSV files ─────────────────────────────────────────────────────
def load_all_years():
    print("Loading all AFIDA holdings data...")
    frames = []
    for year in range(2010, 2025):
        file = OUTPUT_DIR / f"afida_current_holdings_yr{year}_clean.csv"
        if file.exists():
            print(f"  Loading {year}...")
            df = pd.read_csv(file, low_memory=False)
            frames.append(df)
        else:
            print(f"  WARNING: {year} file not found!")
    combined = pd.concat(frames, ignore_index=True)
    print(f"\nTotal records loaded: {len(combined):,}")
    return combined

# ── Summary Statistics ─────────────────────────────────────────────────────
def generate_summary(df):
    print("\n=== SUMMARY STATISTICS ===")

    # Total acres by year
    print("\n-- Total Acres by Year --")
    acres_by_year = df.groupby("ReportYear")["Number of Acres"].sum().reset_index()
    acres_by_year.columns = ["Year", "Total_Acres"]
    acres_by_year["Total_Acres"] = acres_by_year["Total_Acres"].round(2)
    print(acres_by_year.to_string(index=False))
    acres_by_year.to_csv(REPORTS_DIR / "summary_acres_by_year.csv", index=False)

    # Total acres by country (2024 only)
    print("\n-- Top 20 Countries by Acres (2024) --")
    df_2024 = df[df["ReportYear"] == 2024]
    by_country = df_2024.groupby("Country")["Number of Acres"].sum()
    by_country = by_country.sort_values(ascending=False).head(20).reset_index()
    by_country.columns = ["Country", "Total_Acres"]
    by_country["Total_Acres"] = by_country["Total_Acres"].round(2)
    print(by_country.to_string(index=False))
    by_country.to_csv(REPORTS_DIR / "summary_top_countries_2024.csv", index=False)

    # Total acres by state (2024 only)
    print("\n-- Top 20 States by Foreign Owned Acres (2024) --")
    by_state = df_2024.groupby("State")["Number of Acres"].sum()
    by_state = by_state.sort_values(ascending=False).head(20).reset_index()
    by_state.columns = ["State", "Total_Acres"]
    by_state["Total_Acres"] = by_state["Total_Acres"].round(2)
    print(by_state.to_string(index=False))
    by_state.to_csv(REPORTS_DIR / "summary_top_states_2024.csv", index=False)

    # Land values
    print("\n-- Total Estimated Land Value by Year --")
    value_by_year = df.groupby("ReportYear")["Estimated Value"].sum().reset_index()
    value_by_year.columns = ["Year", "Total_Estimated_Value"]
    value_by_year["Total_Estimated_Value"] = value_by_year["Total_Estimated_Value"].round(2)
    print(value_by_year.to_string(index=False))
    value_by_year.to_csv(REPORTS_DIR / "summary_values_by_year.csv", index=False)

    # Foreign interest countries (China, Russia, Iran, North Korea)
    print("\n-- National Security: Foreign Interest Holdings (2024) --")
    security_countries = ["CHINA", "RUSSIA", "IRAN", "NORTH KOREA"]
    security = df_2024[df_2024["Country"].str.upper().isin(security_countries)]
    sec_summary = security.groupby("Country")["Number of Acres"].sum().reset_index()
    sec_summary.columns = ["Country", "Total_Acres"]
    print(sec_summary.to_string(index=False))
    sec_summary.to_csv(REPORTS_DIR / "summary_security_countries_2024.csv", index=False)

    return acres_by_year, by_country, by_state, value_by_year

# ── Main ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    df = load_all_years()
    generate_summary(df)
    print("\n✅ Analysis complete! Results saved to:", REPORTS_DIR)
