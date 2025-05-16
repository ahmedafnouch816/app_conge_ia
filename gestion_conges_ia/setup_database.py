import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

def setup_database():
    # Load environment variables
    load_dotenv()
    
    # Connection parameters
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'root'  # We know this works from the previous test
    }
    
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Get database name from .env
            db_name = os.getenv('DATABASE_NAME', 'gestion_conges_ia')
            new_user = os.getenv('DATABASE_USER', 'MySQL80')
            new_password = os.getenv('DATABASE_PWD', 'Pascal.jemmal1996')
            
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            print(f"Database '{db_name}' created successfully")
            
            # Create new user if it doesn't exist and grant privileges
            try:
                cursor.execute(f"CREATE USER IF NOT EXISTS '{new_user}'@'localhost' IDENTIFIED BY '{new_password}'")
                cursor.execute(f"GRANT ALL PRIVILEGES ON {db_name}.* TO '{new_user}'@'localhost'")
                cursor.execute("FLUSH PRIVILEGES")
                print(f"User '{new_user}' created and granted privileges")
            except Error as e:
                print(f"Error creating user: {e}")
            
            # Update .env file with working credentials
            cursor.execute("SELECT DATABASE()")
            database = cursor.fetchone()[0]
            print(f"\nCurrent database: {database}")
            
            cursor.execute("SHOW GRANTS")
            print("\nGrants for current user:")
            for grant in cursor:
                print(grant[0])
                
            connection.close()
            print("\nSetup completed successfully!")
            
    except Error as e:
        print(f"Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Starting database setup...")
    setup_database()
