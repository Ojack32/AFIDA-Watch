import pandas as pd
import os

BASE_DIR = '/home/afida/apps/AFIDA-Watch'
INPUT_FILE = os.path.join(BASE_DIR, 'output', 'afida_current_holdings_yr2024_clean.csv')
OUTPUT_FILE = os.path.join(BASE_DIR, 'output', 'afida_flagged_2024.csv')

print("Loading data...")
df = pd.read_csv(INPUT_FILE, low_memory=False)
print(f"Loaded {len(df)} records")

adversary_codes = [156, 364, 643, 408]
df['FLAG_adversary_nation'] = df['Country Code'].isin(adversary_codes).astype(int)
df['FLAG_ambiguity'] = df['Country Code'].isin([998, 999]).astype(int)
df['FLAG_foreign_owner'] = (df['US Code'] == 0).astype(int)
df['FLAG_foreign_citizenship'] = (df['Citizenship'] == 2).astype(int)
df['FLAG_trust_beneficiary'] = (df['Type of Interest'] == 4).astype(int)
df['FLAG_leasehold'] = (df['Type of Interest'] == 6).astype(int)
df['FLAG_secondary_china'] = pd.to_numeric(df['Secondary Interest in China'], errors='coerce').fillna(0).astype(int)
df['FLAG_secondary_iran'] = pd.to_numeric(df['Secondary Interest in Iran'], errors='coerce').fillna(0).astype(int)
df['FLAG_secondary_russia'] = pd.to_numeric(df['Secondary Interest in Russia'], errors='coerce').fillna(0).astype(int)
df['FLAG_secondary_nkorea'] = pd.to_numeric(df['Secondary Interest in North Korea'], errors='coerce').fillna(0).astype(int)

df['RISK_SCORE'] = (
    (df['FLAG_adversary_nation'] * 3) +
    (df['FLAG_secondary_china'] * 3) +
    (df['FLAG_secondary_iran'] * 3) +
    (df['FLAG_secondary_russia'] * 3) +
    (df['FLAG_secondary_nkorea'] * 3) +
    (df['FLAG_ambiguity'] * 2) +
    (df['FLAG_trust_beneficiary'] * 2) +
    (df['FLAG_leasehold'] * 2) +
    (df['FLAG_foreign_owner'] * 1) +
    (df['FLAG_foreign_citizenship'] * 1)
)

def risk_tier(score):
    if score >= 6:
        return 'CRITICAL'
    elif score >= 4:
        return 'HIGH'
    elif score >= 2:
        return 'MEDIUM'
    elif score >= 1:
        return 'LOW'
    else:
        return 'NONE'

df['RISK_TIER'] = df['RISK_SCORE'].apply(risk_tier)

def agency_routing(row):
    routes = []
    if row['FLAG_adversary_nation'] or row['FLAG_secondary_china'] or row['FLAG_secondary_iran'] or row['FLAG_secondary_russia'] or row['FLAG_secondary_nkorea']:
        routes.append('OFAC')
        routes.append('DOD')
        routes.append('CFIUS')
    if row['FLAG_ambiguity']:
        routes.append('OFAC')
        routes.append('CFIUS')
    if row['FLAG_trust_beneficiary'] or row['FLAG_leasehold']:
        routes.append('CFIUS')
        routes.append('OFAC')
    if not routes:
        routes.append('USDA-ONLY')
    return ' | '.join(sorted(set(routes)))

df['AGENCY_ROUTING'] = df.apply(agency_routing, axis=1)

flagged_df = df[df['RISK_SCORE'] > 0].copy()
flagged_df = flagged_df.sort_values('RISK_SCORE', ascending=False)

print(f"\nTotal records: {len(df)}")
print(f"Flagged records: {len(flagged_df)}")
print(f"CRITICAL: {len(flagged_df[flagged_df['RISK_TIER'] == 'CRITICAL'])}")
print(f"HIGH: {len(flagged_df[flagged_df['RISK_TIER'] == 'HIGH'])}")
print(f"MEDIUM: {len(flagged_df[flagged_df['RISK_TIER'] == 'MEDIUM'])}")
print(f"LOW: {len(flagged_df[flagged_df['RISK_TIER'] == 'LOW'])}")
print(f"Adversary nation: {df['FLAG_adversary_nation'].sum()}")
print(f"Ambiguity 998/999: {df['FLAG_ambiguity'].sum()}")
print(f"Trust beneficiary: {df['FLAG_trust_beneficiary'].sum()}")
print(f"Leasehold: {df['FLAG_leasehold'].sum()}")
print(f"Agency routing breakdown:")
print(flagged_df['AGENCY_ROUTING'].value_counts())

flagged_df.to_csv(OUTPUT_FILE, index=False)
print(f"\nExported to: {OUTPUT_FILE}")
