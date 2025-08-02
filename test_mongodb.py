#!/usr/bin/env python3
"""
Test script to initialize MongoDB with sample hospital bed data
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.hospital_beds import HospitalBedsDB, initialize_sample_data

def test_mongodb_connection():
    """Test MongoDB connection and basic operations"""
    try:
        print("Testing MongoDB connection...")
        
        # Initialize database with sample data
        db = initialize_sample_data()
        
        # Test basic operations
        print("\n=== Testing Database Operations ===")
        
        # Get all beds
        all_beds = db.get_all_beds()
        print(f"Total beds in database: {len(all_beds)}")
        
        # Get statistics
        stats = db.get_bed_statistics()
        print(f"Database statistics: {stats}")
        
        # Test filtering by status
        available_beds = db.get_beds_by_status('available')
        print(f"Available beds: {len(available_beds)}")
        
        # Test filtering by department
        icu_beds = db.get_beds_by_department('ICU')
        print(f"ICU beds: {len(icu_beds)}")
        
        print("\n✅ MongoDB integration working correctly!")
        print("You can now run your Flask app with: python run.py")
        
    except Exception as e:
        print(f"❌ Error testing MongoDB: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure MongoDB is installed and running")
        print("2. Check your MONGO_URI in the .env file")
        print("3. Ensure you have the required Python packages installed")

if __name__ == "__main__":
    test_mongodb_connection()
