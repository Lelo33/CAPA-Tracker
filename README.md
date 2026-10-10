# CAPA Tracker

A Corrective and Preventive Action (CAPA) tracker with a Streamlit dashboard, built around the way a quality team works.

Live app: https://lelo-capa-tracker.streamlit.app

## Why I built this
I've worked in manufacturing quality control for over 9 years. CAPA is one of the core QC processes: find the problem, fix it, find the root cause, and stop it coming back. This project turns that process into a small app.

## What it does
- Logs CAPAs: source, problem, root cause category (6M), corrective action, preventive action, owner and due date
- Dashboard: total, not closed, overdue and average days to close
- Root cause Pareto chart, to show which causes come up most often
- Flags overdue actions
- Update tab to change status and record an effectiveness check
- Download the log as a CSV

## Notes
- The app starts with made-up sample data. Please don't enter confidential company data, because the app is public.
- Records last only for your session. Download the CSV to keep them. Saving to a database is a planned improvement.

## How to run it
1. Install Python
2. Run: pip install -r requirements.txt
3. Run: streamlit run app.py

## Files
- app.py - the Streamlit app
- requirements.txt - libraries the app needs

## What's next
- Save records to a database so they last between sessions
- Add trend charts for CAPAs opened and closed per month
- Add a 5 Whys section for root cause analysis
