from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PatientDataDB:
    def __init__(self):
        """Initialize MongoDB connection"""
        self.client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
        self.db = self.client.hospital_db
        self.patients_collection = self.db.patients
        self.beds_collection = self.db.beds
        
    def create_patient(self, patient_data):
        """Create a new patient record"""
        patient = {
            'patient_id': patient_data['patient_id'],  # Unique patient identifier
            'name': patient_data['name'],
            'age': patient_data.get('age', None),
            'gender': patient_data.get('gender', ''),
            'phone': patient_data.get('phone', ''),
            'email': patient_data.get('email', ''),
            'address': patient_data.get('address', ''),
            'emergency_contact': patient_data.get('emergency_contact', {}),
            'medical_record_number': patient_data.get('medical_record_number', ''),
            'admission_date': patient_data.get('admission_date', datetime.utcnow()),
            'discharge_date': patient_data.get('discharge_date', None),
            'doctor_report': patient_data.get('doctor_report', ''),
            'incident_report': patient_data.get('incident_report', ''),
            'medical_history': patient_data.get('medical_history', []),
            'diagnosis': patient_data.get('diagnosis', ''),
            'treatment_plan': patient_data.get('treatment_plan', ''),
            'medications': patient_data.get('medications', []),
            'allergies': patient_data.get('allergies', []),
            'is_in_bed': patient_data.get('is_in_bed', False),
            'bed_info': patient_data.get('bed_info', {
                'bed_id': None,
                'bed_number': None,
                'room_number': None,
                'department': None,
                'hospital_id': None
            }),
            'current_hospital': patient_data.get('current_hospital', None),  # Current hospital if admitted
            'admission_history': patient_data.get('admission_history', []),  # List of all hospital admissions
            'status': patient_data.get('status', 'admitted'),  # admitted, discharged, transferred
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Check if patient_id already exists
        existing_patient = self.patients_collection.find_one({'patient_id': patient_data['patient_id']})
        if existing_patient:
            raise ValueError(f"Patient with ID {patient_data['patient_id']} already exists")
        
        result = self.patients_collection.insert_one(patient)
        return str(result.inserted_id)
    
    def get_all_patients(self):
        """Get all patients"""
        patients = list(self.patients_collection.find())
        # Convert ObjectId to string for JSON serialization
        for patient in patients:
            patient['_id'] = str(patient['_id'])
        return patients
    
    def get_patient_by_id(self, patient_id):
        """Get a specific patient by patient_id"""
        patient = self.patients_collection.find_one({'patient_id': patient_id})
        if patient:
            patient['_id'] = str(patient['_id'])
        return patient
    
    def get_patient_by_mongo_id(self, mongo_id):
        """Get a specific patient by MongoDB _id"""
        patient = self.patients_collection.find_one({'_id': ObjectId(mongo_id)})
        if patient:
            patient['_id'] = str(patient['_id'])
        return patient
    
    def update_patient_info(self, patient_id, update_data):
        """Update patient information"""
        update_data['updated_at'] = datetime.utcnow()
        
        result = self.patients_collection.update_one(
            {'patient_id': patient_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    def update_doctor_report(self, patient_id, doctor_report):
        """Update patient's doctor report"""
        return self.update_patient_info(patient_id, {'doctor_report': doctor_report})
    
    def assign_bed_to_patient(self, patient_id, bed_data):
        """Assign a bed to a patient"""
        bed_info = {
            'bed_id': bed_data['bed_id'],
            'bed_number': bed_data['bed_number'],
            'room_number': bed_data['room_number'],
            'department': bed_data['department']
        }
        
        update_data = {
            'is_in_bed': True,
            'bed_info': bed_info,
            'updated_at': datetime.utcnow()
        }
        
        result = self.patients_collection.update_one(
            {'patient_id': patient_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    def remove_bed_from_patient(self, patient_id):
        """Remove bed assignment from patient"""
        update_data = {
            'is_in_bed': False,
            'bed_info': {
                'bed_id': None,
                'bed_number': None,
                'room_number': None,
                'department': None
            },
            'updated_at': datetime.utcnow()
        }
        
        result = self.patients_collection.update_one(
            {'patient_id': patient_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    def get_patients_in_beds(self):
        """Get all patients currently assigned to beds"""
        patients = list(self.patients_collection.find({'is_in_bed': True}))
        for patient in patients:
            patient['_id'] = str(patient['_id'])
        return patients
    
    def get_patients_without_beds(self):
        """Get all patients not assigned to beds"""
        patients = list(self.patients_collection.find({'is_in_bed': False}))
        for patient in patients:
            patient['_id'] = str(patient['_id'])
        return patients
    
    def get_patients_by_hospital(self, hospital_id):
        """Get patients currently in a specific hospital"""
        # Simple approach - just find by current_hospital field
        patients = list(self.patients_collection.find({'current_hospital': hospital_id, 'status': 'admitted'}))
        for patient in patients:
            patient['_id'] = str(patient['_id'])
        return patients
    
    def get_patient_statistics_by_hospital(self, hospital_id):
        """Get statistics about patients for a specific hospital"""
        total_patients = self.patients_collection.count_documents({'current_hospital': hospital_id})
        admitted_patients = self.patients_collection.count_documents({'current_hospital': hospital_id, 'status': 'admitted'})
        discharged_patients = self.patients_collection.count_documents({
            'admission_history.hospital_id': hospital_id,
            'status': 'discharged'
        })
        patients_in_beds = self.patients_collection.count_documents({
            'current_hospital': hospital_id,
            'is_in_bed': True
        })
        patients_without_beds = self.patients_collection.count_documents({
            'current_hospital': hospital_id,
            'is_in_bed': False,
            'status': 'admitted'
        })
        
        # Get patients by department for this hospital
        departments = self.patients_collection.distinct('bed_info.department', {'current_hospital': hospital_id})
        department_stats = {}
        for dept in departments:
            if dept:  # Skip None values
                department_stats[dept] = self.patients_collection.count_documents({
                    'current_hospital': hospital_id,
                    'bed_info.department': dept
                })
        
        return {
            'total_patients': total_patients,
            'admitted_patients': admitted_patients,
            'discharged_patients': discharged_patients,
            'patients_in_beds': patients_in_beds,
            'patients_without_beds': patients_without_beds,
            'department_distribution': department_stats
        }
    
    def transfer_patient_to_hospital(self, patient_id, new_hospital_id):
        """Transfer a patient to a different hospital"""
        patient = self.get_patient_by_id(patient_id)
        if not patient:
            raise ValueError(f"Patient with ID {patient_id} not found")
        
        # Update admission history
        if patient.get('current_hospital'):
            # Close current admission
            self.patients_collection.update_one(
                {'patient_id': patient_id, 'admission_history.hospital_id': patient['current_hospital'], 'admission_history.discharge_date': None},
                {'$set': {'admission_history.$.discharge_date': datetime.utcnow(), 'admission_history.$.status': 'transferred'}}
            )
        
        # Add new admission
        new_admission = {
            'hospital_id': new_hospital_id,
            'admission_date': datetime.utcnow(),
            'status': 'admitted'
        }
        
        update_data = {
            'current_hospital': new_hospital_id,
            'updated_at': datetime.utcnow(),
            '$push': {'admission_history': new_admission}
        }
        
        # Clear bed info since patient is transferring
        update_data['is_in_bed'] = False
        update_data['bed_info'] = {
            'bed_id': None,
            'bed_number': None,
            'room_number': None,
            'department': None,
            'hospital_id': None
        }
        
        result = self.patients_collection.update_one(
            {'patient_id': patient_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    def search_patients(self, search_term):
        """Search patients by name or patient_id"""
        search_pattern = {'$regex': search_term, '$options': 'i'}
        query = {
            '$or': [
                {'name': search_pattern},
                {'patient_id': search_pattern}
            ]
        }
        
        patients = list(self.patients_collection.find(query))
        for patient in patients:
            patient['_id'] = str(patient['_id'])
        return patients
    
    def discharge_patient(self, patient_id):
        """Discharge a patient"""
        patient = self.get_patient_by_id(patient_id)
        if not patient:
            return False
        
        # Update admission history - close current admission
        if patient.get('current_hospital'):
            self.patients_collection.update_one(
                {
                    'patient_id': patient_id,
                    'admission_history': {
                        '$elemMatch': {
                            'hospital_id': patient['current_hospital'],
                            'status': 'admitted'
                        }
                    }
                },
                {
                    '$set': {
                        'admission_history.$.discharge_date': datetime.utcnow(),
                        'admission_history.$.status': 'discharged'
                    }
                }
            )
        
        update_data = {
            'status': 'discharged',
            'discharge_date': datetime.utcnow(),
            'current_hospital': None,
            'is_in_bed': False,
            'bed_info': {
                'bed_id': None,
                'bed_number': None,
                'room_number': None,
                'department': None,
                'hospital_id': None
            },
            'updated_at': datetime.utcnow()
        }
        
        result = self.patients_collection.update_one(
            {'patient_id': patient_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    def delete_patient(self, patient_id):
        """Delete a patient record"""
        result = self.patients_collection.delete_one({'patient_id': patient_id})
        return result.deleted_count > 0
    
    def get_patient_statistics(self):
        """Get statistics about patients"""
        total_patients = self.patients_collection.count_documents({})
        admitted_patients = self.patients_collection.count_documents({'status': 'admitted'})
        discharged_patients = self.patients_collection.count_documents({'status': 'discharged'})
        patients_in_beds = self.patients_collection.count_documents({'is_in_bed': True})
        patients_without_beds = self.patients_collection.count_documents({'is_in_bed': False, 'status': 'admitted'})
        
        # Get patients by department
        departments = self.patients_collection.distinct('bed_info.department')
        department_stats = {}
        for dept in departments:
            if dept:  # Skip None values
                department_stats[dept] = self.patients_collection.count_documents({'bed_info.department': dept})
        
        return {
            'total_patients': total_patients,
            'admitted_patients': admitted_patients,
            'discharged_patients': discharged_patients,
            'patients_in_beds': patients_in_beds,
            'patients_without_beds': patients_without_beds,
            'department_distribution': department_stats
        }

# Example usage and testing functions
def initialize_sample_patients():
    """Initialize some sample patient data for testing"""
    db = PatientDataDB()
    
    # Sample patients
    sample_patients = [
        {
            'patient_id': 'P001',
            'name': 'John Doe',
            'age': 45,
            'gender': 'Male',
            'phone': '555-0123',
            'doctor_report': 'Patient admitted with chest pain. ECG normal. Awaiting cardiac enzyme results.',
            'diagnosis': 'Chest Pain - Rule out MI',
            'is_in_bed': True,
            'bed_info': {
                'bed_id': 'bed_001',
                'bed_number': 'B001',
                'room_number': '101',
                'department': 'Cardiology'
            }
        },
        {
            'patient_id': 'P002',
            'name': 'Jane Smith',
            'age': 32,
            'gender': 'Female',
            'phone': '555-0456',
            'doctor_report': 'Patient recovering well from appendectomy. Vital signs stable.',
            'diagnosis': 'Post-operative appendectomy',
            'is_in_bed': True,
            'bed_info': {
                'bed_id': 'bed_002',
                'bed_number': 'B002',
                'room_number': '102',
                'department': 'Surgery'
            }
        },
        {
            'patient_id': 'P003',
            'name': 'Robert Johnson',
            'age': 67,
            'gender': 'Male',
            'phone': '555-0789',
            'doctor_report': 'Patient awaiting bed assignment. Blood pressure elevated.',
            'diagnosis': 'Hypertension',
            'is_in_bed': False
        }
    ]
    
    # Check if patients already exist
    if db.patients_collection.count_documents({}) == 0:
        for patient in sample_patients:
            try:
                db.create_patient(patient)
                print(f"Patient {patient['name']} created successfully!")
            except ValueError as e:
                print(f"Error creating patient {patient['name']}: {e}")
    else:
        print("Patients already exist in database.")
    
    return db

if __name__ == "__main__":
    # Test the database connection and functions
    try:
        db = initialize_sample_patients()
        
        # Test getting all patients
        all_patients = db.get_all_patients()
        print(f"Total patients: {len(all_patients)}")
        
        # Test getting patients in beds
        patients_in_beds = db.get_patients_in_beds()
        print(f"Patients in beds: {len(patients_in_beds)}")
        
        # Test getting patients without beds
        patients_without_beds = db.get_patients_without_beds()
        print(f"Patients without beds: {len(patients_without_beds)}")
        
        # Test statistics
        stats = db.get_patient_statistics()
        print("Patient Statistics:", stats)
        
        # Test searching patients
        search_results = db.search_patients("John")
        print(f"Search results for 'John': {len(search_results)} patients found")
        
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        print("Make sure MongoDB is running on your system.")