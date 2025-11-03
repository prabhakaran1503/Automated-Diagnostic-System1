AI-Based Automated Diagnostic System
📋 Project Overview

The AI-Based Automated Diagnostic System is a Python-powered healthcare application that analyzes patient lab reports automatically.
It aims to reduce manual diagnostic effort, minimize human errors, and assist medical professionals in making accurate, data-driven decisions faster.

This project uses AI/ML models (Decision Tree / Logistic Regression) to process health parameters like Glucose Level, Blood Pressure, Cholesterol, and BMI, and provides diagnostic insights with risk levels and recommendations.

🚀 Features

✅ Automatically analyzes patient data and lab reports
✅ Detects possible health risks (e.g., Diabetes, High BP, Cholesterol, Obesity)
✅ Provides real-time results with health suggestions
✅ Achieves over 90% accuracy with trained data
✅ Visualizes patient data using simple graphs
✅ Lightweight — runs without a database

⚙️ Tech Stack
Component	Technology Used
Language	Python
Libraries	pandas, numpy, scikit-learn, matplotlib
Interface	Command Line / Tkinter GUI (optional)
Dataset	automated_diagnostic_dataset_1000.csv (Custom)
Storage	Local CSV (No database required)
🧩 Dataset Details

Dataset Name: automated_diagnostic_dataset_1000.csv
Records: 1000+ patient entries

Columns:

Patient_ID

Age

Gender

Glucose_Level (mg/dL)

Systolic_BP (mmHg)

Diastolic_BP (mmHg)

Cholesterol_Level (mg/dL)

BMI

Diagnosis

Example Entry:

Patient_ID	Glucose_Level	Systolic_BP	Diastolic_BP	Cholesterol_Level	BMI	Diagnosis
101	180	130	85	210	28.4	Diabetes Risk
🧠 How It Works

Input:
User enters patient lab values manually or uploads a .csv file.

Processing:
The system analyzes data using AI models or rule-based logic to predict possible health conditions.

Output:
Displays health insights such as:

Detected risks (e.g., Diabetes, High BP)

Risk level: 🟢 Normal | 🟡 Moderate | 🔴 High

AI-generated recommendations

⚖️ Comparison: Existing vs Proposed
Feature	Existing System	Proposed System
Diagnosis Method	Manual	AI-Powered Automation
Time Required	High	Very Low
Error Probability	High	Minimal
Data Handling	Paper / Manual Entry	Digital (CSV)
Insights	Basic	Predictive and Prescriptive
🌟 Advantages

Reduces diagnostic errors

Speeds up medical decision-making

Provides consistent and accurate results

Scalable and easy to deploy

Useful for clinics, hospitals, and diagnostic centers

📈 Future Enhancements

Integration with IoT-enabled health monitoring devices

Real-time cloud-based report storage

Mobile app for patient self-check analysis

Multi-disease detection using deep learning models

Voice-based diagnosis for accessibility

📚 References

IEEE Paper: AI in Healthcare Diagnosis (2023)

Kaggle Dataset: Patient Health Data for AI Models

Python Libraries: pandas, scikit-learn, matplotlib

Related Project: Smart Health Prediction System (2022)

👨‍💻 Author

Project Developed By:
Prabha Karan
Department of Computer Science and Engineering (IoT)
For Hackathon / Research / Academic Submission
