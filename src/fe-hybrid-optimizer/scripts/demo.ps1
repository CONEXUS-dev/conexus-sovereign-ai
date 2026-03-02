# ============================================================
# FE-VRP Optimizer — Repeatable Demo Script
# ============================================================
# Usage: .\scripts\demo.ps1
# Requires: Python 3.10+ (no external deps for stub mode)
# ============================================================

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  DEMO 1: Unit Tests (28 tests)" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

python -m fe_vrp.tests
if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[FAIL] Tests failed. Aborting demo." -ForegroundColor Red
    exit 1
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  DEMO 2: Single Run (stub, n=100)" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

python -m fe_vrp.cli run --n 100 --mode stub --max_gens 50 --pop_size 15

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  DEMO 3: Scaling (stub, n=50,100)" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

python -m fe_vrp.cli scale --sizes 50,100 --seeds 3 --mode stub --max_gens 50 --pop_size 15

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  DEMO COMPLETE (stub mode)" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Results in: results/" -ForegroundColor Green
Write-Host "  Manifest:   results/demo_manifest.json" -ForegroundColor Green
Write-Host "  CSV:        results/scale_results.csv" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

# ============================================================
# DEMO 4: LLM Mode (requires API key + --calibrate)
# Uncomment below after setting ANTHROPIC_API_KEY or OPENAI_API_KEY
# ============================================================
# Write-Host "`n  DEMO 4: LLM Run (gated)" -ForegroundColor Yellow
# python -m fe_vrp.cli run --n 100 --mode llm --max_gens 50 --pop_size 15 --calibrate --llm_provider anthropic
