#!/usr/bin/env python3
"""
Script to add sample patient data to the hospital database.
This script creates realistic patient records for testing purposes.
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hospital import HospitalManagementSystem

def create_sample_patients():
    """Create sample patients for testing"""
    
    # Initialize hospital management system
    hms = HospitalManagementSystem()
    
    # Get the first hospital ID from the database
    hospitals = hms.get_all_hospitals()
    if not hospitals:
        print("No hospitals found. Please create a hospital first.")
        return
    
    hospital_id = hospitals[0]['hospital_id']
    print(f"Adding patients to hospital: {hospital_id}")
    
    # Get available beds for assignment
    beds = hms.get_hospital_beds(hospital_id)
    available_beds = [bed for bed in beds if bed['status'] == 'available']
    
    # Sample patient data
    sample_patients = [
        {
            'patient_id': 'PAT001',
            'name': 'John Smith',
            'age': 45,
            'gender': 'male',
            'phone': '555-0123',
            'email': 'john.smith@email.com',
            'address': '123 Main St, City, State 12345',
            'emergency_contact': {
                'name': 'Jane Smith',
                'relationship': 'Spouse',
                'phone': '555-0124'
            },
            'medical_record_number': 'MRN001',
            'diagnosis': 'Acute chest pain, possible myocardial infarction',
            'treatment_plan': 'Cardiac monitoring, serial ECGs, troponin levels',
            'medications': ['Aspirin 81mg', 'Metoprolol 25mg', 'Atorvastatin 40mg'],
            'allergies': ['Penicillin'],
            'medical_history': ['Hypertension', 'Diabetes Type 2'],
            'admission_date': datetime.utcnow() - timedelta(days=2),
            'doctor_report': 'Patient admitted with acute chest pain. ECG shows mild ST elevation. Cardiac enzymes elevated.',
            'incident_report': 'Patient experienced chest pain at home around 2 PM',
            'status': 'admitted',
            'current_hospital': hospital_id
        },
        {
            'patient_id': 'PAT002',
            'name': 'Maria Garcia',
            'age': 32,
            'gender': 'female',
            'phone': '555-0456',
            'email': 'maria.garcia@email.com',
            'address': '456 Oak Ave, City, State 12345',
            'emergency_contact': {
                'name': 'Carlos Garcia',
                'relationship': 'Husband',
                'phone': '555-0457'
            },
            'medical_record_number': 'MRN002',
            'diagnosis': 'Severe pneumonia with respiratory failure',
            'treatment_plan': 'Ventilator support, IV antibiotics, respiratory therapy',
            'medications': ['Ceftriaxone', 'Azithromycin', 'Prednisone'],
            'allergies': ['Sulfa drugs'],
            'medical_history': ['Asthma'],
            'admission_date': datetime.utcnow() - timedelta(days=4),
            'doctor_report': 'Patient admitted with severe pneumonia. Bilateral consolidation on chest X-ray. Requires ventilator support.',
            'incident_report': 'Patient brought by ambulance with difficulty breathing',
            'status': 'admitted',
            'current_hospital': hospital_id
        },
        {
            'patient_id': 'PAT003',
            'name': 'Robert Johnson',
            'age': 67,
            'gender': 'male',
            'phone': '555-0789',
            'email': 'robert.johnson@email.com',
            'address': '789 Pine St, City, State 12345',
            'emergency_contact': {
                'name': 'Linda Johnson',
                'relationship': 'Wife',
                'phone': '555-0790'
            },
            'medical_record_number': 'MRN003',
            'diagnosis': 'Right hip fracture post fall',
            'treatment_plan': 'Surgical repair, post-operative recovery, physical therapy',
            'medications': ['Tramadol', 'Calcium supplement', 'Vitamin D'],
            'allergies': [],
            'medical_history': ['Osteoporosis', 'Hypertension'],
            'admission_date': datetime.utcnow() - timedelta(days=1),
            'doctor_report': 'Successful open reduction and internal fixation of right hip fracture. Post-operative recovery proceeding well.',
            'incident_report': 'Patient fell at home while getting up from chair',
            'status': 'admitted',
            'current_hospital': hospital_id
        },
        {
            'patient_id': 'PAT004',
            'name': 'Emma Davis',
            'age': 28,
            'gender': 'female',
            'phone': '555-0321',
            'email': 'emma.davis@email.com',
            'address': '321 Elm St, City, State 12345',
            'emergency_contact': {
                'name': 'Tom Davis',
                'relationship': 'Brother',
                'phone': '555-0322'
            },
            'medical_record_number': 'MRN004',
            'diagnosis': 'Appendectomy - recovered',
            'treatment_plan': 'Post-operative follow-up complete',
            'medications': [],
            'allergies': [],
            'medical_history': [],
            'admission_date': datetime.utcnow() - timedelta(days=5),
            'discharge_date': datetime.utcnow() - timedelta(days=2),
            'doctor_report': 'Successful laparoscopic appendectomy. Patient recovered well, no complications.',
            'incident_report': 'Patient presented with acute abdominal pain',
            'status': 'discharged',
            'current_hospital': None
        },
        {
            'patient_id': 'PAT005',
            'name': 'David Wilson',
            'age': 55,
            'gender': 'male',
            'phone': '555-0654',
            'email': 'david.wilson@email.com',
            'address': '654 Maple Dr, City, State 12345',
            'emergency_contact': {
                'name': 'Sarah Wilson',
                'relationship': 'Wife',
                'phone': '555-0655'
            },
            'medical_record_number': 'MRN005',
            'diagnosis': 'Diabetic foot infection, hyperglycemia',
            'treatment_plan': 'IV antibiotics, insulin protocol, wound care',
            'medications': ['Insulin', 'Metformin', 'Cephalexin'],
            'allergies': [],
            'medical_history': ['Diabetes Type 2', 'Peripheral neuropathy'],
            'admission_date': datetime.utcnow(),
            'doctor_report': 'Patient admitted with infected foot ulcer and elevated blood glucose. Responding well to treatment.',
            'incident_report': 'Patient noticed worsening foot wound with fever',
            'status': 'admitted',
            'current_hospital': hospital_id
        },
        {
            'patient_id': 'PAT006',
            'name': 'Sarah Thompson',
            'age': 23,
            'gender': 'female',
            'phone': '555-0987',
            'email': 'sarah.thompson@email.com',
            'address': '987 Cedar Lane, City, State 12345',
            'emergency_contact': {
                'name': 'Mary Thompson',
                'relationship': 'Mother',
                'phone': '555-0988'
            },
            'medical_record_number': 'MRN006',
            'diagnosis': 'Motor vehicle accident - multiple contusions',
            'treatment_plan': 'Observation, pain management, CT monitoring',
            'medications': ['Ibuprofen', 'Acetaminophen'],
            'allergies': [],
            'medical_history': [],
            'admission_date': datetime.utcnow() - timedelta(hours=6),
            'doctor_report': 'Patient involved in MVA. Multiple contusions but no major injuries. Under observation.',
            'incident_report': 'Patient brought by ambulance from accident scene',
            'status': 'admitted',
            'current_hospital': hospital_id
        }
    ]
    
    # Create patients and assign beds where available
    created_count = 0
    for i, patient_data in enumerate(sample_patients):
        try:
            # Assign bed if patient is admitted and bed is available
            if patient_data['status'] == 'admitted' and i < len(available_beds):
                bed = available_beds[i]
                patient_data['is_in_bed'] = True
                patient_data['bed_info'] = {
                    'bed_id': bed['bed_number'],  # Store bed_number as bed_id for display
                    'bed_number': bed['bed_number'],
                    'room_number': bed['room_number'],
                    'department': bed['department'],
                    'hospital_id': hospital_id
                }
                
                # Update bed status using MongoDB _id
                hms.beds_db.update_bed_status(bed['_id'], 'occupied', patient_data['patient_id'])
            
            # Add admission history
            if patient_data['status'] == 'admitted':
                patient_data['admission_history'] = [{
                    'hospital_id': hospital_id,
                    'admission_date': patient_data['admission_date'],
                    'discharge_date': patient_data.get('discharge_date'),
                    'reason': patient_data['diagnosis']
                }]
            elif patient_data['status'] == 'discharged':
                patient_data['admission_history'] = [{
                    'hospital_id': hospital_id,
                    'admission_date': patient_data['admission_date'],
                    'discharge_date': patient_data['discharge_date'],
                    'reason': patient_data['diagnosis']
                }]
            
            # Create patient
            patient_id = hms.patients_db.create_patient(patient_data)
            print(f"✅ Created patient: {patient_data['name']} (ID: {patient_data['patient_id']})")
            
            if patient_data.get('is_in_bed'):
                print(f"   🛏️  Assigned to bed: {patient_data['bed_info']['bed_number']} in {patient_data['bed_info']['department']}")
            
            created_count += 1
            
        except ValueError as e:
            if "already exists" in str(e):
                print(f"⚠️  Patient {patient_data['patient_id']} already exists, skipping...")
            else:
                print(f"❌ Error creating patient {patient_data['patient_id']}: {e}")
        except Exception as e:
            print(f"❌ Error creating patient {patient_data['patient_id']}: {e}")
    
    print(f"\n✅ Successfully created {created_count} patients")
    
    # Display statistics
    try:
        stats = hms.patients_db.get_patient_statistics_by_hospital(hospital_id)
        print(f"\n📊 Patient Statistics for {hospital_id}:")
        print(f"   Total patients: {stats['total_patients']}")
        print(f"   Currently admitted: {stats['admitted_patients']}")
        print(f"   Discharged: {stats['discharged_patients']}")
        print(f"   Patients in beds: {stats['patients_in_beds']}")
        print(f"   Patients without beds: {stats['patients_without_beds']}")
        
        if stats['department_distribution']:
            print(f"   Department distribution:")
            for dept, count in stats['department_distribution'].items():
                print(f"     {dept}: {count} patients")
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")

if __name__ == "__main__":
    create_sample_patients()
