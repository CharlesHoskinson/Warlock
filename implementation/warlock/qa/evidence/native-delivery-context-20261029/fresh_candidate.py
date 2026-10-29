"""Current native receipt facade; preserves historical runtime ownership depth."""
RUNTIME_SHA='a082002671a7d9eda128af1d4230dabe1dd98dc94ad792aa939720b183b5b8ae'
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
