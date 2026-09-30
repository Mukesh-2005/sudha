"""Creates voting.db from schema.sql and seeds sample students/candidates.

Run this once before starting the app: python init_db.py
"""
import sqlite3

DB_PATH = "voting.db"

SAMPLE_STUDENTS = [
    # STUDENT_ID, STUDENT_NAME, DEPARTMENT, YEAR, PASSWORD
    ("S1001", "Arun Kumar", "CSE", "3rd Year", "pass1001"),
    ("S1002", "Divya Sri", "ECE", "2nd Year", "pass1002"),
    ("S1003", "Karthik R", "IT", "4th Year", "pass1003"),
    ("S1004", "Meena Priya", "CSE", "1st Year", "pass1004"),
    ("S1005", "Suresh Babu", "MECH", "3rd Year", "pass1005"),
]

SAMPLE_CANDIDATES = [
    # CANDIDATE_NAME, PARTY
    ("Aarthi Raj", "Unity Party"),
    ("Bala Murugan", "Progress Front"),
    ("Chitra Devi", "Student Voice"),
]


def main():
    conn = sqlite3.connect(DB_PATH)
    with open("schema.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    conn.executemany(
        "INSERT INTO students (STUDENT_ID, STUDENT_NAME, DEPARTMENT, YEAR, PASSWORD) "
        "VALUES (?, ?, ?, ?, ?)",
        SAMPLE_STUDENTS,
    )
    conn.executemany(
        "INSERT INTO candidates (CANDIDATE_NAME, PARTY) VALUES (?, ?)",
        SAMPLE_CANDIDATES,
    )
    conn.commit()
    conn.close()
    print(f"Initialized {DB_PATH} with {len(SAMPLE_STUDENTS)} students and "
          f"{len(SAMPLE_CANDIDATES)} candidates.")


if __name__ == "__main__":
    main()
