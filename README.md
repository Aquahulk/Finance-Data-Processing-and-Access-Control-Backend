# 📊 Finance Data Processing & RBAC Backend

A robust Flask-based backend for a finance dashboard system featuring **Role-Based Access Control (RBAC)**, transaction management, and automated financial insights.

---

## 🚀 Key Features

- **Dashboard Summary**: Real-time aggregation of financial data (Income, Expense, Net Balance, Top Categories, Monthly Trends).
- **Transaction Management**: Full CRUD operations for financial records with advanced filtering.
- **User & Role Management**: Admin panel to manage users with specific roles and statuses.
- **Strict RBAC**: Secure access control for Viewers, Analysts, and Admins.
- **Data Validation**: Schema-based validation using Marshmallow.
- **Persistent Storage**: SQLite database with SQLAlchemy ORM.

---

## 🛠️ Technology Stack

- **Framework**: Flask
- **Database**: SQLite with Flask-SQLAlchemy
- **Serialization**: Flask-Marshmallow
- **CORS**: Flask-CORS
- **Language**: Python 3.x

---

## 🚦 Getting Started

### 1. Prerequisites
Ensure you have Python 3.x installed on your system.

### 2. Installation
Clone the repository and install the required dependencies:
```bash
pip install -r requirements.txt
```

### 3. Run the Application
Start the Flask development server:
```bash
python app.py
```
The API will be available at `http://localhost:5000`.

### 4. Deploy to Vercel
This project is configured for Vercel out of the box. 
1. Push your changes to GitHub.
2. Connect your repo to Vercel.
3. Vercel will automatically detect `vercel.json` and deploy the Flask app.
*Note: SQLite data will reset on every serverless function cold start in `/tmp`.*

### 5. Authentication (Mock)
This project uses a custom header `X-User-ID` to simulate authentication for development and testing.
- An initial **Admin** user is seeded on the first run with `id=1`.
- To act as an Admin, include the header `X-User-ID: 1` in your API requests.

---

## 🔐 Role-Based Access Control (RBAC)

| Role | Access Level | Description |
| :--- | :--- | :--- |
| **Viewer** | Restricted | Can only view the Dashboard Summary. |
| **Analyst** | Intermediate | Can view Dashboard Summary and the Transactions List. |
| **Admin** | Full | Can access everything, including CRUD operations and User Management. |

---

## 📡 API Documentation

### 1. Dashboard Summary (Most Important)
Get a high-level overview of the financial health.
- **Endpoint**: `GET /dashboard/summary`
- **Access**: Viewer, Analyst, Admin
- **Response**:
```json
{
  "totalIncome": 50000,
  "totalExpense": 30000,
  "netBalance": 20000,
  "topCategories": [
    { "category": "Food", "amount": 10000 },
    { "category": "Rent", "amount": 15000 }
  ],
  "recentTransactions": [
    {
      "amount": 2000,
      "type": "expense",
      "category": "Food",
      "date": "2026-04-05"
    }
  ],
  "monthlyTrend": [
    { "month": "Jan", "income": 10000, "expense": 8000 },
    { "month": "Feb", "income": 15000, "expense": 9000 }
  ]
}
```

### 2. Transactions List (With Filtering)
Retrieve all financial records with optional filtering.
- **Endpoint**: `GET /transactions`
- **Access**: Analyst, Admin
- **Example**: `/transactions?type=expense&category=Food&startDate=2026-01-01`
- **Response**:
```json
[
  {
    "id": 1,
    "amount": 500,
    "type": "expense",
    "category": "Food",
    "date": "2026-04-01",
    "description": "Lunch"
  }
]
```

### 3. Transaction CRUD Operations
Modify financial data.
- **Endpoints**:
  - `POST /transactions`: Create a new record.
  - `PUT /transactions/:id`: Update an existing record.
  - `DELETE /transactions/:id`: Remove a record.
- **Access**: Admin Only

### 4. User Management
Manage platform users and their roles.
- **Endpoint**: `GET /users`
- **Access**: Admin Only
- **Response**:
```json
[
  {
    "id": 1,
    "name": "Amit",
    "role": "admin",
    "status": "active"
  }
]
```

---

## 🧪 Testing the API
You can use tools like **Postman**, **Insomnia**, or **cURL** to test the endpoints. Remember to include the `X-User-ID` header.

Example using cURL to get the dashboard summary as an Admin:
```bash
curl -H "X-User-ID: 1" http://localhost:5000/dashboard/summary
```

---

## 📂 Project Structure
- `app.py`: Main application entry point and routes.
- `models.py`: SQLAlchemy database models.
- `auth.py`: RBAC decorators and authentication logic.
- `schemas.py`: Marshmallow validation schemas.
- `requirements.txt`: Project dependencies.
