let healthChart = null;
let radarChart = null;

// Initialize charts on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    
    // Form submission
    document.getElementById('patientForm').addEventListener('submit', function(e) {
        e.preventDefault();
        analyzePatient();
    });
    
    // CSV file input
    document.getElementById('csvFile').addEventListener('change', handleCSVUpload);
});

function initializeCharts() {
    // Health metrics bar chart
    const healthCtx = document.getElementById('healthChart').getContext('2d');
    healthChart = new Chart(healthCtx, {
        type: 'bar',
        data: {
            labels: ['Glucose', 'Systolic BP', 'Diastolic BP', 'Cholesterol', 'BMI'],
            datasets: [{
                label: 'Patient Values',
                data: [0, 0, 0, 0, 0],
                backgroundColor: [
                    'rgba(52, 152, 219, 0.6)',
                    'rgba(52, 152, 219, 0.6)',
                    'rgba(52, 152, 219, 0.6)',
                    'rgba(52, 152, 219, 0.6)',
                    'rgba(52, 152, 219, 0.6)'
                ],
                borderColor: [
                    'rgba(52, 152, 219, 1)',
                    'rgba(52, 152, 219, 1)',
                    'rgba(52, 152, 219, 1)',
                    'rgba(52, 152, 219, 1)',
                    'rgba(52, 152, 219, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });

    // Radar chart
    const radarCtx = document.getElementById('radarChart').getContext('2d');
    radarChart = new Chart(radarCtx, {
        type: 'radar',
        data: {
            labels: ['Glucose', 'Systolic BP', 'Diastolic BP', 'Cholesterol', 'BMI'],
            datasets: [{
                label: 'Patient',
                data: [0, 0, 0, 0, 0],
                backgroundColor: 'rgba(52, 152, 219, 0.2)',
                borderColor: 'rgba(52, 152, 219, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(52, 152, 219, 1)'
            }, {
                label: 'Normal Range',
                data: [0.5, 0.5, 0.5, 0.5, 0.5],
                backgroundColor: 'rgba(46, 204, 113, 0.1)',
                borderColor: 'rgba(46, 204, 113, 1)',
                borderWidth: 2,
                borderDash: [5, 5],
                pointBackgroundColor: 'rgba(46, 204, 113, 1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 1,
                    ticks: {
                        display: false
                    }
                }
            }
        }
    });
}

function analyzePatient() {
    // Get form data
    const patientData = {
        patient_id: document.getElementById('patientId').value || 'PAT_' + Math.random().toString(36).substr(2, 9),
        age: parseInt(document.getElementById('age').value),
        gender: document.getElementById('gender').value,
        glucose: parseFloat(document.getElementById('glucose').value),
        systolic_bp: parseFloat(document.getElementById('systolicBp').value),
        diastolic_bp: parseFloat(document.getElementById('diastolicBp').value),
        cholesterol: parseFloat(document.getElementById('cholesterol').value),
        bmi: parseFloat(document.getElementById('bmi').value)
    };

    // Validate form
    if (!patientData.age || !patientData.gender || !patientData.glucose || 
        !patientData.systolic_bp || !patientData.diastolic_bp || 
        !patientData.cholesterol || !patientData.bmi) {
        showAlert('Please fill in all required fields', 'warning');
        return;
    }

    // Show loading modal
    const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    loadingModal.show();

    // Send data to backend
    fetch('/api/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(patientData)
    })
    .then(response => response.json())
    .then(data => {
        loadingModal.hide();
        
        if (data.error) {
            showAlert('Error: ' + data.error, 'danger');
            return;
        }

        // Update visualizations
        updateCharts(data.visualization);
        
        // Display results
        displayResults(patientData, data.rule_results, data.ml_results);
        
        // Scroll to results
        document.querySelector('.results-card').scrollIntoView({ behavior: 'smooth' });
    })
    .catch(error => {
        loadingModal.hide();
        showAlert('Network error: ' + error.message, 'danger');
    });
}

function updateCharts(vizData) {
    // Update bar chart
    healthChart.data.datasets[0].data = vizData.values;
    healthChart.data.datasets[0].backgroundColor = vizData.colors.map(color => color + '99');
    healthChart.data.datasets[0].borderColor = vizData.colors;
    healthChart.update();

    // Update radar chart
    const normalizedValues = vizData.values.map((value, index) => {
        const range = vizData.normal_ranges[index];
        if (value < range.min) return 0.3;
        if (value > range.max) return Math.min(1.0, 0.5 + (value - range.max) / range.max);
        return 0.5;
    });

    radarChart.data.datasets[0].data = normalizedValues;
    radarChart.update();
}

function displayResults(patientData, ruleResults, mlResults) {
    const resultsContainer = document.getElementById('resultsContainer');
    
    let html = `
        <div class="fade-in">
            <div class="result-item">
                <h6><i class="fas fa-user"></i> Patient Information</h6>
                <p><strong>ID:</strong> ${patientData.patient_id}</p>
                <p><strong>Age:</strong> ${patientData.age} years</p>
                <p><strong>Gender:</strong> ${patientData.gender}</p>
            </div>

            <div class="result-item">
                <h6><i class="fas fa-stethoscope"></i> Detected Conditions</h6>
    `;

    if (ruleResults.conditions.length > 0) {
        ruleResults.conditions.forEach(condition => {
            html += `<p><i class="fas fa-exclamation-triangle text-warning"></i> ${condition}</p>`;
        });
    } else {
        html += `<p><i class="fas fa-check-circle text-success"></i> No specific conditions detected</p>`;
    }

    html += `
            </div>

            <div class="result-item">
                <h6><i class="fas fa-heart"></i> Risk Assessment</h6>
                <div class="text-center">
                    <span class="risk-badge risk-${ruleResults.risk_level.toLowerCase()}">
                        ${ruleResults.risk_emoji} ${ruleResults.risk_level} Risk
                    </span>
                </div>
            </div>
    `;

    if (mlResults && !mlResults.error) {
        html += `
            <div class="result-item">
                <h6><i class="fas fa-robot"></i> AI Prediction</h6>
                <p><strong>Predicted Risk:</strong> ${mlResults.predicted_risk}</p>
                <p><strong>Confidence:</strong> ${mlResults.confidence}%</p>
            </div>
        `;
    }

    html += `
            <div class="result-item">
                <h6><i class="fas fa-lightbulb"></i> Recommendations</h6>
                <div class="recommendations-list">
    `;

    ruleResults.recommendations.forEach(rec => {
        html += `
            <div class="recommendation-item">
                <i class="fas fa-check-circle"></i>
                <span>${rec}</span>
            </div>
        `;
    });

    html += `
                </div>
            </div>

            <div class="alert alert-info mt-3">
                <i class="fas fa-info-circle"></i>
                <strong>Disclaimer:</strong> This AI-assisted diagnostic tool is not a substitute for professional medical advice. Please consult with a qualified healthcare provider.
            </div>
        </div>
    `;

    resultsContainer.innerHTML = html;
}

function uploadCSV() {
    document.getElementById('csvFile').click();
}

function handleCSVUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    fetch('/api/upload_csv', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showAlert('Error: ' + data.error, 'danger');
            return;
        }

        // Fill form with first patient data
        document.getElementById('patientId').value = data.patient_data.Patient_ID || data.patient_data.patient_id;
        document.getElementById('age').value = data.patient_data.Age || data.patient_data.age;
        document.getElementById('gender').value = data.patient_data.Gender || data.patient_data.gender;
        document.getElementById('glucose').value = data.patient_data.Glucose || data.patient_data.glucose;
        document.getElementById('systolicBp').value = data.patient_data.Systolic_BP || data.patient_data.systolic_bp;
        document.getElementById('diastolicBp').value = data.patient_data.Diastolic_BP || data.patient_data.diastolic_bp;
        document.getElementById('cholesterol').value = data.patient_data.Cholesterol || data.patient_data.cholesterol;
        document.getElementById('bmi').value = data.patient_data.BMI || data.patient_data.bmi;

        showAlert(`Successfully loaded ${data.total_records} patient records. First patient data populated.`, 'success');
    })
    .catch(error => {
        showAlert('Error uploading file: ' + error.message, 'danger');
    });

    // Reset file input
    event.target.value = '';
}

function generateSample() {
    fetch('/api/generate_sample')
    .then(response => response.json())
    .then(data => {
        // Fill form with sample data
        document.getElementById('patientId').value = data.patient_id;
        document.getElementById('age').value = data.age;
        document.getElementById('gender').value = data.gender;
        document.getElementById('glucose').value = data.glucose;
        document.getElementById('systolicBp').value = data.systolic_bp;
        document.getElementById('diastolicBp').value = data.diastolic_bp;
        document.getElementById('cholesterol').value = data.cholesterol;
        document.getElementById('bmi').value = data.bmi;

        showAlert('Sample patient data generated successfully!', 'success');
    })
    .catch(error => {
        showAlert('Error generating sample data: ' + error.message, 'danger');
    });
}

function clearForm() {
    document.getElementById('patientForm').reset();
    
    // Reset charts
    healthChart.data.datasets[0].data = [0, 0, 0, 0, 0];
    healthChart.update();
    
    radarChart.data.datasets[0].data = [0, 0, 0, 0, 0];
    radarChart.update();
    
    // Reset results
    document.getElementById('resultsContainer').innerHTML = `
        <div class="text-center text-muted">
            <i class="fas fa-stethoscope fa-3x mb-3"></i>
            <p>Enter patient data and click "Analyze" to see results</p>
        </div>
    `;
    
    showAlert('Form cleared successfully', 'info');
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}