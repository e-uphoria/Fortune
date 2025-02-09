import sqlite3
import os

# Ensure correct path
db_path = os.path.join(os.getcwd(), "instance", "users.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Execute the query and fetch results
cursor.execute("SELECT * FROM user")
column_names = [description[0] for description in cursor.description]
users = cursor.fetchall()

# Convert rows to dictionaries with column names
for user in users:
    user_dict = dict(zip(column_names, user))
    print(user_dict)

conn.close()
