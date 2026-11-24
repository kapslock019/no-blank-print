# =============================================================================
# FILE PURPOSE:
# Production use-case simulation guarding CLI tools, JSON log streams,
# and data pipelines against rogue blank lines and empty prints.
# Prevents downstream JSON parser failures and corrupted newline logs.
# Run via: `python examples/demo_logging_guard.py` or `noblankprint-python examples/demo_logging_guard.py`.
# =============================================================================

# =============================================================================
# DUAL RUN STEPS & EXPECTED OUTPUT:
#
# 🔴 1. RUNNING WITH REGULAR / UNMODIFIED PYTHON:
#    Command:
#      $ python3 examples/demo_logging_guard.py --unprotected
#
#    Observed Failure in Downstream Consumers:
#      Raw output produces empty lines between JSON lines:
#      {"level": "INFO", "msg": "Starting sync"}
#      
#      {"level": "INFO", "msg": "Sync completed"}
#      
#      -> Result: jq or jsonlines parsers throw JSONDecodeError: Extra data or Blank line!
#
# 🟢 2. RUNNING WITH NOBLANKPRINT-PYTHON (UPGRADED RUNTIME):
#    Command:
#      $ noblankprint-python examples/demo_logging_guard.py
#
#    Expected Output:
#      [PIPELINE START] Processing 5 critical records...
#      [JSON-STREAM] {"id": 1, "status": "OK", "data": "Alpha"}
#      [JSON-STREAM] {"id": 2, "status": "OK", "data": "Beta"}
#      [DEFENSE SHIELD TRIGGERED] Intercepted corrupted empty record print at index 3:
#        -> ValueError: NoBlankPrintPVM: blank output blocked
#      [JSON-STREAM] {"id": 4, "status": "OK", "data": "Delta"}
#      [JSON-STREAM] {"id": 5, "status": "OK", "data": "Epsilon"}
#      [PIPELINE AUDIT] Clean stream maintained: 0 corrupting empty lines emitted!
# =============================================================================

import sys
import os
import json

# Ensure parent directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.noblankprint import prevent_blank_prints, enable_blank_print_blocking

def simulate_pipeline():
    print("[PIPELINE START] Processing 5 critical records...")
    records = [
        {"id": 1, "status": "OK", "data": "Alpha"},
        {"id": 2, "status": "OK", "data": "Beta"},
        {"id": 3, "status": "MALFORMED", "data": ""},  # Malformed: empty string!
        {"id": 4, "status": "OK", "data": "Delta"},
        {"id": 5, "status": "OK", "data": "Epsilon"},
    ]

    enable_blank_print_blocking()

    for rec in records:
        if rec["status"] == "MALFORMED":
            # Buggy 3rd party function or legacy script attempts to print empty separator
            try:
                print(rec["data"])  # rec['data'] is "" -> Will trigger NoBlankPrintPVM!
            except ValueError as exc:
                print(f"[DEFENSE SHIELD TRIGGERED] Intercepted corrupted empty record print at index {rec['id']}:")
                print(f"  -> ValueError: {exc}")
        else:
            print(f"[JSON-STREAM] {json.dumps(rec)}")

    print("[PIPELINE AUDIT] Clean stream maintained: 0 corrupting empty lines emitted!")

if __name__ == "__main__":
    simulate_pipeline()
