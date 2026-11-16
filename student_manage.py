import csv
import os
file_name="student.csv"
def create_file():
    if not os.path.exists(file_name):
        with open(file_name,"w",newline="") as file:
            writer=csv.writer(file)
            writer.writerow(["ID","Name","Age","Course","Marks"])
            
create_file()

def add_student():
    try:
        student_id=input("Enter your student id:")
        name=input("Enter student name:")
        age=int(input("Enter student age:"))
        course=input("Enter student course detail:")
        marks=int(input("Enter student marks:"))
        
        with open(file_name, "a", newline="") as file:

            writer = csv.writer(file)

            writer.writerow([
                student_id,
                name,
                age,
                course,
                marks
            ])
        print("Student addes successfully!")
    except ValueError:
        print("Attention :Invalid input!")
        
def view_students():

    try:
        with open(file_name, "r") as file:

            reader = csv.DictReader(file)

            print("\n----- STUDENT RECORDS -----")

            for student in reader:
                print(
                    "ID:", student["ID"],
                    "| Name:", student["Name"],
                    "| Age:", student["Age"],
                    "| Course:", student["Course"],
                    "| Marks:", student["Marks"]
                )

    except FileNotFoundError:
        print("Student file not found!")

def search_student():

    student_id = input("Enter Student ID to search: ")

    found = False

    with open(file_name, "r") as file:

        reader = csv.DictReader(file)

        for student in reader:

            if student["ID"] == student_id:

                print("\nStudent Found")
                print("ID:", student["ID"])
                print("Name:", student["Name"])
                print("Age:", student["Age"])
                print("Course:", student["Course"])
                print("Marks:", student["Marks"])

                found = True
                break

    if not found:
        print("Student not found!")

# --------------------------------
# UPDATE STUDENT
# --------------------------------

def update_student():

    student_id = input("Enter Student ID to update: ")

    students = []
    found = False

    with open(file_name, "r") as file:

        reader = csv.DictReader(file)

        for student in reader:

            if student["ID"] == student_id:

                print("Student found!")

                student["Name"] = input("Enter new name: ")
                student["Age"] = input("Enter new age: ")
                student["Course"] = input("Enter new course: ")
                student["Marks"] = input("Enter new marks: ")

                found = True

            students.append(student)

    if found:

        with open(file_name, "w", newline="") as file:

            fieldnames = [
                "ID",
                "Name",
                "Age",
                "Course",
                "Marks"
            ]

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames
            )

            writer.writeheader()
            writer.writerows(students)

        print("Student updated successfully!")

    else:

        print("Student not found!")


# --------------------------------
# DELETE STUDENT
# --------------------------------

def delete_student():

    student_id = input("Enter Student ID to delete: ")

    students = []
    found = False

    with open(file_name, "r") as file:

        reader = csv.DictReader(file)

        for student in reader:

            if student["ID"] == student_id:

                found = True
                continue

            students.append(student)

    if found:

        with open(file_name, "w", newline="") as file:

            fieldnames = [
                "ID",
                "Name",
                "Age",
                "Course",
                "Marks"
            ]

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames
            )

            writer.writeheader()
            writer.writerows(students)

        print("Student deleted successfully!")

    else:

        print("Student not found!")


# --------------------------------
# SORT STUDENTS
# --------------------------------

def sort_students():

    students = []

    with open(file_name, "r") as file:

        reader = csv.DictReader(file)

        for student in reader:

            students.append(student)

    print("\n1. Sort by Name")
    print("2. Sort by Marks")

    choice = input("Enter choice: ")

    if choice == "1":

        students.sort(
            key=lambda x: x["Name"].lower()
        )

    elif choice == "2":

        students.sort(
            key=lambda x: float(x["Marks"]),
            reverse=True
        )

    else:

        print("Invalid choice!")
        return

    print("\n----- SORTED STUDENTS -----")

    for student in students:

        print(
            student["ID"],
            student["Name"],
            student["Course"],
            student["Marks"]
        )


# --------------------------------
# REPORTS
# --------------------------------

def reports():

    students = []

    with open(file_name, "r") as file:

        reader = csv.DictReader(file)

        for student in reader:

            students.append(student)

    if len(students) == 0:

        print("No records available.")
        return

    marks = []

    for student in students:

        marks.append(
            float(student["Marks"])
        )

    topper = max(
        students,
        key=lambda x: float(x["Marks"])
    )

    average = sum(marks) / len(marks)

    print("\n----- STUDENT REPORT -----")

    print("Topper:")
    print("ID:", topper["ID"])
    print("Name:", topper["Name"])
    print("Marks:", topper["Marks"])

    print("Average Marks:", round(average, 2))

def admin_login():

    username = input("Enter Username: ")
    password = input("Enter Password: ")

    if username == "UAdmin" and password == "1234@ur":

        print("\nLogin successful!")
        return True

    else:

        print("\nInvalid username or password!")
        return False
# --------------------------------
# MAIN MENU
# --------------------------------

def main_menu():

    while True:

        print("\n==============================")
        print("   STUDENT MANAGEMENT SYSTEM")
        print("==============================")

        print("1. Add Student")
        print("2. View Students")
        print("3. Search Student")
        print("4. Update Student")
        print("5. Delete Student")
        print("6. Sort Students")
        print("7. Generate Reports")
        print("8. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            add_student()

        elif choice == "2":
            view_students()

        elif choice == "3":
            search_student()

        elif choice == "4":
            update_student()

        elif choice == "5":
            delete_student()

        elif choice == "6":
            sort_students()

        elif choice == "7":
            reports()

        elif choice == "8":

            print("Thank you!")
            break

        else:

            print("Invalid choice!")


# --------------------------------
# PROGRAM START
# --------------------------------

create_file()

if admin_login():

    main_menu()