#!/usr/bin/env python3
"""
Simple Dual Server Launcher
Starts both servers on separate ports
"""

import subprocess
import sys
import os
import time

def main():
    print("🏥 Hospital Management System - Dual Server")
    print("=" * 50)
    print("🔧 API Server: http://localhost:5000")
    print("🌐 Web Server: http://localhost:8080")
    print("=" * 50)
    print("Starting both servers...")
    print()
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    try:
        # Start API server in background
        print("🔧 Starting API server...")
        api_process = subprocess.Popen([sys.executable, 'start_api.py'])
        time.sleep(3)  # Give API time to start
        
        # Start web server in background
        print("🌐 Starting web server...")
        web_process = subprocess.Popen([sys.executable, 'web_server.py'])
        time.sleep(2)  # Give web server time to start
        
        print("\n🎉 Both servers started!")
        print("   📊 API: http://localhost:5000")
        print("   🌐 Web: http://localhost:8080")
        print("\nPress Ctrl+C to stop both servers")
        
        # Wait for user to stop
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        try:
            api_process.terminate()
            web_process.terminate()
            print("✅ Servers stopped!")
        except:
            pass

if __name__ == '__main__':
    main()
