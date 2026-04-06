import requests
import json
import time
import subprocess
import os
import signal

# Start the Flask app
# process = subprocess.Popen(['python', 'app.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# time.sleep(2) # Wait for the app to start

BASE_URL = 'http://localhost:5000'
ADMIN_HEADER = {'X-User-ID': '1'}

def test_flow():
    print("Testing flow...")
    
    # 1. Test Admin access: Create a user
    print("1. Creating a new analyst user...")
    resp = requests.post(f"{BASE_URL}/users", headers=ADMIN_HEADER, json={
        "username": "analyst1",
        "password": "password",
        "role": "analyst"
    })
    print(f"Status: {resp.status_code}, Body: {resp.json()}")
    analyst_id = str(resp.json().get('id'))
    ANALYST_HEADER = {'X-User-ID': analyst_id}

    # 2. Test Admin access: Create a financial record
    print("2. Creating a financial record...")
    resp = requests.post(f"{BASE_URL}/records", headers=ADMIN_HEADER, json={
        "amount": 1000.50,
        "type": "income",
        "category": "Salary",
        "description": "Monthly salary"
    })
    print(f"Status: {resp.status_code}, Body: {resp.json()}")

    # 3. Test Analyst access: View records
    print("3. Analyst viewing records...")
    resp = requests.get(f"{BASE_URL}/records", headers=ANALYST_HEADER)
    print(f"Status: {resp.status_code}, Body: {len(resp.json())} records found")

    # 4. Test Analyst access: Get dashboard summary
    print("4. Analyst getting dashboard summary...")
    resp = requests.get(f"{BASE_URL}/dashboard/summary", headers=ANALYST_HEADER)
    print(f"Status: {resp.status_code}, Body: {resp.json()}")

    # 5. Test RBAC: Analyst trying to create a record (should fail)
    print("5. Analyst trying to create a record (should be Admin only)...")
    resp = requests.post(f"{BASE_URL}/records", headers=ANALYST_HEADER, json={
        "amount": 500,
        "type": "expense",
        "category": "Food"
    })
    print(f"Status: {resp.status_code}, Body: {resp.json()}")

    # 6. Test Filtering
    print("6. Testing record filtering by type=income...")
    resp = requests.get(f"{BASE_URL}/records?type=income", headers=ANALYST_HEADER)
    print(f"Status: {resp.status_code}, Body: {len(resp.json())} records found")

if __name__ == '__main__':
    try:
        test_flow()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Kill the Flask process
        # os.kill(process.pid, signal.SIGTERM)
        print("Tests finished.")
