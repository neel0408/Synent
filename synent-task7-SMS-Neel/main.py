import json
import os

FILE_NAME = "students.json"

# Load data from file
def load_data():
    if not os.path.exists(FILE_NAME):
        return []
    with open(FILE_NAME, "r") as file:
        return json.load(file)

# Save data to file
def save_data(data):
    with open(FILE_NAME, "w") as file:
        json.dump(data, file, indent=4)

# Add student
def add_student():
    data = load_data()
    roll = input("Enter Roll No: ")
    name = input("Enter Name: ")
    marks = input("Enter Marks: ")

    student = {
        "roll": roll,
        "name": name,
        "marks": marks
    }

    data.append(student)
    save_data(data)
    print("Student Added Successfully!")

# View students
def view_students():
    data = load_data()
    if not data:
        print("No records found!")
        return

    for student in data:
        print(student)

# Update student
def update_student():
    data = load_data()
    roll = input("Enter Roll No to update: ")

    for student in data:
        if student["roll"] == roll:
            student["name"] = input("Enter new name: ")
            student["marks"] = input("Enter new marks: ")
            save_data(data)
            print("Student Updated!")
            return

    print("Student not found!")

# Delete student
def delete_student():
    data = load_data()
    roll = input("Enter Roll No to delete: ")

    new_data = [s for s in data if s["roll"] != roll]

    if len(new_data) == len(data):
        print("Student not found!")
    else:
        save_data(new_data)
        print("Student Deleted!")

# Menu
while True:
    print("\n--- Student Management System ---")
    print("1. Add Student")
    print("2. View Students")
    print("3. Update Student")
    print("4. Delete Student")
    print("5. Exit")

    choice = input("Enter choice: ")

    if choice == "1":
        add_student()
    elif choice == "2":
        view_students()
    elif choice == "3":
        update_student()
    elif choice == "4":
        delete_student()
    elif choice == "5":
        break
    else:
        print("Invalid choice!")