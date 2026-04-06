from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, User, FinancialRecord, RoleType, UserStatus
from schemas import ma, user_schema, users_schema, financial_record_schema, financial_records_schema
from auth import admin_required, analyst_required, viewer_required, get_current_user
from datetime import datetime
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
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

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

# User Management (Admin only)
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

@app.route('/users', methods=['GET'])
@admin_required
def list_users():
    users = User.query.all()
    return users_schema.jsonify(users)

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

# Financial Records (RBAC)
@app.route('/records', methods=['POST'])
@admin_required # Only admin can create records as per requirement
def create_record():
    data = request.json
    try:
        record = financial_record_schema.load(data)
        record.created_by = get_current_user().id
        db.session.add(record)
        db.session.commit()
        return financial_record_schema.jsonify(record), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/records', methods=['GET'])
@viewer_required # Viewers, analysts, admins can view
def list_records():
    query = FinancialRecord.query
    
    # Filtering
    type = request.args.get('type')
    category = request.args.get('category')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if type:
        query = query.filter(FinancialRecord.type == type)
    if category:
        query = query.filter(FinancialRecord.category == category)
    if start_date:
        query = query.filter(FinancialRecord.date >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(FinancialRecord.date <= datetime.fromisoformat(end_date))
    
    records = query.all()
    return financial_records_schema.jsonify(records)

@app.route('/records/<int:id>', methods=['PATCH'])
@admin_required # Only admin can update
def update_record(id):
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
        db.session.commit()
        return financial_record_schema.jsonify(record)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/records/<int:id>', methods=['DELETE'])
@admin_required # Only admin can delete
def delete_record(id):
    record = FinancialRecord.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    return jsonify({"message": "Record deleted successfully"}), 200

# Dashboard Summary APIs (Analyst or Admin)
@app.route('/dashboard/summary', methods=['GET'])
@analyst_required
def dashboard_summary():
    income = db.session.query(func.sum(FinancialRecord.amount)).filter(FinancialRecord.type == 'income').scalar() or 0
    expense = db.session.query(func.sum(FinancialRecord.amount)).filter(FinancialRecord.type == 'expense').scalar() or 0
    balance = income - expense

    category_totals = db.session.query(
        FinancialRecord.category, 
        func.sum(FinancialRecord.amount)
    ).group_by(FinancialRecord.category).all()
    
    category_summary = {cat: total for cat, total in category_totals}

    recent_activity = FinancialRecord.query.order_by(FinancialRecord.date.desc()).limit(5).all()

    return jsonify({
        "total_income": income,
        "total_expense": expense,
        "net_balance": balance,
        "category_summary": category_summary,
        "recent_activity": financial_records_schema.dump(recent_activity)
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
