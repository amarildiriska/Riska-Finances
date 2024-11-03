from flask import Flask, render_template, redirect, url_for, flash, request
from models import db, Customer, Transaction
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///riska_finance.db'
app.config['SECRET_KEY'] = 'your_secret_key'

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    income = db.session.query(db.func.sum(Transaction.amount)).filter_by(type="income").scalar() or 0
    expenses = db.session.query(db.func.sum(Transaction.amount)).filter_by(type="expense").scalar() or 0
    profit = income - expenses
    recent_transactions = Transaction.query.order_by(Transaction.date.desc()).limit(5).all()
    return render_template('index.html', income=income, expenses=expenses, profit=profit, transactions=recent_transactions)

@app.route('/add_transaction', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        try:
            date = request.form['date']  # Get the date from the form
            type = request.form['type']
            amount = float(request.form['amount'])
            description = request.form['description']
            customer_id = request.form.get('customer_id', None)
            new_transaction = Transaction(
                date=datetime.strptime(date, '%Y-%m-%d'),  # Parse the date string to a datetime object
                type=type, 
                amount=amount, 
                description=description, 
                customer_id=customer_id
            )
            db.session.add(new_transaction)
            db.session.commit()
            flash('Transaction added successfully', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f"Error adding transaction: {e}", "danger")
            return redirect(url_for('add_transaction'))
    customers = Customer.query.all()
    return render_template('add_transaction.html', customers=customers)

@app.route('/view_transactions')
def view_transactions():
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    return render_template('view_transactions.html', transactions=transactions)

# Edit Transaction
@app.route('/edit_transaction/<int:id>', methods=['GET', 'POST'])
def edit_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    if request.method == 'POST':
        try:
            transaction.date = request.form['date']  # Update date
            transaction.type = request.form['type']
            transaction.amount = float(request.form['amount'])
            transaction.description = request.form['description']
            db.session.commit()
            flash('Transaction updated successfully', 'success')
            return redirect(url_for('view_transactions'))
        except Exception as e:
            flash(f"Error updating transaction: {e}", "danger")
    return render_template('edit_transaction.html', transaction=transaction)

# Delete Transaction
@app.route('/delete_transaction/<int:id>', methods=['POST'])
def delete_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    try:
        db.session.delete(transaction)
        db.session.commit()
        flash('Transaction deleted successfully', 'success')
    except Exception as e:
        flash(f"Error deleting transaction: {e}", "danger")
    return redirect(url_for('view_transactions'))

@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            new_customer = Customer(name=name, email=email)
            db.session.add(new_customer)
            db.session.commit()
            flash('Customer added successfully', 'success')
            return redirect(url_for('view_customers'))
        except Exception as e:
            flash(f"Error adding customer: {e}", "danger")
            return redirect(url_for('add_customer'))
    return render_template('add_customer.html')

@app.route('/view_customers')
def view_customers():
    customers = Customer.query.all()
    return render_template('view_customers.html', customers=customers)

# Edit Customer
@app.route('/edit_customer/<int:id>', methods=['GET', 'POST'])
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    if request.method == 'POST':
        try:
            customer.name = request.form['name']
            customer.email = request.form['email']
            db.session.commit()
            flash('Customer updated successfully', 'success')
            return redirect(url_for('view_customers'))
        except Exception as e:
            flash(f"Error updating customer: {e}", "danger")
    return render_template('edit_customer.html', customer=customer)

# Delete Customer
@app.route('/delete_customer/<int:id>', methods=['POST'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    try:
        db.session.delete(customer)
        db.session.commit()
        flash('Customer deleted successfully', 'success')
    except Exception as e:
        flash(f"Error deleting customer: {e}", "danger")
    return redirect(url_for('view_customers'))

# Reports Route
@app.route('/report', methods=['GET', 'POST'])
def report():
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    query = Transaction.query
    if start_date:
        query = query.filter(Transaction.date >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(Transaction.date <= datetime.strptime(end_date, '%Y-%m-%d'))

    transactions = query.order_by(Transaction.date).all()
    income = sum(t.amount for t in transactions if t.type == 'income')
    expenses = sum(t.amount for t in transactions if t.type == 'expense')
    profit = income - expenses

    return render_template('report.html', transactions=transactions, income=income, expenses=expenses, profit=profit)

# Error handling for 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
