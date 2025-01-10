# import sqlite3

# def view_database(db_path):
#     """
#     Function to view the contents of an SQLite database.
    
#     Args:
#         db_path (str): Path to the SQLite database file.
#     """
#     try:
#         # Connect to the SQLite database
#         connection = sqlite3.connect(db_path)
#         cursor = connection.cursor()

#         # Fetch all table names
#         cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
#         tables = cursor.fetchall()

#         if not tables:
#             print("No tables found in the database.")
#             return

#         print("Tables in the database:")
#         for table in tables:
#             table_name = table[0]
#             print(f"\nTable: {table_name}")

#             # Fetch all rows from the table
#             cursor.execute(f"SELECT * FROM {table_name};")
#             rows = cursor.fetchall()

#             # Fetch column names
#             cursor.execute(f"PRAGMA table_info({table_name});")
#             columns = [col[1] for col in cursor.fetchall()]
#             print(f"Columns: {columns}")

#             # Print rows
#             if rows:
#                 for row in rows:
#                     print(row)
#             else:
#                 print("No data found in this table.")

#         connection.close()

#     except sqlite3.Error as e:
#         print(f"Error occurred: {e}")

# # Example usage
# db_path = "user_data.db"  # Replace with the path to your database file
# view_database(db_path)
# import streamlit as st

# if "user" in st.session_state:
#     user = st.session_state["user"]
#     user_id = st.session_state.get("user_id")  # Use this ID for further actions
#     print(f"User ID: {user_id}")
# else:
#     st.error("User not found. Please log in or register.")