# =============================================================================
# FILE PURPOSE:
# Demonstrates portable, scoped suppression of blank prints using the
# `prevent_blank_prints()` context manager. Works transparently on both
# native NoBlankPrintPVM (zero overhead) and standard CPython (via fallback).
# Run via: `python examples/demo_context_manager.py` or `noblankprint-python examples/demo_context_manager.py`.
# =============================================================================

# =============================================================================
# DUAL RUN STEPS & EXPECTED OUTPUT:
#
# 🔴 1. RUNNING WITH REGULAR / UNMODIFIED PYTHON:
#    Command:
#      $ python3 -c "import sys; print(); print('')"
#
#    Behavior in Unmodified Python:
#      Outputs 2 invisible blank lines to stdout, corrupting output formatting
#      or polluting structured log parsers with zero warnings or errors.
#
#    Command using fallback wrapper:
#      $ python3 examples/demo_context_manager.py
#
#    Expected Output:
#      [Context Manager Demo] Running in EMULATED user-space mode
#      Outside context: Normal empty print passed silently:
#      Inside context: prevent_blank_prints active!
#      [BLOCKED] Caught expected blank print: NoBlankPrintPVM: blank output blocked
#      [BLOCKED] Caught expected empty string: NoBlankPrintPVM: blank output blocked
#
# 🟢 2. RUNNING WITH NOBLANKPRINT-PYTHON (UPGRADED RUNTIME):
#    Command:
#      $ noblankprint-python examples/demo_context_manager.py
#
#    Expected Output:
#      [Context Manager Demo] Running in NATIVE CPython PVM mode
#      Outside context: Normal empty print passed silently:
#      Inside context: prevent_blank_prints active!
#      [BLOCKED] Caught expected blank print: NoBlankPrintPVM: blank output blocked
#      [BLOCKED] Caught expected empty string: NoBlankPrintPVM: blank output blocked
#      Restored outside context: guard state is False
#      Timing: ~0.0012s (Native C-level instruction check)
# =============================================================================

import sys
import os
import time

# Ensure parent directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.noblankprint import (
    is_native_pvm_supported,
    prevent_blank_prints,
    is_blank_print_blocking_enabled,
)

def main():
    mode = "NATIVE CPython PVM" if is_native_pvm_supported() else "EMULATED user-space"
    print(f"[Context Manager Demo] Running in {mode} mode")

    print("Outside context: Normal empty print passed silently:")
    print()

    start = time.perf_counter()
    with prevent_blank_prints():
        print("Inside context: prevent_blank_prints active!")
        print(f"Current guard state: {is_blank_print_blocking_enabled()}")

        try:
            print()
        except ValueError as err:
            print(f"  [BLOCKED] Caught expected blank print: {err}")

        try:
            print("")
        except ValueError as err:
            print(f"  [BLOCKED] Caught expected empty string: {err}")

    elapsed = time.perf_counter() - start
    print(f"Restored outside context: guard state is {is_blank_print_blocking_enabled()}")
    print(f"Timing: {elapsed:.6f}s")

if __name__ == "__main__":
    main()
