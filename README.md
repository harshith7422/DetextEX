# 🛡️ DetectEx – Python based Online Exam Proctoring System

DetectEx is an intelligent, lightweight online examination platform integrated with a real-time proctoring system that uses computer vision to detect suspicious behaviors during test attempts. It ensures academic integrity by logging violations and providing admin tools for monitoring and evaluation.

---

## 📌 Features

- 🔐 Secure student registration & login  
- 🧠 Intelligent face detection using OpenCV  
- 🎥 Real-time webcam monitoring with violation detection  
- 📄 Automatic logging of anomalies (`detection_log.txt`)  
- 📊 Admin dashboard for viewing student attempts and metrics  
- 📝 MCQ-based test interface with score tracking  
- 📥 Download logs as PDF (for admin use)  

---

## 🧩 System Modules

### 1. **Registration & Login**
Handles user creation, authentication, and secure login with hashed passwords.

### 2. **Exam Interface**
Displays questions from the database with multiple-choice options and records the score.

### 3. **Proctoring Module**
Uses OpenCV’s Haar cascade classifier to detect:
- Absence of face
- Multiple faces
- Face not detected for prolonged duration

All violations are timestamped and stored in `detection_log.txt`.

### 4. **Admin Dashboard**
- View list of all registered students  
- View test attempt scores  
- Download violation logs as PDF  
- View evaluation metrics per test session  

---

## 🧠 Model Implementation

- **Technique**: Haar Cascade (Frontal Face Detection)
- **Tool**: OpenCV (`haarcascade_frontalface_default.xml`)
- **Triggering**:
  - `No face detected`
  - `Multiple faces detected`
- All logs written in real-time to a text file

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/your-username/DetectEx.git
cd DetectEx
```
### 2. Install dependencies
```bash
pip install -r requirements.txt
```
### 3. Run the application
```bash
streamlit run main.py
```

## Developers

Harshith YVS, Deeksha R

Final Year, VIT

Capstone Project - April 2025

Contact: <harshithyvs@email.com> , <deekshar2431@gmail.com>

