# Round 1A – Structured Outline Extractor

## 📜 Problem Overview

Your task was to extract a structured outline from any input PDF. The system must return:
- Title
- All headings (H1, H2, H3)
- Their respective page numbers

The outline should be clean, hierarchical, and compatible with JSON.

## 🧠 Approach

The system processes each PDF in `/app/input` using the `parse_pdf()` function (defined in `utils/pdf_parser.py`), which:
- Uses heuristics based on font size, boldness, and layout
- Detects hierarchical headers (e.g., sections, subsections)
- Assigns heading levels like H1, H2, H3

We avoid brittle logic (like hardcoding text patterns), instead relying on positional cues and consistent formatting across pages.

## 🔧 Project Structure

Adobe-Hackathon-Round-1A/
├── Dockerfile
├── requirements.txt
├── main.py
├── utils/
│ └── __init__.py
│ └── outline_extractor.py
│ └── pdf_parser.py
├── input/
│ └── file01.pdf
│ └── file02.pdf
├── output/
│ └── file01.json
│ └── file02.json


## 🚀 How to Run (as per challenge instructions)

```bash
docker build --platform linux/amd64 -t outline-extractor .
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  outline-extractor
