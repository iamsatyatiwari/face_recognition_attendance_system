import cv2
import pandas as pd
import face_recognition
from os import listdir
from datetime import datetime
import streamlit as st


def detect():
    frame = st.image([])

    # getting the face locations in an image and their encodings
    def encode(images):
        face_location = []
        encodings = []
        if type(images) == list:
            for i in images:
                print(i[0])
                face_location.append(face_recognition.face_locations(i[1])[0])
                encodings.append(face_recognition.face_encodings(i[1])[0])
        else:
            face_location = face_recognition.face_locations(images)
            encodings = face_recognition.face_encodings(images)

        return face_location, encodings

    # loading images
    persons = []
    for file in listdir('People/'):
        name, extension = file.split(".")
        image = face_recognition.load_image_file('People/' + file)
        persons.append([name, cv2.cvtColor(image, cv2.COLOR_BGR2RGB)])

    def compare_and_distances(img, encodings):
        results = []
        faceDis = []

        img_encodings = face_recognition.face_encodings(img)
        for i in img_encodings:
            results.append(face_recognition.compare_faces(encodings, i))
            # lower the distance = better match
            faceDis.append(face_recognition.face_distance(encodings, i))
        return results, faceDis

    known_faces_encodings = encode(persons)
    cap = cv2.VideoCapture(0)  # webcam
    flag = True
    while flag:
        ret, img = cap.read()
        face_loc, enc = encode(img)
        if len(face_loc) != 0:
            preds, face_dist = compare_and_distances(img, known_faces_encodings[1])
            for i in range(len(preds)):
                for j in preds[i]:
                    if j == True:
                        index = preds[i].index(j)
                        name = persons[index][0]

                        x, y, x1, y1 = face_loc[i][3], face_loc[i][0], face_loc[i][1], face_loc[i][2]
                        cv2.putText(img, name, (int(x1 + 15), int(y - 12)), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                    (57, 255, 20), 2)
                        cv2.rectangle(img, (x, y), (x1, y1), (255, 0, 0), 2)
                        df = pd.read_csv('Attendance.csv')
                        if name not in df[df['Date'] == str(datetime.now().date())]['Name'].tolist():
                            df.loc[len(df)] = [name, datetime.now().date(), datetime.now().time()]
                            df.to_csv('Attendance.csv', index=False)
                            flag = False
                            st.success('Your Attendance has been taken')
                            break
                        else:
                            flag = False
                            st.warning('You Attendance for today has been taken already')
                            break
                    else:
                        continue
        frame.image(img, channels="BGR")



# function to register picture of student
def register():
    frame = st.image([])
    cap = cv2.VideoCapture(0)  # webcam
    flag = True
    click = st.button('Save Photo')
    user_input = st.text_input("Enter your Name as Name_Uid")
    # ret, img = cap.read()
    # taking picture of student
    while flag:
        print("in loop")
        ret, img = cap.read()
        frame.image(img, channels="BGR")
        if click:
            flag = False
            frame.image(img, channels="BGR")
            print("save img")
            cv2.imwrite(f"People/{user_input}.jpg", img)
            st.success(f"Congratulations {user_input}\n You've been Registered")



def main():
    # sidebar Section
    selected_box = st.sidebar.radio('Choose any', ('Welcome', 'Take Attendance', 'Register Student', 'Show Attendance'))
    if selected_box == 'Welcome':
        st.image("welcome_img.jpg", width=800, height=100)
        st.write("Hello, welcome to the face recognition based attendance system. "
                 "This web app is made mainly through the streamlit and python. "
                 "Here you can register yourself and can mark your attendance through the webcam which will "
                 "save your time and energy so that you can utilise that somewhere else "
                 "🙂 <3")
        st.write("You can mark your attendance by choosing options which are given below. "
                 "Or you can simply choose the option --Take Attendance-- from the menu below")

    st.write("# Face Recognition Attendance System")
    option = st.selectbox('Choose', ('-', 'Give Attendance Using Webcam'))
    start = st.button('START')
    if option == 'Give Attendance Using Webcam':
        if start:
            detect()
    if selected_box == 'Take Attendance':
        if start:
            detect()
    if selected_box == 'Register Student':
        register()
    if selected_box == 'Show Attendance':
        attendance = st.button('Attendance_sheet')
        if attendance:
            data = pd.read_csv("Attendance.csv")
            st.dataframe(data, width=500, height=500)


# Calling main function
main()
