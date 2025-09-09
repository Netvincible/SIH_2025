from pathlib import Path
import face_recognition
import pickle
from collections import Counter
import os
import mysql.connector
from io import BytesIO


# --- 1. Connect to MySQL ---
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="schoolDB"
)
cursor = conn.cursor()


# --- 2. Dummy student data after face recognition --- 
roll_no = "101"
name = "Vedanti Shukla"
total_lectures = 10
present = 9
absent = total_lectures - present

# Optional: storing image as binary
# Assuming you have an image file path
def convert_to_binary(filename):
    with open(filename, "rb") as f:
        return f.read()

image_data = convert_to_binary("/Users/apple/Documents/ML_prog/sih/students/profile.jpeg")  # replace with your actual path

# --- 3. Insert into attendance table ---
sql = """
INSERT INTO attendance (roll_no, name, total_lectures, present, absent, image)
VALUES (%s, %s, %s, %s, %s, %s) 
"""

values = (roll_no, name, total_lectures, present, absent, image_data)

try:
    cursor.execute(sql, values)
    conn.commit()
    print(f" Dummy attendance record inserted for {name} ({roll_no})")
except Exception as e:
    print(" Database error:", e) 


def fetch_students():
    cursor.execute("SELECT roll_no, image FROM attendance") 
    results = cursor.fetchall()
    return tuple(results) 

result=fetch_students()

print("\nResult tuple-of-tuples (roll_no, image in binary):")
print(result) 

DEFAULT_ENCODINGS_PATH = Path("output/encodings.pkl")

def encode_known_faces(model: str = "hog", encodings_location: Path = DEFAULT_ENCODINGS_PATH) -> None:
    names = []
    encodings = []
    for img,roll in result:
        name = roll
        image = face_recognition.load_image_file(img)
        face_locations = face_recognition.face_locations(image, model=model)
        face_encodings = face_recognition.face_encodings(image, face_locations)
        for encoding in face_encodings:
            names.append(name)
            encodings.append(encoding)
    
    name_encodings = {"names": names, "encodings": encodings}
    with encodings_location.open(mode="wb") as f:
        pickle.dump(name_encodings, f)
encode_known_faces

def _recognize_face(unknown_encoding, loaded_encodings):
    boolean_matches = face_recognition.compare_faces(loaded_encodings["encodings"], unknown_encoding,tolerance=0.52)
    votes = Counter(name for match, name in zip(boolean_matches, loaded_encodings["names"])if match)
    if votes:
        return votes.most_common(1)[0][0]


def recognize_faces( image_location: str, model: str = "hog",encodings_location: Path = DEFAULT_ENCODINGS_PATH,) -> None:
    with encodings_location.open(mode="rb") as f:
        loaded_encodings = pickle.load(f)

    input_image = face_recognition.load_image_file(image_location)

    input_face_locations = face_recognition.face_locations(input_image, model=model)
    input_face_encodings = face_recognition.face_encodings(input_image, input_face_locations)
    for bounding_box, unknown_encoding in zip(input_face_locations, input_face_encodings):
        name = _recognize_face(unknown_encoding, loaded_encodings)
        if not name:
            name = "Unknown"
        print(name, bounding_box)

recognize_faces("unknown/test1.jpeg")


# --- 4. Cleanup ---
cursor.close()
conn.close()