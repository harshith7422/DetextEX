import streamlit as st
import sqlite3
from database import create_connection, create_tables 

def register_user(name, email, registration_number, college, password, role="user"):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, email, registration_number, college, password, role) VALUES (?, ?, ?, ?, ?, ?)", 
        (name, email, registration_number, college, password, role)
    )
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE name=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def main():
    st.set_page_config(page_title="DetectEX", layout="wide")
    st.title("DetectEX - Exam Portal")
    
    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "Login":
        st.subheader("Login to your Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.session_state["logged_in"] = True
                st.session_state["username"] = user[1]
                st.session_state["role"] = user[5]
                st.success(f"Welcome {username}")
                if user[5] == "admin":
                    st.switch_page("pages/admin.py")
                else:
                    st.switch_page("/Users/harshithyvs/Desktop/VIT/Deeksha/pages/user.py")
            else:
                st.error("Invalid username or password")
    
    elif choice == "Register":
        st.subheader("Create a New Account")
        new_user = st.text_input("Name")
        new_email = st.text_input("Email")
        new_reg_no = st.text_input("Registration Number")
        new_college = st.text_input("College Name")
        new_password = st.text_input("Password", type="password")

        if st.button("Register"):
            if new_user and new_email and new_reg_no and new_college and new_password:
                register_user(new_user, new_email, new_reg_no, new_college, new_password)
                st.success("Account created successfully! You can now log in.")
            else:
                st.error("Please fill in all fields.")

if __name__ == "__main__":
    create_tables()
    main()
