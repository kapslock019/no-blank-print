# =============================================================================
# FILE PURPOSE:
# Automated source patcher modifying CPython to integrate NoBlankPrintPVM.
# Inserts native C variables, built-in print interception in builtin_print_impl,
# and exposes sys.get_block_empty_print() / sys.set_block_empty_print() in sysmodule.
# Run via: `python scripts/patch_cpython.py [optional/path/to/cpython-src]`
# =============================================================================

import os
import sys

# -----------------------------------------------------------------------------
# SIDE-BY-SIDE ORIGINAL VS. MODIFIED CODE COMPARISON REFERENCE
# -----------------------------------------------------------------------------
# 1. Include/sysmodule.h
# -----------------------------------------------------------------------------
# [ORIGINAL CODE]:
#   PyAPI_FUNC(PyObject *) PySys_GetXOptions(void);
#
#   #ifdef __cplusplus
#   }
#   #endif
#
# [MODIFIED CODE]:
#   PyAPI_FUNC(PyObject *) PySys_GetXOptions(void);
#   PyAPI_DATA(int) pvm_block_empty_print;
#
#   #ifdef __cplusplus
#   }
#   #endif
# -----------------------------------------------------------------------------
# 2. Python/bltinmodule.c
# -----------------------------------------------------------------------------
# [ORIGINAL CODE]:
#   /*[clinic end generated code: output=38d8def56c837bcc input=ff35cb3d59ee8115]*/
#   {
#       int i;
#
#       if (file == Py_None) {
#           file = PySys_GetAttr(&_Py_ID(stdout));
#
# [MODIFIED CODE]:
#   /*[clinic end generated code: output=38d8def56c837bcc input=ff35cb3d59ee8115]*/
#   {
#       int i;
#
#       if (pvm_block_empty_print) {
#           if (objects_length == 0 ||
#               (objects_length == 1 && PyUnicode_Check(objects[0]) && PyUnicode_GetLength(objects[0]) == 0)) {
#               PyErr_SetString(PyExc_ValueError, "NoBlankPrintPVM: blank output blocked");
#               return NULL;
#           }
#       }
#
#       if (file == Py_None) {
#           file = PySys_GetAttr(&_Py_ID(stdout));
# -----------------------------------------------------------------------------
# 3. Python/sysmodule.c
# -----------------------------------------------------------------------------
# [ORIGINAL CODE]:
#   static PyMethodDef sys_methods[] = {
#       /* Might as well keep this in alphabetic order */
#       SYS_ADDAUDITHOOK_METHODDEF
#
# [MODIFIED CODE]:
#   int pvm_block_empty_print = 0;
#
#   PyDoc_STRVAR(set_block_empty_print_doc,
#   "set_block_empty_print(enabled) -> None\n\n"
#   "Set whether empty print() calls should be blocked in NoBlankPrintPVM.");
#
#   static PyObject *
#   sys_set_block_empty_print(PyObject *module, PyObject *arg)
#   {
#       int enabled = PyObject_IsTrue(arg);
#       if (enabled < 0) {
#           return NULL;
#       }
#       pvm_block_empty_print = enabled;
#       Py_RETURN_NONE;
#   }
#
#   PyDoc_STRVAR(get_block_empty_print_doc,
#   "get_block_empty_print() -> bool\n\n"
#   "Get whether empty print() calls are blocked in NoBlankPrintPVM.");
#
#   static PyObject *
#   sys_get_block_empty_print(PyObject *module, PyObject *Py_UNUSED(ignored))
#   {
#       return PyBool_FromLong(pvm_block_empty_print);
#   }
#
#   static PyMethodDef sys_methods[] = {
#       {"set_block_empty_print", sys_set_block_empty_print, METH_O, set_block_empty_print_doc},
#       {"get_block_empty_print", sys_get_block_empty_print, METH_NOARGS, get_block_empty_print_doc},
#       /* Might as well keep this in alphabetic order */
#       SYS_ADDAUDITHOOK_METHODDEF
# -----------------------------------------------------------------------------


def apply_patch(cpython_dir: str) -> None:
    print(f"Applying NoBlankPrintPVM patches to CPython source in: {cpython_dir}")

    # 1. Patch Include/sysmodule.h
    sysmodule_h = os.path.join(cpython_dir, "Include", "sysmodule.h")
    if not os.path.exists(sysmodule_h):
        print(f"Warning: {sysmodule_h} not found, skipping.")
    else:
        with open(sysmodule_h, "r", encoding="utf-8") as f:
            content = f.read()
        target = "PyAPI_FUNC(PyObject *) PySys_GetXOptions(void);"
        if target in content and "pvm_block_empty_print" not in content:
            content = content.replace(target, target + "\nPyAPI_DATA(int) pvm_block_empty_print;")
            with open(sysmodule_h, "w", encoding="utf-8") as f:
                f.write(content)
            print("  [SUCCESS] Patched Include/sysmodule.h")
        elif "pvm_block_empty_print" in content:
            print("  [INFO] Include/sysmodule.h already patched.")
        else:
            print("  [WARNING] Target anchor not found in Include/sysmodule.h")

    # 2. Patch Python/bltinmodule.c
    bltinmodule_c = os.path.join(cpython_dir, "Python", "bltinmodule.c")
    if not os.path.exists(bltinmodule_c):
        print(f"Warning: {bltinmodule_c} not found, skipping.")
    else:
        with open(bltinmodule_c, "r", encoding="utf-8") as f:
            content = f.read()
        target = """/*[clinic end generated code: output=38d8def56c837bcc input=ff35cb3d59ee8115]*/
{
    int i;"""
        replacement = """/*[clinic end generated code: output=38d8def56c837bcc input=ff35cb3d59ee8115]*/
{
    int i;

    if (pvm_block_empty_print) {
        if (objects_length == 0 ||
            (objects_length == 1 && PyUnicode_Check(objects[0]) && PyUnicode_GetLength(objects[0]) == 0)) {
            PyErr_SetString(PyExc_ValueError, "NoBlankPrintPVM: blank output blocked");
            return NULL;
        }
    }"""
        if target in content and "pvm_block_empty_print" not in content:
            content = content.replace(target, replacement)
            with open(bltinmodule_c, "w", encoding="utf-8") as f:
                f.write(content)
            print("  [SUCCESS] Patched Python/bltinmodule.c")
        elif "pvm_block_empty_print" in content:
            print("  [INFO] Python/bltinmodule.c already patched.")
        else:
            print("  [WARNING] Target anchor not found in Python/bltinmodule.c")

    # 3. Patch Python/sysmodule.c
    sysmodule_c = os.path.join(cpython_dir, "Python", "sysmodule.c")
    if not os.path.exists(sysmodule_c):
        print(f"Warning: {sysmodule_c} not found, skipping.")
    else:
        with open(sysmodule_c, "r", encoding="utf-8") as f:
            content = f.read()

        funcs_target = "static PyMethodDef sys_methods[] = {"
        funcs_code = """int pvm_block_empty_print = 0;

PyDoc_STRVAR(set_block_empty_print_doc,
"set_block_empty_print(enabled) -> None\\n\\n"
"Set whether empty print() calls should be blocked in NoBlankPrintPVM.");

static PyObject *
sys_set_block_empty_print(PyObject *module, PyObject *arg)
{
    int enabled = PyObject_IsTrue(arg);
    if (enabled < 0) {
        return NULL;
    }
    pvm_block_empty_print = enabled;
    Py_RETURN_NONE;
}

PyDoc_STRVAR(get_block_empty_print_doc,
"get_block_empty_print() -> bool\\n\\n"
"Get whether empty print() calls are blocked in NoBlankPrintPVM.");

static PyObject *
sys_get_block_empty_print(PyObject *module, PyObject *Py_UNUSED(ignored))
{
    return PyBool_FromLong(pvm_block_empty_print);
}

static PyMethodDef sys_methods[] = {
    {"set_block_empty_print", sys_set_block_empty_print, METH_O, set_block_empty_print_doc},
    {"get_block_empty_print", sys_get_block_empty_print, METH_NOARGS, get_block_empty_print_doc},"""

        if funcs_target in content and "pvm_block_empty_print" not in content:
            content = content.replace(funcs_target, funcs_code)
            with open(sysmodule_c, "w", encoding="utf-8") as f:
                f.write(content)
            print("  [SUCCESS] Patched Python/sysmodule.c")
        elif "pvm_block_empty_print" in content:
            print("  [INFO] Python/sysmodule.c already patched.")
        else:
            print("  [WARNING] Target anchor not found in Python/sysmodule.c")


if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/pvm-noblankprint/cpython-src")
    apply_patch(target_dir)
