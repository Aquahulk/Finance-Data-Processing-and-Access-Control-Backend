import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, User, FinancialRecord, RoleType, UserStatus
from schemas import ma, user_schema, users_schema, financial_record_schema, financial_records_schema
from auth import admin_required, analyst_required, viewer_required, get_current_user
from datetime import datetime
from sqlalchemy import func

app = Flask(__name__)

# Handle SQLite path for serverless (writable /tmp folder)
if os.environ.get('VERCEL'):
    db_path = '/tmp/finance.db'
else:
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'finance.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
ma.init_app(app)
CORS(app)

# Create the database and seed it with an initial admin user
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password='admin_password', role=RoleType.ADMIN.value)
        db.session.add(admin)
        db.session.commit()
        print("Admin user created.")

# Error Handlers
@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": str(e)}), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404

@app.route('/')
def index():
    return jsonify({
        "message": "Welcome to the Finance Data Processing API",
        "endpoints": {
            "auth_mock": "Use X-User-ID header (1 for Admin)",
            "users": "/users",
            "records": "/records",
            "summary": "/dashboard/summary"
        }
    })

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

# User Management (Admin only)
@app.route('/users', methods=['GET'])
@admin_required
def list_users():
    users = User.query.all()
    # Formatting response to match requested structure
    return jsonify([{
        "id": user.id,
        "name": user.username,
        "role": user.role,
        "status": user.status
    } for user in users])

@app.route('/users', methods=['POST'])
@admin_required
def create_user():
    data = request.json
    try:
        user = user_schema.load(data)
        db.session.add(user)
        db.session.commit()
        return user_schema.jsonify(user), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/users/<int:id>', methods=['PATCH'])
@admin_required
def update_user(id):
    user = User.query.get_or_404(id)
    data = request.json
    if 'role' in data:
        user.role = data['role']
    if 'status' in data:
        user.status = data['status']
    db.session.commit()
    return user_schema.jsonify(user)

# Financial Transactions (RBAC)
@app.route('/transactions', methods=['POST'])
@admin_required # Only admin can create
def create_transaction():
    data = request.json
    try:
        record = financial_record_schema.load(data)
        record.created_by = get_current_user().id
        db.session.add(record)
        db.session.commit()
        return financial_record_schema.jsonify(record), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/transactions', methods=['GET'])
@analyst_required # Analysts and admins can view list
def list_transactions():
    query = FinancialRecord.query
    
    # Filtering as per request
    type = request.args.get('type')
    category = request.args.get('category')
    start_date = request.args.get('startDate') # CamelCase as requested

    if type:
        query = query.filter(FinancialRecord.type == type)
    if category:
        query = query.filter(FinancialRecord.category == category)
    if start_date:
        query = query.filter(FinancialRecord.date >= datetime.fromisoformat(start_date))
    
    records = query.all()
    return jsonify([{
        "id": r.id,
        "amount": r.amount,
        "type": r.type,
        "category": r.category,
        "date": r.date.strftime('%Y-%m-%d'),
        "description": r.description
    } for r in records])

@app.route('/transactions/<int:id>', methods=['PUT']) # Changed to PUT as requested
@admin_required # Only admin can update
def update_transaction(id):
    record = FinancialRecord.query.get_or_404(id)
    data = request.json
    try:
        if 'amount' in data:
            record.amount = data['amount']
        if 'type' in data:
            record.type = data['type']
        if 'category' in data:
            record.category = data['category']
        if 'description' in data:
            record.description = data['description']
        if 'date' in data:
            record.date = datetime.fromisoformat(data['date'])
        db.session.commit()
        return financial_record_schema.jsonify(record)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/transactions/<int:id>', methods=['DELETE'])
@admin_required # Only admin can delete
def delete_transaction(id):
    record = FinancialRecord.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    return jsonify({"message": "Transaction deleted successfully"}), 200

# Dashboard Summary APIs (Viewer, Analyst, or Admin)
@app.route('/dashboard/summary', methods=['GET'])
@viewer_required # As per request, Viewer can call this
def dashboard_summary():
    income = db.session.query(func.sum(FinancialRecord.amount)).filter(FinancialRecord.type == 'income').scalar() or 0
    expense = db.session.query(func.sum(FinancialRecord.amount)).filter(FinancialRecord.type == 'expense').scalar() or 0
    balance = income - expense

    # Top Categories (Group by category, sum amount, order by sum desc)
    category_totals = db.session.query(
        FinancialRecord.category, 
        func.sum(FinancialRecord.amount)
    ).group_by(FinancialRecord.category).order_by(func.sum(FinancialRecord.amount).desc()).limit(5).all()
    
    top_categories = [{"category": cat, "amount": total} for cat, total in category_totals]

    # Recent Transactions
    recent_transactions = FinancialRecord.query.order_by(FinancialRecord.date.desc()).limit(5).all()
    recent_list = [{
        "amount": r.amount,
        "type": r.type,
        "category": r.category,
        "date": r.date.strftime('%Y-%m-%d')
    } for r in recent_transactions]

    # Monthly Trend (Group by Month)
    # This is a bit more complex in SQLite, using strftime to get month
    monthly_stats = db.session.query(
        func.strftime('%m', FinancialRecord.date).label('month'),
        func.sum(FinancialRecord.amount).filter(FinancialRecord.type == 'income').label('income'),
        func.sum(FinancialRecord.amount).filter(FinancialRecord.type == 'expense').label('expense')
    ).group_by(func.strftime('%m', FinancialRecord.date)).all()

    month_names = {
        '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr',
        '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug',
        '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
    }

    monthly_trend = [{
        "month": month_names.get(m, m),
        "income": float(inc or 0),
        "expense": float(exp or 0)
    } for m, inc, exp in monthly_stats]

    return jsonify({
        "totalIncome": income,
        "totalExpense": expense,
        "netBalance": balance,
        "topCategories": top_categories,
        "recentTransactions": recent_list,
        "monthlyTrend": monthly_trend
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
