"""Fixed current-schema5 acquisition; never accepts frontend-selected code."""
import hashlib,importlib.util,json,os,stat,sys
from pathlib import Path
ROOT=next(p for p in Path(__file__).resolve().parents if p.name=='elm-shared-eof-receipt-fixture-v148')
class BackendFailure(RuntimeError):pass
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def verify_backend():
 pin=json.loads((ROOT/'backend-pin.json').read_text())
 report=Path(pin['buildReport'])
 if digest(report)!=pin['buildReportSHA256']:raise BackendFailure('Current schema5 build report changed')
 packet=json.loads(report.read_text())
 if packet.get('passed') is not True:raise BackendFailure('Current schema5 build not passed')
 if digest(Path(pin['componentManifest']))!=pin['componentManifestSHA256']:raise BackendFailure('Current schema5 frozen source changed')
 directory=Path(pin['adapterDirectory'])
 for name,row in pin['adapterFiles'].items():
  p=directory/name
  if p.is_symlink() or not p.is_file() or digest(p)!=row['sha256']:raise BackendFailure('Current schema5 captured adapter changed')
  if digest(Path(row['source']))!=row['sha256']:raise BackendFailure('Current schema5 owning source changed')
 for path,w in pin['tupleFiles'].items():
  if digest(Path(path))!=w:raise BackendFailure('Current owning host tuple changed')
 return directory/'daemon.py'
def load_backend():
 p=verify_backend();directory=p.parent
 for source in directory.glob('*.py'):
  existing=sys.modules.get(source.stem)
  if existing is not None and Path(getattr(existing,'__file__','')).resolve()!=source.resolve():raise BackendFailure('Foreign cached schema5 broker dependency')
 sys.path.insert(0,str(directory))
 spec=importlib.util.spec_from_file_location('current_schema5_receipt_backend',p)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 return module
