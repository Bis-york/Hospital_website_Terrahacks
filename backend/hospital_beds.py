from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class HospitalBedsDB:
    def __init__(self):
        """Initialize MongoDB connection"""
        self.client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
        self.db = self.client.hospital_db
        self.beds_collection = self.db.beds
        self.patients_collection = self.db.patients
        
    def create_bed(self, bed_data):
        """Create a new hospital bed"""
        bed = {
            'hospital_id': bed_data.get('hospital_id', 'DEFAULT'),  # Add hospital_id
            'bed_number': bed_data['bed_number'],
            'room_number': bed_data['room_number'],
            'department': bed_data['department'],
            'bed_type': bed_data.get('bed_type', 'standard'),  # standard, ICU, emergency
            'status': bed_data.get('status', 'available'),  # available, occupied, maintenance
            'patient_id': bed_data.get('patient_id', None),
            'floor': bed_data.get('floor', 1),
            'wing': bed_data.get('wing', 'Main'),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = self.beds_collection.insert_one(bed)
        return str(result.inserted_id)
    
    def get_all_beds(self):
        """Get all hospital beds"""
        beds = list(self.beds_collection.find())
        # Convert ObjectId to string for JSON serialization
        for bed in beds:
            bed['_id'] = str(bed['_id'])
        return beds
    
    def get_bed_by_id(self, bed_id):
        """Get a specific bed by ID"""
        bed = self.beds_collection.find_one({'_id': ObjectId(bed_id)})
        if bed:
            bed['_id'] = str(bed['_id'])
        return bed
    
    def get_beds_by_status(self, status):
        """Get beds by status (available, occupied, maintenance)"""
        beds = list(self.beds_collection.find({'status': status}))
        for bed in beds:
            bed['_id'] = str(bed['_id'])
        return beds
    
    def get_beds_by_hospital(self, hospital_id):
        """Get beds by hospital"""
        beds = list(self.beds_collection.find({'hospital_id': hospital_id}))
        for bed in beds:
            bed['_id'] = str(bed['_id'])
        return beds
    
    def get_departments_by_hospital(self, hospital_id):
        """Get all departments that have beds in a specific hospital"""
        departments = self.beds_collection.distinct('department', {'hospital_id': hospital_id})
        return sorted(departments)
    
    def get_beds_by_department_and_hospital(self, department, hospital_id):
        """Get beds by department and hospital"""
        beds = list(self.beds_collection.find({'department': department, 'hospital_id': hospital_id}))
        for bed in beds:
            bed['_id'] = str(bed['_id'])
        return beds
    
    def get_bed_statistics_by_hospital(self, hospital_id):
        """Get statistics about bed usage for a specific hospital"""
        total_beds = self.beds_collection.count_documents({'hospital_id': hospital_id})
        available_beds = self.beds_collection.count_documents({'hospital_id': hospital_id, 'status': 'available'})
        occupied_beds = self.beds_collection.count_documents({'hospital_id': hospital_id, 'status': 'occupied'})
        maintenance_beds = self.beds_collection.count_documents({'hospital_id': hospital_id, 'status': 'maintenance'})
        
        # Get beds by department for this hospital
        departments = self.beds_collection.distinct('department', {'hospital_id': hospital_id})
        department_stats = {}
        for dept in departments:
            department_stats[dept] = {
                'total': self.beds_collection.count_documents({'department': dept, 'hospital_id': hospital_id}),
                'available': self.beds_collection.count_documents({'department': dept, 'hospital_id': hospital_id, 'status': 'available'}),
                'occupied': self.beds_collection.count_documents({'department': dept, 'hospital_id': hospital_id, 'status': 'occupied'})
            }
        
        return {
            'total_beds': total_beds,
            'available_beds': available_beds,
            'occupied_beds': occupied_beds,
            'maintenance_beds': maintenance_beds,
            'occupancy_rate': round((occupied_beds / total_beds * 100), 2) if total_beds > 0 else 0,
            'department_stats': department_stats
        }
    
    def update_bed_status(self, bed_id, status, patient_id=None):
        """Update bed status and assign/unassign patient"""
        update_data = {
            'status': status,
            'updated_at': datetime.utcnow()
        }
        
        if patient_id:
            update_data['patient_id'] = patient_id
        elif status == 'available':
            update_data['patient_id'] = None
            
        result = self.beds_collection.update_one(
            {'_id': ObjectId(bed_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    def update_bed_details(self, bed_id, update_data):
        """Update bed details (room, type, department, etc.)"""
        # Remove any fields that shouldn't be updated
        allowed_fields = ['bed_number', 'room_number', 'department', 'bed_type', 'floor', 'wing', 'status', 'patient_id']
        filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields}
        filtered_data['updated_at'] = datetime.utcnow()
        
        result = self.beds_collection.update_one(
            {'_id': ObjectId(bed_id)},
            {'$set': filtered_data}
        )
        return result.modified_count > 0
    
    def delete_bed(self, bed_id):
        """Delete a bed"""
        result = self.beds_collection.delete_one({'_id': ObjectId(bed_id)})
        return result.deleted_count > 0
    
    def get_bed_statistics(self):
        """Get statistics about bed usage"""
        total_beds = self.beds_collection.count_documents({})
        available_beds = self.beds_collection.count_documents({'status': 'available'})
        occupied_beds = self.beds_collection.count_documents({'status': 'occupied'})
        maintenance_beds = self.beds_collection.count_documents({'status': 'maintenance'})
        
        # Get beds by department
        departments = self.beds_collection.distinct('department')
        department_stats = {}
        for dept in departments:
            department_stats[dept] = {
                'total': self.beds_collection.count_documents({'department': dept}),
                'available': self.beds_collection.count_documents({'department': dept, 'status': 'available'}),
                'occupied': self.beds_collection.count_documents({'department': dept, 'status': 'occupied'})
            }
        
        return {
            'total_beds': total_beds,
            'available_beds': available_beds,
            'occupied_beds': occupied_beds,
            'maintenance_beds': maintenance_beds,
            'occupancy_rate': round((occupied_beds / total_beds * 100), 2) if total_beds > 0 else 0,
            'department_stats': department_stats
        }
    
    def create_patient(self, patient_data):
        """Create a new patient record"""
        patient = {
            'name': patient_data['name'],
            'age': patient_data['age'],
            'gender': patient_data['gender'],
            'admission_date': patient_data.get('admission_date', datetime.utcnow()),
            'medical_record_number': patient_data['medical_record_number'],
            'diagnosis': patient_data.get('diagnosis', ''),
            'doctor': patient_data.get('doctor', ''),
            'emergency_contact': patient_data.get('emergency_contact', {}),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = self.patients_collection.insert_one(patient)
        return str(result.inserted_id)
    
    def get_patient_by_id(self, patient_id):
        """Get patient information"""
        patient = self.patients_collection.find_one({'_id': ObjectId(patient_id)})
        if patient:
            patient['_id'] = str(patient['_id'])
        return patient
    
    def assign_patient_to_bed(self, patient_id, bed_id):
        """Assign a patient to a bed"""
        # Update bed status to occupied
        bed_updated = self.update_bed_status(bed_id, 'occupied', patient_id)
        
        if bed_updated:
            # Update patient record with bed assignment
            self.patients_collection.update_one(
                {'_id': ObjectId(patient_id)},
                {'$set': {'assigned_bed_id': bed_id, 'updated_at': datetime.utcnow()}}
            )
            return True
        return False
    
    def discharge_patient(self, patient_id):
        """Discharge a patient and free up the bed"""
        # Find patient's bed
        patient = self.get_patient_by_id(patient_id)
        if patient and 'assigned_bed_id' in patient:
            bed_id = patient['assigned_bed_id']
            
            # Free up the bed
            self.update_bed_status(bed_id, 'available')
            
            # Update patient record
            self.patients_collection.update_one(
                {'_id': ObjectId(patient_id)},
                {
                    '$unset': {'assigned_bed_id': ''},
                    '$set': {
                        'discharge_date': datetime.utcnow(),
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            return True
        return False

# Example usage and testing functions
def initialize_sample_data():
    """Initialize some sample data for testing"""
    db = HospitalBedsDB()
    
    # Sample beds
    sample_beds = [
        {'bed_number': 'B001', 'room_number': '101', 'department': 'ICU', 'bed_type': 'ICU'},
        {'bed_number': 'B002', 'room_number': '101', 'department': 'ICU', 'bed_type': 'ICU'},
        {'bed_number': 'B003', 'room_number': '102', 'department': 'General', 'bed_type': 'standard'},
        {'bed_number': 'B004', 'room_number': '103', 'department': 'Emergency', 'bed_type': 'emergency'},
        {'bed_number': 'B005', 'room_number': '104', 'department': 'Pediatrics', 'bed_type': 'standard'},
    ]
    
    # Check if beds already exist
    if db.beds_collection.count_documents({}) == 0:
        for bed in sample_beds:
            db.create_bed(bed)
        print("Sample beds created successfully!")
    else:
        print("Beds already exist in database.")
    
    return db

if __name__ == "__main__":
    # Test the database connection and functions
    try:
        db = initialize_sample_data()
        
        # Test getting all beds
        all_beds = db.get_all_beds()
        print(f"Total beds: {len(all_beds)}")
        
        # Test statistics
        stats = db.get_bed_statistics()
        print("Bed Statistics:", stats)
        
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        print("Make sure MongoDB is running on your system.")