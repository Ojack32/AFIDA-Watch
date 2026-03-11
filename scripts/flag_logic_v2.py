import pandas as pd
import os

MODEL_VERSION = "AFIDA-Watch RiskScore v1.0"
MODEL_DATE = "2026-03-10"

EXPOSURE_FLAGS = ['FLAG_foreign_owner', 'FLAG_foreign_citizenship']
RISK_FLAGS = ['FLAG_adversary_nation', 'FLAG_secondary_any', 'FLAG_ambiguity', 'FLAG_trust_beneficiary', 'FLAG_leasehold']
HARD_FLAGS = ['FLAG_adversary_nation', 'FLAG_secondary_any']

WEIGHTS = {
    'FLAG_adversary_nation': 3,
    'FLAG_secondary_any': 3,
    'FLAG_ambiguity': 2,
    'FLAG_trust_beneficiary': 2,
    'FLAG_leasehold': 2,
    'FLAG_foreign_owner': 1,
    'FLAG_foreign_citizenship': 1
}

BASE_DIR = '/home/afida/apps/AFIDA-Watch'
INPUT_FILE = os.path.join(BASE_DIR, 'output', 'afida_current_holdings_yr2024_clean.csv')
OUTPUT_FILE = os.path.join(BASE_DIR, 'output', 'afida_flagged_2024_v2.csv')
SPEC_FILE = os.path.join(BASE_DIR, 'output', 'flag_coverage_table_v1.csv')
RECONCILE_FILE = os.path.join(BASE_DIR, 'output', 'country_code_reconciliation.csv')

print(f"Model: {MODEL_VERSION}")
print("Loading data...")
df = pd.read_csv(INPUT_FILE, low_memory=False)
print(f"Loaded {len(df)} records")

df['Country Code'] = pd.to_numeric(df['Country Code'], errors='coerce')
df['US Code'] = pd.to_numeric(df['US Code'], errors='coerce')
df['Citizenship'] = pd.to_numeric(df['Citizenship'], errors='coerce')
df['Type of Interest'] = pd.to_numeric(df['Type of Interest'], errors='coerce')

adversary_codes = [156, 364, 643, 408]
df['FLAG_adversary_nation'] = df['Country Code'].isin(adversary_codes).astype(int)

adversary_strings = ['CHINA', 'IRAN', 'RUSSIA', 'NORTH KOREA']
df['_country_upper'] = df['Country'].astype(str).str.upper().str.strip()
string_match = df['_country_upper'].isin(adversary_strings)
code_match = df['Country Code'].isin(adversary_codes)
discrepancy = df[string_match != code_match] [['Owner Id', 'Parcel Id', 'State', 'County', 'Country', 'Country Code', 'Principal Place of Business']].copy()
discrepancy['DISCREPANCY_TYPE'] = 'string_code_mismatch'
discrepancy.to_csv(RECONCILE_FILE, index=False)
print(f"Reconciliation: {len(discrepancy)} discrepant records")

df['FLAG_ambiguity'] = df['Country Code'].isin([998, 999]).astype(int)
df['FLAG_foreign_owner'] = (df['US Code'] == 0).astype(int)
df['FLAG_foreign_citizenship'] = (df['Citizenship'] == 2).astype(int)
df['FLAG_trust_beneficiary'] = (df['Type of Interest'] == 4).astype(int)
df['FLAG_leasehold'] = (df['Type of Interest'] == 6).astype(int)

for col in ['Secondary Interest in China', 'Secondary Interest in Iran', 'Secondary Interest in Russia', 'Secondary Interest in North Korea']:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

df['FLAG_secondary_any'] = (
    (df['Secondary Interest in China'] == 1) |
    (df['Secondary Interest in Iran'] == 1) |
    (df['Secondary Interest in Russia'] == 1) |
    (df['Secondary Interest in North Korea'] == 1)
).astype(int)

all_flags = list(WEIGHTS.keys())
df['RISK_SCORE'] = sum(df[f] * w for f, w in WEIGHTS.items())

def risk_tier(row):
    score = row['RISK_SCORE']
    has_hard_flag = any(row[f] == 1 for f in HARD_FLAGS)
    if score >= 6 and has_hard_flag:
        return 'CRITICAL'
    elif score >= 4:
        return 'HIGH'
    elif score >= 2:
        return 'MEDIUM'
    elif score >= 1:
        return 'LOW'
    else:
        return 'NONE'

df['RISK_TIER'] = df.apply(risk_tier, axis=1)

def reason_codes(row):
    active = []
    for f in all_flags:
        if row[f] == 1:
            active.append(f)
    return ' | '.join(active) if active else 'NONE'

df['REASON_CODES'] = df.apply(reason_codes, axis=1)

def agency_routing(row):
    routes = []
    if row['FLAG_adversary_nation'] or row['FLAG_secondary_any']:
        routes.extend(['OFAC', 'DOD', 'CFIUS'])
    if row['FLAG_ambiguity']:
        routes.extend(['OFAC', 'CFIUS'])
    if row['FLAG_trust_beneficiary'] or row['FLAG_leasehold']:
        routes.extend(['CFIUS', 'OFAC'])
    if not routes:
        routes.append('USDA-ONLY')
    return ' | '.join(sorted(set(routes)))

df['AGENCY_ROUTING'] = df.apply(agency_routing, axis=1)
df['MODEL_VERSION'] = MODEL_VERSION
df['MODEL_DATE'] = MODEL_DATE

coverage = pd.DataFrame({
    'Flag': all_flags,
    'Class': ['Risk' if f in RISK_FLAGS else 'Exposure' for f in all_flags],
    'Count': [df[f].sum() for f in all_flags],
    'Pct_of_Total': [(df[f].sum() / len(df) * 100).round(2) for f in all_flags],
    'Weight': [WEIGHTS[f] for f in all_flags],
    'Rationale': [
        'Direct adversary nation ownership by country code',
        'Secondary interest in adversary nation field',
        'Ambiguous country code requiring enhanced diligence',
        'Trust beneficiary proxy ownership indicator',
        'Long-term leasehold indirect control indicator',
        'Foreign owner under AFIDA reporting logic',
        'Non-US citizenship indicator'
    ]
})
coverage.to_csv(SPEC_FILE, index=False)

flagged_df = df[df['RISK_SCORE'] > 0].copy()
flagged_df = flagged_df.sort_values('RISK_SCORE', ascending=False)

print(f"\n── {MODEL_VERSION} ──────────────────────────────")
print(f"Total records:        {len(df)}")
print(f"Any Exposure flag:    {df[EXPOSURE_FLAGS].any(axis=1).sum()} ({(df[EXPOSURE_FLAGS].any(axis=1).sum()/len(df)*100).round(1)}%)")
print(f"Any Risk flag:        {df[RISK_FLAGS].any(axis=1).sum()} ({(df[RISK_FLAGS].any(axis=1).sum()/len(df)*100).round(1)}%)")
print(f"Any flag combined:    {len(flagged_df)} ({round(len(flagged_df)/len(df)*100, 1)}%)")
print(f"\nCRITICAL:             {len(flagged_df[flagged_df['RISK_TIER'] == 'CRITICAL'])}")
print(f"HIGH:                 {len(flagged_df[flagged_df['RISK_TIER'] == 'HIGH'])}")
print(f"MEDIUM:               {len(flagged_df[flagged_df['RISK_TIER'] == 'MEDIUM'])}")
print(f"LOW:                  {len(flagged_df[flagged_df['RISK_TIER'] == 'LOW'])}")
print(f"\nAdversary nation:     {df['FLAG_adversary_nation'].sum()}")
print(f"Ambiguity 998/999:    {df['FLAG_ambiguity'].sum()}")
print(f"Trust beneficiary:    {df['FLAG_trust_beneficiary'].sum()}")
print(f"Leasehold:            {df['FLAG_leasehold'].sum()}")
print(f"Secondary interest:   {df['FLAG_secondary_any'].sum()}")
print(f"\nFlag coverage table:  {SPEC_FILE}")
print(f"Reconciliation file:  {RECONCILE_FILE}")
print(f"Flagged export:       {OUTPUT_FILE}")

flagged_df.to_csv(OUTPUT_FILE, index=False)
print("Done.")
