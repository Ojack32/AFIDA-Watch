import folium
import pandas as pd

# Load data
df = pd.read_csv('/home/afida/apps/AFIDA-Watch/reports/security_proximity_alerts_2023_final.csv')

# Create map centered on US
m = folium.Map(location=[39.8283, -98.5795], zoom_start=5, tiles='CartoDB positron')

# Define color mapping for countries
def get_color(country_code):
    if country_code == '826':  # UK
        return 'blue'
    elif country_code == '998':  # No foreign investor
        return 'gray'
    elif country_code == '999':  # No predominant country
        return 'gray'
    else:
        return 'red'  # Default for other countries

# Add markers for holdings
for idx, row in df.iterrows():
    color = get_color(row['Country_Code'])
    folium.CircleMarker(
        location=[row['Lat'], row['Lng']],
        radius=8,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        popup=f"""
        <b>{row['Owner']}</b><br>
        {row['State']}, {row['County']}<br>
        {row['Acres']} acres<br>
        {row['Miles_Away']} miles from {row['Nearest_Base']}<br>
        Country: {row['Country_Code']}<br>
        China Flag: {row['China_Flag']}<br>
        Iran Flag: {row['Iran_Flag']}<br>
        Russia Flag: {row['Russia_Flag']}
        """,
        tooltip=row['Owner']
    ).add_to(m)

# Add military bases (you can expand this list)
military_bases = [
    {'name': 'Tinker AFB, OK', 'lat': 35.385, 'lng': -97.415, 'type': 'Air Force'},
    {'name': 'Maxwell AFB, AL', 'lat': 32.498, 'lng': -86.205, 'type': 'Air Force'},
    {'name': 'Fort Moore, GA', 'lat': 32.367, 'lng': -84.975, 'type': 'Army'},
]

for base in military_bases:
    folium.Marker(
        location=[base['lat'], base['lng']],
        icon=folium.Icon(color='black', icon='star', prefix='fa'),
        popup=f"<b>{base['name']}</b><br>{base['type']}",
        tooltip=base['name']
    ).add_to(m)

# Save map
m.save('/home/afida/apps/AFIDA-Watch/reports/interactive_proximity_map.html')
print("✅ Interactive map saved to /home/afida/apps/AFIDA-Watch/reports/interactive_proximity_map.html")
