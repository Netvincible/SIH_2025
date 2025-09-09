import mysql.connector
import sys
import os
from datetime import date

print("Python interpreter:", sys.executable)

# --- 1. Connect to MySQL ---
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="schoolDB"
)
cursor = conn.cursor() 

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
            image LONGBLOB,
            CONSTRAINT fk_attendance_roll
               FOREIGN KEY(roll_no) REFERENCES attendance_2(roll_no)
               ON DELETE CASCADE
               ON UPDATE CASCADE
        )
 """)

# students = [
#     ("101","Nisarg Patel",[
#         "/Users/apple/Documents/ML_prog/sih/students/s1-1.jpeg",
#         "/Users/apple/Documents/ML_prog/sih/students/s1-2.jpeg",
#         "/Users/apple/Documents/ML_prog/sih/students/s1-3.jpeg",
#         "/Users/apple/Documents/ML_prog/sih/students/s1-4.jpeg",
#         "/Users/apple/Documents/ML_prog/sih/students/s1-5.jpeg",
#     ]),
#     ("102","Devang Ajudiya",[ 
#         "/Users/apple/Documents/ML_prog/sih/students/s2-1.jpeg",
#         "/Users/apple/Documents/ML_prog/sih/students/s2-2.jpeg",
#         "/Users/apple/Documents/ML_prog/sih/students/s2-3.jpeg",
#         "/Users/apple/Documents/ML_prog/sih/students/s2-4.jpeg",
#         "/Users/apple/Documents/ML_prog/sih/students/s2-5.jpeg",
#     ]),
#     ("103","Netra Patel",[ 
#         "/Users/apple/Documents/ML_prog/sih/students/s3-1.jpeg",
#         "/Users/apple/Documents/ML_prog/sih/students/s3-2.jpeg",
#         "/Users/apple/Documents/ML_prog/sih/students/s3-3.jpeg",
#         "/Users/apple/Documents/ML_prog/sih/students/s3-4.jpeg",
#     ])
# ]

# --- 4. Utility: convert image to binary ---
def convert_to_binary(filename):
    with open(filename, "rb") as f:
        return f.read()
    

# --- 3. Insert into attendance table --- 

manual_attendance = [
    ("Nisarg Patel", 101, date(2025, 9, 9),"A"),
    ("Devang Ajudiya",102,date(2025, 9, 9),"A"),
    ("Netra Patel",103,date(2025, 9, 9),"A")
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

# --- 7. Insert 5 images per student into student_images ---
for roll_no, name, image_paths in students:
    for img_path in image_paths:
        if not os.path.exists(img_path):
            print(f"Warning: Image not found: {img_path}, skipping...")
            continue
        img_data = convert_to_binary(img_path)
        cursor.execute("""
        INSERT INTO student_images (roll_no,name,image) VALUES (%s, %s, %s)
        """, (roll_no,name,img_data))
    conn.commit()

print(" Manual attendance + student_images inserted successfully")

# --- 8. Fetch roll_no + images ---
cursor.execute("SELECT roll_no, image FROM student_images ORDER BY roll_no, id")
results = cursor.fetchall()

# Group images by roll_no
student_dict = {}
for roll, img in results:
    student_dict.setdefault(roll, []).append(img)

# Convert dict → tuple-of-tuples
final_tuple = tuple((roll, tuple(images)) for roll, images in student_dict.items())

# --- 9. Display grouped tuple ---
print("\nFinal tuple (roll_no, 5 images):")
for roll, images in final_tuple:
    print(f"Roll: {roll}, Total images: {len(images)}")

cursor.close()
conn.close()