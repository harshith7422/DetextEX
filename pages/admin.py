import streamlit as st
import sqlite3
import pandas as pd
from reportlab.pdfgen import canvas
import os

# Database connection
def create_connection():
    conn = sqlite3.connect("exam_system.db")  
    return conn

# Fetch registered students
def get_registered_students():
    conn = create_connection()
    df = pd.read_sql_query("SELECT DISTINCT username, reg_number, college FROM test_attempts", conn)
    conn.close()
    return df

# Fetch test attempts
def get_test_attempts():
    conn = create_connection()
    df = pd.read_sql_query("SELECT username, reg_number, test_id, score FROM test_attempts", conn)
    conn.close()
    return df

# Function to convert detection_log.txt to PDF
def generate_pdf(log_file="detection_log.txt"):
    pdf_path = "detection_log.pdf"
    c = canvas.Canvas(pdf_path)
    c.setFont("Helvetica", 12)
    
    # Check if log file exists
    if os.path.exists(log_file):
        with open(log_file, "r") as file:
            lines = file.readlines()
            y = 800  # Starting Y position
            c.drawString(50, y, "DetectEX Log Report")
            c.line(50, y-5, 550, y-5)  # Line separator
            y -= 20

            for line in lines:
                if y < 50:  # Prevent writing beyond the page
                    c.showPage()
                    y = 800
                c.drawString(50, y, line.strip())
                y -= 20
    else:
        c.drawString(50, 800, "No detection logs available.")

    c.save()
    return pdf_path

# Streamlit UI
st.title("📊 Admin Dashboard")
st.subheader("List of Registered Students")

students_df = get_registered_students()
st.dataframe(students_df)

st.subheader("📜 Test Attempts")
test_attempts_df = get_test_attempts()
st.dataframe(test_attempts_df)

# PDF Download Section
# st.subheader("📥 Detection Log Report")
if st.button("Generate Detection Log PDF"):
    pdf_path = generate_pdf()
    with open(pdf_path, "rb") as file:
        st.download_button(label="📥 Download PDF",
                           data=file,
                           file_name="detection_log.pdf",
                           mime="application/pdf")
