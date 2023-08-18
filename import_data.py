import json
import sqlite3

def import_landmarks_from_json(json_data, db_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Extract the category name and landmarks from the json_data
    category_name, landmarks = list(json_data.items())[0]

    # Loop through the landmarks and insert them into the database
    for landmark in landmarks:
        name = landmark['name']
        state = landmark['state']
        city = landmark['city']
        latitude = landmark['coordinates']['latitude']
        longitude = landmark['coordinates']['longitude']

        query = "INSERT INTO landmarks (name, area_of_significance, state, city, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?);"
        values = (name, category_name, state, city, latitude, longitude)
        cur.execute(query, values)

        # Retrieve the ID of the inserted landmark
        landmark_id = cur.lastrowid

        # Get the category_id for the category_name from the categories table
        cur.execute("SELECT category_id FROM categories WHERE name = ?", (category_name,))
        category_id = cur.fetchone()
        if category_id:
            category_id = category_id[0]
            # Insert the association into the landmarks_categories table
            cur.execute("INSERT INTO landmarks_categories (landmark_id, category_id) VALUES (?, ?)", (landmark_id, category_id))

    # Commit the changes and close the cursor and connection
    conn.commit()
    cur.close()
    conn.close()

    return "Data imported successfully!"

# Load data from the JSON file
with open('landmarks.json', 'r') as file:
    data = json.load(file)

# Run the import function
import_landmarks_from_json(data, 'landmarks.db')
