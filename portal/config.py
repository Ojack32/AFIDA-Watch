import os

BASE_DIR = '/home/afida/apps/AFIDA-Watch'
DATA_FILE = os.path.join(BASE_DIR, 'output', 'afida_flagged_2024_v2.csv')
AUDIT_STAMP = {
    'dataset': 'afida_current_holdings_yr2024_clean.csv',
    'md5': '021fdfc6456b6d51565fee8ba87c5bbf',
    'flag_spec_version': 'v1.0',
    'scoring_spec_version': 'v1.0',
    'run_date': '2026-03-10'
}
SECRET_KEY = 'afida-watch-portal-dev'
DEBUG = False
