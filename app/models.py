from . import db
from datetime import datetime

class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(64), nullable=False)
    type = db.Column(db.String(16), nullable=False)  # 'income' or 'expense'
    note = db.Column(db.String(255))

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "amount": self.amount,
            "category": self.category,
            "type": self.type,
            "note": self.note,
        }
