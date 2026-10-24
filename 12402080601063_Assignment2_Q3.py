
import csv
import getpass
import mysql.connector
from mysql.connector import Error


def create_tables(connection):
    """Create the required tables if they do not exist."""
    statements = [
        """
        CREATE TABLE IF NOT EXISTS Student (
            student_id INT PRIMARY KEY,
            name VARCHAR(100) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS CourseRegistration (
            student_id INT NOT NULL,
            course_id VARCHAR(20) NOT NULL,
            spi DECIMAL(4,2) NOT NULL,
            PRIMARY KEY (student_id, course_id),
            FOREIGN KEY (student_id)
                REFERENCES Student(student_id)
                ON DELETE CASCADE
        )
        """
    ]

    cursor = connection.cursor()
    try:
        for statement in statements:
            cursor.execute(statement)
        connection.commit()
    finally:
        cursor.close()


def import_students(connection, file_path):
    """Insert student records from CSV without replacing existing records."""
    query = """
        INSERT INTO Student (student_id, name)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE name = VALUES(name)
    """

    cursor = connection.cursor()
    try:
        with open(file_path, newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            if not {"student_id", "name"}.issubset(reader.fieldnames or []):
                raise ValueError("Q3_student.csv needs student_id and name columns.")

            for row in reader:
                student_id = int(row["student_id"])
                name = row["name"].strip()

                if student_id <= 0 or not name:
                    raise ValueError("Invalid student record.")

                cursor.execute(query, (student_id, name))

        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()


def import_registrations(connection, file_path):
    """Insert or update course registration records from CSV."""
    query = """
        INSERT INTO CourseRegistration (student_id, course_id, spi)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE spi = VALUES(spi)
    """

    cursor = connection.cursor()
    try:
        with open(file_path, newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            required = {"student_id", "course_id", "spi"}
            if not required.issubset(reader.fieldnames or []):
                raise ValueError(
                    "Q3_registration.csv needs student_id, course_id and spi columns."
                )

            for row in reader:
                student_id = int(row["student_id"])
                course_id = row["course_id"].strip()
                spi = float(row["spi"])

                if (
                    student_id <= 0
                    or not course_id
                    or not 0.0 <= spi <= 10.0
                ):
                    raise ValueError("Invalid course registration record.")

                cursor.execute(
                    query, (student_id, course_id, spi)
                )

        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()


def find_students(connection, course_id, threshold):
    """Return students in a course whose SPI exceeds the threshold."""
    query = """
        SELECT s.student_id, s.name, r.spi
        FROM Student AS s
        JOIN CourseRegistration AS r
          ON s.student_id = r.student_id
        WHERE r.course_id = %s AND r.spi > %s
        ORDER BY r.spi DESC, s.student_id ASC
    """

    cursor = connection.cursor()
    try:
        cursor.execute(query, (course_id, threshold))
        return cursor.fetchall()
    finally:
        cursor.close()


def main():
    """Connect, import data, and display course analytics."""
    connection = None

    try:
        host = input("MySQL host [localhost]: ").strip() or "localhost"
        user = input("MySQL username: ").strip()
        password = getpass.getpass("MySQL password: ")
        database = input("Database name [python_assignment2]: ").strip()
        database = database or "python_assignment2"

        course_id = input("Course ID: ").strip()
        threshold = float(input("SPI threshold: "))

        if not course_id or not 0.0 <= threshold <= 10.0:
            print("Invalid course ID or SPI threshold.")
            return

        # Connect to an existing database.
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        create_tables(connection)
        import_students(connection, "Q3_student.csv")
        import_registrations(connection, "Q3_registration.csv")

        results = find_students(connection, course_id, threshold)

        print("\nStudent ID | Name | SPI")
        print("-" * 35)

        if results:
            for student_id, name, spi in results:
                print(f"{student_id} | {name} | {float(spi):.2f}")
        else:
            print("No matching students found.")

    except (ValueError, OSError) as error:
        print(f"Input or file error: {error}")
    except Error as error:
        print(f"MySQL error: {error}")
    finally:
        if connection is not None and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    main()


