
import sqlite3
import simplekml

def generate_kml(database_path, output_kml_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Query the collinear_landmarks table
    cursor.execute("SELECT * FROM collinear_landmarks")
    collinear_data = cursor.fetchall()

    # Fetch the landmark details
    landmark_data = {}
    for row in collinear_data:
        for landmark_id in [row[1], row[2], row[3]]:
            if landmark_id not in landmark_data:
                cursor.execute(f"SELECT id, name, latitude, longitude FROM landmarks WHERE id = {landmark_id}")
                landmark_data[landmark_id] = cursor.fetchone()

    # Create a new KML object
    kml = simplekml.Kml()

    # Generate the KML content
    for row in collinear_data:
        folder = kml.newfolder(name=f"Collinear Set {row[0]}")
        landmark1 = landmark_data[row[1]]
        landmark2 = landmark_data[row[2]]
        landmark3 = landmark_data[row[3]]
        middle_landmark = landmark_data[row[4]]

        folder.newpoint(name=landmark1[1], coords=[(landmark1[3], landmark1[2])])
        folder.newpoint(name=landmark2[1], coords=[(landmark2[3], landmark2[2])])
        folder.newpoint(name=landmark3[1], coords=[(landmark3[3], landmark3[2])])

        coords = []
        if landmark1[0] != middle_landmark[0]:
            coords.append((landmark1[3], landmark1[2]))
        if landmark2[0] != middle_landmark[0]:
            coords.append((landmark2[3], landmark2[2]))
        if landmark3[0] != middle_landmark[0]:
            coords.append((landmark3[3], landmark3[2]))
        
        # Set line color to blue and create the line
        line = folder.newlinestring(coords=coords)
        line.style.linestyle.color = simplekml.Color.blue

    # Save the KML file
    kml.save(output_kml_path)

if __name__ == "__main__":
    database_path = "landmarks.db"  # Modify this path as needed
    output_kml_path = "collinear_landmarks.kml"  # Modify this path as needed
    generate_kml(database_path, output_kml_path)
