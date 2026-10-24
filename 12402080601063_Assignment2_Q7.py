
import json
import os
from collections import defaultdict
from decimal import Decimal, InvalidOperation


def read_jsonl(file_path):
    """Yield each valid JSON record one at a time."""
    with open(file_path, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                record = json.loads(line)
                if isinstance(record, dict):
                    yield line_number, record, None
                else:
                    yield line_number, None, "Record must be a JSON object."
            except json.JSONDecodeError:
                yield line_number, None, "Invalid JSON."


def transform_records(records):
    """Validate and transform records using a generator."""
    for line_number, record, error in records:
        if error:
            yield {
                "line": line_number,
                "status": "REJECTED",
                "reason": error
            }
            continue

        category = record.get("category")
        amount = record.get("amount")

        if not isinstance(category, str) or not category.strip():
            yield {
                "line": line_number,
                "status": "REJECTED",
                "reason": "Missing or invalid category."
            }
            continue

        if isinstance(amount, bool) or amount is None:
            yield {
                "line": line_number,
                "status": "REJECTED",
                "reason": "Missing or invalid amount."
            }
            continue

        try:
            value = Decimal(str(amount))
            if not value.is_finite() or value < 0:
                raise InvalidOperation
        except (InvalidOperation, ValueError):
            yield {
                "line": line_number,
                "status": "REJECTED",
                "reason": "Amount must be a non-negative number."
            }
            continue

        yield {
            "line": line_number,
            "status": "ACCEPTED",
            "category": category.strip().lower(),
            "amount": value
        }


def aggregate_records(transformed):
    """Aggregate accepted records by category."""
    totals = defaultdict(Decimal)
    counts = defaultdict(int)
    accepted = 0
    rejected = 0

    for record in transformed:
        if record["status"] == "REJECTED":
            rejected += 1
            print(
                f'Rejected line {record["line"]}: {record["reason"]}'
            )
            continue

        accepted += 1
        category = record["category"]
        totals[category] += record["amount"]
        counts[category] += 1

    print("\nETL Summary")
    print("-" * 45)
    print(f"Accepted records: {accepted}")
    print(f"Rejected records: {rejected}")
    print("\nCategory | Count | Total Amount")

    for category in sorted(totals):
        print(
            f"{category} | {counts[category]} | {totals[category]:.2f}"
        )


def main():
    print("Generator-Based JSON ETL Pipeline")
    file_path = input("Enter JSONL file path: ").strip().strip('"')

    if not os.path.isfile(file_path):
        print("Error: File does not exist.")
        return

    try:
        records = read_jsonl(file_path)
        transformed = transform_records(records)
        aggregate_records(transformed)
    except OSError as error:
        print("File error:", error)


if __name__ == "__main__":
    main()
