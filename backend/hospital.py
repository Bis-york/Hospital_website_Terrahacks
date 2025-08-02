from pymongo import MongoClient
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

# Import other database modules
from hospital_beds import HospitalBedsDB
from patient_data import PatientDataDB
from med_inv import MedicalInventoryDB
from staff_inv import StaffManagementDB

# Load environment variables
load_dotenv()

class HospitalManagementSystem:
    def __init__(self):
        """Initialize MongoDB connection and database modules"""
        self.client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
        self.db = self.client.hospital_db
        self.hospitals_collection = self.db.hospitals
        self.departments_collection = self.db.departments
        
        # Initialize other database modules
        self.beds_db = HospitalBedsDB()
        self.patients_db = PatientDataDB()
        self.inventory_db = MedicalInventoryDB()
        self.staff_db = StaffManagementDB()
    
    def create_hospital(self, hospital_data):
        """Create a new hospital"""
        hospital = {
            'hospital_id': hospital_data['hospital_id'],  # Unique hospital identifier
            'name': hospital_data['name'],
            'address': hospital_data['address'],
            'city': hospital_data['city'],
            'state': hospital_data['state'],
            'zip_code': hospital_data['zip_code'],
            'country': hospital_data.get('country', 'USA'),
            'phone': hospital_data['phone'],
            'email': hospital_data.get('email', ''),
            'website': hospital_data.get('website', ''),
            'hospital_type': hospital_data.get('hospital_type', 'general'),  # general, specialty, teaching, etc.
            'license_number': hospital_data.get('license_number', ''),
            'accreditation': hospital_data.get('accreditation', []),  # JCI, NABH, etc.
            'capacity': {
                'total_beds': hospital_data.get('total_beds', 0),
                'icu_beds': hospital_data.get('icu_beds', 0),
                'emergency_beds': hospital_data.get('emergency_beds', 0),
                'operation_theaters': hospital_data.get('operation_theaters', 0)
            },
            'services': hospital_data.get('services', []),  # cardiology, neurology, etc.
            'departments': hospital_data.get('departments', []),
            'facilities': hospital_data.get('facilities', []),  # parking, cafeteria, pharmacy, etc.
            'emergency_services': hospital_data.get('emergency_services', True),
            'trauma_center_level': hospital_data.get('trauma_center_level', None),  # I, II, III, IV
            'established_date': hospital_data.get('established_date', None),
            'administrator': hospital_data.get('administrator', {}),
            'contact_person': hospital_data.get('contact_person', {}),
            'operating_hours': hospital_data.get('operating_hours', '24/7'),
            'insurance_accepted': hospital_data.get('insurance_accepted', []),
            'languages_spoken': hospital_data.get('languages_spoken', ['English']),
            'is_active': hospital_data.get('is_active', True),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Check if hospital_id already exists
        existing_hospital = self.hospitals_collection.find_one({'hospital_id': hospital_data['hospital_id']})
        if existing_hospital:
            raise ValueError(f"Hospital with ID {hospital_data['hospital_id']} already exists")
        
        result = self.hospitals_collection.insert_one(hospital)
        return str(result.inserted_id)
    
    def get_all_hospitals(self):
        """Get all hospitals"""
        hospitals = list(self.hospitals_collection.find())
        for hospital in hospitals:
            hospital['_id'] = str(hospital['_id'])
        return hospitals
    
    def get_hospital_by_id(self, hospital_id):
        """Get hospital by ID"""
        hospital = self.hospitals_collection.find_one({'hospital_id': hospital_id})
        if hospital:
            hospital['_id'] = str(hospital['_id'])
        return hospital
    
    def get_hospital_dashboard(self, hospital_id):
        """Get comprehensive dashboard data for a hospital"""
        hospital = self.get_hospital_by_id(hospital_id)
        if not hospital:
            raise ValueError(f"Hospital with ID {hospital_id} not found")
        
        # Get bed statistics
        bed_stats = self.beds_db.get_bed_statistics()
        
        # Get patient statistics
        patient_stats = self.patients_db.get_patient_statistics()
        
        # Get inventory statistics
        inventory_stats = self.inventory_db.get_inventory_statistics()
        
        # Get staff statistics
        staff_stats = self.staff_db.get_staff_statistics()
        
        # Get current occupancy rate
        occupancy_rate = (bed_stats['occupied_beds'] / bed_stats['total_beds'] * 100) if bed_stats['total_beds'] > 0 else 0
        
        # Get departments with staff count
        departments_info = []
        for dept in hospital.get('departments', []):
            dept_staff = self.staff_db.get_staff_by_department(dept)
            dept_beds = self.beds_db.get_beds_by_department(dept)
            departments_info.append({
                'name': dept,
                'staff_count': len(dept_staff),
                'beds_count': len(dept_beds),
                'on_duty_staff': len([s for s in dept_staff if s['current_status'] == 'on_duty'])
            })
        
        # Get alerts and notifications
        alerts = self.get_hospital_alerts(hospital_id)
        
        dashboard = {
            'hospital_info': hospital,
            'summary': {
                'total_beds': bed_stats['total_beds'],
                'occupied_beds': bed_stats['occupied_beds'],
                'available_beds': bed_stats['available_beds'],
                'occupancy_rate': round(occupancy_rate, 2),
                'total_patients': patient_stats['total_patients'],
                'admitted_patients': patient_stats['admitted_patients'],
                'total_staff': staff_stats['total_staff'],
                'on_duty_staff': staff_stats['on_duty'],
                'total_inventory_items': inventory_stats['total_items'],
                'inventory_value': inventory_stats['total_value']
            },
            'bed_statistics': bed_stats,
            'patient_statistics': patient_stats,
            'inventory_statistics': inventory_stats,
            'staff_statistics': staff_stats,
            'departments': departments_info,
            'alerts': alerts,
            'last_updated': datetime.utcnow()
        }
        
        return dashboard
    
    def get_hospital_alerts(self, hospital_id):
        """Get alerts and notifications for a hospital"""
        alerts = []
        
        # Low stock alerts
        low_stock_items = self.inventory_db.get_low_stock_items()
        if low_stock_items:
            alerts.append({
                'type': 'warning',
                'category': 'inventory',
                'message': f"{len(low_stock_items)} items are running low on stock",
                'count': len(low_stock_items),
                'timestamp': datetime.utcnow()
            })
        
        # Expiring items alerts
        expiring_items = self.inventory_db.get_expiring_items()
        if expiring_items:
            alerts.append({
                'type': 'warning',
                'category': 'inventory',
                'message': f"{len(expiring_items)} items are expiring soon",
                'count': len(expiring_items),
                'timestamp': datetime.utcnow()
            })
        
        # Bed capacity alerts
        bed_stats = self.beds_db.get_bed_statistics()
        occupancy_rate = (bed_stats['occupied_beds'] / bed_stats['total_beds'] * 100) if bed_stats['total_beds'] > 0 else 0
        
        if occupancy_rate > 90:
            alerts.append({
                'type': 'critical',
                'category': 'beds',
                'message': f"Hospital is at {occupancy_rate:.1f}% capacity",
                'occupancy_rate': occupancy_rate,
                'timestamp': datetime.utcnow()
            })
        elif occupancy_rate > 80:
            alerts.append({
                'type': 'warning',
                'category': 'beds',
                'message': f"Hospital capacity is at {occupancy_rate:.1f}%",
                'occupancy_rate': occupancy_rate,
                'timestamp': datetime.utcnow()
            })
        
        # Staff shortage alerts
        departments = self.hospitals_collection.find_one({'hospital_id': hospital_id}).get('departments', [])
        for dept in departments:
            dept_staff = self.staff_db.get_staff_by_department(dept)
            on_duty_staff = [s for s in dept_staff if s['current_status'] == 'on_duty']
            
            if len(on_duty_staff) < 2:  # Minimum staff threshold
                alerts.append({
                    'type': 'warning',
                    'category': 'staffing',
                    'message': f"{dept} department has only {len(on_duty_staff)} staff on duty",
                    'department': dept,
                    'staff_count': len(on_duty_staff),
                    'timestamp': datetime.utcnow()
                })
        
        return alerts
    
    def get_hospital_beds(self, hospital_id):
        """Get all beds for a hospital"""
        # In a multi-hospital system, you might filter by hospital_id
        return self.beds_db.get_all_beds()
    
    def get_hospital_patients(self, hospital_id):
        """Get all patients for a hospital"""
        return self.patients_db.get_all_patients()
    
    def get_hospital_staff(self, hospital_id):
        """Get all staff for a hospital"""
        return self.staff_db.get_all_staff()
    
    def get_hospital_inventory(self, hospital_id):
        """Get all inventory for a hospital"""
        return self.inventory_db.get_all_inventory()
    
    def create_department(self, hospital_id, department_data):
        """Create a new department in a hospital"""
        department = {
            'hospital_id': hospital_id,
            'department_id': department_data['department_id'],
            'name': department_data['name'],
            'description': department_data.get('description', ''),
            'head_of_department': department_data.get('head_of_department', ''),
            'location': department_data.get('location', {}),
            'services': department_data.get('services', []),
            'contact_info': department_data.get('contact_info', {}),
            'operating_hours': department_data.get('operating_hours', '24/7'),
            'bed_capacity': department_data.get('bed_capacity', 0),
            'staff_capacity': department_data.get('staff_capacity', 0),
            'equipment': department_data.get('equipment', []),
            'is_active': department_data.get('is_active', True),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = self.departments_collection.insert_one(department)
        
        # Add department to hospital's department list
        self.hospitals_collection.update_one(
            {'hospital_id': hospital_id},
            {'$addToSet': {'departments': department_data['name']}}
        )
        
        return str(result.inserted_id)
    
    def get_hospital_departments(self, hospital_id):
        """Get all departments for a hospital"""
        departments = list(self.departments_collection.find({'hospital_id': hospital_id}))
        for dept in departments:
            dept['_id'] = str(dept['_id'])
        return departments
    
    def update_hospital(self, hospital_id, update_data):
        """Update hospital information"""
        update_data['updated_at'] = datetime.utcnow()
        
        result = self.hospitals_collection.update_one(
            {'hospital_id': hospital_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    def deactivate_hospital(self, hospital_id, reason=''):
        """Deactivate a hospital"""
        result = self.hospitals_collection.update_one(
            {'hospital_id': hospital_id},
            {'$set': {
                'is_active': False,
                'deactivation_reason': reason,
                'deactivated_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }}
        )
        return result.modified_count > 0
    
    def search_hospitals(self, search_term):
        """Search hospitals by name, city, or hospital_id"""
        search_pattern = {'$regex': search_term, '$options': 'i'}
        query = {
            '$or': [
                {'name': search_pattern},
                {'hospital_id': search_pattern},
                {'city': search_pattern},
                {'state': search_pattern}
            ]
        }
        
        hospitals = list(self.hospitals_collection.find(query))
        for hospital in hospitals:
            hospital['_id'] = str(hospital['_id'])
        return hospitals
    
    def get_system_overview(self):
        """Get overview of all hospitals in the system"""
        total_hospitals = self.hospitals_collection.count_documents({'is_active': True})
        
        # Aggregate statistics across all hospitals
        bed_stats = self.beds_db.get_bed_statistics()
        patient_stats = self.patients_db.get_patient_statistics()
        inventory_stats = self.inventory_db.get_inventory_statistics()
        staff_stats = self.staff_db.get_staff_statistics()
        
        # Get hospitals by state/city
        hospitals_by_location = list(self.hospitals_collection.aggregate([
            {'$match': {'is_active': True}},
            {'$group': {
                '_id': {'state': '$state', 'city': '$city'},
                'count': {'$sum': 1}
            }}
        ]))
        
        return {
            'total_hospitals': total_hospitals,
            'system_statistics': {
                'total_beds': bed_stats['total_beds'],
                'total_patients': patient_stats['total_patients'],
                'total_staff': staff_stats['total_staff'],
                'total_inventory_value': inventory_stats['total_value']
            },
            'hospitals_by_location': hospitals_by_location,
            'last_updated': datetime.utcnow()
        }
    
    def assign_patient_to_bed(self, hospital_id, patient_id, bed_id):
        """Assign a patient to a bed in a specific hospital"""
        return self.beds_db.assign_patient_to_bed(patient_id, bed_id)
    
    def admit_patient(self, hospital_id, patient_data, bed_id=None):
        """Admit a patient to a hospital"""
        # Create patient record
        patient_id = self.patients_db.create_patient(patient_data)
        
        # Assign bed if provided
        if bed_id:
            bed_data = self.beds_db.get_bed_by_id(bed_id)
            if bed_data:
                self.patients_db.assign_bed_to_patient(patient_data['patient_id'], {
                    'bed_id': bed_id,
                    'bed_number': bed_data['bed_number'],
                    'room_number': bed_data['room_number'],
                    'department': bed_data['department']
                })
                self.beds_db.update_bed_status(bed_id, 'occupied', patient_data['patient_id'])
        
        return patient_id
    
    def discharge_patient(self, hospital_id, patient_id):
        """Discharge a patient from a hospital"""
        return self.patients_db.discharge_patient(patient_id)

# Example usage and testing functions
def initialize_sample_hospitals():
    """Initialize some sample hospital data for testing"""
    hms = HospitalManagementSystem()
    
    # Sample hospitals
    sample_hospitals = [
        {
            'hospital_id': 'HOSP001',
            'name': 'Central General Hospital',
            'address': '123 Medical Center Drive',
            'city': 'Metropolitan City',
            'state': 'CA',
            'zip_code': '90210',
            'phone': '555-0100',
            'email': 'info@centralgeneral.com',
            'hospital_type': 'general',
            'total_beds': 500,
            'icu_beds': 50,
            'emergency_beds': 30,
            'operation_theaters': 15,
            'services': ['Emergency', 'Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics'],
            'departments': ['Emergency', 'ICU', 'General', 'Surgery', 'Pediatrics', 'Cardiology'],
            'facilities': ['Parking', 'Cafeteria', 'Pharmacy', 'Laboratory', 'Radiology'],
            'emergency_services': True,
            'trauma_center_level': 'I'
        },
        {
            'hospital_id': 'HOSP002',
            'name': 'St. Mary\'s Heart Institute',
            'address': '456 Cardiac Way',
            'city': 'Heart City',
            'state': 'TX',
            'zip_code': '75001',
            'phone': '555-0200',
            'email': 'info@stmarysheart.com',
            'hospital_type': 'specialty',
            'total_beds': 200,
            'icu_beds': 30,
            'emergency_beds': 10,
            'operation_theaters': 8,
            'services': ['Cardiology', 'Cardiac Surgery', 'Interventional Cardiology'],
            'departments': ['Cardiology', 'Cardiac Surgery', 'CCU', 'Cardiac Rehab'],
            'facilities': ['Parking', 'Cafeteria', 'Pharmacy', 'Cardiac Cath Lab'],
            'emergency_services': False,
            'trauma_center_level': None
        }
    ]
    
    # Check if hospitals already exist
    if hms.hospitals_collection.count_documents({}) == 0:
        for hospital in sample_hospitals:
            try:
                hms.create_hospital(hospital)
                print(f"Hospital {hospital['name']} created successfully!")
            except ValueError as e:
                print(f"Error creating hospital {hospital['name']}: {e}")
    else:
        print("Hospitals already exist in database.")
    
    return hms

if __name__ == "__main__":
    # Test the hospital management system
    try:
        hms = initialize_sample_hospitals()
        
        # Test getting all hospitals
        all_hospitals = hms.get_all_hospitals()
        print(f"Total hospitals: {len(all_hospitals)}")
        
        # Test hospital dashboard
        if all_hospitals:
            hospital_id = all_hospitals[0]['hospital_id']
            dashboard = hms.get_hospital_dashboard(hospital_id)
            print(f"Dashboard for {dashboard['hospital_info']['name']}:")
            print(f"  Total Beds: {dashboard['summary']['total_beds']}")
            print(f"  Occupancy Rate: {dashboard['summary']['occupancy_rate']}%")
            print(f"  Total Staff: {dashboard['summary']['total_staff']}")
            print(f"  Alerts: {len(dashboard['alerts'])}")
        
        # Test system overview
        overview = hms.get_system_overview()
        print(f"\nSystem Overview:")
        print(f"  Total Hospitals: {overview['total_hospitals']}")
        print(f"  Total Beds: {overview['system_statistics']['total_beds']}")
        print(f"  Total Staff: {overview['system_statistics']['total_staff']}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure MongoDB is running and other database modules are available.")