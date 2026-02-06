from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hrms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------ Models ------------------

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(50), db.ForeignKey('employee.emp_id'), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(10), nullable=False)

# ------------------ Routes ------------------

@app.route('/')
def home():
    return render_template('index.html')

# ------------------ Employee APIs ------------------

def valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

@app.route('/api/employees', methods=['POST'])
def add_employee():
    data = request.json
    if not all(k in data for k in ("emp_id", "name", "email", "department")):
        return jsonify({"error": "All fields required"}), 400
    
    if not valid_email(data['email']):
        return jsonify({"error": "Invalid email"}), 400

    if Employee.query.filter_by(emp_id=data['emp_id']).first():
        return jsonify({"error": "Duplicate Employee ID"}), 400

    emp = Employee(**data)
    db.session.add(emp)
    db.session.commit()
    return jsonify({"message": "Employee added"}), 201

@app.route('/api/employees', methods=['GET'])
def get_employees():
    employees = Employee.query.all()
    result = [{
        "emp_id": e.emp_id,
        "name": e.name,
        "email": e.email,
        "department": e.department
    } for e in employees]
    return jsonify(result)

@app.route('/api/employees/<emp_id>', methods=['DELETE'])
def delete_employee(emp_id):
    emp = Employee.query.filter_by(emp_id=emp_id).first()
    if not emp:
        return jsonify({"error": "Employee not found"}), 404
    db.session.delete(emp)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200

# ------------------ Attendance APIs ------------------

@app.route('/api/attendance', methods=['POST'])
def mark_attendance():
    data = request.json
    if not all(k in data for k in ("emp_id", "date", "status")):
        return jsonify({"error": "All fields required"}), 400

    att = Attendance(**data)
    db.session.add(att)
    db.session.commit()
    return jsonify({"message": "Attendance marked"}), 201

@app.route('/api/attendance/<emp_id>', methods=['GET'])
def get_attendance(emp_id):
    records = Attendance.query.filter_by(emp_id=emp_id).all()
    result = [{
        "date": r.date,
        "status": r.status
    } for r in records]
    return jsonify(result)

# ------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
