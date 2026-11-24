# =============================================================================
# FILE PURPOSE:
# Core library module providing high-level Python bindings, context managers,
# and portable runtime fallback detection for the custom NoBlankPrint CPython PVM.
# Run or import this module to interact with runtime blank print blocking flags.
# =============================================================================

import builtins
import contextlib
import sys
from typing import Generator, Any

_ORIGINAL_PRINT = builtins.print
_EMULATED_BLOCKING = False


def is_native_pvm_supported() -> bool:
    """Return True if running on the modified NoBlankPrint CPython runtime."""
    return hasattr(sys, "set_block_empty_print") and hasattr(sys, "get_block_empty_print")


def enable_blank_print_blocking() -> None:
    """Enable blank print blocking at the native PVM level or fallback user-space hook."""
    global _EMULATED_BLOCKING
    if is_native_pvm_supported():
        sys.set_block_empty_print(True)
    else:
        _EMULATED_BLOCKING = True

        def _guarded_print(*args: Any, **kwargs: Any) -> None:
            if _EMULATED_BLOCKING:
                if len(args) == 0 or (len(args) == 1 and isinstance(args[0], str) and len(args[0]) == 0):
                    raise ValueError("NoBlankPrintPVM: blank output blocked")
            return _ORIGINAL_PRINT(*args, **kwargs)

        builtins.print = _guarded_print


def disable_blank_print_blocking() -> None:
    """Disable blank print blocking, restoring normal print behavior."""
    global _EMULATED_BLOCKING
    if is_native_pvm_supported():
        sys.set_block_empty_print(False)
    else:
        _EMULATED_BLOCKING = False
        builtins.print = _ORIGINAL_PRINT


def is_blank_print_blocking_enabled() -> bool:
    """Check whether blank print blocking is currently active."""
    if is_native_pvm_supported():
        return sys.get_block_empty_print()
    return _EMULATED_BLOCKING


@contextlib.contextmanager
def prevent_blank_prints() -> Generator[None, None, None]:
    """Context manager to scope blank print prevention to a critical execution block."""
    previous_state = is_blank_print_blocking_enabled()
    enable_blank_print_blocking()
    try:
        yield
    finally:
        if not previous_state:
            disable_blank_print_blocking()
