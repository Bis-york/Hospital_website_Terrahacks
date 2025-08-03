#!/usr/bin/env python3
"""
Database Utilities for Hospital Management System
Provides functions to reset database and manage hospital data from terminal
"""

import sys
import os
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our database modules
from hospital import HospitalManagementSystem
from hospital_beds import HospitalBedsDB
from patient_data import PatientDataDB
from med_inv import MedicalInventoryDB
from staff_inv import StaffManagementDB

class DatabaseUtils:
    def __init__(self):
        """Initialize MongoDB connection and database modules"""
        self.client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
        self.db = self.client.hospital_db
        
        # Initialize management system
        self.hms = HospitalManagementSystem()
        
        # Get all collections
        self.collections = {
            'hospitals': self.db.hospitals,
            'beds': self.db.beds,
            'patients': self.db.patients,
            'staff': self.db.staff,
            'medical_inventory': self.db.medical_inventory,
            'departments': self.db.departments,
            'staff_attendance': self.db.staff_attendance,
            'staff_schedules': self.db.staff_schedules,
            'patient_assignments': self.db.patient_assignments
        }
    
    def reset_database(self, confirm=True):
        """Reset (clear) all hospital database collections"""
        if confirm:
            print("⚠️  WARNING: This will permanently delete ALL data in the hospital database!")
            print("Collections that will be cleared:")
            for collection_name in self.collections.keys():
                count = self.collections[collection_name].count_documents({})
                print(f"  - {collection_name}: {count} documents")
            
            response = input("\nAre you sure you want to proceed? Type 'YES' to confirm: ")
            if response != 'YES':
                print("❌ Database reset cancelled.")
                return False
        
        print("\n🗑️  Clearing database collections...")
        
        cleared_counts = {}
        for collection_name, collection in self.collections.items():
            count_before = collection.count_documents({})
            if count_before > 0:
                result = collection.delete_many({})
                cleared_counts[collection_name] = result.deleted_count
                print(f"   ✓ Cleared {collection_name}: {result.deleted_count} documents")
            else:
                print(f"   - {collection_name}: already empty")
        
        total_cleared = sum(cleared_counts.values())
        print(f"\n✅ Database reset complete! Cleared {total_cleared} total documents.")
        return True
    
    def add_hospital_interactive(self):
        """Interactive function to add a hospital from terminal"""
        print("\n🏥 Add New Hospital")
        print("=" * 50)
        
        try:
            # Required fields
            hospital_id = input("Hospital ID (e.g., HOSP001): ").strip()
            if not hospital_id:
                print("❌ Hospital ID is required!")
                return None
            
            name = input("Hospital Name: ").strip()
            if not name:
                print("❌ Hospital name is required!")
                return None
            
            address = input("Address: ").strip()
            city = input("City: ").strip()
            state = input("State/Province: ").strip()
            zip_code = input("ZIP/Postal Code: ").strip()
            phone = input("Phone Number: ").strip()
            
            # Optional fields with defaults
            email = input("Email (optional): ").strip()
            website = input("Website (optional): ").strip()
            
            # Hospital type
            print("\nHospital Type:")
            print("1. General")
            print("2. Specialty")
            print("3. Teaching")
            print("4. Rehabilitation")
            print("5. Psychiatric")
            type_choice = input("Select type (1-5, default 1): ").strip()
            
            hospital_types = {
                '1': 'general',
                '2': 'specialty', 
                '3': 'teaching',
                '4': 'rehabilitation',
                '5': 'psychiatric'
            }
            hospital_type = hospital_types.get(type_choice, 'general')
            
            # Capacity information
            print("\n🛏️ Hospital Capacity:")
            total_beds = self._get_int_input("Total beds (default 100): ", 100)
            icu_beds = self._get_int_input("ICU beds (default 10% of total): ", max(1, total_beds // 10))
            emergency_beds = self._get_int_input("Emergency beds (default 5% of total): ", max(1, total_beds // 20))
            operation_theaters = self._get_int_input("Operation theaters (default 5): ", 5)
            
            # Services
            print("\n🩺 Medical Services (comma-separated):")
            print("Example: Emergency, Cardiology, Neurology, Orthopedics, Pediatrics")
            services_input = input("Services: ").strip()
            services = [s.strip() for s in services_input.split(',')] if services_input else []
            
            # Departments
            print("\n🏢 Departments (comma-separated):")
            print("Example: Emergency, ICU, General, Surgery, Pediatrics, Cardiology")
            departments_input = input("Departments: ").strip()
            if departments_input:
                departments = [d.strip() for d in departments_input.split(',')]
            else:
                departments = ['Emergency', 'ICU', 'General', 'Surgery']
            
            # Facilities
            print("\n🏢 Facilities (comma-separated, optional):")
            print("Example: Parking, Cafeteria, Pharmacy, Laboratory, Radiology")
            facilities_input = input("Facilities: ").strip()
            facilities = [f.strip() for f in facilities_input.split(',')] if facilities_input else []
            
            # Emergency services
            emergency_services = self._get_yes_no("Emergency services available? (Y/n): ", True)
            
            # Build hospital data
            hospital_data = {
                'hospital_id': hospital_id,
                'name': name,
                'address': address,
                'city': city,
                'state': state,
                'zip_code': zip_code,
                'phone': phone,
                'email': email,
                'website': website,
                'hospital_type': hospital_type,
                'total_beds': total_beds,
                'icu_beds': icu_beds,
                'emergency_beds': emergency_beds,
                'operation_theaters': operation_theaters,
                'services': services,
                'departments': departments,
                'facilities': facilities,
                'emergency_services': emergency_services
            }
            
            # Confirm before creating
            print("\n📋 Hospital Summary:")
            print(f"ID: {hospital_id}")
            print(f"Name: {name}")
            print(f"Location: {city}, {state}")
            print(f"Type: {hospital_type}")
            print(f"Total Beds: {total_beds}")
            print(f"Departments: {', '.join(departments)}")
            
            if self._get_yes_no("\nCreate this hospital? (Y/n): ", True):
                # Create hospital
                result = self.hms.create_hospital(hospital_data)
                print(f"\n✅ Hospital '{name}' created successfully!")
                print(f"Database ID: {result}")
                
                # Show what was automatically created
                print(f"\n🎉 Automatically created:")
                print(f"   • {total_beds} beds distributed across departments")
                print(f"   • Basic medical inventory")
                print(f"   • Sample staff members")
                
                return hospital_data
            else:
                print("❌ Hospital creation cancelled.")
                return None
                
        except ValueError as e:
            print(f"❌ Error: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None
    
    def list_hospitals(self):
        """List all hospitals in the database"""
        hospitals = self.hms.get_all_hospitals()
        
        if not hospitals:
            print("📭 No hospitals found in the database.")
            return
        
        print(f"\n🏥 Hospitals in Database ({len(hospitals)} total)")
        print("=" * 80)
        
        for i, hospital in enumerate(hospitals, 1):
            print(f"{i}. {hospital['name']}")
            print(f"   ID: {hospital['hospital_id']}")
            print(f"   Location: {hospital.get('city', 'N/A')}, {hospital.get('state', 'N/A')}")
            print(f"   Type: {hospital.get('hospital_type', 'N/A')}")
            print(f"   Beds: {hospital.get('capacity', {}).get('total_beds', 'N/A')}")
            print(f"   Created: {hospital.get('created_at', 'N/A')}")
            print()
    
    def get_database_stats(self):
        """Show database statistics"""
        print("\n📊 Database Statistics")
        print("=" * 50)
        
        for collection_name, collection in self.collections.items():
            count = collection.count_documents({})
            print(f"{collection_name.replace('_', ' ').title()}: {count}")
        
        # Hospital-specific stats
        hospitals = list(self.collections['hospitals'].find())
        if hospitals:
            print(f"\n🏥 Hospital Details:")
            for hospital in hospitals:
                print(f"   • {hospital['name']} ({hospital['hospital_id']})")
                
                # Get hospital-specific counts
                hospital_id = hospital['hospital_id']
                beds_count = self.collections['beds'].count_documents({'hospital_id': hospital_id})
                patients_count = self.collections['patients'].count_documents({'current_hospital': hospital_id})
                staff_count = self.collections['staff'].count_documents({'hospital_id': hospital_id})
                inventory_count = self.collections['medical_inventory'].count_documents({'hospital_id': hospital_id})
                
                print(f"     - Beds: {beds_count}")
                print(f"     - Patients: {patients_count}")
                print(f"     - Staff: {staff_count}")
                print(f"     - Inventory Items: {inventory_count}")
    
    def add_sample_hospitals(self):
        """Add sample hospitals for testing"""
        sample_hospitals = [
            {
                'hospital_id': 'DEMO001',
                'name': 'Metro General Hospital',
                'address': '123 Healthcare Drive',
                'city': 'Metropolitan City',
                'state': 'CA',
                'zip_code': '90210',
                'phone': '555-0100',
                'email': 'info@metrogeneral.com',
                'hospital_type': 'general',
                'total_beds': 200,
                'icu_beds': 20,
                'emergency_beds': 15,
                'operation_theaters': 8,
                'services': ['Emergency', 'Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics'],
                'departments': ['Emergency', 'ICU', 'General', 'Surgery', 'Pediatrics', 'Cardiology'],
                'facilities': ['Parking', 'Cafeteria', 'Pharmacy', 'Laboratory', 'Radiology'],
                'emergency_services': True
            },
            {
                'hospital_id': 'DEMO002',
                'name': 'Sunrise Medical Center',
                'address': '456 Wellness Boulevard',
                'city': 'Sunrise Valley',
                'state': 'TX',
                'zip_code': '75001',
                'phone': '555-0200',
                'email': 'contact@sunrisemedical.com',
                'hospital_type': 'specialty',
                'total_beds': 150,
                'icu_beds': 15,
                'emergency_beds': 10,
                'operation_theaters': 6,
                'services': ['Cardiology', 'Oncology', 'Neurology'],
                'departments': ['Cardiology', 'Oncology', 'Neurology', 'ICU'],
                'facilities': ['Parking', 'Cafeteria', 'Pharmacy'],
                'emergency_services': True
            },
            {
                'hospital_id': 'DEMO003',
                'name': 'University Teaching Hospital',
                'address': '789 Academic Street',
                'city': 'University Town',
                'state': 'NY',
                'zip_code': '10001',
                'phone': '555-0300',
                'email': 'info@universityhospital.edu',
                'hospital_type': 'teaching',
                'total_beds': 300,
                'icu_beds': 30,
                'emergency_beds': 20,
                'operation_theaters': 12,
                'services': ['Emergency', 'Internal Medicine', 'Surgery', 'Pediatrics', 'Psychiatry'],
                'departments': ['Emergency', 'ICU', 'Internal Medicine', 'Surgery', 'Pediatrics', 'Psychiatry'],
                'facilities': ['Parking', 'Cafeteria', 'Pharmacy', 'Laboratory', 'Radiology', 'Library'],
                'emergency_services': True
            }
        ]
        
        print("\n🏥 Adding Sample Hospitals...")
        print("=" * 50)
        
        created_count = 0
        for hospital_data in sample_hospitals:
            try:
                self.hms.create_hospital(hospital_data)
                print(f"✅ Created: {hospital_data['name']}")
                created_count += 1
            except ValueError as e:
                print(f"⚠️  Skipped: {hospital_data['name']} - {e}")
            except Exception as e:
                print(f"❌ Error creating {hospital_data['name']}: {e}")
        
        print(f"\n🎉 Successfully created {created_count} sample hospitals!")
        return created_count
    
    def _get_int_input(self, prompt, default=0):
        """Helper to get integer input with default"""
        response = input(prompt).strip()
        if not response:
            return default
        try:
            return int(response)
        except ValueError:
            print(f"Invalid number, using default: {default}")
            return default
    
    def _get_yes_no(self, prompt, default=True):
        """Helper to get yes/no input with default"""
        response = input(prompt).strip().lower()
        if not response:
            return default
        return response.startswith('y')

def main():
    """Main function for interactive terminal usage"""
    print("🏥 Hospital Database Management Utility")
    print("=" * 50)
    
    try:
        db_utils = DatabaseUtils()
        
        while True:
            print("\nAvailable Commands:")
            print("1. 📊 Show database statistics")
            print("2. 📋 List hospitals")
            print("3. ➕ Add new hospital (interactive)")
            print("4. 🎯 Add sample hospitals")
            print("5. 🗑️  Reset database (clear all data)")
            print("6. ❌ Exit")
            
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == '1':
                db_utils.get_database_stats()
            
            elif choice == '2':
                db_utils.list_hospitals()
            
            elif choice == '3':
                db_utils.add_hospital_interactive()
            
            elif choice == '4':
                db_utils.add_sample_hospitals()
            
            elif choice == '5':
                db_utils.reset_database()
            
            elif choice == '6':
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please select 1-6.")
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure MongoDB is running and accessible.")

if __name__ == "__main__":
    main()
