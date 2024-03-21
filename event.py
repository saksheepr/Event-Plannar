import streamlit as st
import sqlite3
from datetime import datetime

# Function to create the database connection
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        st.error(f"Error creating database connection: {e}")
    return conn

def create_tables(conn):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Events (
                id INTEGER PRIMARY KEY,
                event_name TEXT,
                event_date DATE,
                event_time TIME,
                venue_id INTEGER,
                agenda TEXT,
                goals TEXT,
                collaborators TEXT,
                FOREIGN KEY(venue_id) REFERENCES Venues(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Venues (
                id INTEGER PRIMARY KEY,
                name TEXT,
                capacity INTEGER,
                facilities TEXT,
                pricing TEXT,
                availability BOOLEAN
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Tasks (
                id INTEGER PRIMARY KEY,
                event_id INTEGER,
                task_name TEXT,
                deadline DATE,
                responsibility TEXT,
                completed BOOLEAN,
                FOREIGN KEY(event_id) REFERENCES Events(id)
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Error creating tables: {e}")

# Function to insert event data into the database
def insert_event(conn, event_data):
    try:
        cursor = conn.cursor()
        # Convert time to string in the format HH:MM:SS
        event_data = list(event_data)
        event_data[2] = event_data[2].strftime("%H:%M:%S")
        cursor.execute('''
            INSERT INTO Events (event_name, event_date, event_time, venue_id, agenda, goals, collaborators)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', event_data)
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        st.error(f"Error inserting event data: {e}")
        return None

# Function to insert venue data into the database
def insert_venue(conn, venue_data):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Venues (name, capacity, facilities, pricing, availability)
            VALUES (?, ?, ?, ?, ?)
        ''', venue_data)
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        st.error(f"Error inserting venue data: {e}")
        return None

# Function to insert task data into the database
def insert_task(conn, task_data):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Tasks (event_id, task_name, deadline, responsibility, completed)
            VALUES (?, ?, ?, ?, ?)
        ''', task_data)
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Error inserting task data: {e}")

# Function to update task status in the database
def update_task_status(conn, task_id, completed):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE Tasks
            SET completed = ?
            WHERE id = ?
        ''', (completed, task_id))
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Error updating task status: {e}")

# Main program
def main():
    st.title("Business Event Planner")
    with open('style.css') as f:
        css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

    # Create database connection
    conn = create_connection("event_planner.db")
    if conn is not None:
        create_tables(conn)
    else:
        st.error("Failed to create database connection.")

    # Event Creation and Management
    st.header("Event Creation and Management")
    event_name = st.text_input("Event Name")
    event_date = st.date_input("Event Date")
    event_time = st.time_input("Event Time")

    # Display existing events as a table with headings and all details
    st.subheader("Existing Events")
    existing_events = conn.execute("SELECT event_name, event_date, event_time, venue_id, agenda, goals, collaborators FROM Events").fetchall()
    if existing_events:
        headings = ["Event Name", "Event Date", "Event Time", "Venue ID", "Agenda", "Goals", "Collaborators"]
        existing_events_with_headings = [headings] + existing_events
        st.table(existing_events_with_headings)
    else:
        st.write("No existing events.")

    # Venue Management
    st.header("Venue Management")
    venue_name = st.text_input("Venue Name")
    venue_capacity = st.number_input("Capacity", min_value=1)
    venue_facilities = st.text_area("Facilities")
    venue_pricing = st.text_input("Pricing")
    venue_availability = st.checkbox("Available")

    # Display existing venues as a table with headings
    st.subheader("Existing Venues")
    existing_venues = conn.execute("SELECT name, capacity, facilities, pricing, availability FROM Venues").fetchall()
    if existing_venues:
        headings = ["Name", "Capacity", "Facilities", "Pricing", "Availability"]
        existing_venues_with_headings = [headings] + existing_venues
        st.table(existing_venues_with_headings)
    else:
        st.write("No existing venues.")

    if st.button("Add Venue"):
        venue_data = (venue_name, venue_capacity, venue_facilities, venue_pricing, venue_availability)
        insert_venue(conn, venue_data)
        st.success("Venue added successfully!")

    # Task Management
    st.header("Task Management")

    # Input fields for creating a new task
    st.subheader("Create New Task")
    task_name = st.text_input("Task Name")
    deadline = st.date_input("Deadline")
    responsibility = st.text_input("Responsibility")
    assigned_event = st.selectbox("Select Event", existing_events) if existing_events else None

    if st.button("Create Task") and assigned_event:
        event_id = assigned_event[0]  # Extract event ID from the selected event
        task_data = (event_id, task_name, deadline, responsibility, False)  # Mark task as incomplete initially
        insert_task(conn, task_data)
        st.success("Task created successfully!")

    # Display existing tasks
    st.subheader("Existing Tasks")
    existing_tasks = conn.execute("SELECT task_name, deadline, responsibility, completed FROM Tasks").fetchall()
    if existing_tasks:
        headings = ["Task Name", "Deadline", "Responsibility", "Status"]
        task_list = [headings] + [[task[0], task[1], task[2], "Completed" if task[3] else "Pending"] for task in existing_tasks]
        st.table(task_list)
    else:
        st.write("No existing tasks.")


if __name__ == "__main__":
    main()
