#!/usr/bin/env python3
"""
Hospital Management System API Server
Run this script to start the REST API server
"""

import sys
import os

# Add the backend directory to Python path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

# Don't change directory, just add to path for imports

if __name__ == '__main__':
    try:
        # Import from backend directory
        from backend.api import app
        print("🏥 Hospital Management System API")
        print("=" * 50)
        print("📋 API Documentation: http://localhost:5000/api/docs")
        print("❤️  Health Check: http://localhost:5000/api/health")
        print("🌐 Frontend Demo: Open frontend_demo.html in your browser")
        print("=" * 50)
        print("Starting server on http://localhost:5000")
        print("Press Ctrl+C to stop the server")
        print()
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure all required packages are installed:")
        print("pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("Make sure MongoDB is running on localhost:27017")
