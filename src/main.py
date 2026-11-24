# =============================================================================
# FILE PURPOSE:
# Central codebase entrypoint and quick-start demonstration for NoBlankPrintPVM.
# Displays the architecture map of the entire repository and executes a live
# demonstration of native CPython PVM empty-print suppression and exception raising.
# Run via: `python src/main.py` or `noblankprint-python src/main.py`.
# =============================================================================

# =============================================================================
# CENTRAL CODEBASE DIRECTORY MAP:
#
# NoBlankPrintPVM/
# ├── .gitignore                  - Git exclusions (caches, build artifacts, environments)
# ├── README.md                   - Comprehensive publication documentation & benchmarks
# ├── COMPARISON.md               - Side-by-side original vs modified CPython C code breakdown
# ├── src/
# │   ├── __init__.py             - Package entrypoint and public interface exports
# │   ├── noblankprint.py         - Core wrapper module, context managers & fallback logic
# │   └── main.py                 - Central codebase map & runnable quickstart demo (this file)
# ├── scripts/
# │   ├── patch_cpython.py        - Automated Python script applying C-level patches to CPython
# │   ├── build.sh                - Bash build pipeline script (configure, make, packaging)
# │   └── install.sh              - System installer deploying SDK to /opt and /usr/local/bin
# ├── tests/
# │   └── test_noblankprint.py    - Comprehensive automated test suite (native & emulation)
# └── examples/
#     ├── demo_basic.py           - Minimal direct sys.set_block_empty_print API showcase
#     ├── demo_context_manager.py - Scoped suppression demo using context managers
#     └── demo_logging_guard.py   - Production simulation guarding CLI and pipeline outputs
# =============================================================================

import os
import sys

# Ensure repository root is on sys.path when invoked directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.noblankprint import (
    is_native_pvm_supported,
    enable_blank_print_blocking,
    disable_blank_print_blocking,
    is_blank_print_blocking_enabled,
    prevent_blank_prints,
)


def run_quickstart_demo() -> None:
    print("=" * 70)
    print("NoBlankPrintPVM: Central Quick-Start Demonstration")
    print(f"Python Runtime: {sys.version}")
    native = is_native_pvm_supported()
    print(f"Native NoBlankPrint CPython PVM Detected: {native}")
    print("=" * 70)

    print("\n[Step 1] Baseline execution: normal prints work unrestricted.")
    print("  -> Current blocking status:", is_blank_print_blocking_enabled())
    print("  -> Executing: print('Valid message: Hello NoBlankPrintPVM!')")
    print("  Valid message: Hello NoBlankPrintPVM!")
    print("  -> Executing empty print() while inactive (allowed):")
    print()

    print("[Step 2] Activating NoBlankPrint enforcement...")
    enable_blank_print_blocking()
    print("  -> Current blocking status:", is_blank_print_blocking_enabled())
    print("  -> Printing normal non-empty text (should succeed):")
    print("  [SUCCESS] Payload delivered successfully.")

    print("\n[Step 3] Attempting forbidden empty print() calls:")
    try:
        print("  Executing: print()")
        print()
    except ValueError as err:
        print(f"  [INTERCEPTED] Caught expected ValueError: {err}")

    try:
        print("  Executing: print('')")
        print("")
    except ValueError as err:
        print(f"  [INTERCEPTED] Caught expected ValueError: {err}")

    print("\n[Step 4] Using scoped context manager prevent_blank_prints():")
    disable_blank_print_blocking()
    print("  -> Guard disabled outside context manager.")
    with prevent_blank_prints():
        print("  -> Inside context block (blocking active):")
        try:
            print()
        except ValueError as err:
            print(f"  [INTERCEPTED IN CONTEXT] Caught expected ValueError: {err}")

    print("  -> Exited context block. Guard is restored to:", is_blank_print_blocking_enabled())
    print("\n" + "=" * 70)
    print("DEMO COMPLETE: All NoBlankPrintPVM capabilities validated!")
    print("=" * 70)


if __name__ == "__main__":
    run_quickstart_demo()
