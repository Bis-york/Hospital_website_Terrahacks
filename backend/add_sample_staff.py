"""
Script to add sample staff data to the hospital management system
"""

import sys
import os
from datetime import datetime, timedelta
import random
from pymongo import MongoClient

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from staff_data import staff_manager

def create_sample_staff():
    """Create sample staff members for testing"""
    
    # Get database connection
    client = MongoClient('mongodb://localhost:27017/')
    db = client['hospital_db']
    hospitals_collection = db['hospitals']
    
    # Get existing hospitals
    hospitals = list(hospitals_collection.find())
    if not hospitals:
        print("No hospitals found! Please create hospitals first.")
        return False
    
    # Use the first hospital for sample data
    hospital = hospitals[0]
    hospital_id = hospital.get('hospital_id', 'HOSP001')
    
    print(f"Creating sample staff for hospital: {hospital.get('name', 'Unknown')} (ID: {hospital_id})")
    
    # Sample staff data
    sample_staff = [
        {
            "staff_id": "STAFF001",
            "hospital_id": hospital_id,
            "name": "Dr. Sarah Wilson",
            "email": "sarah.wilson@hospital.com",
            "phone": "+1-555-0101",
            "department": "Cardiology",
            "position": "Senior Cardiologist",
            "employee_type": "Doctor",
            "shift": "Day",
            "status": "active",
            "qualifications": ["MD", "Board Certified Cardiologist", "Fellowship in Interventional Cardiology"],
            "experience_years": 15,
            "specializations": ["Interventional Cardiology", "Heart Surgery", "Cardiac Imaging"],
            "schedule": {
                "Monday": {"start": "08:00", "end": "17:00", "break": "12:00-13:00"},
                "Tuesday": {"start": "08:00", "end": "17:00", "break": "12:00-13:00"},
                "Wednesday": {"start": "08:00", "end": "17:00", "break": "12:00-13:00"},
                "Thursday": {"start": "08:00", "end": "17:00", "break": "12:00-13:00"},
                "Friday": {"start": "08:00", "end": "17:00", "break": "12:00-13:00"},
                "Saturday": "Off",
                "Sunday": "Off"
            },
            "emergency_contact": {
                "name": "John Wilson",
                "phone": "+1-555-0102",
                "relationship": "Spouse"
            },
            "address": "123 Medical Drive, City, State 12345",
            "salary": 250000,
            "last_login": datetime.now() - timedelta(hours=2)
        },
        {
            "staff_id": "STAFF002",
            "hospital_id": hospital_id,
            "name": "Nurse Emma Rodriguez",
            "email": "emma.rodriguez@hospital.com",
            "phone": "+1-555-0201",
            "department": "Emergency",
            "position": "Head Nurse",
            "employee_type": "Nurse",
            "shift": "Night",
            "status": "active",
            "qualifications": ["RN", "BSN", "Emergency Nursing Certification"],
            "experience_years": 8,
            "specializations": ["Emergency Care", "Trauma Nursing", "Critical Care"],
            "schedule": {
                "Monday": "Off",
                "Tuesday": {"start": "19:00", "end": "07:00", "break": "02:00-03:00"},
                "Wednesday": {"start": "19:00", "end": "07:00", "break": "02:00-03:00"},
                "Thursday": {"start": "19:00", "end": "07:00", "break": "02:00-03:00"},
                "Friday": {"start": "19:00", "end": "07:00", "break": "02:00-03:00"},
                "Saturday": "Off",
                "Sunday": "Off"
            },
            "emergency_contact": {
                "name": "Maria Rodriguez",
                "phone": "+1-555-0202",
                "relationship": "Mother"
            },
            "address": "456 Nurse Lane, City, State 12345",
            "salary": 85000,
            "last_login": datetime.now() - timedelta(hours=1)
        },
        {
            "staff_id": "STAFF003",
            "hospital_id": hospital_id,
            "name": "Dr. Michael Chen",
            "email": "michael.chen@hospital.com",
            "phone": "+1-555-0301",
            "department": "Emergency",
            "position": "Emergency Physician",
            "employee_type": "Doctor",
            "shift": "Day",
            "status": "active",
            "qualifications": ["MD", "Emergency Medicine Board Certification", "ACLS", "PALS"],
            "experience_years": 12,
            "specializations": ["Emergency Medicine", "Trauma Care", "Critical Care"],
            "schedule": {
                "Monday": {"start": "07:00", "end": "19:00", "break": "12:00-13:00"},
                "Tuesday": "Off",
                "Wednesday": {"start": "07:00", "end": "19:00", "break": "12:00-13:00"},
                "Thursday": "Off",
                "Friday": {"start": "07:00", "end": "19:00", "break": "12:00-13:00"},
                "Saturday": {"start": "07:00", "end": "19:00", "break": "12:00-13:00"},
                "Sunday": "Off"
            },
            "emergency_contact": {
                "name": "Lisa Chen",
                "phone": "+1-555-0302",
                "relationship": "Spouse"
            },
            "address": "789 Doctor Street, City, State 12345",
            "salary": 220000,
            "last_login": datetime.now() - timedelta(minutes=30)
        },
        {
            "staff_id": "STAFF004",
            "hospital_id": hospital_id,
            "name": "Technician James Park",
            "email": "james.park@hospital.com",
            "phone": "+1-555-0401",
            "department": "ICU",
            "position": "Medical Technician",
            "employee_type": "Technician",
            "shift": "Day",
            "status": "active",
            "qualifications": ["Medical Technology Certificate", "Lab Technician License"],
            "experience_years": 5,
            "specializations": ["Laboratory Testing", "Medical Equipment", "ICU Support"],
            "schedule": {
                "Monday": {"start": "08:00", "end": "16:00", "break": "12:00-13:00"},
                "Tuesday": {"start": "08:00", "end": "16:00", "break": "12:00-13:00"},
                "Wednesday": {"start": "08:00", "end": "16:00", "break": "12:00-13:00"},
                "Thursday": {"start": "08:00", "end": "16:00", "break": "12:00-13:00"},
                "Friday": {"start": "08:00", "end": "16:00", "break": "12:00-13:00"},
                "Saturday": "Off",
                "Sunday": "Off"
            },
            "emergency_contact": {
                "name": "Susan Park",
                "phone": "+1-555-0402",
                "relationship": "Mother"
            },
            "address": "321 Tech Avenue, City, State 12345",
            "salary": 55000,
            "last_login": datetime.now() - timedelta(hours=3)
        },
        {
            "staff_id": "STAFF005",
            "hospital_id": hospital_id,
            "name": "Dr. Lisa Thompson",
            "email": "lisa.thompson@hospital.com",
            "phone": "+1-555-0501",
            "department": "Pediatrics",
            "position": "Pediatrician",
            "employee_type": "Doctor",
            "shift": "Day",
            "status": "on_leave",
            "qualifications": ["MD", "Pediatrics Board Certification", "Child Development Specialist"],
            "experience_years": 10,
            "specializations": ["Pediatric Care", "Child Development", "Adolescent Medicine"],
            "schedule": {
                "Monday": "Off",
                "Tuesday": "Off",
                "Wednesday": "Off",
                "Thursday": "Off",
                "Friday": "Off",
                "Saturday": "Off",
                "Sunday": "Off"
            },
            "emergency_contact": {
                "name": "David Thompson",
                "phone": "+1-555-0502",
                "relationship": "Spouse"
            },
            "address": "654 Pediatric Way, City, State 12345",
            "salary": 180000,
            "last_login": datetime.now() - timedelta(days=7),
            "leave_reason": "Maternity Leave",
            "leave_start_date": datetime.now() - timedelta(days=30),
            "leave_end_date": datetime.now() + timedelta(days=60)
        },
        {
            "staff_id": "STAFF006",
            "hospital_id": hospital_id,
            "name": "Admin Jennifer Lee",
            "email": "jennifer.lee@hospital.com",
            "phone": "+1-555-0601",
            "department": "Administration",
            "position": "Hospital Administrator",
            "employee_type": "Administrator",
            "shift": "Day",
            "status": "active",
            "qualifications": ["MBA Healthcare Management", "Healthcare Administration Certificate"],
            "experience_years": 7,
            "specializations": ["Hospital Operations", "Staff Management", "Budget Planning"],
            "schedule": {
                "Monday": {"start": "08:00", "end": "17:00", "break": "12:00-13:00"},
                "Tuesday": {"start": "08:00", "end": "17:00", "break": "12:00-13:00"},
                "Wednesday": {"start": "08:00", "end": "17:00", "break": "12:00-13:00"},
                "Thursday": {"start": "08:00", "end": "17:00", "break": "12:00-13:00"},
                "Friday": {"start": "08:00", "end": "17:00", "break": "12:00-13:00"},
                "Saturday": "Off",
                "Sunday": "Off"
            },
            "emergency_contact": {
                "name": "Robert Lee",
                "phone": "+1-555-0602",
                "relationship": "Father"
            },
            "address": "987 Admin Boulevard, City, State 12345",
            "salary": 95000,
            "last_login": datetime.now() - timedelta(minutes=45)
        }
    ]
    
    # Insert staff members
    created_count = 0
    for staff_data in sample_staff:
        try:
            # Check if staff member already exists
            existing_staff = db['staff'].find_one({"staff_id": staff_data["staff_id"]})
            if existing_staff:
                print(f"Staff member {staff_data['name']} ({staff_data['staff_id']}) already exists, skipping...")
                continue
            
            staff_id = staff_manager.add_staff_member(staff_data)
            if staff_id:
                print(f"✅ Created staff member: {staff_data['name']} ({staff_data['staff_id']})")
                created_count += 1
            else:
                print(f"❌ Failed to create staff member: {staff_data['name']}")
        except Exception as e:
            print(f"❌ Error creating staff member {staff_data['name']}: {e}")
    
    print(f"\n🎉 Successfully created {created_count} staff members!")
    return True

if __name__ == "__main__":
    print("Creating sample staff data...")
    success = create_sample_staff()
    if success:
        print("Sample staff data creation completed!")
    else:
        print("Failed to create sample staff data!")
