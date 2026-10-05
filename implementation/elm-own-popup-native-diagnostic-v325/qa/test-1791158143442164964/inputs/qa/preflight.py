"""Source-closed inert preparation; actual runtime guard326 required separately."""
import hashlib,json,pathlib,sys,importlib.util,os
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def packet(path,expected=None):
 raw=pathlib.Path(path).read_bytes()
 if len(raw)>32*1024*1024:raise ValueError('metadata byte bound')
 if expected is not None and hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('metadata SHA mismatch')
 return json.loads(raw)
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m

def verify():
 sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
 require_qa_scope()
 pins=json.loads((ROOT/'pins.json').read_text());files={}
 for name,digest in pins.items():
  base=REPO/'implementation'/name;p=base/'component-manifest.json';o=packet(p,digest);files[str(p)]=digest;assert o['sourceHeld'] is True
  rows=o['files']
  if isinstance(rows,list):rows={r['path']:r for r in rows}
  for rel,row in rows.items():
   p=base/rel
   if type(row) is str:row={'sha256':row}
   if 'symlink' in row:assert p.is_symlink() and os.readlink(p)==row['symlink'];continue
   assert sha(p)==row['sha256'];files[str(p)]=row['sha256']
 host=load('diagnostic_owning321_host',ROOT/'runtime/candidate_host.py');host.verify_inputs();host.aq_tuple()
 core=json.loads((ROOT/'runtime/native-build-report.json').read_text());upstream=REPO/'implementation/elm-own-popup-native-tuple-plan-v321/runtime/native-build-report.json';assert (ROOT/'runtime/native-build-report.json').read_bytes()==upstream.read_bytes()
 for p,d in [(core['binary'],core['sha256']),(core['plugin']['path'],core['plugin']['sha256'])]:assert sha(p)==d;files[p]=d
 observer_manifest=json.loads((REPO/'implementation/elm-own-popup-native-grab-join-v315/component-manifest.json').read_text());observer=json.loads(pathlib.Path(observer_manifest['buildReport']).read_text());assert observer['passed'] and observer['core']['path']==core['binary'] and observer['core']['sha256']==core['sha256'];assert sha(observer['binary'])==observer['binarySHA256']
 a=REPO/'implementation/elm-own-popup-host-surface-stamp-v310';m=packet(a/'component-manifest.json',pins[a.name]);hb=pathlib.Path(m['buildReport']);h=packet(hb,m['buildReportSHA256']);host_binary=hb.parent/'host';assert h['passed'] and sha(host_binary)==h['binarySHA256']
 for section in ('dependencies','linkedLibraries','tools'):
  for path,digest in h[section].items():
   assert sha(path)==digest;files[path]=digest
 a=REPO/'implementation/elm-recovery-context-feedback-v592';m=packet(a/'component-manifest.json',pins[a.name]);gb=pathlib.Path(m['buildReport']);g=packet(gb,m['buildReportSHA256']);assert g['passed']
 for rel,d in g['artifacts'].items():assert sha(gb.parent/rel)==d;files[str(gb.parent/rel)]=d
 # Only stamped host differs from592; protocol helpers/C host inheritance closed by310 origin.
 fixture=json.loads((REPO/'implementation/elm-gtk-popup-landmark-fixture-v272/client-build-report.json').read_text());assert fixture['passed'] and sha(fixture['artifact']['path'])==fixture['artifact']['sha256']
 for p in [hb,host_binary,gb,pathlib.Path(fixture['artifact']['path'])]:files[str(p)]=sha(p)
 return host,core,observer,fixture,host_binary,gb.parent,files

def checked_guard():
 """Import the exact once-read pinned source, before any GUI allocation."""
 pin=packet(ROOT/'runtime-guard-pin.json');assert set(pin)=={'manifest','sha256'}
 expected=REPO/'implementation/elm-own-popup-runtime-closure-guard-v330/component-manifest.json'
 assert pathlib.Path(pin['manifest'])==expected and pin['sha256']=='66527cb94aa2fc22e7b2bfc29af1e868a90a42668a2008af33adcc204583960f'
 manifest=packet(expected,pin['sha256']);assert manifest['sourceHeld'] is True and manifest['evidenceIntegrityPassed'] is True
 files={str(expected):pin['sha256']};source=None
 for rel,row in manifest['files'].items():
  assert not pathlib.Path(rel).is_absolute() and '..' not in pathlib.Path(rel).parts
  path=expected.parent/rel;assert path.is_file() and not path.is_symlink()
  raw=path.read_bytes();assert len(raw)==row['size'] and hashlib.sha256(raw).hexdigest()==row['sha256'];files[str(path)]=row['sha256']
  if rel=='guard.py':source=raw
 assert source is not None
 spec=importlib.util.spec_from_file_location('held_runtime_guard330',expected.parent/'guard.py');module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module
 exec(compile(source,str(expected.parent/'guard.py'),'exec'),module.__dict__)
 return module,files
