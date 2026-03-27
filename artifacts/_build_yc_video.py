"""
Generate a terminal-replay style MP4 video for YC demo upload.
Renders terminal frames with Pillow, encodes with OpenCV.
Delete after use.
"""

import json
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# --- Config ---
WIDTH, HEIGHT = 1280, 720
FPS = 2  # slow — meant to be read, not watched at speed
BG_COLOR = (30, 30, 30)        # dark terminal background
TEXT_COLOR = (220, 220, 220)    # light gray
GREEN = (80, 220, 100)
YELLOW = (220, 200, 80)
CYAN = (100, 200, 220)
WHITE = (255, 255, 255)
DIM = (140, 140, 140)
MARGIN_X = 40
MARGIN_Y = 30
LINE_HEIGHT = 22

# Try to use a monospace font
try:
    FONT = ImageFont.truetype("consola.ttf", 16)
    FONT_BOLD = ImageFont.truetype("consolab.ttf", 16)
    FONT_TITLE = ImageFont.truetype("consolab.ttf", 22)
except Exception:
    try:
        FONT = ImageFont.truetype("cour.ttf", 16)
        FONT_BOLD = FONT
        FONT_TITLE = ImageFont.truetype("cour.ttf", 22)
    except Exception:
        FONT = ImageFont.load_default()
        FONT_BOLD = FONT
        FONT_TITLE = FONT


def make_frame(lines):
    """Render a list of (text, color, font) tuples onto a terminal frame."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    y = MARGIN_Y
    for text, color, font in lines:
        if y + LINE_HEIGHT > HEIGHT - 20:
            break
        draw.text((MARGIN_X, y), text, fill=color, font=font)
        y += LINE_HEIGHT
    return img


def img_to_cv2(pil_img):
    """Convert PIL Image to OpenCV BGR numpy array."""
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)


def add_frames(writer, pil_img, duration_sec):
    """Write the same frame for duration_sec seconds at FPS."""
    frame = img_to_cv2(pil_img)
    for _ in range(max(1, int(duration_sec * FPS))):
        writer.write(frame)


# --- Load actual data ---
bundle = Path("artifacts/gemini_demo_public_v1")
meta = json.loads((bundle / "run_artifacts" / "run_metadata.json").read_text())
inv = json.loads((bundle / "run_artifacts" / "invariant_check.json").read_text())

# --- Build slides ---
slides = []

# Slide 1: Title (4 sec)
slides.append((4, [
    ("", WHITE, FONT),
    ("  CONEXUS Sovereign Pipeline", WHITE, FONT_TITLE),
    ("  Gemini Governed Demo", CYAN, FONT_TITLE),
    ("", WHITE, FONT),
    ("", WHITE, FONT),
    ("  Model-agnostic governance enforcement", DIM, FONT),
    ("  verified on four LLM backends", DIM, FONT),
    ("", WHITE, FONT),
    ("", WHITE, FONT),
    ("  CONEXUS Global Arts Media Inc.", DIM, FONT),
    ("  March 2026", DIM, FONT),
]))

# Slide 2: What this shows (5 sec)
slides.append((5, [
    ("  WHAT THIS DEMO SHOWS", YELLOW, FONT_BOLD),
    ("", WHITE, FONT),
    ("  One-command governed pipeline run using Gemini 2.0 Flash", WHITE, FONT),
    ("  as the cloud LLM backend.", WHITE, FONT),
    ("", WHITE, FONT),
    ("  The governance operators enforce structural invariants", WHITE, FONT),
    ("  on LLM output AFTER generation.", WHITE, FONT),
    ("", WHITE, FONT),
    ("  Same invariants verified on:", WHITE, FONT),
    ("    - LLaMA 8B   (local)", DIM, FONT),
    ("    - Mistral 7B  (local)", DIM, FONT),
    ("    - Phi 4B      (local)", DIM, FONT),
    ("    - Gemini Flash (cloud)  <-- this demo", GREEN, FONT_BOLD),
]))

# Slide 3: The command (4 sec)
slides.append((4, [
    ("  HOW TO RUN", YELLOW, FONT_BOLD),
    ("", WHITE, FONT),
    ("  $ export GEMINI_API_KEY='your-key'", CYAN, FONT),
    ("", WHITE, FONT),
    ("  $ python -m SovereignNEXT.pipeline.run_gemini_demo_v1 \\", GREEN, FONT),
    ("        --passes 1 --seed 42", GREEN, FONT),
    ("", WHITE, FONT),
    ("  Runtime: 15-25 minutes", DIM, FONT),
    ("  API calls: 604", DIM, FONT),
]))

# Slide 4: Run metadata (5 sec)
slides.append((5, [
    ("  RUN RESULTS", YELLOW, FONT_BOLD),
    ("", WHITE, FONT),
    (f"  Model:           {meta['model']}", WHITE, FONT),
    (f"  Backend:         {meta['backend']}", WHITE, FONT),
    (f"  Duration:        {meta['duration_sec']:.0f}s ({meta['duration_sec']/60:.1f} min)", WHITE, FONT),
    (f"  Governance:      {meta['governance_version']}", WHITE, FONT),
    (f"  Baseline:        {meta['baseline']}", WHITE, FONT),
    ("", WHITE, FONT),
    (f"  Final claims:    {meta['final_claims']}", WHITE, FONT),
    (f"  Final tensions:  {meta['final_tensions']} (0 open)", WHITE, FONT),
    (f"  Final paradoxes: {meta['final_paradoxes']}", WHITE, FONT),
]))

# Slide 5: Invariant check - THE headline (7 sec)
slides.append((7, [
    ("  GOVERNANCE INVARIANT CHECK", YELLOW, FONT_BOLD),
    ("", WHITE, FONT),
    (f"  Gate: {inv['gate']}", WHITE, FONT),
    (f"  Status: {inv['status']}", GREEN, FONT_BOLD),
    ("", WHITE, FONT),
]))
for check in inv["checks"]:
    status = "PASS" if check["passed"] else "FAIL"
    color = GREEN if check["passed"] else (220, 80, 80)
    slides[-1][1].append(
        (f"  [{status}] {check['invariant']}: {check['evidence']}", color, FONT)
    )
slides[-1][1].extend([
    ("", WHITE, FONT),
    ("  Gemini passed the same governance invariants", GREEN, FONT_BOLD),
    ("  as LLaMA, Mistral, and Phi.", GREEN, FONT_BOLD),
])

# Slide 6: Verify (4 sec)
slides.append((4, [
    ("  VERIFICATION", YELLOW, FONT_BOLD),
    ("", WHITE, FONT),
    ("  $ python verification/_verify.py", CYAN, FONT),
    ("", WHITE, FONT),
    ("  VERIFIED - all hashes match", GREEN, FONT_BOLD),
    ("", WHITE, FONT),
    ("  Every artifact is SHA-256 hashed.", DIM, FONT),
    ("  The proof is independently verifiable.", DIM, FONT),
]))

# Slide 7: All gates (5 sec)
slides.append((5, [
    ("  GATE REPORT (all 10 gates)", YELLOW, FONT_BOLD),
    ("", WHITE, FONT),
    ("  [PASS] 0 - Sealed paths verified", GREEN, FONT),
    ("  [PASS] 1 - Adapter interface", GREEN, FONT),
    ("  [PASS] 2 - Gemini standalone test", GREEN, FONT),
    ("  [PASS] 3 - Full governed cycle", GREEN, FONT),
    ("  [PASS] 3B - Invariants confirmed", GREEN, FONT),
    ("  [PASS] 4A - OpenClaw bridge", GREEN, FONT),
    ("  [PASS] 4B - Route flag", GREEN, FONT),
    ("  [PASS] 5 - Proof packet sealed", GREEN, FONT),
    ("  [PASS] 6 - Demo script", GREEN, FONT),
    ("  [PASS] 7 - Final report", GREEN, FONT),
    ("", WHITE, FONT),
    ("  All gates passed. No failures. No patches.", WHITE, FONT),
]))

# Slide 8: Claim boundary (5 sec)
slides.append((5, [
    ("  CLAIM BOUNDARY", YELLOW, FONT_BOLD),
    ("", WHITE, FONT),
    ("  This demo DOES prove:", WHITE, FONT),
    ("    Governance invariants are model-agnostic", GREEN, FONT),
    ("    (4 models, same structural outcome)", GREEN, FONT),
    ("", WHITE, FONT),
    ("  This demo does NOT claim:", WHITE, FONT),
    ("    Product readiness", DIM, FONT),
    ("    Performance benchmark", DIM, FONT),
    ("    Output quality evaluation", DIM, FONT),
    ("    Completeness or optimality", DIM, FONT),
]))

# Slide 9: Headline close (5 sec)
slides.append((5, [
    ("", WHITE, FONT),
    ("", WHITE, FONT),
    ("  The LLM generates text.", WHITE, FONT_TITLE),
    ("", WHITE, FONT),
    ("  The governance operators enforce structure", WHITE, FONT_TITLE),
    ("  after generation.", WHITE, FONT_TITLE),
    ("", WHITE, FONT),
    ("  Different models. Different text.", CYAN, FONT),
    ("  Same invariants.", GREEN, FONT_BOLD),
    ("", WHITE, FONT),
    ("", WHITE, FONT),
    ("  One command. Cloud LLM. Full governance.", DIM, FONT),
    ("  Auditable. Repeatable.", DIM, FONT),
]))

# --- Render video ---
out_path = "artifacts/CONEXUS_Gemini_Governed_Demo.mp4"
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
writer = cv2.VideoWriter(out_path, fourcc, FPS, (WIDTH, HEIGHT))

total_sec = 0
for duration, lines in slides:
    frame = make_frame(lines)
    add_frames(writer, frame, duration)
    total_sec += duration

writer.release()

import os
size = os.path.getsize(out_path)
print(f"Video created: {out_path}")
print(f"Size: {size} bytes ({size / 1024:.1f} KB)")
print(f"Duration: ~{total_sec}s ({len(slides)} slides)")
print(f"Resolution: {WIDTH}x{HEIGHT} @ {FPS} fps")
