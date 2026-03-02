# OnboardIQ — Onboarding Funnel Intelligence Dashboard

A full-stack onboarding funnel analytics engine built with FastAPI, PostgreSQL, and Streamlit.

This project tracks onboarding events, calculates conversion rates, detects drop-offs, analyzes time between steps, and surfaces actionable insights through an interactive dashboard.

---

## Features

- REST API for onboarding event tracking
- Step-level conversion rate calculation
- Drop-off detection using SQL window functions
- Overall funnel summary metrics
- Step-to-step time analysis
- Slowest transition identification
- Interactive executive dashboard
- Strategic insight generation

---

## Architecture

Backend: FastAPI  
Database: PostgreSQL  
Analytics: SQL (Window Functions + Aggregations)  
Dashboard: Streamlit  

Flow:

Client → FastAPI → PostgreSQL → Analytics Queries → Dashboard → Insights

---

## Sample Dashboard

(Screenshots located in /screenshots folder)

---

## How to Run Locally

1. Clone the repository
2. Create virtual environment:
   python -m venv venv
3. Activate:
   venv\Scripts\Activate.ps1
4. Install dependencies:
   pip install -r requirements.txt

5. Run backend:
   uvicorn app.main:app --reload

6. Run dashboard:
   streamlit run dashboard/dashboard.py

---

Digital onboarding experiences are critical in fintech and digital banking.

This system demonstrates how product teams can:

- Identify friction points
- Quantify drop-offs
- Measure process delays
- Make data-driven improvements

---

## Author
Blessing Okakwu  
Product Analytics | Digital Banking | Data Strategy