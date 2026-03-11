from fpdf import FPDF
import pandas as pd
import matplotlib.pyplot as plt
import os

# Load data
df = pd.read_csv('/home/afida/apps/AFIDA-Watch/reports/security_proximity_alerts_2023_final.csv')

# Create PDF
pdf = FPDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)

# Set font
pdf.set_font("Arial", "B", 16)
pdf.cell(0, 10, "AFIDA-Watch: Foreign Land Holdings Near U.S. Military Bases", ln=True, align="C")

# Executive Summary
pdf.set_font("Arial", "B", 12)
pdf.cell(0, 10, "Executive Summary", ln=True)
pdf.set_font("Arial", "", 10)
pdf.multi_cell(0, 5, "302 unattributed foreign holdings within 50 miles of U.S. military bases. Tinker AFB, OK has 118 holdings nearby. Iran holdings dropped 87% from 2022 to 2024 (4324 to 547 acres).")

# Key Findings
pdf.set_font("Arial", "B", 12)
pdf.cell(0, 10, "Key Findings", ln=True)
pdf.set_font("Arial", "", 10)
pdf.multi_cell(0, 5, "302 holdings, 441787 acres\nTop bases: Tinker AFB (118), Maxwell AFB (36), Fort Moore (26)\nChina-flagged: STA Pharmaceutical USA near Aberdeen Proving Ground\nShell networks: Cayman Islands (701K acres), BVI (369K), Singapore (712K)")

# Charts
pdf.set_font("Arial", "B", 12)
pdf.cell(0, 10, "Charts", ln=True)

# Chart 1: Holdings by Base
base_counts = df['Nearest_Base'].value_counts().head(10)
plt.figure(figsize=(10, 6))
base_counts.plot(kind='bar')
plt.title("Top 10 Most Exposed Military Bases")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('/home/afida/apps/AFIDA-Watch/reports/base_chart.png')
plt.close()

# Add chart to PDF
pdf.image('/home/afida/apps/AFIDA-Watch/reports/base_chart.png', x=10, y=None, w=190)

# Chart 2: Holdings by Country Code
country_counts = df['Country_Code'].value_counts()
plt.figure(figsize=(8, 6))
country_counts.plot(kind='pie', autopct='%1.1f%%')
plt.title("Holdings by Country Code")
plt.tight_layout()
plt.savefig('/home/afida/apps/AFIDA-Watch/reports/country_chart.png')
plt.close()

# Add chart to PDF
pdf.image('/home/afida/apps/AFIDA-Watch/reports/country_chart.png', x=10, y=None, w=190)

# Recommendations
pdf.set_font("Arial", "B", 12)
pdf.cell(0, 10, "Recommendations", ln=True)
pdf.set_font("Arial", "", 10)
pdf.multi_cell(0, 5, "Policy: Close 998/999 loopholes\nIntelligence: Monitor Tinker AFB, Maxwell AFB\nMarket: Track agricultural REITs with foreign exposure")

# Save PDF
pdf.output('/home/afida/apps/AFIDA-Watch/reports/AFIDA-Watch_Security_Report_2026.pdf')
print("✅ PDF report saved to /home/afida/apps/AFIDA-Watch/reports/AFIDA-Watch_Security_Report_2026.pdf")
