import folium
import pandas as pd
import json
df = pd.read_csv("/home/afida/apps/AFIDA-Watch/reports/security_proximity_alerts_2023_final.csv")
data_json = df.to_json(orient="records")
china = len(df[df["China_Flag"] == 1.0])
iran = len(df[df["Iran_Flag"] == 1.0])
russia = len(df[df["Russia_Flag"] == 1.0])
total_acres = int(df["Acres"].sum())
top_base = df["Nearest_Base"].value_counts().index
top_count = df["Nearest_Base"].value_counts().iloc
m = folium.Map(location=[39.8283, -98.5795], zoom_start=5, tiles="CartoDB positron")
def get_color(code):
    code = str(code)
    if "999" in code: return "orange"
    if "998" in code: return "gray"
    if "156" in code: return "red"
    if "364" in code: return "purple"
    if "643" in code: return "darkred"
    return "blue"
for idx, row in df.iterrows():
    color = get_color(row["Country_Code"])
    popup = "<div style=width:300px;font-family:Arial;font-size:12px;>"
    popup += "<b>" + str(row["Owner"]) + "</b><hr>"
    popup += "State: " + str(row["State"]) + "<br>"
    popup += "County: " + str(row["County"]) + "<br>"
    popup += "Country Code: " + str(row["Country_Code"]) + "<br>"
    popup += "Acres: " + str(row["Acres"]) + "<br>"
    popup += "Acquired: " + str(row["Acq_Year"]) + "<br>"
    popup += "Nearest Base: " + str(row["Nearest_Base"]) + "<br>"
    popup += "Distance: " + str(row["Miles_Away"]) + " miles<br>"
    popup += "China: " + str(row["China_Flag"]) + " | Iran: " + str(row["Iran_Flag"]) + " | Russia: " + str(row["Russia_Flag"]) + "<br>"
    folium.CircleMarker(
        location=[row["Lat"], row["Lng"]],
        radius=8, color=color, fill=True,
        fill_color=color, fill_opacity=0.7,
        popup=folium.Popup(popup, max_width=320),
        tooltip=str(row["Owner"]) + " | " + str(row["Miles_Away"]) + " mi"
    ).add_to(m)
from branca.element import MacroElement, Template
stats = str(len(df))
acres = str(int(df["Acres"].sum()))
top = str(df["Nearest_Base"].value_counts().index)
top_n = str(df["Nearest_Base"].value_counts().iloc)
china = str(len(df[df["China_Flag"] == 1.0]))
iran = str(len(df[df["Iran_Flag"] == 1.0]))
russia = str(len(df[df["Russia_Flag"] == 1.0]))
panel = MacroElement()
panel._template = Template("""
{% macro html(this, kwargs) %}
<style>
.cfius-stats{position:fixed!important;top:80px!important;right:20px!important;width:260px!important;background:white!important;border:3px solid #333!important;z-index:99999!important;padding:12px!important;border-radius:8px!important;font-family:Arial!important;font-size:12px!important;box-shadow:4px 4px 10px rgba(0,0,0,0.4)!important;}
.cfius-filter{position:fixed!important;top:80px!important;left:20px!important;width:220px!important;background:white!important;border:3px solid #333!important;z-index:99999!important;padding:12px!important;border-radius:8px!important;font-family:Arial!important;font-size:12px!important;box-shadow:4px 4px 10px rgba(0,0,0,0.4)!important;}
</style>
js = "<script>var allData=" + data_json + ";"
js += "function downloadCSV(){"
js += "var h=['Owner','State','County','Country_Code','Acres','Acq_Year','Nearest_Base','Miles_Away','China_Flag','Iran_Flag','Russia_Flag','NK_Flag'];"
js += "var csv=h.join(',')+'\n';"
js += "allData.forEach(function(r){csv+=[r.Owner,r.State,r.County,r.Country_Code,r.Acres,r.Acq_Year,r.Nearest_Base,r.Miles_Away,r.China_Flag,r.Iran_Flag,r.Russia_Flag,r.NK_Flag].join(',')+'\n';});"
js += "var b=new Blob([csv],{type:'text/csv'});"
js += "var a=document.createElement('a');"
js += "a.href=URL.createObjectURL(b);"
js += "a.download='CFIUS_AFIDA_Holdings.csv';"
js += "a.click();}"
js += "</script>"
m.get_root().html.add_child(folium.Element(js))
m.save("/home/afida/apps/AFIDA-Watch/reports/CFIUS_DASHBOARD_V4.html")
print("CFIUS Dashboard V4 complete!")
print("Access: http://76.13.58.40:8080/CFIUS_DASHBOARD_V4.html")
