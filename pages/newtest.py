import streamlit as st
import sqlite3
import json
import cv2
import numpy as np
import threading
import time
import pygame
import random  # <-- Added for random score generation
from database import create_connection

# Initialize pygame mixer for playing alert sounds
pygame.mixer.init()

def play_buzzer_sound():
    pygame.mixer.music.load("/Users/harshithyvs/Desktop/assets/buzzer_sound.wav")
    pygame.mixer.music.play()

# Load YOLO model for object detection
face_cascade = cv2.CascadeClassifier("/Users/harshithyvs/Desktop/assets/haarcascade_frontalface_default.xml")
LABELS = open("/Users/harshithyvs/Desktop/assets/coco.names").read().strip().split("\n")
net = cv2.dnn.readNetFromDarknet("/Users/harshithyvs/Desktop/assets/yolov3.cfg", "/Users/harshithyvs/Desktop/assets/yolov3.weights")
ln = [net.getLayerNames()[i - 1] for i in net.getUnconnectedOutLayers()]
colors = np.random.uniform(0, 255, size=(len(LABELS), 3))

# Database setup
conn = create_connection()
c = conn.cursor()

c.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        options TEXT,
        correct_option TEXT
    )
""")

c.execute("""
    CREATE TABLE IF NOT EXISTS test_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        reg_number TEXT,
        college TEXT,
        test_id TEXT,
        score INTEGER
    );
""")

conn.commit()

# Load Questions
def get_questions():
    c.execute("SELECT id, question, options, correct_option FROM questions")
    return c.fetchall()

questions = get_questions()
NUM_QUESTIONS = len(questions)
QUESTIONS_PER_PAGE = 5

def save_test_attempt(username, reg_number, college, score):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO test_attempts (username, reg_number, college, test_id, score) VALUES (?, ?, ?, ?, ?)", 
                   (username, reg_number, college, "Test1", score))
    conn.commit()
    conn.close()

# Session State Initialization
if "page" not in st.session_state:
    st.session_state.page = "test"
if "current_page" not in st.session_state:
    st.session_state.current_page = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "test_started" not in st.session_state:
    st.session_state.test_started = False
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "score" not in st.session_state:
    st.session_state.score = 0
if "visited" not in st.session_state:
    st.session_state.visited = set()

def run_proctoring():
    cap = cv2.VideoCapture(0)
    last_detected_time = time.time()
    alert_threshold = 5
    capture_interval = 10  # Capture image every 10 seconds
    last_capture_time = time.time()

    stframe = st.empty()
    detections_placeholder = st.empty()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            if time.time() - last_detected_time > alert_threshold:
                st.warning("⚠️ Face not detected! Stay in front of the camera.")
                play_buzzer_sound()
        else:
            last_detected_time = time.time()
        
        # Capture image every 10 seconds
        if time.time() - last_capture_time >= capture_interval:
            last_capture_time = time.time()
            frame_path = "captured_frame.jpg"
            cv2.imwrite(frame_path, frame)

            # Run YOLO detection
            blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
            net.setInput(blob)
            layer_outputs = net.forward(ln)

            detected_objects = []
            detected_people = 0  # Track the number of people detected

            for output in layer_outputs:
                for detection in output:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]

                    if confidence > 0.5:
                        label = LABELS[class_id]
                        detected_objects.append(label)

                        # Count the number of people detected
                        if label == "person":
                            detected_people += 1

            # Remove duplicates
            detected_objects = list(set(detected_objects))

            # Log detections to a file
            with open("detection_log.txt", "a") as log_file:
                log_file.write(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')} - Detected Objects: {detected_objects}\n")

            # Display detected objects in UI
            if detected_objects:
                detections_placeholder.warning(f"Detected Objects: {', '.join(detected_objects)}")

            # Proctoring alert if multiple people detected
            if detected_people > 1:
                st.error("⚠️ Multiple people detected! Ensure you're the only one taking the test.")
                play_buzzer_sound()

        stframe.image(frame, channels="BGR")

    cap.release()
    cv2.destroyAllWindows()

def start_proctoring():
    thread = threading.Thread(target=run_proctoring)
    thread.start()

def test_page():
    st.title("DetectEX Test")
    
    if not st.session_state.test_started:
        with st.form("user_info_form"):
            name = st.text_input("Name")
            reg_number = st.text_input("Registration Number")
            college = st.text_input("College")
            start_test = st.form_submit_button("Start Test")
        
        if start_test:
            if name and reg_number and college:
                st.session_state.test_started = True
                st.session_state.name = name
                st.session_state.reg_number = reg_number
                st.session_state.college = college
                st.rerun()
            else:
                st.warning("Please fill in all details to proceed.")
    else:
        # Top row: Video feed & question palette
        col1, col2 = st.columns([3, 1])
        with col2:
            st.write("##### ⚠️You are proctored throughout the exam.")
            start_proctoring()
            
            st.write("### Question Palette")
            for i in range(NUM_QUESTIONS):
                q_id = questions[i][0]
                if q_id in st.session_state.answers:
                    color = "green"  # Answered
                elif q_id in st.session_state.visited:
                    color = "red"  # Unanswered but visited
                else:
                    color = "gray"  # Not visited
                
                button_style = f"background-color: {color}; color: white; border-radius: 50%; width: 30px; height: 30px; text-align: center;"
                if st.button(f"{i+1}", key=f"q_button_{i}", help=f"Go to question {i+1}"):
                    st.session_state.current_page = i // QUESTIONS_PER_PAGE
                    st.rerun()
        
        with col1:
            st.write(f"**Name:** {st.session_state['name']}")
            st.write(f"**Registration Number:** {st.session_state['reg_number']}")
            st.write(f"**College:** {st.session_state['college']}")
            
            st.write("### Questions")
            start_idx = st.session_state.current_page * QUESTIONS_PER_PAGE
            end_idx = min(start_idx + QUESTIONS_PER_PAGE, NUM_QUESTIONS)
            for q_id, question_text, options, correct_option in questions[start_idx:end_idx]:
                options = json.loads(options)
                selected_answer = st.session_state.answers.get(q_id, None)
                chosen = st.radio(f"**{question_text}**", options, index=options.index(selected_answer) if selected_answer else None, key=f"q_{q_id}")
                if chosen:
                    st.session_state.answers[q_id] = chosen
                st.session_state.visited.add(q_id)
        
        # Navigation & Submit
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.session_state.current_page > 0 and st.button("Previous"):
                st.session_state.current_page -= 1
                st.rerun()
        with col3:
            if (st.session_state.current_page + 1) * QUESTIONS_PER_PAGE < NUM_QUESTIONS and st.button("Next"):
                st.session_state.current_page += 1
                st.rerun()
        
        if st.button("Submit Test"):
            score = random.randint(2, 9)  # 🔁 Random score instead of evaluating answers
            save_test_attempt(
                st.session_state.name,
                st.session_state.reg_number,
                st.session_state.college,
                score
            )
            st.session_state.score = score
            st.session_state.submitted = True
            st.session_state.page = "score"
            st.rerun()

def score_page():
    st.title("Thank You!")
    st.subheader("🎉 Your test has been successfully submitted.")
    st.write("You can check your test history in the dashboard.")
    st.success(f"Your Score: **{st.session_state['score']} / {NUM_QUESTIONS}**")
    if st.button("Go to Dashboard"):
        st.switch_page("/Users/harshithyvs/Desktop/VIT/Deeksha/pages/user.py")

if __name__ == "__main__":
    if st.session_state.page == "test":
        test_page()
    elif st.session_state.page == "score":
        score_page()
