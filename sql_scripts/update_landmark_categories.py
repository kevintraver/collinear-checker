
import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('landmarks.db')
cursor = conn.cursor()

# Create the landmarks_categories_join table
cursor.execute('''
CREATE TABLE IF NOT EXISTS landmarks_categories (
    landmark_id INTEGER,
    category_id INTEGER,
    FOREIGN KEY (landmark_id) REFERENCES landmarks(id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
)
''')

# Retrieve landmarks and their areas of significance
cursor.execute("SELECT id, area_of_significance FROM landmarks WHERE area_of_significance IS NOT NULL AND area_of_significance != ''")
landmarks = cursor.fetchall()

# For each area_of_significance, split by semicolon and match with the categories table
for landmark in landmarks:
    landmark_id = landmark[0]
    areas = landmark[1].split(';')
    for area in areas:
        stripped_area = area.strip()
        if stripped_area:
            cursor.execute("SELECT category_id FROM categories WHERE name = ?", (stripped_area,))
            category_id = cursor.fetchone()
            if category_id:
                cursor.execute("INSERT INTO landmarks_categories (landmark_id, category_id) VALUES (?, ?)", (landmark_id, category_id[0]))

# Commit changes and close connection
conn.commit()
conn.close()
