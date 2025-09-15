from datetime import datetime
from collections import defaultdict
from .models import Transaction
from . import db

def get_summary_and_chart_data():
    """
    Returns:
      - total_income, total_expense, balance
      - monthly_totals (list of dicts for chart)
      - category_breakdown (dict category -> total expense)
    """
    from sqlalchemy import func
    # totals
    income_total = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(Transaction.type == 'income').scalar()
    expense_total = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(Transaction.type == 'expense').scalar()

    balance = (income_total or 0) - (expense_total or 0)

    # monthly totals (last 12 months)
    from datetime import date, timedelta
    import calendar
    today = date.today()
    months = []
    monthly_income = []
    monthly_expense = []

    # Prepare months labels (YYYY-MM)
    for i in range(11, -1, -1):
        m = (today.replace(day=1).toordinal() - 1)  # safety
    # simpler approach: use month/year tuples
    import pandas as pd
    # fetch all transactions
    txs = Transaction.query.order_by(Transaction.date).all()
    df = None
    if txs:
        df = pd.DataFrame([t.to_dict() for t in txs])
        df['date'] = pd.to_datetime(df['date']).dt.to_period('M').dt.to_timestamp()
        months_index = pd.date_range(end=pd.Timestamp.today(), periods=12, freq='M')
        monthly = df.groupby(['date','type'])['amount'].sum().unstack(fill_value=0).reindex(months_index, fill_value=0)
        # ensure columns
        if 'income' not in monthly.columns:
            monthly['income'] = 0
        if 'expense' not in monthly.columns:
            monthly['expense'] = 0
        months = [d.strftime('%Y-%m') for d in monthly.index]
        monthly_income = monthly['income'].tolist()
        monthly_expense = monthly['expense'].tolist()
    else:
        import datetime
        months = [(datetime.date.today().replace(day=1) - pd.DateOffset(months=i)).strftime('%Y-%m') for i in reversed(range(12))]
        monthly_income = [0]*12
        monthly_expense = [0]*12

    # category breakdown (expenses only)
    cat_totals = db.session.query(Transaction.category, func.coalesce(func.sum(Transaction.amount), 0.0)).filter(Transaction.type=='expense').group_by(Transaction.category).all()
    category_breakdown = {c: v for c, v in cat_totals}

    return {
        "income_total": float(income_total or 0),
        "expense_total": float(expense_total or 0),
        "balance": float(balance or 0),
        "months": months,
        "monthly_income": monthly_income,
        "monthly_expense": monthly_expense,
        "category_breakdown": category_breakdown
    }
