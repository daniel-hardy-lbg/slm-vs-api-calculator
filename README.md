# Self-host vs Gemini API Calculator

Streamlit app that compares monthly cost of:
- Gemini 2.5 Flash API (token-based pricing)
- Self-hosted open-weight SLMs (GPU fixed cost + overhead)

## What it is
A deterministic calculator using frozen assumptions (April 2026 pricing / benchmark throughput).

## What it is NOT
- Not a procurement quote
- Not a latency/SLA planner
- Not a full infra architecture tool

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py