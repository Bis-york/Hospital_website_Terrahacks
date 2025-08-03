#!/usr/bin/env python3
"""
Hospital Management System - Web Server (Port 8080)
Clean and optimized version for serving frontend HTML templates
"""

from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_cors import CORS
import requests

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

# API proxy - forward all /api requests to the API server
@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_proxy(path):
    """Proxy API requests to the API server on port 5000"""
    try:
        api_url = f'http://localhost:5000/api/{path}'
        
        # Forward the request to the API server
        if request.method == 'GET':
            response = requests.get(api_url, params=request.args)
        elif request.method == 'POST':
            response = requests.post(api_url, json=request.get_json(), params=request.args)
        elif request.method == 'PUT':
            response = requests.put(api_url, json=request.get_json(), params=request.args)
        elif request.method == 'DELETE':
            response = requests.delete(api_url, params=request.args)
        
        # Return the response from the API server
        return response.json(), response.status_code, {'Content-Type': 'application/json'}
    
    except requests.exceptions.ConnectionError:
        return {'error': 'API server is not running on port 5000'}, 503
    except Exception as e:
        return {'error': str(e)}, 500

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
