import fitz  # PyMuPDF
import re
import json

def extract_metadata(page_text):
    title = None
    act_number = None
    certification_date = None
    gazette_date = None

    # Title
    title_match = re.search(r"^(.*ACT.*)", page_text, re.MULTILINE | re.IGNORECASE)
    if title_match:
        title = title_match.group(1).strip()

    # Act number
    act_number_match = re.search(r"Act[, ]No[.]?\s*(\d+\s*of\s*\d{4})", page_text, re.IGNORECASE)
    if act_number_match:
        act_number = act_number_match.group(1).strip()

    # Certification date
    cert_match = re.search(r"\[Certified on\s*([^\]]+)\]", page_text, re.IGNORECASE)
    if cert_match:
        certification_date = cert_match.group(1).strip()

    # Gazette date
    gaz_match = re.search(r"Gazette.*?(\w+\s+\d{1,2},?\s+\d{4})", page_text, re.IGNORECASE)
    if gaz_match:
        gazette_date = gaz_match.group(1).strip()

    return {
        "title": title or "",
        "act_number": act_number or "",
        "certification_date": certification_date or "",
        "gazette_date": gazette_date or ""
    }

def extract_sections(pdf_path, left_margin=180, right_margin=180):
    doc = fitz.open(pdf_path)
    metadata = extract_metadata(doc[0].get_text())

    sections = []
    section_count = 0

    for page_num in range(1, len(doc)):
        page = doc[page_num]
        width = page.rect.width
        blocks = page.get_text("dict")["blocks"]

        margin_notes = []
        content_spans = []

        # Step 1: Separate margin notes and main content
        for b in blocks:
            if "lines" not in b:
                continue
            x0, y0, x1, y1 = b.get("bbox", [0,0,0,0])
            text = " ".join(span["text"] for line in b["lines"] for span in line["spans"]).strip()
            if not text:
                continue

            if x1 < left_margin or x0 > (width - right_margin):
                margin_notes.append({'y': y0, 'text': text})
            else:
                for line in b["lines"]:
                    for span in line["spans"]:
                        content_spans.append({
                            "text": span["text"].strip(),
                            "bold": "Bold" in span["font"] or span["flags"] & 2,
                            "y": y0
                        })

        margin_notes.sort(key=lambda x: x['y'])
        content_spans.sort(key=lambda x: x['y'])

        current_section = None

        for i, span in enumerate(content_spans):
            # Check if span is a bold number (section start)
            if span["bold"] and re.match(r"^\d+\.$", span["text"]):
                # Save previous section
                if current_section:
                    sections.append(current_section)
                    section_count += 1

                # Step 2: Find nearest margin note for title
                nearest_margin = None
                nearest_distance = float("inf")
                for mn in margin_notes:
                    distance = abs(mn["y"] - span["y"])
                    if distance < nearest_distance:
                        nearest_distance = distance
                        nearest_margin = mn
                section_title = nearest_margin["text"] if nearest_margin else ""

                # Step 3: Start new section
                current_section = {
                    "section_number": span["text"].strip("."),
                    "section_title": section_title,
                    "content": ""
                }
            else:
                # Add text to current section
                if current_section:
                    current_section["content"] += " " + span["text"]

        # Add last section on page
        if current_section:
            sections.append(current_section)
            section_count += 1

    return {
        "metadata": metadata,
        "sections": sections,
        "total_sections": section_count
    }

if __name__ == "__main__":
    pdf_file = "01-2013_E.pdf"  # Change to your PDF path
    extracted_data = extract_sections(pdf_file)

    print(json.dumps(extracted_data, indent=4, ensure_ascii=False))
    with open("extracted_act_01-2013_E.json", "w", encoding="utf-8") as f:
         json.dump(extracted_data, f, ensure_ascii=False, indent=4)
