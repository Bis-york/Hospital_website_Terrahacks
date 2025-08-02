from pymongo import MongoClient
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MedicalInventoryDB:
    def __init__(self):
        """Initialize MongoDB connection"""
        self.client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
        self.db = self.client.hospital_db
        self.inventory_collection = self.db.medical_inventory
        self.transactions_collection = self.db.inventory_transactions
        self.suppliers_collection = self.db.suppliers
        
    def create_inventory_item(self, item_data):
        """Create a new inventory item"""
        item = {
            'item_id': item_data['item_id'],  # Unique item identifier
            'name': item_data['name'],
            'category': item_data['category'],  # medicine, equipment, consumable, PPE, etc.
            'subcategory': item_data.get('subcategory', ''),  # antibiotics, surgical, masks, etc.
            'description': item_data.get('description', ''),
            'manufacturer': item_data.get('manufacturer', ''),
            'brand': item_data.get('brand', ''),
            'unit_of_measurement': item_data['unit_of_measurement'],  # pieces, mg, ml, boxes, etc.
            'current_stock': item_data.get('current_stock', 0),
            'minimum_threshold': item_data.get('minimum_threshold', 10),
            'maximum_capacity': item_data.get('maximum_capacity', 1000),
            'unit_price': item_data.get('unit_price', 0.0),
            'total_value': item_data.get('current_stock', 0) * item_data.get('unit_price', 0.0),
            'supplier_info': item_data.get('supplier_info', {}),
            'storage_location': item_data.get('storage_location', ''),
            'storage_conditions': item_data.get('storage_conditions', ''),  # temperature, humidity requirements
            'expiry_date': item_data.get('expiry_date', None),
            'batch_number': item_data.get('batch_number', ''),
            'barcode': item_data.get('barcode', ''),
            'is_prescription_required': item_data.get('is_prescription_required', False),
            'is_controlled_substance': item_data.get('is_controlled_substance', False),
            'status': item_data.get('status', 'active'),  # active, discontinued, recalled
            'last_restocked': item_data.get('last_restocked', None),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Check if item_id already exists
        existing_item = self.inventory_collection.find_one({'item_id': item_data['item_id']})
        if existing_item:
            raise ValueError(f"Item with ID {item_data['item_id']} already exists")
        
        result = self.inventory_collection.insert_one(item)
        return str(result.inserted_id)
    
    def get_all_inventory(self):
        """Get all inventory items"""
        items = list(self.inventory_collection.find())
        for item in items:
            item['_id'] = str(item['_id'])
        return items
    
    def get_item_by_id(self, item_id):
        """Get a specific item by item_id"""
        item = self.inventory_collection.find_one({'item_id': item_id})
        if item:
            item['_id'] = str(item['_id'])
        return item
    
    def get_items_by_category(self, category):
        """Get items by category"""
        items = list(self.inventory_collection.find({'category': category}))
        for item in items:
            item['_id'] = str(item['_id'])
        return items
    
    def get_low_stock_items(self):
        """Get items with stock below minimum threshold"""
        pipeline = [
            {
                '$addFields': {
                    'is_low_stock': {
                        '$lte': ['$current_stock', '$minimum_threshold']
                    }
                }
            },
            {
                '$match': {
                    'is_low_stock': True,
                    'status': 'active'
                }
            }
        ]
        
        items = list(self.inventory_collection.aggregate(pipeline))
        for item in items:
            item['_id'] = str(item['_id'])
        return items
    
    def get_expiring_items(self, days_ahead=30):
        """Get items expiring within specified days"""
        expiry_threshold = datetime.utcnow() + timedelta(days=days_ahead)
        
        items = list(self.inventory_collection.find({
            'expiry_date': {
                '$lte': expiry_threshold,
                '$gte': datetime.utcnow()
            },
            'status': 'active'
        }))
        
        for item in items:
            item['_id'] = str(item['_id'])
        return items
    
    def update_stock(self, item_id, quantity_change, transaction_type, reason='', user_id=''):
        """Update stock quantity and log transaction"""
        item = self.get_item_by_id(item_id)
        if not item:
            raise ValueError(f"Item with ID {item_id} not found")
        
        new_stock = item['current_stock'] + quantity_change
        if new_stock < 0:
            raise ValueError("Insufficient stock for this operation")
        
        # Update item stock
        new_total_value = new_stock * item['unit_price']
        update_data = {
            'current_stock': new_stock,
            'total_value': new_total_value,
            'updated_at': datetime.utcnow()
        }
        
        if transaction_type == 'restock':
            update_data['last_restocked'] = datetime.utcnow()
        
        result = self.inventory_collection.update_one(
            {'item_id': item_id},
            {'$set': update_data}
        )
        
        # Log transaction
        if result.modified_count > 0:
            self.log_transaction(item_id, quantity_change, transaction_type, reason, user_id)
        
        return result.modified_count > 0
    
    def log_transaction(self, item_id, quantity_change, transaction_type, reason='', user_id=''):
        """Log inventory transaction"""
        transaction = {
            'item_id': item_id,
            'quantity_change': quantity_change,
            'transaction_type': transaction_type,  # restock, dispense, adjust, waste, expired
            'reason': reason,
            'user_id': user_id,
            'timestamp': datetime.utcnow()
        }
        
        self.transactions_collection.insert_one(transaction)
    
    def dispense_item(self, item_id, quantity, patient_id='', department='', reason=''):
        """Dispense items (reduce stock)"""
        return self.update_stock(item_id, -quantity, 'dispense', 
                               f"Dispensed to patient: {patient_id}, Department: {department}, Reason: {reason}")
    
    def restock_item(self, item_id, quantity, supplier='', batch_number='', expiry_date=None):
        """Restock items (increase stock)"""
        # Update batch number and expiry date if provided
        if batch_number or expiry_date:
            update_data = {'updated_at': datetime.utcnow()}
            if batch_number:
                update_data['batch_number'] = batch_number
            if expiry_date:
                update_data['expiry_date'] = expiry_date
            
            self.inventory_collection.update_one(
                {'item_id': item_id},
                {'$set': update_data}
            )
        
        return self.update_stock(item_id, quantity, 'restock', 
                               f"Restocked from supplier: {supplier}, Batch: {batch_number}")
    
    def adjust_stock(self, item_id, new_quantity, reason=''):
        """Adjust stock to a specific quantity"""
        item = self.get_item_by_id(item_id)
        if not item:
            raise ValueError(f"Item with ID {item_id} not found")
        
        quantity_change = new_quantity - item['current_stock']
        return self.update_stock(item_id, quantity_change, 'adjust', reason)
    
    def search_inventory(self, search_term):
        """Search inventory by name, item_id, manufacturer, or brand"""
        search_pattern = {'$regex': search_term, '$options': 'i'}
        query = {
            '$or': [
                {'name': search_pattern},
                {'item_id': search_pattern},
                {'manufacturer': search_pattern},
                {'brand': search_pattern},
                {'description': search_pattern}
            ]
        }
        
        items = list(self.inventory_collection.find(query))
        for item in items:
            item['_id'] = str(item['_id'])
        return items
    
    def get_inventory_statistics(self):
        """Get comprehensive inventory statistics"""
        total_items = self.inventory_collection.count_documents({'status': 'active'})
        total_value = list(self.inventory_collection.aggregate([
            {'$match': {'status': 'active'}},
            {'$group': {'_id': None, 'total': {'$sum': '$total_value'}}}
        ]))
        
        low_stock_count = len(self.get_low_stock_items())
        expiring_soon_count = len(self.get_expiring_items())
        
        # Category breakdown
        category_stats = list(self.inventory_collection.aggregate([
            {'$match': {'status': 'active'}},
            {'$group': {
                '_id': '$category',
                'count': {'$sum': 1},
                'total_value': {'$sum': '$total_value'},
                'total_stock': {'$sum': '$current_stock'}
            }}
        ]))
        
        return {
            'total_items': total_items,
            'total_value': total_value[0]['total'] if total_value else 0,
            'low_stock_items': low_stock_count,
            'expiring_soon': expiring_soon_count,
            'category_breakdown': category_stats
        }
    
    def get_transaction_history(self, item_id=None, days=30):
        """Get transaction history for an item or all items"""
        query = {
            'timestamp': {
                '$gte': datetime.utcnow() - timedelta(days=days)
            }
        }
        
        if item_id:
            query['item_id'] = item_id
        
        transactions = list(self.transactions_collection.find(query).sort('timestamp', -1))
        for transaction in transactions:
            transaction['_id'] = str(transaction['_id'])
        
        return transactions
    
    def create_supplier(self, supplier_data):
        """Create a new supplier"""
        supplier = {
            'supplier_id': supplier_data['supplier_id'],
            'name': supplier_data['name'],
            'contact_person': supplier_data.get('contact_person', ''),
            'phone': supplier_data.get('phone', ''),
            'email': supplier_data.get('email', ''),
            'address': supplier_data.get('address', ''),
            'products_supplied': supplier_data.get('products_supplied', []),
            'rating': supplier_data.get('rating', 0),
            'is_active': supplier_data.get('is_active', True),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = self.suppliers_collection.insert_one(supplier)
        return str(result.inserted_id)
    
    def delete_item(self, item_id):
        """Soft delete an item by setting status to discontinued"""
        result = self.inventory_collection.update_one(
            {'item_id': item_id},
            {'$set': {'status': 'discontinued', 'updated_at': datetime.utcnow()}}
        )
        return result.modified_count > 0

# Example usage and testing functions
def initialize_sample_inventory():
    """Initialize some sample inventory data for testing"""
    db = MedicalInventoryDB()
    
    # Sample inventory items
    sample_items = [
        {
            'item_id': 'MED001',
            'name': 'Paracetamol 500mg',
            'category': 'medicine',
            'subcategory': 'analgesic',
            'description': 'Pain relief and fever reducer',
            'manufacturer': 'PharmaCorp',
            'unit_of_measurement': 'tablets',
            'current_stock': 500,
            'minimum_threshold': 100,
            'unit_price': 0.25,
            'storage_location': 'Pharmacy-A1',
            'expiry_date': datetime(2025, 12, 31),
            'batch_number': 'PAR2024001',
            'is_prescription_required': False
        },
        {
            'item_id': 'PPE001',
            'name': 'N95 Face Masks',
            'category': 'PPE',
            'subcategory': 'respiratory_protection',
            'description': 'N95 filtering facepiece respirator',
            'manufacturer': 'SafetyFirst',
            'unit_of_measurement': 'pieces',
            'current_stock': 200,
            'minimum_threshold': 50,
            'unit_price': 2.50,
            'storage_location': 'PPE-Storage-B2',
            'expiry_date': datetime(2027, 6, 30),
            'batch_number': 'N95-2024-A'
        },
        {
            'item_id': 'SURG001',
            'name': 'Surgical Gloves (Latex)',
            'category': 'consumable',
            'subcategory': 'surgical_supplies',
            'description': 'Sterile latex surgical gloves, size M',
            'manufacturer': 'MedGlove Inc',
            'unit_of_measurement': 'pairs',
            'current_stock': 1000,
            'minimum_threshold': 200,
            'unit_price': 0.75,
            'storage_location': 'Surgery-Supply-C1',
            'expiry_date': datetime(2026, 8, 15),
            'batch_number': 'SG-LAT-2024-M'
        },
        {
            'item_id': 'INJ001',
            'name': 'Insulin Injection',
            'category': 'medicine',
            'subcategory': 'hormone',
            'description': 'Rapid-acting insulin injection',
            'manufacturer': 'DiabetesCare',
            'unit_of_measurement': 'vials',
            'current_stock': 25,
            'minimum_threshold': 10,
            'unit_price': 45.00,
            'storage_location': 'Refrigerated-D1',
            'storage_conditions': 'Store at 2-8°C',
            'expiry_date': datetime(2025, 10, 20),
            'batch_number': 'INS-2024-R01',
            'is_prescription_required': True,
            'is_controlled_substance': True
        },
        {
            'item_id': 'EQUIP001',
            'name': 'Digital Thermometer',
            'category': 'equipment',
            'subcategory': 'diagnostic',
            'description': 'Digital oral/rectal thermometer',
            'manufacturer': 'MedTech Solutions',
            'unit_of_measurement': 'pieces',
            'current_stock': 15,
            'minimum_threshold': 5,
            'unit_price': 25.00,
            'storage_location': 'Equipment-E1'
        }
    ]
    
    # Check if inventory already exists
    if db.inventory_collection.count_documents({}) == 0:
        for item in sample_items:
            try:
                db.create_inventory_item(item)
                print(f"Item {item['name']} created successfully!")
            except ValueError as e:
                print(f"Error creating item {item['name']}: {e}")
    else:
        print("Inventory items already exist in database.")
    
    return db

if __name__ == "__main__":
    # Test the database connection and functions
    try:
        db = initialize_sample_inventory()
        
        # Test getting all inventory
        all_items = db.get_all_inventory()
        print(f"Total inventory items: {len(all_items)}")
        
        # Test getting low stock items
        low_stock = db.get_low_stock_items()
        print(f"Low stock items: {len(low_stock)}")
        
        # Test getting expiring items
        expiring = db.get_expiring_items()
        print(f"Items expiring soon: {len(expiring)}")
        
        # Test statistics
        stats = db.get_inventory_statistics()
        print("Inventory Statistics:", stats)
        
        # Test search
        search_results = db.search_inventory("mask")
        print(f"Search results for 'mask': {len(search_results)} items found")
        
        # Test stock operations
        print("\nTesting stock operations:")
        # Dispense some masks
        db.dispense_item('PPE001', 10, 'P001', 'ICU', 'Patient care')
        print("Dispensed 10 N95 masks")
        
        # Restock paracetamol
        db.restock_item('MED001', 200, 'PharmaCorp', 'PAR2024002')
        print("Restocked 200 Paracetamol tablets")
        
        # Check updated stock
        updated_item = db.get_item_by_id('PPE001')
        print(f"N95 masks current stock: {updated_item['current_stock']}")
        
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        print("Make sure MongoDB is running on your system.")