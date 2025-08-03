from flask import Blueprint, render_template, request, jsonify
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))
from hospital_beds import HospitalBedsDB

main = Blueprint('main', __name__)

# Initialize database connection
db = HospitalBedsDB()

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/patients')
def patients():
    return render_template('patients.html')

@main.route('/staff')
def staff():
    return render_template('staff.html')

@main.route('/inventory')
def inventory():
    return render_template('inventory.html')

@main.route('/api/beds', methods=['GET'])
def get_beds():
    """Get all beds or filter by status/department"""
    status = request.args.get('status')
    department = request.args.get('department')
    
    if status:
        beds = db.get_beds_by_status(status)
    elif department:
        beds = db.get_beds_by_department(department)
    else:
        beds = db.get_all_beds()
    
    return jsonify(beds)

@main.route('/api/beds', methods=['POST'])
def create_bed():
    """Create a new bed"""
    bed_data = request.json
    bed_id = db.create_bed(bed_data)
    return jsonify({'id': bed_id, 'message': 'Bed created successfully'})

@main.route('/api/beds/<bed_id>', methods=['PUT'])
def update_bed(bed_id):
    """Update bed status"""
    data = request.json
    status = data.get('status')
    patient_id = data.get('patient_id')
    
    success = db.update_bed_status(bed_id, status, patient_id)
    if success:
        return jsonify({'message': 'Bed updated successfully'})
    else:
        return jsonify({'error': 'Failed to update bed'}), 400

@main.route('/api/beds/<bed_id>', methods=['DELETE'])
def delete_bed(bed_id):
    """Delete a bed"""
    success = db.delete_bed(bed_id)
    if success:
        return jsonify({'message': 'Bed deleted successfully'})
    else:
        return jsonify({'error': 'Failed to delete bed'}), 400

@main.route('/api/statistics')
def get_statistics():
    """Get bed statistics"""
    stats = db.get_bed_statistics()
    return jsonify(stats)

@main.route('/api/patients', methods=['POST'])
def create_patient():
    """Create a new patient"""
    patient_data = request.json
    patient_id = db.create_patient(patient_data)
    return jsonify({'id': patient_id, 'message': 'Patient created successfully'})

@main.route('/api/assign-bed', methods=['POST'])
def assign_bed():
    """Assign a patient to a bed"""
    data = request.json
    patient_id = data.get('patient_id')
    bed_id = data.get('bed_id')
    
    success = db.assign_patient_to_bed(patient_id, bed_id)
    if success:
        return jsonify({'message': 'Patient assigned to bed successfully'})
    else:
        return jsonify({'error': 'Failed to assign patient to bed'}), 400

@main.route('/api/discharge/<patient_id>', methods=['POST'])
def discharge_patient(patient_id):
    """Discharge a patient"""
    success = db.discharge_patient(patient_id)
    if success:
        return jsonify({'message': 'Patient discharged successfully'})
    else:
        return jsonify({'error': 'Failed to discharge patient'}), 400