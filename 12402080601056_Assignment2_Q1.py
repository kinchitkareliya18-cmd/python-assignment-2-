
import re
import os
import sys
from collections import defaultdict


# Match an email with a permitted top-level domain.
EMAIL_PATTERN = re.compile(
    r"(?<![A-Za-z0-9._%+-])"
    r"([A-Za-z0-9_%+-]+(?:\.[A-Za-z0-9_%+-]+)*"
    r"@[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)*"
    r"\.(?:com|edu|org))"
    r"(?![A-Za-z0-9_-])",
    re.IGNORECASE
)

ALLOWED_DOMAINS = {".com", ".edu", ".org"}


def extract_emails(file_path):
    """Read a text file line by line and collect unique valid emails."""
    unique_emails = set()

    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            for match in EMAIL_PATTERN.finditer(line):
                email = match.group(1).lower()

                # Basic validation of the local part and domain.
                local_part, domain = email.rsplit("@", 1)

                if (
                    not local_part
                    or len(local_part) > 64
                    or len(email) > 254
                    or ".." in local_part
                    or domain.startswith(".")
                    or domain.endswith(".")
                ):
                    continue

                if not any(domain.endswith(tld) for tld in ALLOWED_DOMAINS):
                    continue

                unique_emails.add(email)

    return unique_emails


def build_domain_statistics(emails):
    """Group unique emails and calculate statistics for each domain."""
    domain_emails = defaultdict(list)

    for email in emails:
        domain = email.rsplit("@", 1)[1]
        domain_emails[domain].append(email)

    statistics = []

    for domain in sorted(domain_emails):
        users = sorted(domain_emails[domain])

        statistics.append(
            (domain, len(users), users[0])
        )

    return statistics


def main():
    """Validate input, process the file, and print domain statistics."""
    if len(sys.argv) > 2:
        print("Usage: python 12402080601018_Assignment2_Q1.py [file_path]")
        return

    if len(sys.argv) == 2:
        file_path = sys.argv[1]
    else:
        file_path = input("Enter the path of the text file: ").strip().strip('"')

    if not os.path.isfile(file_path):
        print("Error: File does not exist.")
        return

    try:
        emails = extract_emails(file_path)
        statistics = build_domain_statistics(emails)

        print("\nDomain | Unique Users | Smallest Email")
        print("-" * 65)

        if not statistics:
            print("No valid email addresses found.")
            return

        for domain, count, smallest_email in statistics:
            print(f"{domain} | {count} | {smallest_email}")

        print(f"\nTotal unique valid emails: {len(emails)}")

    except (OSError, UnicodeError) as error:
        print(f"Error reading file: {error}")


if __name__ == "__main__":
    main()
