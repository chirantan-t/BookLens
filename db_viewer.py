import sqlite3
import os

def view_table_data(db_file, table_name):
    """Connects to SQLite DB and prints all data from a specified table."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Get column names (PRAGMA table_info is best for this)
        cursor.execute(f"PRAGMA table_info({table_name});")
        column_info = cursor.fetchall()
        column_names = [info[1] for info in column_info] # Column name is at index 1

        # Fetch all rows from the table
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()

        print(f"\n--- Data in table '{table_name.upper()}' ---")
        if not rows:
            print("No records found.")
            return

        # Print header
        header_line = " | ".join(column_names)
        print(header_line)
        print("-" * len(header_line))

        # Print rows
        for row in rows:
            print(" | ".join(map(str, row))) # Convert all elements to string for joining

    except sqlite3.Error as e:
        print(f"Error fetching data from table '{table_name}': {e}")
    finally:
        if conn:
            conn.close()

def get_all_table_names(db_file):
    """Returns a list of all table names in the database."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        return [table[0] for table in tables]
    except sqlite3.Error as e:
        print(f"Error connecting to database or fetching table names: {e}")
        return []
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Construct the path to app.db relative to this script
    # Assumes app.db is in the 'instance' folder, which is sibling to this script
    db_file_path = os.path.join('instance', 'app.db')

    # Ensure the database file exists
    if not os.path.exists(db_file_path):
        print(f"Error: Database file not found at '{db_file_path}'.")
        print("Please ensure your Flask app has run at least once to create the database.")
    else:
        print(f"Attempting to connect to database: {db_file_path}")
        all_tables = get_all_table_names(db_file_path)

        if all_tables:
            print(f"\nDiscovered tables in '{db_file_path}':")
            for table in all_tables:
                print(f"- {table}")
            print("\n--- Displaying Data for Recognized Tables ---")

            # List of tables we expect from your models.py (lowercase names)
            expected_tables = ['user', 'book', 'review']

            for table_name in expected_tables:
                if table_name in all_tables:
                    view_table_data(db_file_path, table_name)
                else:
                    print(f"\nTable '{table_name.upper()}' not found in the database. Skipping.")
            print("\n--- End of Database Inspection ---")

        else:
            print(f"No tables found in '{db_file_path}'.")