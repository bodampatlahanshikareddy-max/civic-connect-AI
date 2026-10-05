import streamlit as st
import sqlite3
import random
from datetime import datetime

# Database
conn = sqlite3.connect("civicconnect.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id TEXT,
    name TEXT,
    phone TEXT,
    category TEXT,
    location TEXT,
    description TEXT,
    status TEXT,
    date TEXT
)
""")
conn.commit()

st.set_page_config(page_title="CivicConnect", page_icon="🏙️")

st.title("🏙️ CivicConnect")
st.subheader("Smart Public Service Complaint System")

menu = st.sidebar.selectbox(
    "Menu",
    ["Register Complaint", "Track Complaint", "Admin Dashboard"]
)

# ---------------- REGISTER ----------------
if menu == "Register Complaint":

    st.header("📝 Report a Public Service Issue")

    name = st.text_input("Your Name")
    phone = st.text_input("Phone Number")

    category = st.selectbox(
        "Problem Category",
        [
            "Garbage",
            "Water Supply",
            "Street Light",
            "Road Damage",
            "Drainage",
            "Electricity",
            "Public Toilet",
            "Other"
        ]
    )

    location = st.text_input("Problem Location")
    description = st.text_area("Describe the Problem")

    if st.button("Submit Complaint"):

        if name and phone and location and description:

            cid = "CC" + str(random.randint(10000, 99999))
            date = datetime.now().strftime("%Y-%m-%d %H:%M")

            cur.execute("""
            INSERT INTO complaints
            (complaint_id,name,phone,category,location,
             description,status,date)
            VALUES (?,?,?,?,?,?,?,?)
            """,
            (cid, name, phone, category, location,
             description, "Pending", date))

            conn.commit()

            st.success("Complaint submitted successfully!")
            st.info(f"Your Complaint ID is: **{cid}**")

        else:
            st.warning("Please fill all fields.")

# ---------------- TRACK ----------------
elif menu == "Track Complaint":

    st.header("🔍 Track Your Complaint")

    cid = st.text_input("Enter Complaint ID")

    if st.button("Track"):

        cur.execute(
            "SELECT * FROM complaints WHERE complaint_id=?",
            (cid,)
        )

        data = cur.fetchone()

        if data:
            st.success(f"Status: {data[7]}")

            st.write("**Category:**", data[4])
            st.write("**Location:**", data[5])
            st.write("**Description:**", data[6])
            st.write("**Submitted On:**", data[8])

        else:
            st.error("Complaint not found.")

# ---------------- ADMIN ----------------
elif menu == "Admin Dashboard":

    st.header("👨‍💼 Admin Dashboard")

    password = st.text_input(
        "Admin Password",
        type="password"
    )

    if password == "admin123":

        cur.execute("SELECT * FROM complaints")
        complaints = cur.fetchall()

        st.metric("Total Complaints", len(complaints))

        for c in complaints:

            with st.expander(
                f"{c[1]} - {c[4]} - {c[7]}"
            ):

                st.write("**Citizen:**", c[2])
                st.write("**Phone:**", c[3])
                st.write("**Location:**", c[5])
                st.write("**Problem:**", c[6])

                new_status = st.selectbox(
                    "Update Status",
                    ["Pending", "In Progress", "Resolved"],
                    index=[
                        "Pending",
                        "In Progress",
                        "Resolved"
                    ].index(c[7]),
                    key=c[0]
                )

                if st.button(
                    "Update",
                    key="update" + str(c[0])
                ):

                    cur.execute(
                        "UPDATE complaints SET status=? WHERE id=?",
                        (new_status, c[0])
                    )

                    conn.commit()

                    st.success("Status updated!")
                    st.rerun()

    elif password:
        st.error("Incorrect password.")