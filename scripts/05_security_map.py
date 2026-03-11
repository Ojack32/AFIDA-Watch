import folium
import csv
import sys
sys.path.insert(0, "/home/afida/apps/AFIDA-Watch/scripts")
from military_bases import MILITARY_BASES

ALERTS = "/home/afida/apps/AFIDA-Watch/reports/security_proximity_alerts_2023_final.csv"
OUTPUT = "/home/afida/apps/AFIDA-Watch/reports/charts/security_map.html"

m = folium.Map(location=[38.5, -96.0], zoom_start=5, tiles="CartoDB positron")

base_group = folium.FeatureGroup(name="Military Installations")
for blat, blng, bname, btype in MILITARY_BASES:
    folium.Marker(
        location=[blat, blng],
        popup=folium.Popup(bname + " (" + btype + ")", max_width=200),
        icon=folium.Icon(color="blue", icon="star", prefix="fa"),
        tooltip=bname
    ).add_to(base_group)
    folium.Circle(
        location=[blat, blng],
        radius=80467,
        color="blue",
        fill=True,
        fill_opacity=0.05,
        weight=1
    ).add_to(base_group)
base_group.add_to(m)

alert_group = folium.FeatureGroup(name="Unattributed 998/999 Holdings")
china_group = folium.FeatureGroup(name="China Flagged Holdings")

def threat_context(row):
    flags = []
    if row["China_Flag"] == "1.0": flags.append("CHINA secondary interest")
    if row["Iran_Flag"] == "1.0": flags.append("IRAN secondary interest")
    if row["Russia_Flag"] == "1.0": flags.append("RUSSIA secondary interest")
    if row["NK_Flag"] == "1.0": flags.append("NORTH KOREA secondary interest")
    if "998" in row["Country_Code"]: flags.append("998: No foreign investor listed")
    if "999" in row["Country_Code"]: flags.append("999: No predominant country code")
    return flags

with open(ALERTS) as f:
    for row in csv.DictReader(f):
        lat = float(row["Lat"])
        lng = float(row["Lng"])
        acres = float(row["Acres"])
        china = row["China_Flag"] == "1.0"
        flags = threat_context(row)
        flag_html = "".join(["<br>⚠️ " + f for f in flags])
        popup_text = (
            "<b style=color:red>" + row["Owner"] + "</b><br>"
            + "<b>Location:</b> " + row["State"] + ", " + row["County"] + "<br>"
            + "<b>Acres:</b> " + str(acres) + "<br>"
            + "<b>Acquired:</b> " + row["Acq_Year"] + "<br>"
            + "<b>Reported Country:</b> " + row["Country_Code"] + "<br>"
            + "<b>Nearest Base:</b> " + row["Nearest_Base"] + "<br>"
            + "<b>Distance:</b> " + str(row["Miles_Away"]) + " miles<br>"
            + "<b>Base Type:</b> " + row["Base_Type"] + "<br>"
            + "<hr><b>Threat Indicators:</b>" + flag_html
        )
        if china:
            folium.CircleMarker(
                location=[lat, lng],
                radius=10,
                color="orange",
                fill=True,
                fill_color="orange",
                fill_opacity=0.9,
                popup=folium.Popup(popup_text, max_width=350),
                tooltip="CHINA FLAGGED: " + row["Owner"]
            ).add_to(china_group)
        else:
            folium.CircleMarker(
                location=[lat, lng],
                radius=max(4, min(int(acres/1000), 15)),
                color="red",
                fill=True,
                fill_color="red",
                fill_opacity=0.6,
                popup=folium.Popup(popup_text, max_width=350),
                tooltip=row["Owner"] + " | " + str(acres) + " acres"
            ).add_to(alert_group)

alert_group.add_to(m)
china_group.add_to(m)
folium.LayerControl().add_to(m)

# Add legend
legend_html = """
<div style="position:fixed; bottom:30px; left:30px; z-index:1000;
     background:white; padding:15px; border-radius:8px;
     border:2px solid #333; font-size:13px; font-family:Arial">
<b>AFIDA-Watch Security Map</b><br>
<b>Unattributed Foreign Land Near US Military</b><br><br>
<span style="color:blue">&#9733;</span> Military Installation (50mi radius)<br>
<span style="color:red">&#9679;</span> Unattributed 998/999 Holding<br>
<span style="color:orange">&#9679;</span> China Secondary Interest Flagged<br><br>
<i>Data: USDA AFIDA 2023 | 302 alerts | 441,787 acres</i>
</div>
"""
folium.Marker(
    location=[25.0, -120.0],
    icon=folium.DivIcon(html=legend_html)
).add_to(m)

m.save(OUTPUT)
print("Map saved to " + OUTPUT)
