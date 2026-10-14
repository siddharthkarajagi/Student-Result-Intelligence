import pdfplumber, glob, os, re, csv

pattern = os.path.expandvars(r"%USERPROFILE%\Downloads\11263 - 4th Sem*.pdf")
files = glob.glob(pattern)

if not files:
    raise SystemExit("PDF NOT FOUND in Downloads")

pdf_path = files[0]
subjects = [
    "BTAIC401", "BTAIC402", "BTAIL406", "BTAIPE405D",
    "BTAIS407", "BTBS404", "BTHM403", "BTUHV34"
]
subject_x = [131, 212, 294, 375, 457, 538, 620, 701]

def group_rows(words):
    rows = []
    for word in sorted(words, key=lambda w: w["top"]):
        match = next(
            (r for r in rows if abs(r["y"] - word["top"]) <= 2.5),
            None
        )
        if match is None:
            rows.append({"y": word["top"], "words": [word]})
        else:
            match["words"].append(word)
    for row in rows:
        row["words"].sort(key=lambda w: w["x0"])
    return rows

def row_near(rows, target_y, tolerance=4):
    options = [r for r in rows if abs(r["y"] - target_y) <= tolerance]
    return min(options, key=lambda r: abs(r["y"] - target_y)) if options else None

def words_text(row):
    return " ".join(w["text"] for w in row["words"]) if row else ""

def subject_values(row):
    values = [""] * len(subjects)
    if row:
        for w in row["words"]:
            for i, x in enumerate(subject_x):
                if x - 18 <= w["x0"] < x + 45 and re.fullmatch(r"\d{1,3}", w["text"]):
                    values[i] = w["text"]
                    break
    return values

records = []

with pdfplumber.open(pdf_path) as pdf:
    for page_no, page in enumerate(pdf.pages, start=1):
        rows = group_rows(page.extract_words())
        for header in rows:
            seat_word = next(
                (w for w in header["words"]
                 if w["x0"] < 100 and re.fullmatch(r"\d{10,16}", w["text"])),
                None
            )
            if not seat_word:
                continue

            y = header["y"]
            header_words = header["words"]
            name_words = [
                w["text"] for w in header_words
                if 100 <= w["x0"] < 260 and w["text"] != seat_word["text"]
            ]
            result_word = next(
                (w["text"] for w in header_words if w["x0"] > 1500),
                ""
            )

            total_row = row_near(rows, y + 66)
            sgpa_row = row_near(rows, y + 15)
            total_marks_row = row_near(rows, y + 42)

            record = {
                "seat_no": seat_word["text"],
                "student_name": " ".join(name_words),
                "result": result_word,
                "sgpa": "",
                "total_marks": "",
                "source_page": page_no,
            }

            if sgpa_row:
                record["sgpa"] = next(
                    (w["text"] for w in sgpa_row["words"]
                     if 1350 < w["x0"] < 1450 and re.fullmatch(r"\d+(?:\.\d+)?", w["text"])),
                    ""
                )

            if total_marks_row:
                record["total_marks"] = next(
                    (w["text"] for w in total_marks_row["words"]
                     if w["x0"] > 1500 and re.fullmatch(r"\d+(?:\.\d+)?", w["text"])),
                    ""
                )

            totals = subject_values(total_row)
            for subject, value in zip(subjects, totals):
                record[subject + "_total"] = value

            records.append(record)

if not records:
    raise SystemExit("No student records detected. Do not use this output yet.")

out_path = os.path.join(os.path.dirname(pdf_path), "student_result_parser_test.csv")
with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=records[0].keys())
    writer.writeheader()
    writer.writerows(records)

print("PDF:", os.path.basename(pdf_path))
print("Student records detected:", len(records))
print("Test CSV created:", out_path)
print("\nFirst 3 parsed records:")
for record in records[:3]:
    print(record)
