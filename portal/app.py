from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import folium
import os
import io
from config import BASE_DIR, DATA_FILE, AUDIT_STAMP, SECRET_KEY

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

print("Loading AFIDA data...")
df = pd.read_csv(DATA_FILE, low_memory=False)
print(f"Loaded {len(df)} records")

county_stats = df.groupby(['State', 'County']).agg({
    'RISK_TIER': lambda x: (x.isin(['CRITICAL', 'HIGH'])).sum(),
    'RISK_SCORE': 'count'
}).reset_index()
county_stats.columns = ['State', 'County', 'CRITICAL_HIGH_count', 'Total']
county_stats['Risk_Rate'] = (county_stats['CRITICAL_HIGH_count'] / county_stats['Total'] * 100).round(1)

@app.route('/')
def home():
    metrics = {
        'total_records': len(df),
        'critical': len(df[df['RISK_TIER'] == 'CRITICAL']),
        'high': len(df[df['RISK_TIER'] == 'HIGH']),
        'medium': len(df[df['RISK_TIER'] == 'MEDIUM']),
        'low': len(df[df['RISK_TIER'] == 'LOW'])
    }
    return render_template('home.html', metrics=metrics, audit=AUDIT_STAMP)

@app.route('/map')
def map_view():
    m = folium.Map(location=[39.8283, -98.5795], zoom_start=4, tiles='OpenStreetMap')
    return render_template('map.html', audit=AUDIT_STAMP)

@app.route('/methods')
def methods():
    return render_template('methods.html', audit=AUDIT_STAMP)

@app.route('/deliverables')
def deliverables():
    return render_template('deliverables.html', audit=AUDIT_STAMP)

@app.route('/pricing')
def pricing():
    return render_template('pricing.html', audit=AUDIT_STAMP)

@app.route('/parcel-verification')
def parcel_verification():
    return render_template('parcel_verification.html', audit=AUDIT_STAMP)

@app.route('/contact')
def contact():
    return render_template('contact.html', audit=AUDIT_STAMP)

@app.route('/download-feed')
def download_feed():
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    return send_file(io.BytesIO(csv_buffer.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='afida_flagged_2024_v2.csv')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
