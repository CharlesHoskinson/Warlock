"""Boot actual candidate sources before original unittest discovery."""
import sys
from pathlib import Path
import unittest

B=Path(__file__).resolve().parent
sys.path.insert(0,str(B))
# The real collector imports its selected service before allocating anything.
# Legacy archival test imports must not choose service modules for this process.
import service_observer
import module_binding
initial=module_binding._observe('CPU-candidate-bootstrap-before-test-discovery')
if initial['errors']:raise RuntimeError('actual source bootstrap refused: '+repr(initial['errors']))
if len(initial['modules'])!=19 or any(not row['matched'] for row in initial['links']):raise RuntimeError('complete actual nineteen modules required')
suite=unittest.defaultTestLoader.discover(str(B),pattern='test*.py')
result=unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(not result.wasSuccessful() or bool(result.skipped))
