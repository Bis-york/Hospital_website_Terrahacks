"""
Script to add sample inventory data to the hospital management system
"""

import sys
import os
from datetime import datetime, timedelta
import random
from pymongo import MongoClient

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from inventory_data import inventory_manager

def create_sample_inventory():
    """Create sample inventory items for testing"""
    
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
    
    print(f"Creating sample inventory for hospital: {hospital.get('name', 'Unknown')} (ID: {hospital_id})")
    
    # Sample inventory data
    sample_inventory = [
        {
            "item_id": "INV001",
            "hospital_id": hospital_id,
            "name": "Paracetamol 500mg",
            "category": "Medications",
            "description": "Pain relief and fever reducer tablets",
            "manufacturer": "PharmaCorp",
            "current_stock": 1500,
            "min_stock": 500,
            "max_stock": 3000,
            "unit": "tablets",
            "unit_price": 0.25,
            "location": "Pharmacy - Shelf A1",
            "barcode": "123456789001",
            "batch_number": "PAR2024001",
            "expiry_date": datetime.now() + timedelta(days=365),
            "supplier": "Medical Supplies Inc.",
            "supplier_contact": "+1-555-1001",
            "reorder_level": 600,
            "status": "in_stock"
        },
        {
            "item_id": "INV002",
            "hospital_id": hospital_id,
            "name": "Surgical Gloves (Latex-Free)",
            "category": "Medical Supplies",
            "description": "Sterile surgical gloves, size medium",
            "manufacturer": "SafetyFirst Medical",
            "current_stock": 50,
            "min_stock": 100,
            "max_stock": 500,
            "unit": "boxes",
            "unit_price": 15.99,
            "location": "Supply Room - Cabinet B2",
            "barcode": "123456789002",
            "batch_number": "GLV2024002",
            "expiry_date": datetime.now() + timedelta(days=730),
            "supplier": "Surgical Supplies Co.",
            "supplier_contact": "+1-555-1002",
            "reorder_level": 120,
            "status": "low_stock"
        },
        {
            "item_id": "INV003",
            "hospital_id": hospital_id,
            "name": "Insulin (Rapid-Acting)",
            "category": "Medications",
            "description": "Rapid-acting insulin for diabetes management",
            "manufacturer": "DiabetesCare Pharma",
            "current_stock": 25,
            "min_stock": 50,
            "max_stock": 200,
            "unit": "vials",
            "unit_price": 45.00,
            "location": "Pharmacy - Refrigerated Section",
            "barcode": "123456789003",
            "batch_number": "INS2024003",
            "expiry_date": datetime.now() + timedelta(days=90),
            "supplier": "Diabetes Solutions Ltd.",
            "supplier_contact": "+1-555-1003",
            "reorder_level": 60,
            "status": "low_stock"
        },
        {
            "item_id": "INV004",
            "hospital_id": hospital_id,
            "name": "X-Ray Film",
            "category": "Equipment",
            "description": "Digital X-ray film for radiography",
            "manufacturer": "RadiologyTech",
            "current_stock": 200,
            "min_stock": 100,
            "max_stock": 500,
            "unit": "sheets",
            "unit_price": 3.50,
            "location": "Radiology Department - Storage Room",
            "barcode": "123456789004",
            "batch_number": "XRF2024004",
            "expiry_date": datetime.now() + timedelta(days=1095),
            "supplier": "Medical Imaging Co.",
            "supplier_contact": "+1-555-1004",
            "reorder_level": 150,
            "status": "in_stock"
        },
        {
            "item_id": "INV005",
            "hospital_id": hospital_id,
            "name": "Face Masks (N95)",
            "category": "Medical Supplies",
            "description": "N95 respirator masks for infection control",
            "manufacturer": "ProtectiveMed",
            "current_stock": 0,
            "min_stock": 200,
            "max_stock": 1000,
            "unit": "masks",
            "unit_price": 2.50,
            "location": "PPE Storage - Room C1",
            "barcode": "123456789005",
            "batch_number": "N95-2024005",
            "expiry_date": datetime.now() + timedelta(days=1460),
            "supplier": "PPE Distributors Inc.",
            "supplier_contact": "+1-555-1005",
            "reorder_level": 300,
            "status": "out_of_stock"
        },
        {
            "item_id": "INV006",
            "hospital_id": hospital_id,
            "name": "Blood Glucose Test Strips",
            "category": "Medical Supplies",
            "description": "Test strips for blood glucose monitoring",
            "manufacturer": "GlucoTest",
            "current_stock": 800,
            "min_stock": 300,
            "max_stock": 1500,
            "unit": "strips",
            "unit_price": 0.75,
            "location": "Lab Supplies - Drawer D3",
            "barcode": "123456789006",
            "batch_number": "BGT2024006",
            "expiry_date": datetime.now() + timedelta(days=45),
            "supplier": "Diagnostic Supplies Co.",
            "supplier_contact": "+1-555-1006",
            "reorder_level": 400,
            "status": "in_stock"
        },
        {
            "item_id": "INV007",
            "hospital_id": hospital_id,
            "name": "Defibrillator Pads",
            "category": "Equipment",
            "description": "Electrode pads for defibrillator machines",
            "manufacturer": "CardiacTech",
            "current_stock": 45,
            "min_stock": 30,
            "max_stock": 100,
            "unit": "pairs",
            "unit_price": 25.00,
            "location": "Emergency Department - Equipment Room",
            "barcode": "123456789007",
            "batch_number": "DEF2024007",
            "expiry_date": datetime.now() + timedelta(days=548),
            "supplier": "Emergency Equipment Ltd.",
            "supplier_contact": "+1-555-1007",
            "reorder_level": 40,
            "status": "in_stock"
        },
        {
            "item_id": "INV008",
            "hospital_id": hospital_id,
            "name": "Antibiotic (Amoxicillin)",
            "category": "Medications",
            "description": "Broad-spectrum antibiotic capsules",
            "manufacturer": "AntibioPharm",
            "current_stock": 300,
            "min_stock": 200,
            "max_stock": 800,
            "unit": "capsules",
            "unit_price": 0.85,
            "location": "Pharmacy - Shelf B2",
            "barcode": "123456789008",
            "batch_number": "AMX2024008",
            "expiry_date": datetime.now() + timedelta(days=30),
            "supplier": "Pharmaceutical Solutions Inc.",
            "supplier_contact": "+1-555-1008",
            "reorder_level": 250,
            "status": "in_stock"
        },
        {
            "item_id": "INV009",
            "hospital_id": hospital_id,
            "name": "IV Fluid (Normal Saline)",
            "category": "Medications",
            "description": "Intravenous normal saline solution",
            "manufacturer": "FluidMed",
            "current_stock": 120,
            "min_stock": 100,
            "max_stock": 400,
            "unit": "bags",
            "unit_price": 4.25,
            "location": "Pharmacy - IV Storage",
            "barcode": "123456789009",
            "batch_number": "SAL2024009",
            "expiry_date": datetime.now() + timedelta(days=1095),
            "supplier": "IV Solutions Co.",
            "supplier_contact": "+1-555-1009",
            "reorder_level": 150,
            "status": "in_stock"
        },
        {
            "item_id": "INV010",
            "hospital_id": hospital_id,
            "name": "Wheelchairs",
            "category": "Equipment",
            "description": "Standard patient wheelchairs",
            "manufacturer": "MobilityPlus",
            "current_stock": 15,
            "min_stock": 20,
            "max_stock": 50,
            "unit": "units",
            "unit_price": 250.00,
            "location": "Equipment Storage - Ground Floor",
            "barcode": "123456789010",
            "batch_number": "WCH2024010",
            "expiry_date": datetime.now() + timedelta(days=3650),
            "supplier": "Medical Equipment Depot",
            "supplier_contact": "+1-555-1010",
            "reorder_level": 25,
            "status": "low_stock"
        }
    ]
    
    # Insert inventory items
    created_count = 0
    for item_data in sample_inventory:
        try:
            # Check if item already exists
            existing_item = db['inventory'].find_one({"item_id": item_data["item_id"]})
            if existing_item:
                print(f"Inventory item {item_data['name']} ({item_data['item_id']}) already exists, skipping...")
                continue
            
            item_id = inventory_manager.add_inventory_item(item_data)
            if item_id:
                print(f"✅ Created inventory item: {item_data['name']} ({item_data['item_id']})")
                created_count += 1
            else:
                print(f"❌ Failed to create inventory item: {item_data['name']}")
        except Exception as e:
            print(f"❌ Error creating inventory item {item_data['name']}: {e}")
    
    print(f"\n🎉 Successfully created {created_count} inventory items!")
    return True

if __name__ == "__main__":
    print("Creating sample inventory data...")
    success = create_sample_inventory()
    if success:
        print("Sample inventory data creation completed!")
    else:
        print("Failed to create sample inventory data!")
