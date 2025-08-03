#!/usr/bin/env python3
"""
Hospital Management System - Web Server (Port 8080)
Clean and optimized version for serving frontend HTML templates
"""

from flask import Flask, render_template, send_from_directory
from flask_cors import CORS

# Create Flask app
app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
CORS(app)

# Web page routes
@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/beds.html')
def beds():
    return render_template('beds.html')

@app.route('/patients.html')
def patients():
    return render_template('patients.html')

@app.route('/staff.html')
def staff():
    return render_template('staff.html')

@app.route('/inventory.html')
def inventory():
    return render_template('inventory.html')

@app.route('/hospital.html')
def hospital():
    return render_template('hospital.html')

@app.route('/drugCheck.html')
def drug_check():
    return render_template('drugCheck.html')

# Serve static files (CSS, JS, images)
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('app/static', filename)

# Health check for monitoring
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'server': 'Hospital Web Server'}, 200

if __name__ == '__main__':
    print("🌐 Hospital Management System - Web Server")
    print("=" * 50)
    print("📱 Frontend: http://localhost:8080")
    print("❤️  Health: http://localhost:8080/health")
    print("=" * 50)
    print("Starting web server on port 8080...")
    print("Press Ctrl+C to stop")
    print()
    
    app.run(debug=True, host='0.0.0.0', port=8080)
