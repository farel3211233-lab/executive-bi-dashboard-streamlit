from __future__ import annotations

import base64
import csv
import gzip
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_CSV = Path(r"D:\MataKuliah\makul semester 5\business intelegensi\latihan1.csv")
COLUMNS = [
    "Student_ID", "Gender", "Age", "Study_Hours", "Sleep_Hours",
    "Attendance", "Exam_Score", "Monthly_Spending", "Screen_Hours",
    "Satisfaction",
]


def main() -> None:
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV
    destination = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "student_data.js"
    if not source.is_file():
        raise SystemExit(f"CSV not found: {source}")

    csv_bytes = source.read_bytes()
    with source.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        missing = [column for column in COLUMNS if column not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit("Required columns missing: " + ", ".join(missing))
        row_count = sum(1 for _ in reader)

    compressed = gzip.compress(csv_bytes, compresslevel=9, mtime=0)
    encoded = base64.b64encode(compressed).decode("ascii")
    js = f'window.STUDENT_DATA_GZIP_B64 = "{encoded}";\n'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(js, encoding="utf-8")
    print(f"Converted {row_count} rows to {destination}")
    print(f"CSV: {len(csv_bytes):,} bytes; JS gzip: {destination.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
