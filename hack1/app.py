from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'diagnostic_system_secret_key' # Used for flashing messages

# --- Database Initialization ---
def init_db():
    """Creates the database and table if they don't exist."""
    if not os.path.exists('database'):
        os.makedirs('database')
    
    conn = sqlite3.connect('database/patients.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        gender TEXT NOT NULL,
        glucose REAL,
        systolic_bp REAL,
        diastolic_bp REAL,
        cholesterol REAL,
        diagnosis TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

# --- Core Logic ---
def analyze_patient_data(data):
    """Analyzes patient data and returns a dictionary of results."""
    results = []
    
    # Check glucose level
    try:
        glucose = float(data.get('glucose', 0))
        if glucose > 140:
            results.append({'parameter': 'Glucose', 'value': glucose, 'status': 'risk', 'message': 'Possible diabetes risk'})
        else:
            results.append({'parameter': 'Glucose', 'value': glucose, 'status': 'normal', 'message': 'Normal glucose level'})
    except (ValueError, TypeError):
        results.append({'parameter': 'Glucose', 'value': 'N/A', 'status': 'error', 'message': 'Invalid input'})

    # Check blood pressure
    try:
        systolic = float(data.get('systolic_bp', 0))
        diastolic = float(data.get('diastolic_bp', 0))
        if systolic > 140 or diastolic > 90:
            results.append({'parameter': 'Blood Pressure', 'value': f"{systolic}/{diastolic}", 'status': 'risk', 'message': 'Possible hypertension'})
        else:
            results.append({'parameter': 'Blood Pressure', 'value': f"{systolic}/{diastolic}", 'status': 'normal', 'message': 'Normal blood pressure'})
    except (ValueError, TypeError):
        results.append({'parameter': 'Blood Pressure', 'value': 'N/A', 'status': 'error', 'message': 'Invalid input'})

    # Check cholesterol
    try:
        cholesterol = float(data.get('cholesterol', 0))
        if cholesterol > 200:
            results.append({'parameter': 'Cholesterol', 'value': cholesterol, 'status': 'risk', 'message': 'High cholesterol risk'})
        else:
            results.append({'parameter': 'Cholesterol', 'value': cholesterol, 'status': 'normal', 'message': 'Normal cholesterol level'})
    except (ValueError, TypeError):
        results.append({'parameter': 'Cholesterol', 'value': 'N/A', 'status': 'error', 'message': 'Invalid input'})
    
    # Overall assessment
    risk_count = sum(1 for r in results if r['status'] == 'risk')
    if risk_count > 0:
        overall_status = 'risk'
        overall_message = f'{risk_count} potential health risk(s) detected'
    else:
        overall_status = 'normal'
        overall_message = 'All parameters normal ✅'
    
    return {
        'results': results,
        'overall_status': overall_status,
        'overall_message': overall_message
    }

def save_patient_data(data, diagnosis):
    """Saves patient data and diagnosis to the SQLite database."""
    conn = sqlite3.connect('database/patients.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO patients (name, age, gender, glucose, systolic_bp, diastolic_bp, cholesterol, diagnosis)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('name'),
        data.get('age'),
        data.get('gender'),
        data.get('glucose'),
        data.get('systolic_bp'),
        data.get('diastolic_bp'),
        data.get('cholesterol'),
        diagnosis
    ))
    
    conn.commit()
    conn.close()

# --- Routes ---
@app.route('/')
def index():
    """Renders the main input form page."""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Processes the form data, analyzes it, and shows the results."""
    patient_data = {
        'name': request.form.get('name'),
        'age': request.form.get('age'),
        'gender': request.form.get('gender'),
        'glucose': request.form.get('glucose'),
        'systolic_bp': request.form.get('systolic_bp'),
        'diastolic_bp': request.form.get('diastolic_bp'),
        'cholesterol': request.form.get('cholesterol')
    }
    
    analysis = analyze_patient_data(patient_data)
    save_patient_data(patient_data, analysis['overall_message'])
    
    # FIX: Generate the date here in Python and pass it to the template
    current_date = datetime.now().strftime('%B %d, %Y at %I:%M %p')
    
    return render_template('result.html', 
                          patient_data=patient_data, 
                          analysis=analysis,
                          current_date=current_date) # Pass the date to the template

@app.route('/history')
def history():
    """Shows a history of all patient records."""
    conn = sqlite3.connect('database/patients.db')
    conn.row_factory = sqlite3.Row # This allows accessing columns by name
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM patients ORDER BY created_at DESC LIMIT 20')
    patients = cursor.fetchall()
    
    conn.close()
    
    return render_template('history.html', patients=patients)

# --- Main Execution ---
if __name__ == '__main__':
    init_db() # Initialize the database before running the app
    app.run(debug=True)