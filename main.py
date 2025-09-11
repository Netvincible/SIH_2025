import os
from datetime import date
import MySQLdb
import mysql.connector
from pathlib import Path
import face_recognition
import pickle
from collections import Counter
from io import BytesIO

# --- 1. Connect to MySQL ---
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="netvincible",
    password="12345678",
    database="schoolDB"
)
cursor = conn.cursor() 

# --- 2. Create Table in MySQL ---
def create_table():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance_2 (
                name VARCHAR(20), 
                roll_no VARCHAR(20) PRIMARY KEY,
                attendance_date DATE,
                status VARCHAR(10)
            )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_images (
                id INT AUTO_INCREMENT PRIMARY KEY, 
                roll_no VARCHAR(20) ,
                name VARCHAR(20),
                image LONGBLOB UNIQUE,
                CONSTRAINT fk_attendance_roll
                FOREIGN KEY(roll_no) REFERENCES attendance_2(roll_no)
                ON DELETE CASCADE
                ON UPDATE CASCADE
            )
    """)

# --- Utility: convert image to binary ---
def convert_to_binary(filename):
    with open(filename, "rb") as f:
        return f.read()

# --- 3. Insert into attendance table --- 
def set_absent():
    today=date.today()
    cursor.execute("""SELECT 1 FROM attendance_2 WHERE attendance_date = %s LIMIT 1;""",(today,))
    is_marked=cursor.fetchall()
    if(is_marked):
        print("attendance is already marked for this day: ",today)
        return
    manual_attendance = [
        ("Nisarg Patel", 101,today,"A"),
        ("Devang Ajudiya",102,today,"A"),
        ("Netra Sorathiya",103,today,"A"),
        ("Vedanti Shukla",104,today,"A"),
        ("Prince Panara",105,today,"A"),
        ("Hitarth Bhatt",106,today,"A"),


    ]


    for name, roll_no, attendance_date, status in manual_attendance:
        try :
            cursor.execute("""
            INSERT INTO attendance_2(name,roll_no,attendance_date,status)
            VALUES (%s,%s,%s,%s) 
    """,(name, roll_no,attendance_date, status))
            conn.commit()
        except mysql.connector.IntegrityError:
            pass

# --- 4. Insert 5 images per student into student_images ---
def insert_known_images(students):
    count=0
    for roll_no, name, image_paths in students:
        cursor.execute("""SELECT 1 FROM student_images WHERE roll_no = %s LIMIT 1;""",(roll_no,))
        is_roll=cursor.fetchall()
        if(is_roll):
            count+=1
            continue
        for img_path in image_paths:
            if not os.path.exists(img_path):
                print(f"Warning: Image not found: {img_path}, skipping...")
                continue
            img_data = convert_to_binary(img_path)
            try:
                cursor.execute("""
                INSERT INTO student_images (roll_no,name,image) VALUES (%s, %s, %s)
                """, (roll_no,name,img_data))
                conn.commit()
            except :
                print("same image was inserted")

        conn.commit()

    if(count==len(students)):
        print("student images are already inserted")
        return False
    else:
        print(" Manual attendance + student_images inserted successfully")
        return True

# --- 5. Fetch roll_no + images ---
def get_images_n_rolls():
    cursor.execute("SELECT roll_no, image FROM student_images ORDER BY roll_no, id")
    return cursor.fetchall()

# --- 6. save known encodings ---
DEFAULT_ENCODINGS_PATH = Path("output/encodings.pkl")
def encode_known_faces(student_n_images: list, model: str = "hog", encodings_location: Path = DEFAULT_ENCODINGS_PATH) -> None:
    rolls = []
    encodings = []
    for roll,img in student_n_images:
        roll=int(roll)
        image_stream=BytesIO(img)
        student_image=face_recognition.load_image_file(image_stream)
        face_locations = face_recognition.face_locations(student_image, model=model)
        face_encodings = face_recognition.face_encodings(student_image, face_locations,num_jitters=5)
        for encoding in face_encodings:
            rolls.append(roll)
            encodings.append(encoding)
    
    roll_encodings = {"rolls": rolls, "encodings": encodings}
    with encodings_location.open(mode="wb") as f:
        pickle.dump(roll_encodings, f)

# --- 7. helper function for comparing faces ---
def _recognize_face(unknown_encoding, loaded_encodings):
    boolean_matches = face_recognition.compare_faces(loaded_encodings["encodings"], unknown_encoding,tolerance=0.42)
    votes = Counter(roll for match, roll in zip(boolean_matches, loaded_encodings["rolls"])if match)
    if votes:
        return votes.most_common(1)[0][0]

# --- 8. recognizing faces in input image and marking attendance ---
def mark_attendance( image_location: str, model: str = "hog",encodings_location: Path = DEFAULT_ENCODINGS_PATH,) -> None:
    with encodings_location.open(mode="rb") as f:
        loaded_encodings = pickle.load(f)

    input_image = face_recognition.load_image_file(image_location)
    input_face_locations = face_recognition.face_locations(input_image, model=model,number_of_times_to_upsample=2)
    input_face_encodings = face_recognition.face_encodings(input_image, input_face_locations,num_jitters=5)
    for bounding_box, unknown_encoding in zip(input_face_locations, input_face_encodings):
        roll = _recognize_face(unknown_encoding, loaded_encodings)
        if roll:
            roll=int(roll)
            val=("P",roll,date.today())
            sql="UPDATE attendance_2 SET status=%s WHERE roll_no=%s AND attendance_date=%s"
            cursor.execute(sql,val)
            conn.commit()
            print(roll)

create_table()
set_absent()
students = [
        (101,"Nisarg Patel",[
            "training/students/s1-1.jpeg",
            "training/students/s1-2.jpeg",
            "training/students/s1-3.jpeg",
            "training/students/s1-4.jpeg",
            "training/students/s1-5.jpeg",
        ]),
        (102,"Devang Ajudiya",[ 
            "training/students/s2-1.jpeg",
            "training/students/s2-2.jpeg",
            "training/students/s2-3.jpeg",
            "training/students/s2-4.jpeg"
        ]),
        (103,"Netra Sorathiya",[ 
            "training/students/s3-1.jpeg",
            "training/students/s3-2.jpeg",
            "training/students/s3-3.jpeg",
            "training/students/s3-4.jpeg",
        ]),
        (104,"Vedanti Shukla",[ 
            "training/students/s4-1.jpeg",
            "training/students/s4-2.jpeg",
            "training/students/s4-3.jpeg",
        ]),
        (105,"Prince Panara",[ 
            "training/students/s5-1.jpeg",
            "training/students/s5-2.jpeg",
            "training/students/s5-3.jpeg",
            "training/students/s5-4.jpeg"
        ]),
        (106,"Hitarth Bhatt",[ 
            "training/students/s6-1.jpeg",
            "training/students/s6-2.jpeg",
            "training/students/s6-3.jpeg",
            "training/students/s6-4.jpeg",
            "training/students/s6-5.jpeg"
        ])
    ]
if(len(students)>0 and insert_known_images(students)):  #check for len of students as in future we plan to get students list from webpage's backend
    roll_n_images=get_images_n_rolls()
    encode_known_faces(roll_n_images)
file=next(Path("Webpage/students").glob("*.jp*g"))
mark_attendance(file)
os.remove(file)

cursor.close()
conn.close()