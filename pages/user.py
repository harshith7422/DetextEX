import streamlit as st
import sqlite3
from database import create_connection

def get_user_tests(username):
    """Fetch past test attempts of the user."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT test_id, score FROM test_attempts WHERE username=?", (username,))
    tests = cursor.fetchall()
    conn.close()
    return tests

def user_dashboard():
    st.title("User Dashboard")
    
    # Ensure user is logged in
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.warning("Please log in first!")
        st.stop()
    
    username = st.session_state["username"]
    st.subheader(f"Welcome, {username}!")

    # Show past test attempts
    st.write("### Your Test History")
    tests = get_user_tests(username)
    if tests:
        for test in tests:
            st.write(f"📝 Test ID: {test[0]}, Score: {test[1]}")
    else:
        st.info("No test history found.")

    # Start Test Button
    if st.button("Start Test"):
        st.switch_page("/Users/harshithyvs/Desktop/VIT/Deeksha/pages/newtest.py")

    # Logout Button
    if st.button("Logout"):
        st.session_state.clear()
        st.success("Logged out successfully!")
        st.rerun()

if __name__ == "__main__":
    user_dashboard()
