import pandas as pd
from pathlib import Path

source = Path.home() / "Downloads" / "student_result_parser_test.csv"
output = Path.home() / "Downloads" / "student_results_clean.csv"

if not source.exists():
    raise SystemExit("Parser CSV not found. Run pdf_parser_test.py first.")

df = pd.read_csv(source, dtype={"seat_no": str})

# Remove the institute code accidentally appended to student names.
df["student_name"] = (
    df["student_name"].fillna("").str.replace(r"\s+06756$", "", regex=True).str.strip()
)

# Convert marks and SGPA to numeric values for analysis.
numeric_cols = [
    c for c in df.columns
    if c.endswith("_total") or c in ["sgpa", "total_marks"]
]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

print("Student records:", len(df))
print("Duplicate seat numbers:", df["seat_no"].duplicated().sum())
print("Missing names:", df["student_name"].eq("").sum())
print("Missing SGPA:", df["sgpa"].isna().sum())
print("\nPreview:")
print(df[["seat_no", "student_name", "total_marks", "sgpa", "result"]].head(5).to_string(index=False))

df.to_csv(output, index=False, encoding="utf-8-sig")
print("\nClean CSV saved to:", output)
