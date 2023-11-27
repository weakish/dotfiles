import importlib.util
import sys

def is_importable(name):
    return importlib.util.find_spec(name) is not None

def bool_to_exitcode(b):
    return 0 if b else 1

sys.exit(bool_to_exitcode(is_importable('doit')))
