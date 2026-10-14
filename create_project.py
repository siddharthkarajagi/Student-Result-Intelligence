from pathlib import Path

folders = [
    "core", "data/raw", "data/processed",
    "reports", "assets", "tests"
]

for folder in folders:
    Path(folder).mkdir(parents=True, exist_ok=True)

Path("requirements.txt").write_text(
    "streamlit\npandas\nnumpy\nplotly\nopenpyxl\npython-docx\npypdf\npdfplumber\nreportlab\nxlsxwriter\n",
    encoding="utf-8"
)

Path(".gitignore").write_text(
    ".venv/\n__pycache__/\n*.pyc\n",
    encoding="utf-8"
)

print("SUCCESS: Project folders created!")
