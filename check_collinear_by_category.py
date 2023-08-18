
import sqlite3
from geopy.distance import geodesic
from itertools import combinations

# Define a function to check if three coordinates are collinear
def are_collinear(coord1, coord2, coord3, tolerance=1/5280, min_distance=300.0):
    distance1 = geodesic(coord1, coord2).miles
    distance2 = geodesic(coord2, coord3).miles
    distance3 = geodesic(coord1, coord3).miles

    # Exclude points that are within min_distance of each other
    if distance1 < min_distance or distance2 < min_distance or distance3 < min_distance:
        return False

    max_distance = max(distance1, distance2, distance3)
    return abs((distance1 + distance2 + distance3) - 2 * max_distance) <= tolerance

# Connect to SQLite database
conn = sqlite3.connect('landmarks.db')
cursor = conn.cursor()

# Create a table for collinear landmarks
cursor.execute('''
CREATE TABLE IF NOT EXISTS collinear_landmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    landmark1_id INTEGER,
    landmark2_id INTEGER,
    landmark3_id INTEGER
)
''')

# Input area of significance (now renamed to category name)
category_name = input("Enter the category name you want to search for: ")

# Retrieve the category_id for the entered category name
cursor.execute("SELECT category_id FROM categories WHERE name = ?", (category_name,))
category_id = cursor.fetchone()

if category_id:
    # Retrieve the coordinates and names for landmarks associated with the specified category
    cursor.execute(
    "SELECT landmarks.id, landmarks.name, landmarks.latitude, landmarks.longitude "
    "FROM landmarks "
    "JOIN landmarks_categories ON landmarks.id = landmarks_categories.landmark_id "
    "WHERE landmarks_categories.category_id = ?", (category_id[0],))
    landmarks = cursor.fetchall()

    # Check all combinations of three landmarks for collinearity
    for landmark1, landmark2, landmark3 in combinations(landmarks, 3):
        id1, name1, coord1 = landmark1[0], landmark1[1], (landmark1[2], landmark1[3])
        id2, name2, coord2 = landmark2[0], landmark2[1], (landmark2[2], landmark2[3])
        id3, name3, coord3 = landmark3[0], landmark3[1], (landmark3[2], landmark3[3])
        if are_collinear(coord1, coord2, coord3):
            cursor.execute("INSERT INTO collinear_landmarks (landmark1_id, landmark2_id, landmark3_id) VALUES (?, ?, ?)", (id1, id2, id3))
            print(f"The landmarks {name1}, {name2}, and {name3} are collinear.")
else:
    print(f"No landmarks found for category: {category_name}")

# Commit changes and close connection
conn.commit()
conn.close()
