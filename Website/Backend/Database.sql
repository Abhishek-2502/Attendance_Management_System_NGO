-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS attendance_db;
USE attendance_db;

-- Create the Class table (for students)
CREATE TABLE IF NOT EXISTS Class (
    ClassID INT PRIMARY KEY AUTO_INCREMENT,
    ClassName VARCHAR(50) NOT NULL,
    Year VARCHAR(10) NOT NULL
);

-- Create the Student table
CREATE TABLE IF NOT EXISTS Student (
    StudentID INT PRIMARY KEY AUTO_INCREMENT,
    StudentName VARCHAR(100) NOT NULL,
    ClassID INT,                             -- Foreign key to Class table
    CONSTRAINT fk_class FOREIGN KEY (ClassID) REFERENCES Class(ClassID) ON DELETE SET NULL
);

-- Create the Teacher table
CREATE TABLE IF NOT EXISTS Teacher (
    TeacherID INT PRIMARY KEY AUTO_INCREMENT,
    TeacherName VARCHAR(100) NOT NULL
);

-- Create the DateDimension table (common for both students and teachers)
CREATE TABLE IF NOT EXISTS DateDimension (
    DateID INT PRIMARY KEY AUTO_INCREMENT,
    Date DATE NOT NULL,
    Year INT NOT NULL,
    Month INT NOT NULL,
    Day INT NOT NULL,
    MonthName VARCHAR(20),
    WeekdayName VARCHAR(20),
    UNIQUE(Date)
);

-- Create the StudentAttendance table (for student attendance, without OutTime)
CREATE TABLE IF NOT EXISTS StudentAttendance (
    AttendanceID INT PRIMARY KEY AUTO_INCREMENT,
    StudentID INT NOT NULL,                     -- Foreign key to Student table
    DateID INT NOT NULL,                        -- Foreign key to DateDimension table
    Status ENUM('Present', 'Absent') NOT NULL,  -- Attendance status
    InTime TIME,                                -- In time for the student
    CONSTRAINT fk_student FOREIGN KEY (StudentID) REFERENCES Student(StudentID) ON DELETE CASCADE,
    CONSTRAINT fk_date_student FOREIGN KEY (DateID) REFERENCES DateDimension(DateID) ON DELETE CASCADE
);

-- Create the TeacherAttendance table (for teacher attendance)
CREATE TABLE IF NOT EXISTS TeacherAttendance (
    AttendanceID INT PRIMARY KEY AUTO_INCREMENT,
    TeacherID INT NOT NULL,                     -- Foreign key to Teacher table
    DateID INT NOT NULL,                        -- Foreign key to DateDimension table
    Status ENUM('Present', 'Absent') NOT NULL,  -- Attendance status
    InTime TIME,                                -- In time for the teacher
    OutTime TIME,                               -- Out time for the teacher
    CONSTRAINT fk_teacher FOREIGN KEY (TeacherID) REFERENCES Teacher(TeacherID) ON DELETE CASCADE,
    CONSTRAINT fk_date_teacher FOREIGN KEY (DateID) REFERENCES DateDimension(DateID) ON DELETE CASCADE
);

-- Create an index on StudentID and DateID in StudentAttendance for faster querying
CREATE INDEX idx_student_attendance ON StudentAttendance (StudentID, DateID);

-- Create an index on TeacherID and DateID in TeacherAttendance for faster querying
CREATE INDEX idx_teacher_attendance ON TeacherAttendance (TeacherID, DateID);
