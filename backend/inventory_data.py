"""
Inventory Management System for Hospital Management
Handles all inventory-related database operations
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
import os
from bson import ObjectId
from typing import List, Dict, Optional

class InventoryManager:
    def __init__(self):
        # Connect to MongoDB
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['hospital_db']
        self.inventory_collection = self.db['inventory']
        self.hospitals_collection = self.db['hospitals']
        
    def get_inventory_by_hospital(self, hospital_id: str, category: str = None) -> List[Dict]:
        """Get all inventory items for a specific hospital"""
        try:
            # Build query
            query = {"hospital_id": hospital_id}
            if category:
                query["category"] = category
                
            inventory_list = list(self.inventory_collection.find(query))
            
            # Convert ObjectId to string and format data
            for item in inventory_list:
                item['_id'] = str(item['_id'])
                # Ensure all date fields are properly formatted
                if 'expiry_date' in item and isinstance(item['expiry_date'], datetime):
                    item['expiry_date'] = item['expiry_date'].isoformat()
                if 'last_updated' in item and isinstance(item['last_updated'], datetime):
                    item['last_updated'] = item['last_updated'].isoformat()
                if 'created_at' in item and isinstance(item['created_at'], datetime):
                    item['created_at'] = item['created_at'].isoformat()
                    
            return inventory_list
        except Exception as e:
            print(f"Error fetching inventory: {e}")
            return []
    
    def get_item_by_id(self, item_id: str) -> Optional[Dict]:
        """Get a specific inventory item by ID"""
        try:
            item = self.inventory_collection.find_one({"_id": ObjectId(item_id)})
            if item:
                item['_id'] = str(item['_id'])
                # Format dates
                if 'expiry_date' in item and isinstance(item['expiry_date'], datetime):
                    item['expiry_date'] = item['expiry_date'].isoformat()
                if 'last_updated' in item and isinstance(item['last_updated'], datetime):
                    item['last_updated'] = item['last_updated'].isoformat()
                if 'created_at' in item and isinstance(item['created_at'], datetime):
                    item['created_at'] = item['created_at'].isoformat()
            return item
        except Exception as e:
            print(f"Error fetching inventory item: {e}")
            return None
    
    def get_inventory_by_category(self, hospital_id: str, category: str) -> List[Dict]:
        """Get inventory items by category"""
        try:
            query = {
                "hospital_id": hospital_id,
                "category": category
            }
            inventory_list = list(self.inventory_collection.find(query))
            
            # Convert ObjectId to string and format data
            for item in inventory_list:
                item['_id'] = str(item['_id'])
                if 'expiry_date' in item and isinstance(item['expiry_date'], datetime):
                    item['expiry_date'] = item['expiry_date'].isoformat()
                if 'last_updated' in item and isinstance(item['last_updated'], datetime):
                    item['last_updated'] = item['last_updated'].isoformat()
                if 'created_at' in item and isinstance(item['created_at'], datetime):
                    item['created_at'] = item['created_at'].isoformat()
                    
            return inventory_list
        except Exception as e:
            print(f"Error fetching inventory by category: {e}")
            return []
    
    def get_low_stock_items(self, hospital_id: str) -> List[Dict]:
        """Get items that are running low on stock"""
        try:
            # Find items where current_stock <= min_stock
            pipeline = [
                {"$match": {"hospital_id": hospital_id}},
                {"$addFields": {
                    "is_low_stock": {"$lte": ["$current_stock", "$min_stock"]}
                }},
                {"$match": {"is_low_stock": True}}
            ]
            
            low_stock_items = list(self.inventory_collection.aggregate(pipeline))
            
            # Convert ObjectId to string and format data
            for item in low_stock_items:
                item['_id'] = str(item['_id'])
                if 'expiry_date' in item and isinstance(item['expiry_date'], datetime):
                    item['expiry_date'] = item['expiry_date'].isoformat()
                if 'last_updated' in item and isinstance(item['last_updated'], datetime):
                    item['last_updated'] = item['last_updated'].isoformat()
                    
            return low_stock_items
        except Exception as e:
            print(f"Error fetching low stock items: {e}")
            return []
    
    def get_expiring_items(self, hospital_id: str, days_ahead: int = 30) -> List[Dict]:
        """Get items that are expiring soon"""
        try:
            expiry_date = datetime.now() + timedelta(days=days_ahead)
            
            query = {
                "hospital_id": hospital_id,
                "expiry_date": {"$lte": expiry_date}
            }
            
            expiring_items = list(self.inventory_collection.find(query))
            
            # Convert ObjectId to string and format data
            for item in expiring_items:
                item['_id'] = str(item['_id'])
                if 'expiry_date' in item and isinstance(item['expiry_date'], datetime):
                    item['expiry_date'] = item['expiry_date'].isoformat()
                if 'last_updated' in item and isinstance(item['last_updated'], datetime):
                    item['last_updated'] = item['last_updated'].isoformat()
                    
            return expiring_items
        except Exception as e:
            print(f"Error fetching expiring items: {e}")
            return []
    
    def add_inventory_item(self, item_data: Dict) -> str:
        """Add a new inventory item"""
        try:
            # Add timestamps
            item_data['created_at'] = datetime.now()
            item_data['last_updated'] = datetime.now()
            
            # Convert expiry_date string to datetime if provided
            if 'expiry_date' in item_data and isinstance(item_data['expiry_date'], str):
                item_data['expiry_date'] = datetime.fromisoformat(item_data['expiry_date'])
            
            # Insert inventory item
            result = self.inventory_collection.insert_one(item_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error adding inventory item: {e}")
            return None
    
    def update_inventory_item(self, item_id: str, update_data: Dict) -> bool:
        """Update an inventory item's information"""
        try:
            update_data['last_updated'] = datetime.now()
            
            # Convert expiry_date string to datetime if provided
            if 'expiry_date' in update_data and isinstance(update_data['expiry_date'], str):
                update_data['expiry_date'] = datetime.fromisoformat(update_data['expiry_date'])
            
            result = self.inventory_collection.update_one(
                {"_id": ObjectId(item_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating inventory item: {e}")
            return False
    
    def update_stock_level(self, item_id: str, new_stock: int) -> bool:
        """Update the stock level of an item"""
        try:
            result = self.inventory_collection.update_one(
                {"_id": ObjectId(item_id)},
                {"$set": {"current_stock": new_stock, "last_updated": datetime.now()}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating stock level: {e}")
            return False
    
    def delete_inventory_item(self, item_id: str) -> bool:
        """Delete an inventory item"""
        try:
            result = self.inventory_collection.delete_one({"_id": ObjectId(item_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting inventory item: {e}")
            return False
    
    def get_inventory_statistics(self, hospital_id: str) -> Dict:
        """Get inventory statistics for a hospital"""
        try:
            total_items = self.inventory_collection.count_documents({"hospital_id": hospital_id})
            
            # Low stock items
            low_stock_pipeline = [
                {"$match": {"hospital_id": hospital_id}},
                {"$addFields": {
                    "is_low_stock": {"$lte": ["$current_stock", "$min_stock"]}
                }},
                {"$match": {"is_low_stock": True}},
                {"$count": "low_stock_count"}
            ]
            low_stock_result = list(self.inventory_collection.aggregate(low_stock_pipeline))
            low_stock_items = low_stock_result[0]["low_stock_count"] if low_stock_result else 0
            
            # Out of stock items
            out_of_stock = self.inventory_collection.count_documents({
                "hospital_id": hospital_id,
                "current_stock": 0
            })
            
            # Expiring items (next 30 days)
            expiry_date = datetime.now() + timedelta(days=30)
            expiring_items = self.inventory_collection.count_documents({
                "hospital_id": hospital_id,
                "expiry_date": {"$lte": expiry_date}
            })
            
            # Category breakdown
            pipeline = [
                {"$match": {"hospital_id": hospital_id}},
                {"$group": {"_id": "$category", "count": {"$sum": 1}}}
            ]
            category_stats = list(self.inventory_collection.aggregate(pipeline))
            
            # Total value
            value_pipeline = [
                {"$match": {"hospital_id": hospital_id}},
                {"$addFields": {
                    "total_value": {"$multiply": ["$current_stock", "$unit_price"]}
                }},
                {"$group": {"_id": None, "total_value": {"$sum": "$total_value"}}}
            ]
            value_result = list(self.inventory_collection.aggregate(value_pipeline))
            total_value = value_result[0]["total_value"] if value_result else 0
            
            return {
                "total_items": total_items,
                "low_stock_items": low_stock_items,
                "out_of_stock_items": out_of_stock,
                "expiring_items": expiring_items,
                "total_value": round(total_value, 2),
                "category_breakdown": {stat["_id"]: stat["count"] for stat in category_stats}
            }
        except Exception as e:
            print(f"Error getting inventory statistics: {e}")
            return {}
    
    def close_connection(self):
        """Close the database connection"""
        if self.client:
            self.client.close()

# Initialize the inventory manager
inventory_manager = InventoryManager()
