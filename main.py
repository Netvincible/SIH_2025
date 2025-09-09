from pathlib import Path
import face_recognition
import pickle
from collections import Counter
import os

DEFAULT_ENCODINGS_PATH = Path("output/encodings.pkl")

def encode_known_faces(model: str = "hog", encodings_location: Path = DEFAULT_ENCODINGS_PATH) -> None:
    rolls = []
    encodings = []
    for tup in list:
        roll = tup[0]
        for img in tup[1]:
            image_stream=Bytes_IO(img)
            student_image=face_recognition.load_image_file(image_stream)
            face_locations = face_recognition.face_locations(student_image, model=model)
            face_encodings = face_recognition.face_encodings(student_image, face_locations)
            for encoding in face_encodings:
                rolls.append(roll)
                encodings.append(encoding)
    
    roll_encodings = {"rolls": rolls, "encodings": encodings}
    with encodings_location.open(mode="wb") as f:
        pickle.dump(roll_encodings, f)

def _recognize_face(unknown_encoding, loaded_encodings):
    boolean_matches = face_recognition.compare_faces(loaded_encodings["encodings"], unknown_encoding,tolerance=0.52)
    votes = Counter(roll for match, roll in zip(boolean_matches, loaded_encodings["rolls"])if match)
    if votes:
        return votes.most_common(1)[0][0]


def recognize_faces( image_location: str, model: str = "hog",encodings_location: Path = DEFAULT_ENCODINGS_PATH,) -> None:
    with encodings_location.open(mode="rb") as f:
        loaded_encodings = pickle.load(f)

    input_image = face_recognition.load_image_file(image_location)
    input_face_locations = face_recognition.face_locations(input_image, model=model)
    input_face_encodings = face_recognition.face_encodings(input_image, input_face_locations)
    for bounding_box, unknown_encoding in zip(input_face_locations, input_face_encodings):
        roll = _recognize_face(unknown_encoding, loaded_encodings)
        if roll:
            sql="UPDATE ATTENDENCE SET P_A=%s WHERE ROLL=%s AND DATE=%s"
            val=("P",roll,"1/1/2025")
            cursor.execute(sql,val)


file=next(Path("Webpage/students").glob("*.jpeg"))
recognize_faces(file)
os.remove(file)
