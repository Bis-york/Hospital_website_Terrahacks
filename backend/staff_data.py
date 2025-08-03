"""
Staff Management System for Hospital Management
Handles all staff-related database operations
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
import os
from bson import ObjectId
from typing import List, Dict, Optional

class StaffManager:
    def __init__(self):
        # Connect to MongoDB
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['hospital_db']
        self.staff_collection = self.db['staff']
        self.hospitals_collection = self.db['hospitals']
        
    def get_staff_by_hospital(self, hospital_id: str, status: str = None) -> List[Dict]:
        """Get all staff members for a specific hospital"""
        try:
            # Build query
            query = {"hospital_id": hospital_id}
            if status:
                query["status"] = status
                
            staff_list = list(self.staff_collection.find(query))
            
            # Convert ObjectId to string and format data
            for staff in staff_list:
                staff['_id'] = str(staff['_id'])
                # Ensure all date fields are properly formatted
                if 'hire_date' in staff and isinstance(staff['hire_date'], datetime):
                    staff['hire_date'] = staff['hire_date'].isoformat()
                if 'last_login' in staff and isinstance(staff['last_login'], datetime):
                    staff['last_login'] = staff['last_login'].isoformat()
                    
            return staff_list
        except Exception as e:
            print(f"Error fetching staff: {e}")
            return []
    
    def get_staff_by_id(self, staff_id: str) -> Optional[Dict]:
        """Get a specific staff member by ID"""
        try:
            staff = self.staff_collection.find_one({"_id": ObjectId(staff_id)})
            if staff:
                staff['_id'] = str(staff['_id'])
                # Format dates
                if 'hire_date' in staff and isinstance(staff['hire_date'], datetime):
                    staff['hire_date'] = staff['hire_date'].isoformat()
                if 'last_login' in staff and isinstance(staff['last_login'], datetime):
                    staff['last_login'] = staff['last_login'].isoformat()
            return staff
        except Exception as e:
            print(f"Error fetching staff member: {e}")
            return None
    
    def get_staff_by_department(self, hospital_id: str, department: str) -> List[Dict]:
        """Get staff members by department"""
        try:
            query = {
                "hospital_id": hospital_id,
                "department": department
            }
            staff_list = list(self.staff_collection.find(query))
            
            # Convert ObjectId to string and format data
            for staff in staff_list:
                staff['_id'] = str(staff['_id'])
                if 'hire_date' in staff and isinstance(staff['hire_date'], datetime):
                    staff['hire_date'] = staff['hire_date'].isoformat()
                if 'last_login' in staff and isinstance(staff['last_login'], datetime):
                    staff['last_login'] = staff['last_login'].isoformat()
                    
            return staff_list
        except Exception as e:
            print(f"Error fetching staff by department: {e}")
            return []
    
    def add_staff_member(self, staff_data: Dict) -> str:
        """Add a new staff member"""
        try:
            # Add timestamps
            staff_data['hire_date'] = datetime.now()
            staff_data['created_at'] = datetime.now()
            staff_data['updated_at'] = datetime.now()
            
            # Insert staff member
            result = self.staff_collection.insert_one(staff_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error adding staff member: {e}")
            return None
    
    def update_staff_member(self, staff_id: str, update_data: Dict) -> bool:
        """Update a staff member's information"""
        try:
            update_data['updated_at'] = datetime.now()
            
            result = self.staff_collection.update_one(
                {"_id": ObjectId(staff_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating staff member: {e}")
            return False
    
    def update_staff_status(self, staff_id: str, status: str) -> bool:
        """Update a staff member's status"""
        try:
            result = self.staff_collection.update_one(
                {"_id": ObjectId(staff_id)},
                {"$set": {"status": status, "updated_at": datetime.now()}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating staff status: {e}")
            return False
    
    def delete_staff_member(self, staff_id: str) -> bool:
        """Delete a staff member (soft delete by updating status)"""
        try:
            result = self.staff_collection.update_one(
                {"_id": ObjectId(staff_id)},
                {"$set": {"status": "inactive", "updated_at": datetime.now()}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error deleting staff member: {e}")
            return False
    
    def get_staff_statistics(self, hospital_id: str) -> Dict:
        """Get staff statistics for a hospital"""
        try:
            total_staff = self.staff_collection.count_documents({"hospital_id": hospital_id})
            active_staff = self.staff_collection.count_documents({
                "hospital_id": hospital_id, 
                "status": "active"
            })
            on_leave = self.staff_collection.count_documents({
                "hospital_id": hospital_id, 
                "status": "on_leave"
            })
            
            # Department breakdown
            pipeline = [
                {"$match": {"hospital_id": hospital_id}},
                {"$group": {"_id": "$department", "count": {"$sum": 1}}}
            ]
            department_stats = list(self.staff_collection.aggregate(pipeline))
            
            # Shift breakdown
            pipeline = [
                {"$match": {"hospital_id": hospital_id, "status": "active"}},
                {"$group": {"_id": "$shift", "count": {"$sum": 1}}}
            ]
            shift_stats = list(self.staff_collection.aggregate(pipeline))
            
            return {
                "total_staff": total_staff,
                "active_staff": active_staff,
                "on_leave": on_leave,
                "inactive_staff": total_staff - active_staff,
                "department_breakdown": {stat["_id"]: stat["count"] for stat in department_stats},
                "shift_breakdown": {stat["_id"]: stat["count"] for stat in shift_stats}
            }
        except Exception as e:
            print(f"Error getting staff statistics: {e}")
            return {}
    
    def close_connection(self):
        """Close the database connection"""
        if self.client:
            self.client.close()

# Initialize the staff manager
staff_manager = StaffManager()
