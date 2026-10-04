"""Run byte-unchanged installed backend tests with only backend import redirected."""
import hashlib
import importlib.machinery
import os
from pathlib import Path
import runpy
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

BASE = Path(__file__).resolve().parents[1]
SUITE = Path('/home/hoskinson/.local/share/hypr-taskbar/test_backend.py')
ORIGIN = Path('/home/hoskinson/.local/bin/hypr-taskbar')
sys.path.insert(0, str(BASE))
loader = importlib.machinery.SourceFileLoader


def redirected(name, path, *args, **kwargs):
    return loader(name, str(BASE / 'hypr-taskbar') if path == str(ORIGIN) else path, *args, **kwargs)


if __name__ == '__main__':
    before = SUITE.read_bytes()
    print('Unchanged installed suite SHA256:', hashlib.sha256(before).hexdigest(), flush=True)
    print('Origin helper SHA256:', hashlib.sha256(ORIGIN.read_bytes()).hexdigest(), flush=True)
    print('Candidate helper SHA256:', hashlib.sha256((BASE / 'hypr-taskbar').read_bytes()).hexdigest(), flush=True)
    with tempfile.TemporaryDirectory() as cache, patch.dict(os.environ, {'XDG_CACHE_HOME': cache}):
        with patch('importlib.machinery.SourceFileLoader', redirected):
            namespace = runpy.run_path(str(SUITE), run_name='candidate_backend_suite')
        module = types.ModuleType('candidate_backend_suite')
        module.__dict__.update(namespace)
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(module))
    if SUITE.read_bytes() != before:
        raise RuntimeError('Installed suite changed while executing')
    sys.exit(0 if result.wasSuccessful() else 1)
