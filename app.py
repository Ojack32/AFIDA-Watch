from pathlib import Path
from flask import Flask, render_template, send_from_directory, abort

app = Flask(__name__)

OUTPUT_DIR = Path("/home/afida/apps/AFIDA-Watch/output")

def is_safe_filename(name: str) -> bool:
    if not name or '/' in name or '\0' in name or name.startswith('.'):
        return False
    return True

@app.get("/")
def home():
    return render_template("home.html")

@app.get("/reports")
def reports():
    files = []
    if OUTPUT_DIR.exists():
        files = sorted(
            p.name for p in OUTPUT_DIR.iterdir()
            if p.is_file() and p.suffix.lower() == ".csv"
        )
    return render_template("reports.html", files=files)

@app.get("/download/<path:filename>")
def download(filename):
    if not is_safe_filename(filename):
        abort(404)
    file_path = OUTPUT_DIR / filename
    if not file_path.exists() or not file_path.is_file():
        abort(404)
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)
