from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

REPORTS_DIR = Path("/home/afida/apps/AFIDA-Watch/reports")
CHARTS_DIR = Path("/home/afida/apps/AFIDA-Watch/reports/charts")
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

NAVY, GOLD, WHITE, LIGHT, RED, GREEN = "#0A2342", "#C9A84C", "#FFFFFF", "#E8EEF4", "#C0392B", "#1A6B3C"

plt.rcParams.update({"font.family": "DejaVu Serif", "figure.facecolor": WHITE, "axes.facecolor": LIGHT})

def save_fig(name):
    plt.savefig(CHARTS_DIR / name, dpi=150, bbox_inches="tight", facecolor=WHITE)
    plt.close()
    print(f"  ✅ {name}")

def chart_1():
    print("\n📊 Chart 1: Total Acres by Year...")
    df = pd.read_csv(REPORTS_DIR / "summary_acres_by_year.csv")
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df["Year"], df["Total_Acres"] / 1e6, color=NAVY, linewidth=2.5, marker="o", markersize=6)
    ax.fill_between(df["Year"], df["Total_Acres"] / 1e6, alpha=0.3, color=NAVY)
    ax.set_title("Total Foreign-Owned US Agricultural Land (2010–2024)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Million Acres")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    save_fig("01_total_acres_by_year.png")

def chart_2():
    print("\n📊 Chart 2: Top Countries (2024)...")
    df = pd.read_csv(REPORTS_DIR / "summary_top_countries_2024.csv")
    df = df[~df["Country"].str.startswith("99")].head(15)
    fig, ax = plt.subplots(figsize=(12, 7))
    colors = [GOLD if i == 0 else NAVY for i in range(len(df))]
    ax.barh(df["Country"], df["Total_Acres"] / 1e6, color=colors, edgecolor=WHITE)
    ax.set_title("Top 15 Foreign Countries by US Land Ownership (2024)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Million Acres")
    ax.invert_yaxis()
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    fig.tight_layout()
    save_fig("02_top_countries_2024.png")

def chart_3():
    print("\n📊 Chart 3: Top States (2024)...")
    df = pd.read_csv(REPORTS_DIR / "summary_top_states_2024.csv").head(15)
    fig, ax = plt.subplots(figsize=(12, 7))
    colors = [GOLD if i == 0 else NAVY for i in range(len(df))]
    ax.barh(df["State"], df["Total_Acres"] / 1e6, color=colors, edgecolor=WHITE)
    ax.set_title("Top 15 US States by Foreign Land Ownership (2024)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Million Acres")
    ax.invert_yaxis()
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    fig.tight_layout()
    save_fig("03_top_states_2024.png")

def chart_4():
    print("\n📊 Chart 4: Security Countries Timeline...")
    df = pd.read_csv(REPORTS_DIR / "security_countries_by_year.csv")
    fig, ax = plt.subplots(figsize=(12, 6))
    for country in df["Country"].unique():
        subset = df[df["Country"] == country]
        ax.plot(subset["Year"], subset["Total_Acres"] / 1e6, marker="o", linewidth=2, label=country)
    ax.set_title("Security-Concern Countries: US Land Ownership Over Time", fontsize=14, fontweight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Million Acres")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    save_fig("04_security_countries_timeline.png")

if __name__ == "__main__":
    chart_1()
    chart_2()
    chart_3()
    chart_4()
