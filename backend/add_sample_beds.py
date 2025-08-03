#!/usr/bin/env python3
"""
Add sample beds to different departments for testing
"""

import sys
import os
from pymongo import MongoClient
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hospital_beds import HospitalBedsDB
from hospital import HospitalManagementSystem

def add_sample_beds():
    """Add sample beds to different departments"""
    print("🛏️ Adding Sample Beds to Different Departments")
    print("=" * 50)
    
    try:
        # Initialize the hospital management system
        hms = HospitalManagementSystem()
        beds_db = HospitalBedsDB()
        
        # Get the first hospital
        hospitals = hms.get_all_hospitals()
        if not hospitals:
            print("❌ No hospitals found. Please create a hospital first.")
            return
        
        hospital_id = hospitals[0]['_id']
        hospital_name = hospitals[0]['name']
        print(f"🏥 Adding beds to: {hospital_name}")
        print()
        
        # Sample beds for different departments
        sample_beds = [
            # Emergency Department
            {'bed_number': 'E001', 'room_number': '101', 'department': 'emergency', 'bed_type': 'monitor', 'status': 'occupied', 'patient_id': 'P001'},
            {'bed_number': 'E002', 'room_number': '101', 'department': 'emergency', 'bed_type': 'standard', 'status': 'available'},
            {'bed_number': 'E003', 'room_number': '102', 'department': 'emergency', 'bed_type': 'intensive', 'status': 'occupied', 'patient_id': 'P002'},
            {'bed_number': 'E004', 'room_number': '102', 'department': 'emergency', 'bed_type': 'isolation', 'status': 'maintenance'},
            
            # ICU Department
            {'bed_number': 'I001', 'room_number': '301', 'department': 'icu', 'bed_type': 'intensive', 'status': 'occupied', 'patient_id': 'P003'},
            {'bed_number': 'I002', 'room_number': '301', 'department': 'icu', 'bed_type': 'intensive', 'status': 'occupied', 'patient_id': 'P004'},
            {'bed_number': 'I003', 'room_number': '302', 'department': 'icu', 'bed_type': 'intensive', 'status': 'available'},
            {'bed_number': 'I004', 'room_number': '302', 'department': 'icu', 'bed_type': 'intensive', 'status': 'maintenance'},
            
            # General Ward
            {'bed_number': 'G001', 'room_number': '201', 'department': 'general', 'bed_type': 'standard', 'status': 'occupied', 'patient_id': 'P005'},
            {'bed_number': 'G002', 'room_number': '201', 'department': 'general', 'bed_type': 'standard', 'status': 'available'},
            {'bed_number': 'G003', 'room_number': '202', 'department': 'general', 'bed_type': 'monitor', 'status': 'occupied', 'patient_id': 'P006'},
            {'bed_number': 'G004', 'room_number': '202', 'department': 'general', 'bed_type': 'standard', 'status': 'available'},
            
            # Cardiology Department
            {'bed_number': 'C001', 'room_number': '401', 'department': 'cardiology', 'bed_type': 'monitor', 'status': 'occupied', 'patient_id': 'P007'},
            {'bed_number': 'C002', 'room_number': '401', 'department': 'cardiology', 'bed_type': 'monitor', 'status': 'available'},
            {'bed_number': 'C003', 'room_number': '402', 'department': 'cardiology', 'bed_type': 'intensive', 'status': 'occupied', 'patient_id': 'P008'},
            
            # Pediatrics Department
            {'bed_number': 'P001', 'room_number': '501', 'department': 'pediatrics', 'bed_type': 'standard', 'status': 'occupied', 'patient_id': 'P009'},
            {'bed_number': 'P002', 'room_number': '501', 'department': 'pediatrics', 'bed_type': 'standard', 'status': 'available'},
            {'bed_number': 'P003', 'room_number': '502', 'department': 'pediatrics', 'bed_type': 'monitor', 'status': 'available'},
            
            # Surgery Department
            {'bed_number': 'S001', 'room_number': '601', 'department': 'surgery', 'bed_type': 'monitor', 'status': 'occupied', 'patient_id': 'P010'},
            {'bed_number': 'S002', 'room_number': '601', 'department': 'surgery', 'bed_type': 'standard', 'status': 'available'},
            {'bed_number': 'S003', 'room_number': '602', 'department': 'surgery', 'bed_type': 'monitor', 'status': 'maintenance'},
        ]
        
        # Add beds to the database
        created_count = 0
        for bed_data in sample_beds:
            bed_data['hospital_id'] = hospital_id
            bed_data['floor'] = 1
            bed_data['wing'] = 'Main'
            bed_data['notes'] = f'Sample bed for {bed_data["department"]} department'
            
            try:
                bed_id = beds_db.create_bed(bed_data)
                print(f"✅ Created bed {bed_data['bed_number']} in {bed_data['department']} department")
                created_count += 1
            except Exception as e:
                print(f"⚠️  Failed to create bed {bed_data['bed_number']}: {str(e)}")
        
        print()
        print(f"🎉 Successfully created {created_count} sample beds!")
        print(f"📊 Departments with beds:")
        
        # Show department summary
        departments = beds_db.get_departments_by_hospital(hospital_id)
        for dept in departments:
            dept_beds = beds_db.get_beds_by_department_and_hospital(dept, hospital_id)
            available = len([b for b in dept_beds if b['status'] == 'available'])
            occupied = len([b for b in dept_beds if b['status'] == 'occupied'])
            maintenance = len([b for b in dept_beds if b['status'] == 'maintenance'])
            print(f"   • {dept.title()}: {len(dept_beds)} beds ({available} available, {occupied} occupied, {maintenance} maintenance)")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    add_sample_beds()
