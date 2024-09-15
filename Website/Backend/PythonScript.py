import pandas as pd
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime

# Establish the database connection
db_config = {
    'user': 'root',  
    'password': 'armaan',  
    'host': 'localhost',
    'database': 'attendance_db'
}

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Read the Excel files
    student_df = pd.read_excel(r"D:\service learning\student attendance.xlsx")
    teacher_df = pd.read_excel(r"D:\service learning\teacher attendance.xlsx")

    # Debug: Check if data is being read correctly
    print("Student DataFrame head:\n", student_df.head())
    print("\nTeacher DataFrame head:\n", teacher_df.head())

    # Inserting into Class Table
    class_data = student_df[['ClassName']].drop_duplicates()
    print("\nInserting into Class table:")
    for _, row in class_data.iterrows():
        print(f"Inserting: {row['ClassName']}")
        cursor.execute(
            "INSERT INTO Class (ClassName, Year) VALUES (%s, '2024') ON DUPLICATE KEY UPDATE ClassName=VALUES(ClassName);",
            (row['ClassName'],)
        )
    conn.commit()

    # Inserting into Student Table
    print("\nInserting into Student table:")
    for _, row in student_df.iterrows():
        if pd.isna(row['StudentID']) or pd.isna(row['ClassName']):
            print(f"Skipping student record due to missing data: {row}")
            continue
        print(f"Inserting Student: {row['StudentName']} in Class: {row['ClassName']}")
        cursor.execute(
            "INSERT INTO Student (StudentID, StudentName, ClassID) VALUES (%s, %s, (SELECT ClassID FROM Class WHERE ClassName=%s)) ON DUPLICATE KEY UPDATE StudentName=VALUES(StudentName);",
            (row['StudentID'], row['StudentName'], row['ClassName'])
        )
    conn.commit()

    # Inserting into Teacher Table
    print("\nInserting into Teacher table:")
    for _, row in teacher_df.iterrows():
        if pd.isna(row['TeacherID']):
            print(f"Skipping teacher record due to missing data: {row}")
            continue
        print(f"Inserting Teacher: {row['TeacherName']}")
        cursor.execute(
            "INSERT INTO Teacher (TeacherID, TeacherName) VALUES (%s, %s) ON DUPLICATE KEY UPDATE TeacherName=VALUES(TeacherName);",
            (row['TeacherID'], row['TeacherName'])
        )
    conn.commit()

    # Insert into DateDimension Table
    all_dates = pd.concat([student_df['Date'], teacher_df['Date']]).drop_duplicates().sort_values()
    print("\nInserting into DateDimension table:")
    for date in all_dates:
        date_obj = pd.to_datetime(date).date()
        print(f"Inserting Date: {date_obj}")
        cursor.execute(
            "INSERT INTO DateDimension (Date, Year, Month, Day, MonthName, WeekdayName) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE Date=VALUES(Date);",
            (date_obj, date_obj.year, date_obj.month, date_obj.day, date_obj.strftime('%B'), date_obj.strftime('%A'))
        )
    conn.commit()

    # Inserting into StudentAttendance Table
    print("\nInserting into StudentAttendance table:")
    for _, row in student_df.iterrows():
        if pd.isna(row['StudentID']) or pd.isna(row['Date']):
            print(f"Skipping student attendance record due to missing data: {row}")
            continue
        date_obj = pd.to_datetime(row['Date']).date()

        # Handle missing InTime for absent students
        in_time = row['InTime'] if row['Status'] == 'Present' and pd.notna(row['InTime']) else None

        # Get DateID for the current date
        cursor.execute("SELECT DateID FROM DateDimension WHERE Date=%s", (date_obj,))
        date_id = cursor.fetchone()[0]

        print(f"Inserting StudentAttendance for StudentID: {row['StudentID']} on Date: {date_obj}")
        cursor.execute(
            """
            INSERT INTO StudentAttendance (StudentID, DateID, Status, InTime)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE Status=VALUES(Status), InTime=VALUES(InTime);
            """,
            (row['StudentID'], date_id, row['Status'], in_time)
        )
    conn.commit()

    # Inserting into TeacherAttendance Table
    print("\nInserting into TeacherAttendance table:")
    for _, row in teacher_df.iterrows():
        if pd.isna(row['TeacherID']) or pd.isna(row['Date']):
            print(f"Skipping teacher attendance record due to missing data: {row}")
            continue
        date_obj = pd.to_datetime(row['Date']).date()

        # Handle missing InTime and OutTime for absent teachers
        in_time = row['InTime'] if row['Status'] == 'Present' and pd.notna(row['InTime']) else None
        out_time = row['OutTime'] if row['Status'] == 'Present' and pd.notna(row['OutTime']) else None

        # Get DateID for the current date
        cursor.execute("SELECT DateID FROM DateDimension WHERE Date=%s", (date_obj,))
        date_id = cursor.fetchone()[0]

        print(f"Inserting TeacherAttendance for TeacherID: {row['TeacherID']} on Date: {date_obj}")
        cursor.execute(
            """
            INSERT INTO TeacherAttendance (TeacherID, DateID, Status, InTime, OutTime)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE Status=VALUES(Status), InTime=VALUES(InTime), OutTime=VALUES(OutTime);
            """,
            (row['TeacherID'], date_id, row['Status'], in_time, out_time)
        )
    conn.commit()

    print("Data inserted/updated successfully!")

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
finally:
    cursor.close()
    conn.close()
