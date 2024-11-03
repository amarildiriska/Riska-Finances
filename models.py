from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()  # Initialize SQLAlchemy instance

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True)
    transactions = db.relationship('Transaction', backref='customer', lazy=True)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10))  # "income" or "expense"
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(100))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
