from flask import request, redirect, url_for, render_template, flash
from models import db, Customer, Transaction  # Import db and models

def setup_routes(app):
    @app.route('/')
    def index():
        # Calculations for dashboard
        income = db.session.query(db.func.sum(Transaction.amount)).filter_by(type="income").scalar() or 0
        expenses = db.session.query(db.func.sum(Transaction.amount)).filter_by(type="expense").scalar() or 0
        profit = income - expenses
        transactions = Transaction.query.order_by(Transaction.date.desc()).limit(5).all()
        return render_template('index.html', income=income, expenses=expenses, profit=profit, transactions=transactions)

    @app.route('/add_transaction', methods=['GET', 'POST'])
    def add_transaction():
        if request.method == 'POST':
            type = request.form['type']
            amount = float(request.form['amount'])
            description = request.form['description']
            customer_id = request.form.get('customer_id')
            transaction = Transaction(type=type, amount=amount, description=description, customer_id=customer_id)
            db.session.add(transaction)
            db.session.commit()
            flash('Transaction added successfully')
            return redirect(url_for('index'))
        customers = Customer.query.all()
        return render_template('add_transaction.html', customers=customers)

    @app.route('/view_transactions')
    def view_transactions():
        transactions = Transaction.query.order_by(Transaction.date.desc()).all()
        return render_template('view_transactions.html', transactions=transactions)

    @app.route('/add_customer', methods=['GET', 'POST'])
    def add_customer():
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            customer = Customer(name=name, email=email)
            db.session.add(customer)
            db.session.commit()
            flash('Customer added successfully')
            return redirect(url_for('view_customers'))
        return render_template('add_customer.html')

    @app.route('/view_customers')
    def view_customers():
        customers = Customer.query.all()
        return render_template('view_customers.html', customers=customers)
