
import re
import getpass
import mysql.connector
from mysql.connector import Error


# Only these columns can be selected, filtered, or sorted.
ALLOWED_COLUMNS = {
    "student_id": "s.student_id",
    "student_name": "s.name",
    "course_id": "r.course_id",
    "spi": "r.spi",
}

OPERATORS = {"=", "!=", ">", ">=", "<", "<=", "LIKE", "BETWEEN"}


def build_query(columns, filters, order_column, direction, limit):
    """Validate user choices and build a parameterized SQL query."""
    if not columns:
        raise ValueError("Select at least one column.")

    if any(column not in ALLOWED_COLUMNS for column in columns):
        raise ValueError("Invalid selected column.")

    if order_column not in ALLOWED_COLUMNS:
        raise ValueError("Invalid sort column.")

    if direction not in {"ASC", "DESC"}:
        raise ValueError("Sort direction must be ASC or DESC.")

    if not 1 <= limit <= 1000:
        raise ValueError("Limit must be between 1 and 1000.")

    select_clause = ", ".join(ALLOWED_COLUMNS[c] for c in columns)

    conditions = []
    parameters = []

    for column, operator, value in filters:
        if column not in ALLOWED_COLUMNS:
            raise ValueError(f"Invalid filter column: {column}")

        operator = operator.upper()
        if operator not in OPERATORS:
            raise ValueError(f"Unsupported operator: {operator}")

        if operator == "BETWEEN":
            if not isinstance(value, tuple) or len(value) != 2:
                raise ValueError("BETWEEN requires two values.")
            conditions.append(f"{ALLOWED_COLUMNS[column]} BETWEEN %s AND %s")
            parameters.extend(value)
        else:
            if isinstance(value, tuple):
                raise ValueError("This operator requires one value.")
            conditions.append(f"{ALLOWED_COLUMNS[column]} {operator} %s")
            parameters.append(value)

    query = f"""
        SELECT {select_clause}
        FROM Student AS s
        JOIN CourseRegistration AS r
          ON s.student_id = r.student_id
    """

    if conditions:
        query += "\nWHERE " + " AND ".join(conditions)

    query += f"\nORDER BY {ALLOWED_COLUMNS[order_column]} {direction}"
    query += "\nLIMIT %s"
    parameters.append(limit)

    return query, parameters


def parse_filter(raw):
    """Parse a filter in column operator value format."""
    parts = raw.strip().split(maxsplit=2)

    if len(parts) != 3:
        raise ValueError(
            "Use: column operator value, e.g. spi >= 8.0"
        )

    column, operator, value = parts
    operator = operator.upper()

    if column not in ALLOWED_COLUMNS:
        raise ValueError("Unknown column.")

    if operator == "BETWEEN":
        bounds = value.split()
        if len(bounds) != 2:
            raise ValueError("For BETWEEN, enter two values.")
        return column, operator, (bounds[0], bounds[1])

    if operator == "LIKE":
        return column, operator, value

    if operator not in OPERATORS:
        raise ValueError("Unsupported operator.")

    if column == "spi":
        try:
            value = float(value)
        except ValueError:
            raise ValueError("SPI filter must be numeric.")
        if not 0 <= value <= 10:
            raise ValueError("SPI must be between 0 and 10.")
    elif column == "student_id":
        try:
            value = int(value)
        except ValueError:
            raise ValueError("Student ID must be an integer.")
    else:
        # Names and course IDs are strings.
        value = value.strip()

    return column, operator, value


def main():
    """Collect query options, validate, execute and display results."""
    connection = None

    print("Available columns:", ", ".join(ALLOWED_COLUMNS))
    print("Examples: spi >= 8.0, course_id = PY101, student_name LIKE A%")

    try:
        columns = [
            item.strip()
            for item in input("Columns (comma-separated): ").split(",")
        ]

        filter_count = int(input("Number of filters (0-10): "))
        if not 0 <= filter_count <= 10:
            raise ValueError("Filter count must be between 0 and 10.")

        filters = []
        for i in range(filter_count):
            raw = input(f"Filter {i + 1}: ")
            filters.append(parse_filter(raw))

        order_column = input("Order by column: ").strip()
        direction = input("Sort direction (ASC/DESC): ").strip().upper()
        limit = int(input("Limit (1-1000): "))

        query, parameters = build_query(
            columns, filters, order_column, direction, limit
        )

        print("\nGenerated SQL template:")
        print(query)
        print("Parameters:", parameters)

        host = input("MySQL host [localhost]: ").strip() or "localhost"
        user = input("MySQL username [root]: ").strip() or "root"
        password = getpass.getpass("MySQL password: ")

        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database="python_assignment2"
        )

        cursor = connection.cursor()
        cursor.execute(query, parameters)

        print("\nQuery results:")
        for row in cursor.fetchall():
            print(" | ".join(str(value) for value in row))

        cursor.close()

    except (ValueError, Error) as error:
        print("Error:", error)
    finally:
        if connection is not None and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    main()
