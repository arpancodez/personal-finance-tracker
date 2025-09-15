# Personal Finance Tracker

A simple web-based personal finance tracker built with Flask + SQLite.

## Features
- Add income and expenses
- Dashboard with monthly income/expense line chart (last 12 months)
- Expense breakdown by category (doughnut chart)
- View, paginate, delete transactions
- CSV import / export

## Tech
- Python 3.10+
- Flask
- SQLAlchemy (SQLite)
- Chart.js for charts
- pandas for CSV import convenience

## Setup (local)
```bash
git clone <repo-url>
cd personal-finance-tracker
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
export FLASK_APP=run.py
export FLASK_ENV=development
flask run
