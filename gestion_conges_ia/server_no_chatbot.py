#!/usr/bin/env python
"""
Simple server script to run Django without the chatbot.
This allows testing routes with the frontend for leave accrual.
"""
import os
import sys

def run_server():
    """Run Django development server without the chatbot"""
    # Use test settings that exclude the chatbot app and use SQLite
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_conges_ia.test_settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # You can customize these server parameters
    port = 8000
    host = '127.0.0.1'
    
    # Start the server with the runserver command
    # The --noreload flag prevents automatic code reloading
    server_args = ['runserver', f'{host}:{port}', '--noreload']
    
    print(f"Starting Django server at http://{host}:{port}/ (without chatbot)")
    print("Press CTRL+C to stop the server")
    
    execute_from_command_line(['manage.py'] + server_args)

if __name__ == '__main__':
    run_server()
