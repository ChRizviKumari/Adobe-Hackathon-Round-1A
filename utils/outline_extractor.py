from collections import Counter
import re

def extract_outline_and_title(doc):
    font_sizes = []
    text_spans = []

    # Extract all text spans from the PDF pages
    for i, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if b['type'] != 0:
                continue
            for line in b["lines"]:
                for span in line["spans"]:
                    text = span.get('text', '').strip()
                    if not text:
                        continue
                    font_sizes.append(span['size'])
                    text_spans.append({
                        "text": text,
                        "font_size": span['size'],
                        "bold": "Bold" in span['font'],
                        "font": span['font'],
                        "page": i + 1,
                    })

    # Return default if no text found
    if not font_sizes:
        return {
            "title": "Unknown Title",
            "outline": []
        }

    # Most common font size considered as body text size
    size_counts = Counter(font_sizes)
    body_size = size_counts.most_common(1)[0][0]

    # Unique font sizes sorted from largest to smallest
    font_sizes_sorted = sorted(set(font_sizes), reverse=True)

    # Headings are font sizes at least this ratio larger than body font size
    MIN_SIZE_RATIO = 1.15
    heading_sizes = [s for s in font_sizes_sorted if s >= body_size * MIN_SIZE_RATIO]

    # If no heading sizes found, fallback to largest font size
    if not heading_sizes:
        heading_sizes = [font_sizes_sorted[0]]

    # Map heading font sizes to levels: largest -> Title, then H1, H2
    levels = ["Title", "H1", "H2", "H3"]
    H_LEVELS = {}
    for idx, sz in enumerate(heading_sizes[:3]):
        H_LEVELS[sz] = levels[idx]

    # Other sizes mapped to Body
    for s in font_sizes_sorted:
        if s not in H_LEVELS:
            H_LEVELS[s] = "Body"

    # Keywords to exclude headings commonly found in tables/forms
    skip_keywords = {
        "s.no", "name", "age", "date", "signature", "amount", "rs", "pay", "designation",
        "service", "persons", "relationship", "declaration", "undertake", "application", "form",
        "date of entering", "home town",
        # Add more as needed
    }

    def is_meaningful_heading(text):
        text = text.strip()
        if len(text) < 5:
            return False
        # Exclude pure digits/spaces/punctuations (e.g., "1.", "2)", "...")
        if re.fullmatch(r'[\d\s\.\-\(\),:;]+', text):
            return False
        if any(keyword in text.lower() for keyword in skip_keywords):
            return False
        return True

    def is_date_like(text):
        date_pattern = re.compile(
            r'^\d{1,2}\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC|'
            r'JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\s+\d{4}$',
            re.IGNORECASE
        )
        return bool(date_pattern.match(text.strip()))

    def get_heading_level(text):
        text = text.strip()
        match = re.match(r'^(\d+(\.\d+)*)[.\)]?\s+(.*)$', text)
        if match:
            numbering = match.group(1)
            after_text = match.group(3)
            if len(after_text.strip()) < 4:
                return None  # Probably list item, not heading
            level = numbering.count('.') + 1
            if level > 3:
                level = 3  # Cap at H3
            return level
        return None

    # Title determination: use metadata if valid, else fallback largest Title font text on page 1
    doc_title = doc.metadata.get("title", "").strip()
    invalid_prefixes = ["microsoft word", "untitled", "doc", "pdf"]
    if (
        not doc_title
        or len(doc_title) < 5
        or any(prefix in doc_title.lower() for prefix in invalid_prefixes)
        or doc_title.lower().endswith((".doc", ".docx", ".pdf"))
    ):
        first_page_title_spans = [
            span for span in text_spans if span['page'] == 1 and H_LEVELS.get(span['font_size']) == "Title"
        ]
        if first_page_title_spans:
            largest_span = max(first_page_title_spans, key=lambda x: x['font_size'])
            doc_title = largest_span['text'].strip()
        else:
            first_page_spans = [span for span in text_spans if span['page'] == 1]
            if first_page_spans:
                largest_span = max(first_page_spans, key=lambda x: x['font_size'])
                doc_title = largest_span['text'].strip()
            else:
                doc_title = "Unknown Title"

    # Build outline combining numbering-based and font size based heading detection
    outline = []
    for span in text_spans:
        text = span["text"].strip()
        if is_date_like(text):
            continue  # Skip date entries

        number_level = get_heading_level(text)
        if number_level:
            heading_level = f"H{number_level}"
        else:
            lvl = H_LEVELS.get(span['font_size'], "Body")
            heading_level = lvl if lvl in ["H1", "H2", "H3"] else None

        if heading_level and heading_level in ["H1", "H2", "H3"] and is_meaningful_heading(text):
            outline.append({
                "level": heading_level,
                "text": text,
                "page": span["page"]
            })

    return {
        "title": doc_title,
        "outline": outline,
    }
