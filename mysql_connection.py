import mysql.connector

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

for roll, img in result:
    print(f"Roll : {roll}, Image bytes length : {len(img)}")
    with open(f"{roll}.jpeg","wb") as f:
        f.write(img)
    print(f"Image for roll {roll} saved as {roll}.jpeg")

# --- 4. Cleanup ---
cursor.close()
conn.close()