from datetime import datetime
import uuid
import os
import csv
import streamlit as st

SESSION_LOG_FILE = "session_log.csv"


def track_session():
    """Log a session visit ONCE, then do nothing on subsequent reruns."""

    # If we already tracked this session, return immediately.
    # This is the key optimization — skip ALL work on reruns.
    if st.session_state.get("_session_tracked", False):
        return st.session_state.get("_session_count", 0)

    # First run for this browser session — generate ID and log it
    session_id = str(uuid.uuid4())
    now = datetime.now()

    # Log to CSV
    _log_to_csv(session_id, now)

    # Mark as tracked so we never do this again in this session
    st.session_state["_session_tracked"] = True
    st.session_state["_session_count"] = _get_logged_session_count()

    return st.session_state["_session_count"]


def _log_to_csv(session_id, timestamp):
    """Append a session entry to the CSV log."""
    file_exists = os.path.exists(SESSION_LOG_FILE)
    try:
        with open(SESSION_LOG_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["SessionID", "Timestamp"])
            writer.writerow([session_id, timestamp.strftime("%Y-%m-%d %H:%M:%S")])
    except Exception:
        pass  # Don't let logging failures break the app


def _get_logged_session_count():
    """Count total sessions from the CSV log."""
    try:
        # Use csv.reader instead of pd.read_csv — much faster for
        # just counting rows, and avoids importing pandas here.
        with open(SESSION_LOG_FILE, "r") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            return sum(1 for _ in reader)
    except FileNotFoundError:
        return 0

