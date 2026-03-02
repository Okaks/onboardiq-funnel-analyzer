# OnboardIQ — Onboarding Funnel Intelligence Engine

A full-stack onboarding analytics system built with **FastAPI, PostgreSQL, and Streamlit**.

OnboardIQ simulates a real-world onboarding intelligence platform used by fintech and digital banking teams to measure conversion, detect friction, and optimize customer onboarding journeys.

---

## Project Objective

Digital onboarding is one of the most critical growth levers in financial services.

This project demonstrates how product teams can:

- Track onboarding behavior in real-time  
- Quantify drop-offs between steps  
- Measure time delays in verification processes  
- Identify bottlenecks in approval flows  
- Generate structured, data-driven insights  

It mirrors how internal product analytics systems operate inside modern digital banks.

---

## Core Capabilities

### Step-Level Analytics
- Users at each step  
- Drop-off counts and percentages  
- Conversion rate calculations using SQL window functions  

### Funnel Summary Metrics
- Total started  
- Total completed  
- Overall conversion rate  
- Biggest drop-off step detection  

### Time-Based Process Analysis
- Average time between onboarding steps  
- Min / Max transition times  
- Slowest transition identification  

### Executive Dashboard
Built using Streamlit:
- Clean metric cards  
- Funnel visualization  
- Drop-off charts  
- Time analysis tables  
- Strategic recommendations  

---

## Architecture Overview

**Backend:** FastAPI  
**Database:** PostgreSQL  
**Analytics Layer:** SQL (Window Functions + Aggregations)  
**Dashboard:** Streamlit  

**Data Flow:**

Client → FastAPI → PostgreSQL → SQL Analytics Engine → Streamlit Dashboard → Insights

---

## Project Structure
onboardiq-funnel-analyzer/
│
├── app/
│ ├── main.py
│ ├── database.py
│
├── dashboard/
│ └── dashboard.py
│
├── screenshots/
├── requirements.txt
├── README.md
└── .gitignore
 
---
##  Running Locally

1️⃣ Create virtual environment
python -m venv venv
2️⃣ Activate  
venv\Scripts\Activate.ps1
3️⃣ Install dependencies  
pip install -r requirements.txt
4️⃣ Start backend  
uvicorn app.main:app --reload
5️⃣ Launch dashboard  
streamlit run dashboard/dashboard.py