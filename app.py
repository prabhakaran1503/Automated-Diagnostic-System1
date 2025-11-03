from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import numpy as np
import os
import sys
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
import json
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

# Fix directory creation issue
def ensure_directory_exists(directory):
    """Safely create directory if it doesn't exist"""
    try:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Directory created/verified: {directory}")
        return True
    except Exception as e:
        print(f"❌ Error creating directory {directory}: {e}")
        return False

# Configure upload folder with error handling
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
if not ensure_directory_exists(UPLOAD_FOLDER):
    print("⚠️  Warning: Could not create upload directory. File uploads may not work.")
    # Fallback to current directory
    app.config['UPLOAD_FOLDER'] = 'uploads'
    ensure_directory_exists(app.config['UPLOAD_FOLDER'])

# Global variables for ML model
ml_model = None
label_encoder = None

class AIDiagnosticSystem:
    def __init__(self):
        self.reference_ranges = {
            'glucose': {'normal': (70, 100), 'prediabetes': (100, 126), 'diabetes': (126, 400)},
            'systolic_bp': {'normal': (90, 120), 'elevated': (120, 130), 'hypertension1': (130, 140), 'hypertension2': (140, 200)},
            'diastolic_bp': {'normal': (60, 80), 'elevated': (80, 85), 'hypertension1': (85, 90), 'hypertension2': (90, 130)},
            'cholesterol': {'normal': (0, 200), 'borderline': (200, 240), 'high': (240, 400)},
            'bmi': {'underweight': (0, 18.5), 'normal': (18.5, 24.9), 'overweight': (25, 29.9), 'obese': (30, 50)}
        }
        
    def train_model(self):
        """Train ML model with synthetic data"""
        global ml_model, label_encoder
        
        try:
            print("🤖 Training AI model...")
            
            # Generate synthetic training data
            np.random.seed(42)
            n_samples = 1000
            
            # Create features
            age = np.random.randint(18, 80, n_samples)
            gender = np.random.choice(['Male', 'Female'], n_samples)
            glucose = np.random.normal(100, 30, n_samples)
            systolic_bp = np.random.normal(120, 15, n_samples)
            diastolic_bp = np.random.normal(80, 10, n_samples)
            cholesterol = np.random.normal(190, 30, n_samples)
            bmi = np.random.normal(25, 5, n_samples)
            
            # Create labels based on medical rules
            labels = []
            for i in range(n_samples):
                conditions = []
                
                # Check glucose
                if glucose[i] >= 126:
                    conditions.append(2)  # Diabetes
                elif glucose[i] >= 100:
                    conditions.append(1)  # Prediabetes
                else:
                    conditions.append(0)  # Normal
                    
                # Check BP
                if systolic_bp[i] >= 140 or diastolic_bp[i] >= 90:
                    conditions.append(2)  # Hypertension
                elif systolic_bp[i] >= 130 or diastolic_bp[i] >= 85:
                    conditions.append(1)  # Elevated
                else:
                    conditions.append(0)  # Normal
                    
                # Check cholesterol
                if cholesterol[i] >= 240:
                    conditions.append(2)  # High
                elif cholesterol[i] >= 200:
                    conditions.append(1)  # Borderline
                else:
                    conditions.append(0)  # Normal
                    
                # Check BMI
                if bmi[i] >= 30:
                    conditions.append(2)  # Obese
                elif bmi[i] >= 25:
                    conditions.append(1)  # Overweight
                elif bmi[i] < 18.5:
                    conditions.append(1)  # Underweight
                else:
                    conditions.append(0)  # Normal
                    
                # Overall risk level
                if any(c == 2 for c in conditions):
                    labels.append(2)  # High risk
                elif any(c == 1 for c in conditions):
                    labels.append(1)  # Moderate risk
                else:
                    labels.append(0)  # Normal
            
            # Create DataFrame
            X = pd.DataFrame({
                'age': age,
                'gender': gender,
                'glucose': glucose,
                'systolic_bp': systolic_bp,
                'diastolic_bp': diastolic_bp,
                'cholesterol': cholesterol,
                'bmi': bmi
            })
            
            # Encode gender
            label_encoder = LabelEncoder()
            X['gender'] = label_encoder.fit_transform(X['gender'])
            
            # Train model
            ml_model = DecisionTreeClassifier(max_depth=5, random_state=42)
            ml_model.fit(X, np.array(labels))
            
            print("✅ AI model trained successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error training model: {e}")
            return False
    
    def analyze_patient(self, patient_data):
        """Analyze patient data using both rule-based and ML approaches"""
        try:
            # Rule-based analysis
            rule_results = self.rule_based_analysis(patient_data)
            
            # ML prediction
            ml_results = self.ml_prediction(patient_data)
            
            # Generate visualization data
            viz_data = self.prepare_visualization_data(patient_data)
            
            return {
                'rule_results': rule_results,
                'ml_results': ml_results,
                'visualization': viz_data
            }
        except Exception as e:
            print(f"❌ Error analyzing patient: {e}")
            return {'error': str(e)}
    
    def rule_based_analysis(self, patient_data):
        """Perform rule-based medical analysis"""
        conditions = []
        risk_factors = []
        
        # Analyze glucose
        glucose = patient_data['glucose']
        if glucose >= 126:
            conditions.append("Diabetes")
            risk_factors.append("High glucose level")
        elif glucose >= 100:
            conditions.append("Prediabetes Risk")
            risk_factors.append("Elevated glucose level")
            
        # Analyze blood pressure
        systolic = patient_data['systolic_bp']
        diastolic = patient_data['diastolic_bp']
        
        if systolic >= 140 or diastolic >= 90:
            conditions.append("Hypertension")
            risk_factors.append("High blood pressure")
        elif systolic >= 130 or diastolic >= 85:
            conditions.append("Elevated Blood Pressure")
            risk_factors.append("Elevated blood pressure")
            
        # Analyze cholesterol
        cholesterol = patient_data['cholesterol']
        if cholesterol >= 240:
            conditions.append("High Cholesterol")
            risk_factors.append("High cholesterol level")
        elif cholesterol >= 200:
            conditions.append("Borderline High Cholesterol")
            risk_factors.append("Borderline cholesterol level")
            
        # Analyze BMI
        bmi = patient_data['bmi']
        if bmi >= 30:
            conditions.append("Obesity")
            risk_factors.append("High BMI")
        elif bmi >= 25:
            conditions.append("Overweight")
            risk_factors.append("Elevated BMI")
        elif bmi < 18.5:
            conditions.append("Underweight")
            risk_factors.append("Low BMI")
            
        # Determine overall risk level
        if len(conditions) == 0:
            risk_level = "Normal"
            risk_emoji = "🟢"
        elif len(conditions) <= 2:
            risk_level = "Moderate"
            risk_emoji = "🟡"
        else:
            risk_level = "High"
            risk_emoji = "🔴"
            
        # Generate recommendations
        recommendations = self.generate_recommendations(conditions, risk_factors)
        
        return {
            'conditions': conditions,
            'risk_factors': risk_factors,
            'risk_level': risk_level,
            'risk_emoji': risk_emoji,
            'recommendations': recommendations
        }
    
    def ml_prediction(self, patient_data):
        """Perform ML-based prediction"""
        global ml_model, label_encoder
        
        if ml_model is None:
            return {'error': 'Model not trained'}
        
        try:
            # Prepare features
            features = np.array([[
                patient_data['age'],
                label_encoder.transform([patient_data['gender']])[0],
                patient_data['glucose'],
                patient_data['systolic_bp'],
                patient_data['diastolic_bp'],
                patient_data['cholesterol'],
                patient_data['bmi']
            ]])
            
            # Make prediction
            prediction = ml_model.predict(features)[0]
            prediction_proba = ml_model.predict_proba(features)[0]
            
            risk_levels = ["Normal", "Moderate", "High"]
            predicted_risk = risk_levels[prediction]
            confidence = max(prediction_proba) * 100
            
            return {
                'predicted_risk': predicted_risk,
                'confidence': round(confidence, 1)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def generate_recommendations(self, conditions, risk_factors):
        """Generate personalized recommendations"""
        recommendations = [
            "Schedule regular check-ups with your healthcare provider",
            "Maintain a balanced diet rich in fruits and vegetables",
            "Engage in regular physical activity (30 minutes daily)"
        ]
        
        # Specific recommendations based on conditions
        if "Diabetes" in conditions or "Prediabetes Risk" in conditions:
            recommendations.extend([
                "Monitor blood glucose levels regularly",
                "Limit sugar and refined carbohydrate intake",
                "Consider consulting with an endocrinologist"
            ])
            
        if "Hypertension" in conditions or "Elevated Blood Pressure" in conditions:
            recommendations.extend([
                "Reduce sodium intake to less than 2,300mg per day",
                "Practice stress management techniques",
                "Monitor blood pressure regularly at home"
            ])
            
        if "High Cholesterol" in conditions or "Borderline High Cholesterol" in conditions:
            recommendations.extend([
                "Choose foods low in saturated fat and cholesterol",
                "Increase intake of omega-3 fatty acids",
                "Consider cholesterol-lowering medications if prescribed"
            ])
            
        if "Obesity" in conditions or "Overweight" in conditions:
            recommendations.extend([
                "Create a calorie-controlled meal plan",
                "Increase physical activity gradually",
                "Consider consulting with a nutritionist"
            ])
            
        if "Underweight" in conditions:
            recommendations.extend([
                "Increase calorie intake with nutrient-dense foods",
                "Include strength training exercises",
                "Consult with a healthcare provider for weight gain plan"
            ])
            
        return recommendations
    
    def prepare_visualization_data(self, patient_data):
        """Prepare data for visualization"""
        metrics = ['Glucose', 'Systolic BP', 'Diastolic BP', 'Cholesterol', 'BMI']
        values = [
            patient_data['glucose'],
            patient_data['systolic_bp'],
            patient_data['diastolic_bp'],
            patient_data['cholesterol'],
            patient_data['bmi']
        ]
        
        # Normal ranges
        normal_ranges = [
            {'min': 70, 'max': 100},  # Glucose
            {'min': 90, 'max': 120},  # Systolic BP
            {'min': 60, 'max': 80},   # Diastolic BP
            {'min': 0, 'max': 200},   # Cholesterol
            {'min': 18.5, 'max': 24.9}  # BMI
        ]
        
        # Determine colors
        colors = []
        for i, metric in enumerate(metrics):
            value = values[i]
            range_data = normal_ranges[i]
            
            if metric == 'Glucose':
                if value < 70:
                    colors.append('#3498db')  # Blue - Low
                elif value <= 100:
                    colors.append('#2ecc71')  # Green - Normal
                elif value <= 126:
                    colors.append('#f39c12')  # Orange - Prediabetes
                else:
                    colors.append('#e74c3c')  # Red - Diabetes
            elif metric == 'Systolic BP':
                if value < 90:
                    colors.append('#3498db')
                elif value <= 120:
                    colors.append('#2ecc71')
                elif value <= 130:
                    colors.append('#f39c12')
                else:
                    colors.append('#e74c3c')
            elif metric == 'Diastolic BP':
                if value < 60:
                    colors.append('#3498db')
                elif value <= 80:
                    colors.append('#2ecc71')
                elif value <= 85:
                    colors.append('#f39c12')
                else:
                    colors.append('#e74c3c')
            elif metric == 'Cholesterol':
                if value < 200:
                    colors.append('#2ecc71')
                elif value < 240:
                    colors.append('#f39c12')
                else:
                    colors.append('#e74c3c')
            elif metric == 'BMI':
                if value < 18.5:
                    colors.append('#3498db')
                elif value < 25:
                    colors.append('#2ecc71')
                elif value < 30:
                    colors.append('#f39c12')
                else:
                    colors.append('#e74c3c')
        
        return {
            'metrics': metrics,
            'values': values,
            'normal_ranges': normal_ranges,
            'colors': colors
        }

# Initialize AI system
ai_system = AIDiagnosticSystem()

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Error loading template: {e}", 500

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        result = ai_system.analyze_patient(data)
        if 'error' in result:
            return jsonify(result), 500
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload_csv', methods=['POST'])
def upload_csv():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and file.filename.endswith('.csv'):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            
            # Read CSV
            df = pd.read_csv(filename)
            
            # Get first patient data
            first_patient = df.iloc[0].to_dict()
            
            return jsonify({
                'success': True,
                'patient_data': first_patient,
                'total_records': len(df)
            })
        else:
            return jsonify({'error': 'Invalid file format. Please upload a CSV file.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate_sample')
def generate_sample():
    """Generate sample patient data"""
    try:
        np.random.seed(42)
        sample_data = {
            'patient_id': f"SAMPLE_{np.random.randint(1000, 9999)}",
            'age': np.random.randint(25, 75),
            'gender': np.random.choice(["Male", "Female"]),
            'glucose': np.random.randint(70, 180),
            'systolic_bp': np.random.randint(90, 160),
            'diastolic_bp': np.random.randint(60, 100),
            'cholesterol': np.random.randint(150, 280),
            'bmi': round(np.random.uniform(18, 35), 1)
        }
        return jsonify(sample_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_trained': ml_model is not None,
        'upload_folder': app.config['UPLOAD_FOLDER']
    })

if __name__ == '__main__':
    print("🚀 Starting AI Diagnostic System...")
    print(f"📁 Upload folder: {app.config['UPLOAD_FOLDER']}")
    
    # Train model on startup
    if ai_system.train_model():
        print("✅ System ready!")
        print("🌐 Open http://localhost:5000 in your browser")
    else:
        print("❌ Failed to train model. System may not work properly.")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("🔄 Trying alternative port 5001...")
        app.run(debug=True, host='0.0.0.0', port=5001)