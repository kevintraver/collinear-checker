
import sqlite3
from geopy.distance import geodesic
from itertools import combinations
from math import radians, sin, asin, cos, atan2

def bearing(coord1, coord2):
    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])
    dlon = lon2 - lon1
    y = sin(dlon) * cos(lat2)
    x = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)
    return atan2(y, x)

def cross_track_distance(point, start, end):
    R = 6371  # Earth's radius in km
    d_start_point = geodesic(start, point).kilometers
    theta_start_point = bearing(start, point)
    theta_start_end = bearing(start, end)
    d_xt = asin(sin(d_start_point/R) * sin(theta_start_point - theta_start_end)) * R
    return abs(d_xt)

def are_collinear(coord1, coord2, coord3, tolerance=0.3):
    d1 = cross_track_distance(coord1, coord2, coord3)
    d2 = cross_track_distance(coord2, coord1, coord3)
    d3 = cross_track_distance(coord3, coord1, coord2)
    return max(d1, d2, d3) <= tolerance, max(d1, d2, d3) * 1000  # Convert km to meters

# Connect to SQLite database
conn = sqlite3.connect('landmarks.db')
cursor = conn.cursor()

# Modify the table for collinear landmarks to include the offset column
cursor.execute('''
CREATE TABLE IF NOT EXISTS collinear_landmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    landmark1_id INTEGER,
    landmark2_id INTEGER,
    landmark3_id INTEGER,
    offset REAL
)
''')

# Input category name
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
        collinear, offset = are_collinear(coord1, coord2, coord3)
        if collinear:
            cursor.execute("INSERT INTO collinear_landmarks (landmark1_id, landmark2_id, landmark3_id, offset) VALUES (?, ?, ?, ?)", (id1, id2, id3, offset))
            print(f"The landmarks {name1}, {name2}, and {name3} are collinear with an offset of {offset:.2f} meters.")
else:
    print(f"No landmarks found for category: {category_name}")

# Commit changes and close connection
conn.commit()
conn.close()
