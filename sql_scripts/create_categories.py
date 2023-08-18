
import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('landmarks.db')
cursor = conn.cursor()

# Create the categories table
cursor.execute('''
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
)
''')

# Retrieve distinct area_of_significance and split by semicolon
cursor.execute("SELECT DISTINCT area_of_significance FROM landmarks WHERE area_of_significance IS NOT NULL AND area_of_significance != ''")
areas = cursor.fetchall()

# List to hold all unique categories
unique_categories = set()

for area_tuple in areas:
    for category in area_tuple[0].split(';'):
        stripped_category = category.strip()
        if stripped_category:  # Ensure the category isn't empty after stripping
            unique_categories.add(stripped_category)

# Insert unique categories into the categories table
for category in unique_categories:
    cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))

# Commit changes and close connection
conn.commit()
conn.close()
