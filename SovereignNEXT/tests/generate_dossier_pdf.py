"""
SovereignNEXT — Phase 4 Proof Dossier PDF Generator
Converts phase4_proof_dossier.md to phase4_proof_dossier.pdf using fpdf2.
No additional content beyond the Markdown source.
"""

import re
from pathlib import Path
from fpdf import FPDF

TESTS_DIR = Path(__file__).resolve().parent
MD_PATH = TESTS_DIR / "phase4_proof_dossier.md"
PDF_PATH = TESTS_DIR / "phase4_proof_dossier.pdf"


class DossierPDF(FPDF):
    """Custom PDF layout for the Phase 4 Proof Dossier."""

    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="Letter")
        self.set_auto_page_break(auto=True, margin=20)
        # Core fonts (built-in, no file needed)
        self.add_page()

    def _set_font_safe(self, family, style="", size=10):
        """Set font, falling back to Helvetica if family unavailable."""
        try:
            self.set_font(family, style, size)
        except Exception:
            self.set_font("Helvetica", style, size)

    def title_page(self, title, subtitle_lines):
        """Render a title page."""
        self.ln(40)
        self._set_font_safe("Helvetica", "B", 22)
        w = self.w - self.l_margin - self.r_margin
        self.multi_cell(w, 10, self._sanitize_text(title), align="C")
        self.ln(8)
        self._set_font_safe("Helvetica", "", 11)
        for line in subtitle_lines:
            if not line.strip():
                self.ln(4)
            else:
                self.multi_cell(w, 6, self._sanitize_text(line), align="C")
        self.ln(20)
        self._set_font_safe("Helvetica", "I", 10)
        self.multi_cell(w, 6, "SEALED -- Immutable ground truth for all subsequent phases.", align="C")
        self.add_page()

    def section_heading(self, text, level=1):
        """Render a section heading."""
        if level == 1:
            self.ln(4)
            self._set_font_safe("Helvetica", "B", 16)
            self.multi_cell(0, 8, self._sanitize_text(text))
            # Draw underline
            y = self.get_y()
            self.line(self.l_margin, y, self.w - self.r_margin, y)
            self.ln(3)
        elif level == 2:
            self.ln(3)
            self._set_font_safe("Helvetica", "B", 13)
            self.multi_cell(0, 7, self._sanitize_text(text))
            self.ln(1)
        elif level == 3:
            self.ln(2)
            self._set_font_safe("Helvetica", "B", 11)
            self.multi_cell(0, 6, self._sanitize_text(text))
            self.ln(1)

    def body_text(self, text):
        """Render body paragraph text with inline bold support."""
        self._set_font_safe("Helvetica", "", 10)
        # Process inline bold markers **text**
        parts = re.split(r'(\*\*[^*]+\*\*)', text)
        line_parts = []
        for part in parts:
            if part.startswith("**") and part.endswith("**"):
                line_parts.append(("B", part[2:-2]))
            else:
                line_parts.append(("", part))

        # Simple approach: write as multi_cell with style changes
        # For complex inline formatting, concatenate and use write()
        for style, content in line_parts:
            if not content:
                continue
            self._set_font_safe("Helvetica", style, 10)
            self.write(5, self._sanitize_text(content))
        self.ln(5)

    def code_block(self, text):
        """Render a code/diagram block in monospace."""
        self._set_font_safe("Courier", "", 7.5)
        self.set_fill_color(245, 245, 245)

        lines = text.split("\n")
        # Calculate block height to check page break
        line_height = 3.8
        block_height = len(lines) * line_height + 4

        # Check if we need a page break
        if self.get_y() + block_height > self.h - self.b_margin:
            self.add_page()

        x = self.l_margin
        w = self.w - self.l_margin - self.r_margin

        # Background rectangle
        y_start = self.get_y()
        self.rect(x, y_start, w, block_height, "F")

        self.ln(2)
        for line in lines:
            # Replace box-drawing characters with ASCII equivalents for font compatibility
            safe_line = self._sanitize_for_courier(line)
            self.set_x(x + 2)
            self.cell(w - 4, line_height, safe_line)
            self.ln(line_height)
        self.ln(2)

    @staticmethod
    def _sanitize_text(text):
        """Replace common Unicode chars with Latin-1 safe equivalents."""
        replacements = {
            "\u2014": "--",   # —
            "\u2013": "-",    # –
            "\u201c": '"',    # \u201c
            "\u201d": '"',    # \u201d
            "\u2018": "'",    # '
            "\u2019": "'",    # '
            "\u2026": "...",  # …
            "\u2264": "<=",   # ≤
            "\u2265": ">=",   # ≥
            "\u2208": "in",   # ∈
            "\u00d7": "x",    # ×
        }
        for uc, asc in replacements.items():
            text = text.replace(uc, asc)
        return text.encode("latin-1", errors="replace").decode("latin-1")

    def _sanitize_for_courier(self, text):
        """Replace Unicode box-drawing chars with ASCII for Courier font."""
        replacements = {
            "\u250c": "+",   # ┌
            "\u2510": "+",   # ┐
            "\u2514": "+",   # └
            "\u2518": "+",   # ┘
            "\u2502": "|",   # │
            "\u2500": "-",   # ─
            "\u251c": "+",   # ├
            "\u2524": "+",   # ┤
            "\u252c": "+",   # ┬
            "\u2534": "+",   # ┴
            "\u253c": "+",   # ┼
            "\u2190": "<-",  # ←
            "\u2192": "->",  # →
            "\u2191": "^",   # ↑
            "\u2193": "v",   # ↓
            "\u25b6": ">",   # ▶
            "\u25bc": "v",   # ▼
            "\u25c4": "<",   # ◄
            "\u2581": "_",   # ▁
            "\u2588": "#",   # █
            "\u2550": "=",   # ═
            "\u2551": "||",  # ║
            "\u2554": "+",   # ╔
            "\u2557": "+",   # ╗
            "\u255a": "+",   # ╚
            "\u255d": "+",   # ╝
            "\u2560": "+",   # ╠
            "\u2563": "+",   # ╣
            "\u2566": "+",   # ╦
            "\u2569": "+",   # ╩
            "\u256c": "+",   # ╬
            "\u2013": "-",   # –
            "\u2014": "--",  # —
            "\u201c": '"',   # "
            "\u201d": '"',   # "
            "\u2018": "'",   # '
            "\u2019": "'",   # '
            "\u2026": "...", # …
            "\u2264": "<=",  # ≤
            "\u2265": ">=",  # ≥
            "\u2208": "in",  # ∈
        }
        for uc, asc in replacements.items():
            text = text.replace(uc, asc)
        # Fallback: replace any remaining non-latin1 chars
        return text.encode("latin-1", errors="replace").decode("latin-1")

    def render_table(self, headers, rows, col_widths=None):
        """Render a simple table."""
        self._set_font_safe("Helvetica", "", 9)

        usable_w = self.w - self.l_margin - self.r_margin
        n_cols = len(headers)

        if col_widths is None:
            col_widths = [usable_w / n_cols] * n_cols

        # Ensure widths sum to usable width
        total = sum(col_widths)
        if abs(total - usable_w) > 1:
            scale = usable_w / total
            col_widths = [w * scale for w in col_widths]

        line_height = 5.5

        # Check page break for header + first few rows
        needed = line_height * (min(len(rows), 3) + 2)
        if self.get_y() + needed > self.h - self.b_margin:
            self.add_page()

        # Header
        self.set_fill_color(220, 220, 220)
        self._set_font_safe("Helvetica", "B", 9)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], line_height, self._sanitize_text(h), border=1, fill=True)
        self.ln(line_height)

        # Rows
        self._set_font_safe("Helvetica", "", 9)
        for row in rows:
            # Check page break
            if self.get_y() + line_height > self.h - self.b_margin:
                self.add_page()
                # Re-print header
                self.set_fill_color(220, 220, 220)
                self._set_font_safe("Helvetica", "B", 9)
                for i, h in enumerate(headers):
                    self.cell(col_widths[i], line_height, self._sanitize_text(h), border=1, fill=True)
                self.ln(line_height)
                self._set_font_safe("Helvetica", "", 9)

            for i, val in enumerate(row):
                self.cell(col_widths[i], line_height, self._sanitize_text(str(val)), border=1)
            self.ln(line_height)

        self.ln(2)

    def bullet(self, text, indent=0):
        """Render a bullet point."""
        self._set_font_safe("Helvetica", "", 10)
        x = self.l_margin + indent
        self.set_x(x)
        bullet_w = 5

        # Handle inline bold
        parts = re.split(r'(\*\*[^*]+\*\*)', text)
        self.cell(bullet_w, 5, "-")
        for part in parts:
            if part.startswith("**") and part.endswith("**"):
                self._set_font_safe("Helvetica", "B", 10)
                self.write(5, self._sanitize_text(part[2:-2]))
            elif part:
                self._set_font_safe("Helvetica", "", 10)
                self.write(5, self._sanitize_text(part))
        self.ln(5)

    def horizontal_rule(self):
        """Draw a horizontal rule."""
        self.ln(3)
        y = self.get_y()
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.ln(3)

    def footer(self):
        """Page footer with page number."""
        self.set_y(-15)
        self._set_font_safe("Helvetica", "I", 8)
        self.cell(0, 10, f"Phase 4 Proof Dossier | US 63/898,911 | Page {self.page_no()}", align="C")


# ---------------------------------------------------------------------------
# Markdown Parser -> PDF
# ---------------------------------------------------------------------------

def parse_md_to_pdf(md_text: str) -> DossierPDF:
    """Parse the dossier Markdown and render to PDF."""
    pdf = DossierPDF()

    # Title page
    pdf.title_page(
        "Phase 4 Proof Dossier",
        [
            "SovereignNEXT Collapse Validation",
            "",
            "Project: CONEXUS SovereignNEXT",
            "Patent: US 63/898,911",
            "Phase: 4 -- Collapse Validation",
            "Date: 2026-03-04",
        ],
    )

    lines = md_text.split("\n")
    i = 0
    in_code_block = False
    code_buffer = []
    in_table = False
    table_headers = []
    table_rows = []

    # Skip the title block (first ~8 lines with # title and metadata)
    # Find first --- separator
    start_idx = 0
    for idx, line in enumerate(lines):
        if line.strip() == "---" and idx > 3:
            start_idx = idx + 1
            break

    i = start_idx

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Code block toggle
        if stripped.startswith("```"):
            if in_code_block:
                # End code block
                pdf.code_block("\n".join(code_buffer))
                code_buffer = []
                in_code_block = False
            else:
                # Flush any pending table
                if in_table:
                    _flush_table(pdf, table_headers, table_rows)
                    in_table = False
                    table_headers = []
                    table_rows = []
                in_code_block = True
            i += 1
            continue

        if in_code_block:
            code_buffer.append(line)
            i += 1
            continue

        # Table detection
        if "|" in stripped and not stripped.startswith("#"):
            cells = [c.strip() for c in stripped.split("|")]
            cells = [c for c in cells if c]  # Remove empty from leading/trailing |

            # Skip separator rows like |---|---|
            if all(re.match(r'^[-:]+$', c) for c in cells):
                i += 1
                continue

            if not in_table:
                in_table = True
                table_headers = cells
            else:
                table_rows.append(cells)
            i += 1
            continue
        else:
            # Flush pending table
            if in_table:
                _flush_table(pdf, table_headers, table_rows)
                in_table = False
                table_headers = []
                table_rows = []

        # Headings
        if stripped.startswith("### "):
            pdf.section_heading(stripped[4:], level=3)
            i += 1
            continue
        if stripped.startswith("## "):
            pdf.section_heading(stripped[3:], level=2)
            i += 1
            continue
        if stripped.startswith("# "):
            pdf.section_heading(stripped[2:], level=1)
            i += 1
            continue

        # Horizontal rule
        if stripped == "---":
            pdf.horizontal_rule()
            i += 1
            continue

        # Bullet points
        if stripped.startswith("- "):
            pdf.bullet(stripped[2:])
            i += 1
            continue

        # Numbered list
        m = re.match(r'^(\d+)\.\s+(.+)', stripped)
        if m:
            pdf.bullet(f"{m.group(1)}. {m.group(2)}")
            i += 1
            continue

        # Italic-only lines (like the footer)
        if stripped.startswith("*") and stripped.endswith("*") and not stripped.startswith("**"):
            pdf._set_font_safe("Helvetica", "I", 10)
            clean = DossierPDF._sanitize_text(stripped.strip("*"))
            pdf.multi_cell(0, 5, clean)
            pdf.ln(1)
            i += 1
            continue

        # Empty line
        if not stripped:
            pdf.ln(2)
            i += 1
            continue

        # Regular paragraph — collect consecutive non-empty lines
        para_lines = [stripped]
        j = i + 1
        while j < len(lines):
            next_stripped = lines[j].strip()
            if (not next_stripped or next_stripped.startswith("#") or
                    next_stripped.startswith("```") or next_stripped.startswith("- ") or
                    next_stripped.startswith("---") or next_stripped.startswith("|") or
                    re.match(r'^\d+\.\s+', next_stripped) or
                    (next_stripped.startswith("*") and next_stripped.endswith("*"))):
                break
            para_lines.append(next_stripped)
            j += 1

        full_para = " ".join(para_lines)
        pdf.body_text(full_para)
        i = j
        continue

    # Flush any remaining table
    if in_table:
        _flush_table(pdf, table_headers, table_rows)

    return pdf


def _flush_table(pdf, headers, rows):
    """Render a collected table."""
    if not headers:
        return

    n_cols = len(headers)
    usable_w = pdf.w - pdf.l_margin - pdf.r_margin

    # Estimate column widths based on content
    col_max_len = [len(h) for h in headers]
    for row in rows:
        for ci in range(min(len(row), n_cols)):
            col_max_len[ci] = max(col_max_len[ci], len(str(row[ci])))

    total_chars = sum(col_max_len) or 1
    col_widths = [(cl / total_chars) * usable_w for cl in col_max_len]

    # Ensure rows have correct number of columns
    padded_rows = []
    for row in rows:
        padded = list(row) + [""] * (n_cols - len(row))
        padded_rows.append(padded[:n_cols])

    pdf.render_table(headers, padded_rows, col_widths)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(f"Reading: {MD_PATH.name}")
    if not MD_PATH.exists():
        print(f"ABORT: {MD_PATH} not found")
        return

    md_text = MD_PATH.read_text(encoding="utf-8")

    print("Generating PDF...")
    pdf = parse_md_to_pdf(md_text)

    print(f"Writing: {PDF_PATH.name}")
    pdf.output(str(PDF_PATH))

    size_kb = PDF_PATH.stat().st_size / 1024
    print(f"Done. {PDF_PATH.name} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
