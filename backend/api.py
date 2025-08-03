from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import sys
import os

# Add the backend directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hospital import HospitalManagementSystem
from hospital_beds import HospitalBedsDB
from patient_data import PatientDataDB
from med_inv import MedicalInventoryDB
from staff_inv import StaffManagementDB

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the hospital management system
hms = HospitalManagementSystem()

# Error handler
@app.errorhandler(Exception)
def handle_error(e):
    return jsonify({'error': str(e)}), 500

# ==================== HOSPITAL ENDPOINTS ====================

@app.route('/api/hospitals', methods=['GET'])
def get_all_hospitals():
    """Get all hospitals"""
    try:
        hospitals = hms.get_all_hospitals()
        return jsonify({'success': True, 'data': hospitals})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospitals', methods=['POST'])
def create_hospital():
    """Create a new hospital"""
    try:
        data = request.get_json()
        hospital_id = hms.create_hospital(data)
        return jsonify({'success': True, 'hospital_id': hospital_id}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/hospitals/<hospital_id>', methods=['GET'])
def get_hospital(hospital_id):
    """Get hospital by ID"""
    try:
        hospital = hms.get_hospital_by_id(hospital_id)
        if hospital:
            return jsonify({'success': True, 'data': hospital})
        else:
            return jsonify({'success': False, 'error': 'Hospital not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospitals/<hospital_id>/dashboard', methods=['GET'])
def get_hospital_dashboard(hospital_id):
    """Get hospital dashboard"""
    try:
        dashboard = hms.get_hospital_dashboard(hospital_id)
        # Convert datetime objects to strings for JSON serialization
        dashboard['last_updated'] = dashboard['last_updated'].isoformat()
        for alert in dashboard['alerts']:
            alert['timestamp'] = alert['timestamp'].isoformat()
        return jsonify({'success': True, 'data': dashboard})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospitals/<hospital_id>', methods=['PUT'])
def update_hospital(hospital_id):
    """Update hospital information"""
    try:
        data = request.get_json()
        success = hms.update_hospital(hospital_id, data)
        if success:
            return jsonify({'success': True, 'message': 'Hospital updated successfully'})
        else:
            return jsonify({'success': False, 'error': 'Hospital not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospitals/<hospital_id>/deactivate', methods=['PUT'])
def deactivate_hospital(hospital_id):
    """Deactivate a hospital"""
    try:
        data = request.get_json()
        reason = data.get('reason', '')
        success = hms.deactivate_hospital(hospital_id, reason)
        if success:
            return jsonify({'success': True, 'message': 'Hospital deactivated successfully'})
        else:
            return jsonify({'success': False, 'error': 'Hospital not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospitals/search', methods=['GET'])
def search_hospitals():
    """Search hospitals"""
    try:
        search_term = request.args.get('q', '')
        if not search_term:
            return jsonify({'success': False, 'error': 'Search term required'}), 400
        hospitals = hms.search_hospitals(search_term)
        return jsonify({'success': True, 'data': hospitals})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== BED ENDPOINTS ====================

@app.route('/api/hospitals/<hospital_id>/beds', methods=['GET'])
def get_hospital_beds(hospital_id):
    """Get all beds for a hospital"""
    try:
        beds = hms.get_hospital_beds(hospital_id)
        return jsonify({'success': True, 'data': beds})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospitals/<hospital_id>/departments', methods=['GET'])
def get_hospital_departments(hospital_id):
    """Get all departments for a hospital"""
    try:
        departments = hms.beds_db.get_departments_by_hospital(hospital_id)
        return jsonify({'success': True, 'data': departments})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospitals/<hospital_id>/beds', methods=['POST'])
def create_bed(hospital_id):
    """Create a new bed in a hospital"""
    try:
        data = request.get_json()
        data['hospital_id'] = hospital_id
        bed_id = hms.beds_db.create_bed(data)
        return jsonify({'success': True, 'bed_id': bed_id}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/beds/<bed_id>/status', methods=['PUT'])
def update_bed_status(bed_id):
    """Update bed status"""
    try:
        data = request.get_json()
        status = data.get('status')
        patient_id = data.get('patient_id')
        success = hms.beds_db.update_bed_status(bed_id, status, patient_id)
        if success:
            return jsonify({'success': True, 'message': 'Bed status updated successfully'})
        else:
            return jsonify({'success': False, 'error': 'Bed not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospitals/<hospital_id>/beds/stats', methods=['GET'])
def get_hospital_bed_stats(hospital_id):
    """Get bed statistics for a hospital"""
    try:
        stats = hms.beds_db.get_bed_statistics_by_hospital(hospital_id)
        return jsonify({'success': True, 'data': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospitals/<hospital_id>/beds/department/<department>', methods=['GET'])
def get_hospital_beds_by_department(hospital_id, department):
    """Get beds by department for a hospital"""
    try:
        beds = hms.beds_db.get_beds_by_department_and_hospital(department, hospital_id)
        return jsonify({'success': True, 'data': beds})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/beds/<bed_id>', methods=['GET'])
def get_bed_details(bed_id):
    """Get specific bed details"""
    try:
        bed = hms.beds_db.get_bed_by_id(bed_id)
        if bed:
            return jsonify({'success': True, 'data': bed})
        else:
            return jsonify({'success': False, 'error': 'Bed not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/beds/<bed_id>', methods=['PUT'])
def update_bed_details(bed_id):
    """Update bed details"""
    try:
        data = request.get_json()
        success = hms.beds_db.update_bed_details(bed_id, data)
        if success:
            return jsonify({'success': True, 'message': 'Bed updated successfully'})
        else:
            return jsonify({'success': False, 'error': 'Bed not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== PATIENT ENDPOINTS ====================

@app.route('/api/hospitals/<hospital_id>/patients', methods=['GET'])
def get_hospital_patients(hospital_id):
    """Get all patients for a hospital"""
    try:
        patients = hms.get_hospital_patients(hospital_id)
        # Convert datetime objects to strings
        for patient in patients:
            if 'created_at' in patient:
                patient['created_at'] = patient['created_at'].isoformat()
            if 'updated_at' in patient:
                patient['updated_at'] = patient['updated_at'].isoformat()
            if 'admission_history' in patient:
                for admission in patient['admission_history']:
                    if 'admission_date' in admission:
                        admission['admission_date'] = admission['admission_date'].isoformat()
                    if 'discharge_date' in admission:
                        admission['discharge_date'] = admission['discharge_date'].isoformat()
        return jsonify({'success': True, 'data': patients})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospitals/<hospital_id>/patients', methods=['POST'])
def admit_patient(hospital_id):
    """Admit a patient to a hospital"""
    try:
        data = request.get_json()
        bed_id = data.get('bed_id')
        patient_id = hms.admit_patient_to_hospital(hospital_id, data, bed_id)
        return jsonify({'success': True, 'patient_id': patient_id}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/patients/<patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Get patient by ID"""
    try:
        patient = hms.patients_db.get_patient_by_id(patient_id)
        if patient:
            # Convert datetime objects to strings
            if 'created_at' in patient:
                patient['created_at'] = patient['created_at'].isoformat()
            if 'updated_at' in patient:
                patient['updated_at'] = patient['updated_at'].isoformat()
            if 'admission_history' in patient:
                for admission in patient['admission_history']:
                    if 'admission_date' in admission:
                        admission['admission_date'] = admission['admission_date'].isoformat()
                    if 'discharge_date' in admission:
                        admission['discharge_date'] = admission['discharge_date'].isoformat()
            return jsonify({'success': True, 'data': patient})
        else:
            return jsonify({'success': False, 'error': 'Patient not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/patients/<patient_id>/discharge', methods=['PUT'])
def discharge_patient(patient_id):
    """Discharge a patient"""
    try:
        success = hms.patients_db.discharge_patient(patient_id)
        if success:
            return jsonify({'success': True, 'message': 'Patient discharged successfully'})
        else:
            return jsonify({'success': False, 'error': 'Patient not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== STAFF ENDPOINTS ====================

@app.route('/api/hospitals/<hospital_id>/staff', methods=['GET'])
def get_hospital_staff(hospital_id):
    """Get all staff for a hospital"""
    try:
        staff = hms.get_hospital_staff(hospital_id)
        # Convert datetime objects to strings
        for member in staff:
            if 'created_at' in member:
                member['created_at'] = member['created_at'].isoformat()
            if 'updated_at' in member:
                member['updated_at'] = member['updated_at'].isoformat()
            if 'last_login' in member and member['last_login']:
                member['last_login'] = member['last_login'].isoformat()
        return jsonify({'success': True, 'data': staff})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospitals/<hospital_id>/staff', methods=['POST'])
def add_staff(hospital_id):
    """Add staff member to a hospital"""
    try:
        data = request.get_json()
        staff_id = hms.add_staff_to_hospital(hospital_id, data)
        return jsonify({'success': True, 'staff_id': staff_id}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/staff/<staff_id>/status', methods=['PUT'])
def update_staff_status(staff_id):
    """Update staff status"""
    try:
        data = request.get_json()
        status = data.get('status')
        success = hms.staff_db.update_staff_status(staff_id, status)
        if success:
            return jsonify({'success': True, 'message': 'Staff status updated successfully'})
        else:
            return jsonify({'success': False, 'error': 'Staff member not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/staff/login', methods=['POST'])
def staff_login():
    """Staff login"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        staff = hms.staff_db.authenticate_staff(email, password)
        if staff:
            # Convert datetime objects to strings
            if 'created_at' in staff:
                staff['created_at'] = staff['created_at'].isoformat()
            if 'updated_at' in staff:
                staff['updated_at'] = staff['updated_at'].isoformat()
            if 'last_login' in staff and staff['last_login']:
                staff['last_login'] = staff['last_login'].isoformat()
            return jsonify({'success': True, 'data': staff})
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== INVENTORY ENDPOINTS ====================

@app.route('/api/hospitals/<hospital_id>/inventory', methods=['GET'])
def get_hospital_inventory(hospital_id):
    """Get all inventory for a hospital"""
    try:
        inventory = hms.get_hospital_inventory(hospital_id)
        # Convert datetime objects to strings
        for item in inventory:
            if 'created_at' in item:
                item['created_at'] = item['created_at'].isoformat()
            if 'updated_at' in item:
                item['updated_at'] = item['updated_at'].isoformat()
            if 'expiry_date' in item and item['expiry_date']:
                item['expiry_date'] = item['expiry_date'].isoformat()
        return jsonify({'success': True, 'data': inventory})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospitals/<hospital_id>/inventory', methods=['POST'])
def add_inventory_item(hospital_id):
    """Add inventory item to a hospital"""
    try:
        data = request.get_json()
        data['hospital_id'] = hospital_id
        item_id = hms.inventory_db.create_inventory_item(data)
        return jsonify({'success': True, 'item_id': item_id}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/inventory/<item_id>/stock', methods=['PUT'])
def update_inventory_stock(item_id):
    """Update inventory stock"""
    try:
        data = request.get_json()
        quantity = data.get('quantity')
        operation = data.get('operation', 'set')  # 'set', 'add', 'subtract'
        
        if operation == 'add':
            success = hms.inventory_db.add_stock(item_id, quantity)
        elif operation == 'subtract':
            success = hms.inventory_db.use_stock(item_id, quantity)
        else:  # set
            success = hms.inventory_db.update_stock(item_id, quantity)
        
        if success:
            return jsonify({'success': True, 'message': 'Stock updated successfully'})
        else:
            return jsonify({'success': False, 'error': 'Item not found or insufficient stock'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hospitals/<hospital_id>/inventory/low-stock', methods=['GET'])
def get_low_stock_items(hospital_id):
    """Get low stock items for a hospital"""
    try:
        items = hms.inventory_db.get_low_stock_items_by_hospital(hospital_id)
        # Convert datetime objects to strings
        for item in items:
            if 'created_at' in item:
                item['created_at'] = item['created_at'].isoformat()
            if 'updated_at' in item:
                item['updated_at'] = item['updated_at'].isoformat()
            if 'expiry_date' in item and item['expiry_date']:
                item['expiry_date'] = item['expiry_date'].isoformat()
        return jsonify({'success': True, 'data': items})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== SYSTEM ENDPOINTS ====================

@app.route('/api/system/overview', methods=['GET'])
def get_system_overview():
    """Get system overview"""
    try:
        overview = hms.get_system_overview()
        overview['last_updated'] = overview['last_updated'].isoformat()
        return jsonify({'success': True, 'data': overview})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/initialize-sample-data', methods=['POST'])
def initialize_sample_data():
    """Initialize sample hospital data"""
    try:
        from hospital import initialize_sample_hospitals
        hms = initialize_sample_hospitals()
        return jsonify({'success': True, 'message': 'Sample data initialized successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check"""
    try:
        # Test database connection
        hms.hospitals_collection.find_one()
        return jsonify({
            'success': True, 
            'message': 'API is healthy',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': 'Database connection failed',
            'details': str(e)
        }), 500

# ==================== API DOCUMENTATION ====================

@app.route('/api/docs', methods=['GET'])
def api_documentation():
    """API documentation"""
    docs = {
        'title': 'Hospital Management System API',
        'version': '1.0.0',
        'description': 'REST API for managing hospitals, patients, staff, beds, and inventory',
        'endpoints': {
            'hospitals': {
                'GET /api/hospitals': 'Get all hospitals',
                'POST /api/hospitals': 'Create a new hospital',
                'GET /api/hospitals/{id}': 'Get hospital by ID',
                'PUT /api/hospitals/{id}': 'Update hospital',
                'GET /api/hospitals/{id}/dashboard': 'Get hospital dashboard',
                'PUT /api/hospitals/{id}/deactivate': 'Deactivate hospital',
                'GET /api/hospitals/search?q={term}': 'Search hospitals'
            },
            'beds': {
                'GET /api/hospitals/{id}/beds': 'Get hospital beds',
                'POST /api/hospitals/{id}/beds': 'Create bed',
                'PUT /api/beds/{id}/status': 'Update bed status'
            },
            'patients': {
                'GET /api/hospitals/{id}/patients': 'Get hospital patients',
                'POST /api/hospitals/{id}/patients': 'Admit patient',
                'GET /api/patients/{id}': 'Get patient by ID',
                'PUT /api/patients/{id}/discharge': 'Discharge patient'
            },
            'staff': {
                'GET /api/hospitals/{id}/staff': 'Get hospital staff',
                'POST /api/hospitals/{id}/staff': 'Add staff member',
                'PUT /api/staff/{id}/status': 'Update staff status',
                'POST /api/staff/login': 'Staff login'
            },
            'inventory': {
                'GET /api/hospitals/{id}/inventory': 'Get hospital inventory',
                'POST /api/hospitals/{id}/inventory': 'Add inventory item',
                'PUT /api/inventory/{id}/stock': 'Update inventory stock',
                'GET /api/hospitals/{id}/inventory/low-stock': 'Get low stock items'
            },
            'system': {
                'GET /api/system/overview': 'Get system overview',
                'POST /api/initialize-sample-data': 'Initialize sample data',
                'GET /api/health': 'Health check',
                'GET /api/docs': 'API documentation'
            }
        }
    }
    return jsonify(docs)

if __name__ == '__main__':
    print("Starting Hospital Management System API...")
    print("API Documentation available at: http://localhost:5000/api/docs")
    print("Health Check available at: http://localhost:5000/api/health")
    app.run(debug=True, host='0.0.0.0', port=5000)
