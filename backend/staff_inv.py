from pymongo import MongoClient
from datetime import datetime, timedelta, time
from bson.objectid import ObjectId
import os
import hashlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class StaffManagementDB:
    def __init__(self):
        """Initialize MongoDB connection"""
        self.client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
        self.db = self.client.hospital_db
        self.staff_collection = self.db.staff
        self.attendance_collection = self.db.staff_attendance
        self.schedules_collection = self.db.staff_schedules
        self.patient_assignments_collection = self.db.patient_assignments
        
    def hash_password(self, password):
        """Hash password for security"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_staff_member(self, staff_data):
        """Create a new staff member"""
        staff = {
            'staff_id': staff_data['staff_id'],  # Unique staff identifier
            'employee_number': staff_data.get('employee_number', ''),
            'first_name': staff_data['first_name'],
            'last_name': staff_data['last_name'],
            'full_name': f"{staff_data['first_name']} {staff_data['last_name']}",
            'email': staff_data['email'],
            'phone': staff_data.get('phone', ''),
            'password_hash': self.hash_password(staff_data['password']),
            'role': staff_data['role'],  # doctor, nurse, technician, admin, cleaner, security, etc.
            'specialization': staff_data.get('specialization', ''),  # cardiology, surgery, etc.
            'department': staff_data['department'],
            'primary_location': staff_data.get('primary_location', {}),  # building, floor, room
            'shift': staff_data.get('shift', 'day'),  # day, night, rotating
            'employment_type': staff_data.get('employment_type', 'full_time'),  # full_time, part_time, contract
            'hire_date': staff_data.get('hire_date', datetime.utcnow()),
            'salary': staff_data.get('salary', 0.0),
            'qualifications': staff_data.get('qualifications', []),
            'certifications': staff_data.get('certifications', []),
            'emergency_contact': staff_data.get('emergency_contact', {}),
            'address': staff_data.get('address', {}),
            'date_of_birth': staff_data.get('date_of_birth', None),
            'gender': staff_data.get('gender', ''),
            'current_status': staff_data.get('current_status', 'off_duty'),  # on_duty, off_duty, break, lunch, vacation, sick_leave
            'current_location': staff_data.get('current_location', {}),  # current working location
            'assigned_patients': staff_data.get('assigned_patients', []),
            'is_active': staff_data.get('is_active', True),
            'last_login': None,
            'last_logout': None,
            'permissions': staff_data.get('permissions', []),
            'supervisor_id': staff_data.get('supervisor_id', None),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Check if staff_id or email already exists
        existing_staff = self.staff_collection.find_one({
            '$or': [
                {'staff_id': staff_data['staff_id']},
                {'email': staff_data['email']}
            ]
        })
        if existing_staff:
            raise ValueError(f"Staff member with ID {staff_data['staff_id']} or email {staff_data['email']} already exists")
        
        result = self.staff_collection.insert_one(staff)
        return str(result.inserted_id)
    
    def authenticate_staff(self, identifier, password):
        """Authenticate staff member by email or staff_id"""
        password_hash = self.hash_password(password)
        
        staff = self.staff_collection.find_one({
            '$and': [
                {
                    '$or': [
                        {'email': identifier},
                        {'staff_id': identifier}
                    ]
                },
                {'password_hash': password_hash},
                {'is_active': True}
            ]
        })
        
        if staff:
            # Update last login
            self.staff_collection.update_one(
                {'_id': staff['_id']},
                {'$set': {'last_login': datetime.utcnow(), 'updated_at': datetime.utcnow()}}
            )
            staff['_id'] = str(staff['_id'])
            # Don't return password hash
            del staff['password_hash']
            return staff
        
        return None
    
    def clock_in(self, staff_id, location=None):
        """Clock in staff member"""
        staff = self.get_staff_by_id(staff_id)
        if not staff:
            raise ValueError(f"Staff member with ID {staff_id} not found")
        
        # Update staff status
        update_data = {
            'current_status': 'on_duty',
            'updated_at': datetime.utcnow()
        }
        
        if location:
            update_data['current_location'] = location
        
        self.staff_collection.update_one(
            {'staff_id': staff_id},
            {'$set': update_data}
        )
        
        # Log attendance
        attendance = {
            'staff_id': staff_id,
            'clock_in': datetime.utcnow(),
            'clock_out': None,
            'total_hours': 0,
            'break_times': [],
            'location': location or staff.get('primary_location', {}),
            'date': datetime.utcnow().date()
        }
        
        result = self.attendance_collection.insert_one(attendance)
        return str(result.inserted_id)
    
    def clock_out(self, staff_id):
        """Clock out staff member"""
        # Update staff status
        self.staff_collection.update_one(
            {'staff_id': staff_id},
            {'$set': {
                'current_status': 'off_duty',
                'last_logout': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }}
        )
        
        # Update attendance record
        today = datetime.utcnow().date()
        attendance = self.attendance_collection.find_one({
            'staff_id': staff_id,
            'date': today,
            'clock_out': None
        })
        
        if attendance:
            clock_out_time = datetime.utcnow()
            total_hours = (clock_out_time - attendance['clock_in']).total_seconds() / 3600
            
            self.attendance_collection.update_one(
                {'_id': attendance['_id']},
                {'$set': {
                    'clock_out': clock_out_time,
                    'total_hours': round(total_hours, 2)
                }}
            )
            
            return True
        return False
    
    def update_staff_status(self, staff_id, status, location=None, reason=''):
        """Update staff status (break, lunch, etc.)"""
        valid_statuses = ['on_duty', 'off_duty', 'break', 'lunch', 'vacation', 'sick_leave', 'emergency_leave']
        
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        
        update_data = {
            'current_status': status,
            'updated_at': datetime.utcnow()
        }
        
        if location:
            update_data['current_location'] = location
        
        # Log break times if applicable
        if status in ['break', 'lunch']:
            today = datetime.utcnow().date()
            self.attendance_collection.update_one(
                {'staff_id': staff_id, 'date': today, 'clock_out': None},
                {'$push': {
                    'break_times': {
                        'type': status,
                        'start_time': datetime.utcnow(),
                        'reason': reason
                    }
                }}
            )
        
        result = self.staff_collection.update_one(
            {'staff_id': staff_id},
            {'$set': update_data}
        )
        
        return result.modified_count > 0
    
    def assign_patient_to_staff(self, staff_id, patient_id, assignment_type='primary'):
        """Assign a patient to staff member"""
        assignment = {
            'staff_id': staff_id,
            'patient_id': patient_id,
            'assignment_type': assignment_type,  # primary, secondary, consultant
            'assigned_at': datetime.utcnow(),
            'is_active': True
        }
        
        # Add to patient assignments collection
        result = self.patient_assignments_collection.insert_one(assignment)
        
        # Update staff's assigned patients list
        self.staff_collection.update_one(
            {'staff_id': staff_id},
            {'$addToSet': {'assigned_patients': patient_id}}
        )
        
        return str(result.inserted_id)
    
    def remove_patient_from_staff(self, staff_id, patient_id):
        """Remove patient assignment from staff member"""
        # Deactivate assignment
        self.patient_assignments_collection.update_one(
            {'staff_id': staff_id, 'patient_id': patient_id, 'is_active': True},
            {'$set': {'is_active': False, 'unassigned_at': datetime.utcnow()}}
        )
        
        # Remove from staff's assigned patients list
        result = self.staff_collection.update_one(
            {'staff_id': staff_id},
            {'$pull': {'assigned_patients': patient_id}}
        )
        
        return result.modified_count > 0
    
    def get_all_staff(self):
        """Get all staff members"""
        staff_list = list(self.staff_collection.find({}, {'password_hash': 0}))
        for staff in staff_list:
            staff['_id'] = str(staff['_id'])
        return staff_list
    
    def get_staff_by_id(self, staff_id):
        """Get staff member by ID"""
        staff = self.staff_collection.find_one({'staff_id': staff_id}, {'password_hash': 0})
        if staff:
            staff['_id'] = str(staff['_id'])
        return staff
    
    def get_staff_by_department(self, department):
        """Get staff members by department"""
        staff_list = list(self.staff_collection.find({'department': department}, {'password_hash': 0}))
        for staff in staff_list:
            staff['_id'] = str(staff['_id'])
        return staff_list
    
    def get_staff_by_role(self, role):
        """Get staff members by role"""
        staff_list = list(self.staff_collection.find({'role': role}, {'password_hash': 0}))
        for staff in staff_list:
            staff['_id'] = str(staff['_id'])
        return staff_list
    
    def get_staff_by_status(self, status):
        """Get staff members by current status"""
        staff_list = list(self.staff_collection.find({'current_status': status}, {'password_hash': 0}))
        for staff in staff_list:
            staff['_id'] = str(staff['_id'])
        return staff_list
    
    def get_on_duty_staff(self):
        """Get all staff currently on duty"""
        return self.get_staff_by_status('on_duty')
    
    def get_staff_on_break(self):
        """Get all staff currently on break or lunch"""
        staff_list = list(self.staff_collection.find(
            {'current_status': {'$in': ['break', 'lunch']}}, 
            {'password_hash': 0}
        ))
        for staff in staff_list:
            staff['_id'] = str(staff['_id'])
        return staff_list
    
    def get_staff_attendance(self, staff_id=None, date_from=None, date_to=None):
        """Get attendance records"""
        query = {}
        
        if staff_id:
            query['staff_id'] = staff_id
        
        if date_from or date_to:
            date_query = {}
            if date_from:
                date_query['$gte'] = date_from
            if date_to:
                date_query['$lte'] = date_to
            query['date'] = date_query
        
        attendance = list(self.attendance_collection.find(query).sort('date', -1))
        for record in attendance:
            record['_id'] = str(record['_id'])
        
        return attendance
    
    def create_staff_schedule(self, schedule_data):
        """Create staff schedule"""
        schedule = {
            'staff_id': schedule_data['staff_id'],
            'date': schedule_data['date'],
            'shift_start': schedule_data['shift_start'],
            'shift_end': schedule_data['shift_end'],
            'break_times': schedule_data.get('break_times', []),
            'department': schedule_data.get('department', ''),
            'location': schedule_data.get('location', {}),
            'notes': schedule_data.get('notes', ''),
            'created_at': datetime.utcnow()
        }
        
        result = self.schedules_collection.insert_one(schedule)
        return str(result.inserted_id)
    
    def get_staff_schedule(self, staff_id, date_from=None, date_to=None):
        """Get staff schedule"""
        query = {'staff_id': staff_id}
        
        if date_from or date_to:
            date_query = {}
            if date_from:
                date_query['$gte'] = date_from
            if date_to:
                date_query['$lte'] = date_to
            query['date'] = date_query
        
        schedules = list(self.schedules_collection.find(query).sort('date', 1))
        for schedule in schedules:
            schedule['_id'] = str(schedule['_id'])
        
        return schedules
    
    def search_staff(self, search_term):
        """Search staff by name, staff_id, or email"""
        search_pattern = {'$regex': search_term, '$options': 'i'}
        query = {
            '$or': [
                {'full_name': search_pattern},
                {'first_name': search_pattern},
                {'last_name': search_pattern},
                {'staff_id': search_pattern},
                {'email': search_pattern},
                {'employee_number': search_pattern}
            ]
        }
        
        staff_list = list(self.staff_collection.find(query, {'password_hash': 0}))
        for staff in staff_list:
            staff['_id'] = str(staff['_id'])
        return staff_list
    
    def get_staff_statistics(self):
        """Get comprehensive staff statistics"""
        total_staff = self.staff_collection.count_documents({'is_active': True})
        on_duty = self.staff_collection.count_documents({'current_status': 'on_duty'})
        on_break = self.staff_collection.count_documents({'current_status': {'$in': ['break', 'lunch']}})
        on_vacation = self.staff_collection.count_documents({'current_status': 'vacation'})
        sick_leave = self.staff_collection.count_documents({'current_status': 'sick_leave'})
        
        # Department breakdown
        department_stats = list(self.staff_collection.aggregate([
            {'$match': {'is_active': True}},
            {'$group': {
                '_id': '$department',
                'total': {'$sum': 1},
                'on_duty': {'$sum': {'$cond': [{'$eq': ['$current_status', 'on_duty']}, 1, 0]}}
            }}
        ]))
        
        # Role breakdown
        role_stats = list(self.staff_collection.aggregate([
            {'$match': {'is_active': True}},
            {'$group': {
                '_id': '$role',
                'count': {'$sum': 1}
            }}
        ]))
        
        return {
            'total_staff': total_staff,
            'on_duty': on_duty,
            'on_break': on_break,
            'on_vacation': on_vacation,
            'sick_leave': sick_leave,
            'department_breakdown': department_stats,
            'role_breakdown': role_stats
        }
    
    def update_staff_location(self, staff_id, location):
        """Update staff current location"""
        result = self.staff_collection.update_one(
            {'staff_id': staff_id},
            {'$set': {
                'current_location': location,
                'updated_at': datetime.utcnow()
            }}
        )
        return result.modified_count > 0
    
    def deactivate_staff(self, staff_id, reason=''):
        """Deactivate staff member"""
        result = self.staff_collection.update_one(
            {'staff_id': staff_id},
            {'$set': {
                'is_active': False,
                'deactivation_reason': reason,
                'deactivated_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }}
        )
        return result.modified_count > 0

# Example usage and testing functions
def initialize_sample_staff():
    """Initialize some sample staff data for testing"""
    db = StaffManagementDB()
    
    # Sample staff members
    sample_staff = [
        {
            'staff_id': 'DR001',
            'employee_number': 'EMP001',
            'first_name': 'Dr. Sarah',
            'last_name': 'Johnson',
            'email': 'sarah.johnson@hospital.com',
            'phone': '555-0101',
            'password': 'password123',
            'role': 'doctor',
            'specialization': 'Cardiology',
            'department': 'Cardiology',
            'primary_location': {
                'building': 'Main Hospital',
                'floor': '3',
                'room': 'Cardiology Wing'
            },
            'shift': 'day',
            'qualifications': ['MD', 'Board Certified Cardiologist'],
            'certifications': ['ACLS', 'BLS']
        },
        {
            'staff_id': 'NUR001',
            'employee_number': 'EMP002',
            'first_name': 'Maria',
            'last_name': 'Garcia',
            'email': 'maria.garcia@hospital.com',
            'phone': '555-0102',
            'password': 'nurse123',
            'role': 'nurse',
            'department': 'ICU',
            'primary_location': {
                'building': 'Main Hospital',
                'floor': '2',
                'room': 'ICU-A'
            },
            'shift': 'night',
            'qualifications': ['RN', 'BSN'],
            'certifications': ['BLS', 'ACLS', 'Critical Care']
        },
        {
            'staff_id': 'TECH001',
            'employee_number': 'EMP003',
            'first_name': 'Robert',
            'last_name': 'Smith',
            'email': 'robert.smith@hospital.com',
            'phone': '555-0103',
            'password': 'tech123',
            'role': 'technician',
            'department': 'Radiology',
            'primary_location': {
                'building': 'Main Hospital',
                'floor': '1',
                'room': 'Radiology Dept'
            },
            'shift': 'day',
            'qualifications': ['RT', 'Associate Degree'],
            'certifications': ['ARRT']
        },
        {
            'staff_id': 'ADM001',
            'employee_number': 'EMP004',
            'first_name': 'Jennifer',
            'last_name': 'Brown',
            'email': 'jennifer.brown@hospital.com',
            'phone': '555-0104',
            'password': 'admin123',
            'role': 'admin',
            'department': 'Administration',
            'primary_location': {
                'building': 'Administrative Building',
                'floor': '1',
                'room': 'Office 101'
            },
            'shift': 'day',
            'permissions': ['user_management', 'reporting', 'scheduling']
        }
    ]
    
    # Check if staff already exists
    if db.staff_collection.count_documents({}) == 0:
        for staff in sample_staff:
            try:
                db.create_staff_member(staff)
                print(f"Staff member {staff['first_name']} {staff['last_name']} created successfully!")
            except ValueError as e:
                print(f"Error creating staff member {staff['first_name']} {staff['last_name']}: {e}")
    else:
        print("Staff members already exist in database.")
    
    return db

if __name__ == "__main__":
    # Test the database connection and functions
    try:
        db = initialize_sample_staff()
        
        # Test getting all staff
        all_staff = db.get_all_staff()
        print(f"Total staff members: {len(all_staff)}")
        
        # Test authentication
        auth_result = db.authenticate_staff('sarah.johnson@hospital.com', 'password123')
        if auth_result:
            print(f"Authentication successful for {auth_result['full_name']}")
        
        # Test clock in/out
        print("\nTesting clock in/out:")
        db.clock_in('DR001', {'building': 'Main Hospital', 'floor': '3', 'room': '301'})
        print("Dr. Sarah Johnson clocked in")
        
        # Test status updates
        db.update_staff_status('DR001', 'lunch', reason='Lunch break')
        print("Dr. Sarah Johnson status updated to lunch")
        
        # Test getting on-duty staff
        on_duty_staff = db.get_on_duty_staff()
        print(f"Staff members on duty: {len(on_duty_staff)}")
        
        # Test statistics
        stats = db.get_staff_statistics()
        print("Staff Statistics:", stats)
        
        # Test search
        search_results = db.search_staff("Sarah")
        print(f"Search results for 'Sarah': {len(search_results)} staff members found")
        
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        print("Make sure MongoDB is running on your system.")