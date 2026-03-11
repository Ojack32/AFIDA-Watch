import csv
import math
import sys
from collections import Counter
sys.path.insert(0, "/home/afida/apps/AFIDA-Watch/scripts")
from military_bases import MILITARY_BASES
INPUT_CSV = "/home/afida/apps/AFIDA-Watch/reports/unattributed_998_999_2023.csv"
OUTPUT_CSV = "/home/afida/apps/AFIDA-Watch/reports/security_proximity_alerts_2023.csv"
THRESHOLD = 50
def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))
alerts = []
with open(INPUT_CSV) as f:
    for row in csv.DictReader(f):
        lat = float(row["Lat"])
        lng = float(row["lng"])
        acres = float(row["Number of Acres"] or 0)
        closest = None
        closest_dist = 9999
        for blat, blng, bname, btype in MILITARY_BASES:
            dist = haversine(lat, lng, blat, blng)
            if dist <= THRESHOLD and dist < closest_dist:
                closest_dist = dist
                closest = (bname, btype)
        if closest:
            alerts.append({"Owner": row["Owner Name 1/"], "State": row["State"], "County": row["County"], "Country_Code": row["Country"], "Acres": round(acres, 2), "Acq_Year": row["Acquisition Year"], "Lat": lat, "Lng": lng, "Miles_Away": round(closest_dist, 1), "Nearest_Base": closest, "Base_Type": closest, "China_Flag": row["Secondary Interest in China"], "Iran_Flag": row["Secondary Interest in Iran"], "Russia_Flag": row["Secondary Interest in Russia"], "NK_Flag": row["Secondary Intereset in North Korea"]})
alerts.sort(key=lambda x: x["Miles_Away"])
fields = ["Owner","State","County","Country_Code","Acres","Acq_Year","Lat","Lng","Miles_Away","Nearest_Base","Base_Type","China_Flag","Iran_Flag","Russia_Flag","NK_Flag"]
with open(OUTPUT_CSV, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(alerts)
print("SECURITY PROXIMITY ALERTS SUMMARY")
print("=" * 55)
print("Total alerts: " + str(len(alerts)))
print("Total acres:  " + str(round(sum(a["Acres"] for a in alerts), 0)))
by_type = Counter(a["Base_Type"] for a in alerts)
print("Alerts by Base Type:")
for t, c in by_type.most_common():
    print("  " + str(t) + ": " + str(c))
print("Top 20 Closest:")
print("-" * 100)
for a in alerts[:20]:
    print("  " + str(a["Owner"]).ljust(45) + str(a["State"]).ljust(12) + str(int(a["Acres"])).rjust(8) + " acres  " + str(a["Miles_Away"]).rjust(5) + " mi  " + str(a["Nearest_Base"]))
print("Saved to " + OUTPUT_CSV)
