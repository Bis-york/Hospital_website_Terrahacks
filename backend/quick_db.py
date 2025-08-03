#!/usr/bin/env python3
"""
Quick Database Operations
Simple commands for common database tasks
"""

import sys
import os

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from db_utils import DatabaseUtils

def quick_reset():
    """Quick database reset without prompts"""
    print("🗑️  Quick Database Reset")
    db_utils = DatabaseUtils()
    db_utils.reset_database(confirm=False)

def quick_add_samples():
    """Quick add sample hospitals"""
    print("🏥 Quick Add Sample Hospitals")
    db_utils = DatabaseUtils()
    db_utils.add_sample_hospitals()

def quick_stats():
    """Quick database statistics"""
    print("📊 Quick Database Statistics")
    db_utils = DatabaseUtils()
    db_utils.get_database_stats()

def quick_list():
    """Quick list hospitals"""
    print("📋 Quick List Hospitals")
    db_utils = DatabaseUtils()
    db_utils.list_hospitals()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Quick Database Operations")
        print("=" * 30)
        print("Usage: python quick_db.py <command>")
        print("\nCommands:")
        print("  reset     - Reset database (clear all data)")
        print("  samples   - Add sample hospitals")
        print("  stats     - Show database statistics")
        print("  list      - List all hospitals")
        print("\nExamples:")
        print("  python quick_db.py reset")
        print("  python quick_db.py samples")
        print("  python quick_db.py stats")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    try:
        if command == "reset":
            quick_reset()
        elif command == "samples":
            quick_add_samples()
        elif command == "stats":
            quick_stats()
        elif command == "list":
            quick_list()
        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: reset, samples, stats, list")
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure MongoDB is running and accessible.")
        sys.exit(1)
