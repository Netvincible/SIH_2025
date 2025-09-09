import face_recognition
from io import BytesIO

Hash={}
attendence=face_recognition.load_image_file("imag.jpg")
face_locations = face_recognition.face_locations(attendence)
face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
for face_encoding in face_encodings:
    Hash[face_encoding]=1


for bin_student_image,roll in bin_images_and_roll():
    image_stream=Bytes_IO(bin_student_image)
    student_image=face_recognition.load_image_file(image_stream)
    student_img_encoding=face_recognition.face_encodings(student_image)[0]
    # if(Hash[student_img_encoding]):
    #     <<present>>



picture_of_me = face_recognition.load_image_file("face_recog/me.jpg")
my_face_encoding = face_recognition.face_encodings(picture_of_me)[0]
print(picture_of_me)
# my_face_encoding now contains a universal 'encoding' of my facial features that can be compared to any other picture of a face!

unknown_picture = face_recognition.load_image_file("t1.jpg")
unknown_face_encoding = face_recognition.face_encodings(unknown_picture)[0]

# Now we can see the two face encodings are of the same person with `compare_faces`!

results = face_recognition.compare_faces([my_face_encoding], unknown_face_encoding)

if results[0] == True:
    print("It's a picture of me!")
else:
    print("It's not a picture of me!")