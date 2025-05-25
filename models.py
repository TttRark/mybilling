from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ledgers = db.relationship('Ledger', backref='owner', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Ledger(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transactions = db.relationship('Transaction', backref='ledger', lazy='dynamic')

    @property
    def balance(self):
        income = self.transactions.filter_by(transaction_type='income')\
                     .with_entities(db.func.sum(Transaction.amount)).scalar() or 0
        expense = self.transactions.filter_by(transaction_type='expense')\
                      .with_entities(db.func.sum(Transaction.amount)).scalar() or 0
        return income - expense

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(256))
    category = db.Column(db.String(64))
    transaction_type = db.Column(db.String(20), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ledger_id = db.Column(db.Integer, db.ForeignKey('ledger.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 