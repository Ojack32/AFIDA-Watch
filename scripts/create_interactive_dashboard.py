import folium
import pandas as pd
from datetime import datetime

# Load data
df = pd.read_csv('/home/afida/apps/AFIDA-Watch/reports/security_proximity_alerts_2023_final.csv')

# Create map
m = folium.Map(location=[39.8283, -98.5795], zoom_start=5, tiles='CartoDB positron')

# Add title
title_html = '<div style="position: fixed; top: 10px; left: 50px; background-color: white; border:2px solid grey; z-index:9999; padding: 10px; border-radius: 5px;"><b>AFIDA-Watch: CFIUS Intelligence Dashboard</b><br><small>Real-Time Access to Foreign Holdings Near Military Bases</small><br><small style="color: green;">Updated: ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '</small></div>'
m.get_root().html.add_child(folium.Element(title_html))

# Add markers
for idx, row in df.iterrows():
    color = 'red' if '999' not in str(row['Country_Code']) else 'orange'
    popup_text = f"<b>{row['Owner']}</b><br>State: {row['State']}<br>Acres: {row['Acres']}<br>Distance: {row['Miles_Away']} mi<br>Base: {row['Nearest_Base']}"
    
    folium.CircleMarker(
        location=[row['Lat'], row['Lng']],
        radius=8,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        popup=popup_text,
        tooltip=row['Owner']
    ).add_to(m)

# Save
m.save('/home/afida/apps/AFIDA-Watch/reports/CFIUS_INTERACTIVE_DASHBOARD.html')
print('CFIUS Interactive Dashboard created!')
print('Access at: http://76.13.58.40:8080/CFIUS_INTERACTIVE_DASHBOARD.html')
