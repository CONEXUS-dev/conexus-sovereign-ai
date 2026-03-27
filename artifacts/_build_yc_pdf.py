"""One-shot script to generate the YC demo PDF. Delete after use."""

from fpdf import FPDF
import os


class DemoPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 8, "CONEXUS Sovereign Pipeline - Gemini Governed Demo",
                  align="C", new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def section(self, title):
        self.set_font("Helvetica", "B", 13)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def subsection(self, title):
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body(self, text):
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def mono(self, text):
        self.set_font("Courier", "", 9)
        self.set_fill_color(240, 240, 240)
        self.multi_cell(0, 5, text, fill=True)
        self.set_font("Helvetica", "", 10)
        self.ln(2)

    def table_row(self, col1, col2, bold=False):
        style = "B" if bold else ""
        self.set_font("Helvetica", style, 10)
        self.cell(95, 7, col1, border=1)
        self.set_font("Helvetica", "", 10)
        self.cell(95, 7, col2, border=1, new_x="LMARGIN", new_y="NEXT")


pdf = DemoPDF()
pdf.set_auto_page_break(auto=True, margin=20)

# ===== PAGE 1 =====
pdf.add_page()

pdf.section("What This Demo Shows")
pdf.body(
    "A one-command, reproducible governed run of the CONEXUS Sovereign "
    "pipeline using Gemini 2.0 Flash as the cloud LLM backend."
)
pdf.body(
    "The pipeline's governance operators (Collapse, Become, Paradox-Hold, "
    "Observer) enforce structural invariants on LLM output after generation. "
    "This demo confirms those invariants hold identically whether the LLM "
    "is a local model or a cloud API."
)
pdf.body(
    "The same invariants were previously verified on three local models "
    "(LLaMA 8B, Mistral 7B, Phi 4B). Gemini Flash is the fourth model to pass."
)

pdf.section("Headline Result")
pdf.table_row("Invariant", "Result", bold=True)
pdf.table_row("Open tensions after Collapse", "0")
pdf.table_row("Paradoxes held", "94 / 94  (100%)")
pdf.table_row("Paradoxes vetoed", "94 / 94  (100%)")
pdf.table_row("Observer attestations", "3")
pdf.ln(4)
pdf.set_font("Helvetica", "B", 11)
pdf.cell(0, 8, "Gemini is the fourth model to pass these governance invariants.",
         new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "", 10)
pdf.body(
    "Four models. Different architectures. Different providers. "
    "Same structural outcome. The governance operators are model-agnostic."
)

pdf.section("Run Summary")
pdf.table_row("Metric", "Value", bold=True)
pdf.table_row("Model", "gemini-2.0-flash (Google, cloud API)")
pdf.table_row("Baseline", "Sovereign-V5-Anchor (sealed)")
pdf.table_row("Governance", "v1")
pdf.table_row("Operator sequence", "Collapse > Become > Paradox-Hold > Observer")
pdf.table_row("Duration", "17.5 minutes")
pdf.table_row("Gemini API calls", "604")
pdf.table_row("Final claims", "862")
pdf.table_row("Final tensions", "1,602 (0 open)")
pdf.table_row("Paradoxes", "94 (100% held, 100% vetoed)")

# ===== PAGE 2 =====
pdf.add_page()

pdf.section("How To Run This Demo")
pdf.body(
    "Prerequisites: Python 3.10+, google-genai package, "
    "a Gemini API key (free tier sufficient)."
)

pdf.subsection("Setup")
pdf.mono(
    'export GEMINI_API_KEY="your-key"              # Linux/Mac\n'
    '$env:GEMINI_API_KEY = "your-key"              # PowerShell'
)

pdf.subsection("Run")
pdf.mono(
    "python -m SovereignNEXT.pipeline.run_gemini_demo_v1 --passes 1 --seed 42"
)
pdf.body(
    "Expected runtime: 15-25 minutes. Governance outcomes (zero open tensions, "
    "100% held, 100% vetoed) are deterministic for a given seed. "
    "Text content varies due to LLM non-determinism."
)

pdf.subsection("Verify")
pdf.mono("python verification/_verify.py")
pdf.body("Expected output: VERIFIED - all hashes match.")

pdf.section("What This Demo Does NOT Claim")
pdf.body(
    "This is not a product or hosted service.\n"
    "This is not a performance benchmark.\n"
    "This does not prove optimality or completeness.\n"
    "This does not replace the Phase One three-model proof (sealed separately).\n"
    "LLM output quality is not evaluated - only governance enforcement is tested."
)

pdf.section("Claim Boundary")
pdf.body(
    "This demo extends the governance invariance result to a fourth model "
    "(Gemini Flash, cloud API). It confirms the Sovereign pipeline's "
    "structural enforcement is independent of the LLM provider."
)
pdf.body(
    "The LLM generates text. The governance operators enforce structure "
    "after generation. Different models produce different text, but the "
    "invariants are identical. The operators are model-agnostic. "
    "That is the proof."
)

# ===== PAGE 3 =====
pdf.add_page()

pdf.section("Gate Report")
pdf.table_row("Gate", "Result", bold=True)
pdf.table_row("0 - Sealed paths verified before run", "PASSED")
pdf.table_row("1 - Adapter interface created", "PASSED")
pdf.table_row("2 - Gemini standalone test", "PASSED")
pdf.table_row("3 - Full governed cycle via Gemini", "PASSED")
pdf.table_row("3B - Governance invariants confirmed", "PASSED")
pdf.table_row("4A - OpenClaw Gateway bridge created", "PASSED")
pdf.table_row("4B - Route-via-OpenClaw flag", "PASSED")
pdf.table_row("5 - Demo proof packet sealed", "PASSED")
pdf.table_row("6 - 90-second demo script", "PASSED")
pdf.table_row("7 - Final report + sealed path verification", "PASSED")
pdf.ln(4)
pdf.body(
    "All gates passed. No failures. No patches. "
    "All sealed Phase One paths hash-verified unchanged "
    "before and after execution."
)

pdf.section("Architecture (Single Pass)")
pdf.body(
    "1. Load sealed V5 baseline snapshot "
    "(650 claims, 1505 tensions, 84 paradoxes)\n"
    "2. Become pass via Gemini: claim expansion + tension detection "
    "(604 API calls)\n"
    "3. Collapse operator: commit or hold all tensions (0 left open)\n"
    "4. Become operator: apply structural transforms\n"
    "5. Paradox-Hold operator: enforce hold on all paradoxes "
    "(94/94 held, 94/94 vetoed)\n"
    "6. Observer: attestation and anomaly detection (3 attestations)"
)

pdf.section("Source Code")
pdf.body(
    "Repository: github.com/CONEXUS-dev/conexus-sovereign-ai\n"
    "Demo runner: SovereignNEXT/pipeline/run_gemini_demo_v1.py\n"
    "Gemini adapter: SovereignNEXT/adapters/cloud_llm/gemini_client.py"
)

pdf.ln(8)
pdf.set_font("Helvetica", "I", 9)
pdf.body(
    "CONEXUS Global Arts Media Inc. | March 2026 | "
    "contact: Dangell@conexusglobalarts.media"
)

out = os.path.join("artifacts", "CONEXUS_Gemini_Governed_Demo.pdf")
pdf.output(out)
size = os.path.getsize(out)
print(f"PDF created: {out}")
print(f"Size: {size} bytes ({size / 1024:.1f} KB)")
print(f"Pages: {pdf.pages_count}")
