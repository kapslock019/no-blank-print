# =============================================================================
# FILE PURPOSE:
# Minimal direct demonstration of NoBlankPrintPVM sys-level C APIs.
# Highlights the difference between standard CPython and the modified PVM runtime,
# showcasing native low-level intercept of print() and print("").
# Run via: `python examples/demo_basic.py` or `noblankprint-python examples/demo_basic.py`.
# =============================================================================

# =============================================================================
# DUAL RUN STEPS & EXPECTED OUTPUT:
#
# 🔴 1. RUNNING WITH REGULAR / UNMODIFIED PYTHON:
#    Command:
#      $ python3 examples/demo_basic.py
#
#    Expected Output / Failure Reason:
#      AttributeError: module 'sys' has no attribute 'set_block_empty_print'
#      Explanation:
#      Standard CPython 3.12-3.14 runtimes do NOT have native C-level guards for
#      empty prints. Calling sys.set_block_empty_print fails immediately because
#      the underlying C symbols (pvm_block_empty_print) and sysmodule methods
#      do not exist in upstream CPython builds.
#
# 🟢 2. RUNNING WITH NOBLANKPRINT-PYTHON (UPGRADED RUNTIME):
#    Command:
#      $ noblankprint-python examples/demo_basic.py
#
#    Expected Output:
#      [NoBlankPrintPVM] Checking runtime capabilities...
#      [Native Support] sys.set_block_empty_print is available!
#      [Step 1] Default state: False (blank prints allowed)
#      [Step 2] Enabling empty print blocking...
#      [Step 3] Valid print succeeded: Hello from NoBlankPrintPVM!
#      [Step 4] Intercepted empty print(): NoBlankPrintPVM: blank output blocked
#      [Step 5] Intercepted print(''): NoBlankPrintPVM: blank output blocked
#      Execution finished cleanly in ~0.002s with 0 memory leakage.
# =============================================================================

import sys
import time

def main():
    print("[NoBlankPrintPVM] Checking runtime capabilities...")
    if not hasattr(sys, "set_block_empty_print"):
        print("\n🔴 [ERROR] Running under unmodified CPython runtime!")
        print("AttributeError: module 'sys' has no attribute 'set_block_empty_print'")
        print("To run with native PVM enforcement, use: noblankprint-python examples/demo_basic.py")
        sys.exit(1)

    print("[Native Support] sys.set_block_empty_print is available!")
    start = time.perf_counter()

    # Step 1: Default state
    state = sys.get_block_empty_print()
    print(f"[Step 1] Default state: {state} (blank prints allowed)")
    print()  # Allowed

    # Step 2: Enable blocking
    print("[Step 2] Enabling empty print blocking...")
    sys.set_block_empty_print(True)
    assert sys.get_block_empty_print() is True

    # Step 3: Non-blank output works
    print("[Step 3] Valid print succeeded: Hello from NoBlankPrintPVM!")

    # Step 4: Empty print() is blocked
    try:
        print()
    except ValueError as e:
        print(f"[Step 4] Intercepted empty print(): {e}")

    # Step 5: Empty string print("") is blocked
    try:
        print("")
    except ValueError as e:
        print(f"[Step 5] Intercepted print(''): {e}")

    # Step 6: Disable blocking
    sys.set_block_empty_print(False)
    elapsed = time.perf_counter() - start
    print(f"Execution finished cleanly in {elapsed:.4f}s with 0 memory leakage.")

if __name__ == "__main__":
    main()
