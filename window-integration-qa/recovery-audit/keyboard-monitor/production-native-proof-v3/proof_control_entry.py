"""Owned private fixture for actual frozen control.main; no product flags changed."""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
from private_runtime_guard import checked_runtime
checked_runtime()
sys.path.insert(0,str(HERE/'payload'))
import control
actual=control.Control
def private_factory(*args,**kwargs):
    if 'approved' in kwargs:raise RuntimeError('fixture approval injection duplicated')
    return actual(*args,approved=False,**kwargs)
control.Control=private_factory
control.main()
