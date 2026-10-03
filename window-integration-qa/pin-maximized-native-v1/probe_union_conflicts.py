"""Actual temporary kernel objects expose inter-row declaration conflicts."""
import importlib.util,json,os,tempfile
from pathlib import Path
B=Path(__file__).resolve().parent

def load(path):
 s=importlib.util.spec_from_file_location('union_probe',path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def probe(m,kind):
 with tempfile.TemporaryDirectory()as tmp:
  root=Path(tmp)/'packet';root.mkdir();other=Path(tmp)/'external';other.mkdir();one=other/'one';two=other/'two';one.write_text('one');two.write_text('two');one.chmod(0o600);two.chmod(0o600);alias=other/'alias';alias.symlink_to('one')
  def rows():
   if kind=='literal':
    yield dict(inputs={},inputModes={},symlinks={str(alias):'one'})
    alias.unlink();alias.symlink_to('two')
    yield dict(inputs={},inputModes={},symlinks={str(alias):'two'})
   elif kind=='alias':
    yield dict(inputs={str(alias):m.digest(alias)},inputModes={str(alias):0o600},symlinks={str(alias):'one'})
    one.write_text('changed')
    yield dict(inputs={str(alias):m.digest(alias)},inputModes={str(alias):0o600},symlinks={str(alias):'one'})
   elif kind=='mode':
    yield dict(inputs={str(alias):m.digest(alias)},inputModes={str(alias):0o600},symlinks={str(alias):'one'})
    one.chmod(0o644)
    yield dict(inputs={str(alias):m.digest(alias)},inputModes={str(alias):0o644},symlinks={str(alias):'one'})
   else:
    other.chmod(0o700)
    yield dict(inputs={},inputModes={},symlinks={},directoryModes={str(other):0o700})
    other.chmod(0o755)
    yield dict(inputs={},inputModes={},symlinks={},directoryModes={str(other):0o755})
  try:
   m.union(root,rows());return dict(kind=kind,accepted=True)
  except RuntimeError as e:return dict(kind=kind,accepted=False,error=str(e))
if __name__=='__main__':
 old=load(B/'retained-first-union-conflict-gap/closure_union.py');new=load(B/'proposed/closure_union.py')
 evidence=dict(nativeExecuted=False,temporaryKernelObjectsOnly=True,preimage=[probe(old,k)for k in ['literal','alias','mode','directory']],corrected=[probe(new,k)for k in ['literal','alias','mode','directory']])
 assert all(r['accepted']for r in evidence['preimage']);assert all(not r['accepted']for r in evidence['corrected'])
 (B/'retained-first-union-conflict-gap/counterexample-and-correction.json').write_text(json.dumps(evidence,indent=2)+'\n');print(json.dumps(evidence,indent=2))
