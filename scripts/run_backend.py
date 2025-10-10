#!/usr/bin/env python3
"""Run Flask backend server"""
from backend.app import create_app
import os

os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

app = create_app()

if __name__ == '__main__':
    print("🚀 Starting Flask backend server...")
    print("   URL: http://localhost:5000")
    print("   API Base: http://localhost:5000/api")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

