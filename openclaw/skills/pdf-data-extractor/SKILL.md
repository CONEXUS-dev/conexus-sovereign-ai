---
name: pdf-data-extractor
description: Extract text, tables, metadata, and structured data from PDF files. Supports OCR fallback, table detection, and multi-page extraction. Outputs clean markdown or JSON.
version: "1.0.0"
source: "online"
tags: [pdf, extraction, data, tables, ocr, utility]
mode: collapse
visibility: shared
permissions:
  agents: [sway, opie, outer]
  execution: "governed"
requires:
  bins: [python3]
  packages: [pymupdf, tabula-py, pdfplumber]
---

# PDF Data Extractor

Extract structured data from PDF documents.

## Capabilities

### Text Extraction
- Full-text extraction with layout preservation
- Page-by-page or full-document modes
- Heading and paragraph detection
- Footnote and header/footer separation

### Table Extraction
- Detect and extract tables from PDF pages
- Output as markdown tables, CSV, or JSON
- Handle merged cells and multi-line rows
- Support for bordered and borderless tables

### Metadata Extraction
- Title, author, creation date, modification date
- Page count, file size, PDF version
- Embedded fonts and images summary

### OCR Fallback
- Detect image-only PDFs
- Apply OCR when text layer is missing
- Confidence scoring for OCR results

## Usage

```bash
# Extract all text
python scripts/extract.py --input document.pdf --mode text

# Extract tables
python scripts/extract.py --input document.pdf --mode tables --format markdown

# Extract metadata
python scripts/extract.py --input document.pdf --mode metadata
```

## Output Format

- **Text:** Clean markdown with headings preserved
- **Tables:** Markdown tables or JSON arrays
- **Metadata:** JSON object

## Safety

- Read-only: no file modification
- Local processing only — no external API calls
- No execution of embedded PDF scripts or macros
- File paths validated before access
