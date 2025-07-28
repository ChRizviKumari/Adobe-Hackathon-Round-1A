import os
import json
from utils.pdf_parser import parse_pdf

INPUT_DIR = "/app/input"
OUTPUT_DIR = "/app/output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

for fname in os.listdir(INPUT_DIR):
    if fname.lower().endswith(".pdf"):
        in_path = os.path.join(INPUT_DIR, fname)
        print(f"Processing {in_path}")
        result = parse_pdf(in_path)
        out_json = os.path.splitext(fname)[0] + ".json"
        with open(os.path.join(OUTPUT_DIR, out_json), "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
