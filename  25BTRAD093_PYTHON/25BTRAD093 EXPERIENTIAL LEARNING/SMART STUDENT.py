
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date

# Database connection
conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    usn TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usn TEXT,
    attendance_date TEXT,
    status TEXT,
    UNIQUE(usn, attendance_date),
    FOREIGN KEY(usn) REFERENCES students(usn)
)
""")

conn.commit()

# Main window
root = tk.Tk()
root.title("Student Attendance Management System")
root.geometry("750x550")

tk.Label(
    root,
    text="STUDENT ATTENDANCE MANAGEMENT SYSTEM",
    font=("Arial", 16, "bold")
).pack(pady=15)

# Input fields
frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="USN:").grid(row=0, column=0, padx=5, pady=5)
usn_entry = tk.Entry(frame)
usn_entry.grid(row=0, column=1, padx=5)

tk.Label(frame, text="Name:").grid(row=1, column=0, padx=5, pady=5)
name_entry = tk.Entry(frame)
name_entry.grid(row=1, column=1, padx=5)

tk.Label(frame, text="Department:").grid(row=2, column=0, padx=5, pady=5)
dept_entry = tk.Entry(frame)
dept_entry.grid(row=2, column=1, padx=5)

# Add student
def add_student():
    usn = usn_entry.get().strip()
    name = name_entry.get().strip()
    dept = dept_entry.get().strip()

    if not usn or not name or not dept:
        messagebox.showwarning("Warning", "Fill all fields")
        return

    try:
        cursor.execute(
            "INSERT INTO students VALUES (?, ?, ?)",
            (usn, name, dept)
        )
        conn.commit()
        messagebox.showinfo("Success", "Student added successfully")

        usn_entry.delete(0, tk.END)
        name_entry.delete(0, tk.END)
        dept_entry.delete(0, tk.END)

        view_students()

    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "USN already exists")

# View students
def view_students():
    for item in tree.get_children():
        tree.delete(item)

    cursor.execute("SELECT * FROM students")

    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)

# Mark attendance
def mark_attendance(status):
    selected = tree.selection()

    if not selected:
        messagebox.showwarning("Warning", "Select a student")
        return

    values = tree.item(selected[0], "values")
    usn = values[0]
    today = date.today().isoformat()

    cursor.execute("""
    INSERT INTO attendance
    (usn, attendance_date, status)
    VALUES (?, ?, ?)
    ON CONFLICT(usn, attendance_date)
    DO UPDATE SET status = excluded.status
    """, (usn, today, status))

    conn.commit()
    messagebox.showinfo("Success", "Attendance marked: " + status)

# Search student
def search_student():
    search = usn_entry.get().strip()

    if not search:
        messagebox.showwarning("Warning", "Enter a USN to search")
        return

    cursor.execute(
        "SELECT * FROM students WHERE usn = ?",
        (search,)
    )

    result = cursor.fetchone()

    if result:
        messagebox.showinfo(
            "Student Found",
            f"USN: {result[0]}\nName: {result[1]}\nDepartment: {result[2]}"
        )
    else:
        messagebox.showerror("Error", "Student not found")

# Attendance percentage
def attendance_percentage():
    selected = tree.selection()

    if not selected:
        messagebox.showwarning("Warning", "Select a student")
        return

    usn = tree.item(selected[0], "values")[0]

    cursor.execute("""
    SELECT COUNT(*),
    SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END)
    FROM attendance WHERE usn = ?
    """, (usn,))

    total, present = cursor.fetchone()

    if total == 0:
        percentage = 0
    else:
        percentage = (present / total) * 100

    messagebox.showinfo(
        "Attendance Percentage",
        f"Attendance: {percentage:.2f}%\n"
        f"Present: {present or 0}\n"
        f"Total marked days: {total}"
    )

# Buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(button_frame, text="Add Student",
          command=add_student).grid(row=0, column=0, padx=5)

tk.Button(button_frame, text="View Students",
          command=view_students).grid(row=0, column=1, padx=5)

tk.Button(button_frame, text="Search USN",
          command=search_student).grid(row=0, column=2, padx=5)

# Student table
tree = ttk.Treeview(
    root,
    columns=("USN", "Name", "Department"),
    show="headings"
)

tree.heading("USN", text="USN")
tree.heading("Name", text="Student Name")
tree.heading("Department", text="Department")

tree.pack(fill="both", expand=True, padx=15, pady=10)

# Attendance buttons
tk.Button(
    root,
    text="Mark Present",
    command=lambda: mark_attendance("Present"),
    bg="lightgreen"
).pack(side="left", padx=25, pady=10)

tk.Button(
    root,
    text="Mark Absent",
    command=lambda: mark_attendance("Absent"),
    bg="lightcoral"
).pack(side="left", padx=10, pady=10)

tk.Button(
    root,
    text="Attendance Percentage",
    command=attendance_percentage
).pack(side="left", padx=10, pady=10)

# Initial display
view_students()

root.mainloop()

conn.close()
