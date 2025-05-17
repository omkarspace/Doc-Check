import sqlite3
from pathlib import Path

def check_database():
    db_path = Path("docugenie.db")
    if not db_path.exists():
        print("Error: Database file not found!")
        return
    
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get the list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("Tables in the database:")
        for table in tables:
            table_name = table[0]
            print(f"\nTable: {table_name}")
            print("-" * (len(table_name) + 7))
            
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print("Columns:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
        
        # Check if admin user exists
        try:
            cursor.execute("SELECT * FROM users WHERE username = 'admin';")
            admin_user = cursor.fetchone()
            if admin_user:
                print("\nAdmin user exists in the database!")
                print(f"Username: {admin_user[2]}")
                print(f"Email: {admin_user[1]}")
                print(f"Role: {admin_user[5]}")
            else:
                print("\nAdmin user not found in the database!")
        except sqlite3.Error as e:
            print(f"Error checking admin user: {e}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_database()
