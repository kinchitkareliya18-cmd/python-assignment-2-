
import re
from collections import deque
from datetime import datetime
import os


# Expected log format:
# 2026-10-10 10:00:00 ERROR Database connection failed

LOG_PATTERN = re.compile(
    r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+"
    r"(INFO|WARNING|ERROR|CRITICAL)\s+(.*)$"
)

ERROR_LEVELS = {"ERROR", "CRITICAL"}


def parse_log_line(line):
    """Parse one log line; return timestamp, level, message or None."""
    match = LOG_PATTERN.match(line.strip())
    if not match:
        return None

    timestamp_text, level, message = match.groups()

    try:
        timestamp = datetime.strptime(
            timestamp_text, "%Y-%m-%d %H:%M:%S"
        )
    except ValueError:
        return None

    return timestamp, level, message


def detect_anomalies(file_path, window_seconds, threshold):
    """Find windows containing at least threshold error-level entries."""
    if window_seconds <= 0 or threshold <= 0:
        raise ValueError("Window and threshold must be positive.")

    events = deque()
    anomalies = []
    malformed = 0
    valid_logs = 0

    with open(file_path, "r", encoding="utf-8", errors="replace") as file:
        for line_number, line in enumerate(file, start=1):
            parsed = parse_log_line(line)

            if parsed is None:
                malformed += 1
                continue

            timestamp, level, message = parsed
            valid_logs += 1

            if level not in ERROR_LEVELS:
                continue

            events.append((timestamp, line_number, message))

            # Remove events outside the current window.
            while (
                events
                and (timestamp - events[0][0]).total_seconds()
                > window_seconds
            ):
                events.popleft()

            if len(events) >= threshold:
                anomalies.append({
                    "start": events[0][0],
                    "end": timestamp,
                    "count": len(events),
                    "line_numbers": [event[1] for event in events],
                })

    return anomalies, valid_logs, malformed


def main():
    print("Log Anomaly Detector")
    print("--------------------")

    file_path = input("Enter log file path: ").strip().strip('"')

    if not os.path.isfile(file_path):
        print("Error: Log file does not exist.")
        return

    try:
        window_seconds = int(input("Sliding window (seconds): "))
        threshold = int(input("Error threshold: "))

        anomalies, valid_logs, malformed = detect_anomalies(
            file_path, window_seconds, threshold
        )

        print("\nValid log lines:", valid_logs)
        print("Malformed lines:", malformed)
        print("\nAnomalies:")

        if not anomalies:
            print("No anomalies detected.")
        else:
            for index, anomaly in enumerate(anomalies, start=1):
                print(
                    f"{index}. {anomaly['start']} to {anomaly['end']} | "
                    f"errors={anomaly['count']} | "
                    f"lines={anomaly['line_numbers']}"
                )

    except ValueError as error:
        print("Input error:", error)
    except OSError as error:
        print("File error:", error)


if __name__ == "__main__":
    main()
