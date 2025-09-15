from flask import render_template, request, redirect, url_for, current_app, send_file, flash
from datetime import datetime
from . import db
from .models import Transaction
from .utils import get_summary_and_chart_data
import io
import csv
import pandas as pd

from flask import current_app as app

@app.route('/')
def index():
    summary = get_summary_and_chart_data()
    recent = Transaction.query.order_by(Transaction.date.desc()).limit(8).all()
    return render_template('index.html', summary=summary, recent=recent)

@app.route('/transactions')
def transactions():
    page = int(request.args.get('page', 1))
    per_page = 25
    q = Transaction.query.order_by(Transaction.date.desc())
    pagination = q.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('transactions.html', pagination=pagination)

@app.route('/add', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        date_str = request.form.get('date')
        amount = request.form.get('amount')
        category = request.form.get('category', 'Uncategorized')
        ttype = request.form.get('type', 'expense')
        note = request.form.get('note', '')

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            amount = float(amount)
        except Exception as e:
            flash("Invalid input: ensure date is YYYY-MM-DD and amount is numeric.", "danger")
            return redirect(url_for('add_transaction'))

        tx = Transaction(date=date, amount=amount, category=category, type=ttype, note=note)
        db.session.add(tx)
        db.session.commit()
        flash("Transaction added.", "success")
        return redirect(url_for('index'))

    # GET
    return render_template('add_transaction.html')

@app.route('/export')
def export_csv():
    txs = Transaction.query.order_by(Transaction.date.desc()).all()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['id', 'date', 'amount', 'category', 'type', 'note'])
    for t in txs:
        cw.writerow([t.id, t.date.isoformat(), t.amount, t.category, t.type, t.note])
    output = io.BytesIO()
    output.write(si.getvalue().encode())
    output.seek(0)
    return send_file(output, mimetype='text/csv', as_attachment=True, download_name='transactions.csv')

@app.route('/import', methods=['POST'])
def import_csv():
    if 'file' not in request.files:
        flash("No file part", "danger")
        return redirect(url_for('transactions'))
    file = request.files['file']
    if file.filename == '':
        flash("No selected file", "danger")
        return redirect(url_for('transactions'))

    try:
        df = pd.read_csv(file)
        # expect columns: date, amount, category, type, note (id optional)
        for _, row in df.iterrows():
            date = pd.to_datetime(row['date']).date()
            amount = float(row['amount'])
            category = str(row.get('category', 'Uncategorized'))
            ttype = str(row.get('type', 'expense'))
            note = str(row.get('note', ''))
            tx = Transaction(date=date, amount=amount, category=category, type=ttype, note=note)
            db.session.add(tx)
        db.session.commit()
        flash("CSV imported successfully.", "success")
    except Exception as e:
        flash(f"Failed to import CSV: {e}", "danger")

    return redirect(url_for('transactions'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_transaction(id):
    tx = Transaction.query.get_or_404(id)
    db.session.delete(tx)
    db.session.commit()
    flash("Transaction deleted.", "success")
    return redirect(url_for('transactions'))
