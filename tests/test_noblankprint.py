# =============================================================================
# FILE PURPOSE:
# Automated unit and integration test suite for NoBlankPrintPVM.
# Validates default state, non-empty prints, zero-arg print() interception,
# empty string print("") blocking, toggle behavior, and context manager scoping.
# Run via: `python -m unittest tests/test_noblankprint.py` or `noblankprint-python -m unittest tests/test_noblankprint.py`.
# =============================================================================

import io
import os
import sys
import unittest

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.noblankprint import (
    is_native_pvm_supported,
    enable_blank_print_blocking,
    disable_blank_print_blocking,
    is_blank_print_blocking_enabled,
    prevent_blank_prints,
)


class TestNoBlankPrintPVM(unittest.TestCase):
    def setUp(self):
        # Ensure clean state before each test
        disable_blank_print_blocking()

    def tearDown(self):
        # Reset state after each test
        disable_blank_print_blocking()

    def test_default_state_inactive(self):
        """Verify that blank print blocking is disabled by default."""
        self.assertFalse(is_blank_print_blocking_enabled())
        if is_native_pvm_supported():
            self.assertFalse(sys.get_block_empty_print())

        # Empty prints must pass without raising exceptions
        buffer = io.StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = buffer
            print()
            print("")
        finally:
            sys.stdout = old_stdout
        self.assertEqual(buffer.getvalue(), "\n\n")

    def test_blocking_activation_and_deactivation(self):
        """Verify toggling blank print blocking on and off."""
        enable_blank_print_blocking()
        self.assertTrue(is_blank_print_blocking_enabled())
        if is_native_pvm_supported():
            self.assertTrue(sys.get_block_empty_print())

        disable_blank_print_blocking()
        self.assertFalse(is_blank_print_blocking_enabled())
        if is_native_pvm_supported():
            self.assertFalse(sys.get_block_empty_print())

    def test_allowed_prints_while_active(self):
        """Verify valid non-empty prints succeed normally while blocking is active."""
        enable_blank_print_blocking()
        buffer = io.StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = buffer
            print("Production payload 1")
            print("Key", "Value", 42)
            print(" ")  # Non-empty string (whitespace character)
        finally:
            sys.stdout = old_stdout

        output = buffer.getvalue()
        self.assertIn("Production payload 1\n", output)
        self.assertIn("Key Value 42\n", output)
        self.assertIn(" \n", output)

    def test_blocks_zero_argument_print(self):
        """Verify print() with 0 arguments raises ValueError with correct message."""
        enable_blank_print_blocking()
        with self.assertRaises(ValueError) as ctx:
            print()
        self.assertEqual(str(ctx.exception), "NoBlankPrintPVM: blank output blocked")

    def test_blocks_empty_string_print(self):
        """Verify print('') with empty string raises ValueError with correct message."""
        enable_blank_print_blocking()
        with self.assertRaises(ValueError) as ctx:
            print("")
        self.assertEqual(str(ctx.exception), "NoBlankPrintPVM: blank output blocked")

    def test_context_manager_scoping(self):
        """Verify context manager enables blocking only inside its block."""
        self.assertFalse(is_blank_print_blocking_enabled())
        with prevent_blank_prints():
            self.assertTrue(is_blank_print_blocking_enabled())
            with self.assertRaises(ValueError):
                print()
            with self.assertRaises(ValueError):
                print("")
        self.assertFalse(is_blank_print_blocking_enabled())

        # Should work again after context exit
        buffer = io.StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = buffer
            print()
        finally:
            sys.stdout = old_stdout
        self.assertEqual(buffer.getvalue(), "\n")


if __name__ == "__main__":
    unittest.main()
