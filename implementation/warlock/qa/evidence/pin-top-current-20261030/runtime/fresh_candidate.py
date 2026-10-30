"""Current native receipt facade; preserves historical runtime ownership depth."""
RUNTIME_SHA='4532b20394a62db96d70923b4efcff10bee0b07c5263efdf6b189d0da1b3a69e'
import hashlib,importlib.util
from pathlib import Path
PATH=Path(__file__).resolve().parent/'runtime_candidate.py'
body=PATH.read_bytes()
if hashlib.sha256(body).hexdigest()!=RUNTIME_SHA:raise RuntimeError('Runtime adapter changed')
spec=importlib.util.spec_from_loader('current_delivery_runtime',loader=None)
original=importlib.util.module_from_spec(spec);original.__file__=str(PATH)
exec(compile(body,str(PATH),'exec'),original.__dict__)
def verify_tuple():return original.verify_tuple()
PrivateHyprSession=original.PrivateHyprSession
def __getattr__(name):return getattr(original,name)
