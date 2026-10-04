"""Current626 build / owning205594AQ155 /634 fixture byte closure, read-only."""
import hashlib,json,importlib.util,os,sys
from pathlib import Path
REPO=Path(__file__).resolve().parents[3]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify_current(root):
 pins={}
 def check(p,digest):
  p=Path(p);assert p.is_file() and sha(p)==digest,str(p);pins[str(p.resolve())]=digest
 def manifest(directory,digest):
  p=directory/'component-manifest.json';check(p,digest);d=json.loads(p.read_text())
  for rel,v in d['files'].items():
   p=directory/rel;assert not p.is_symlink();check(p,v['sha256']);assert p.stat().st_size==v['size']
  return d
 gui=REPO/'implementation/elm-recovery-delivery-integrated-gui-v640';core=REPO/'implementation/elm-grant-retirement-runtime-v595';fixture=REPO/'implementation/elm-recovery-delivery-current-fixture-v660'
 manifest(gui,'f09652e1b61b5850d9efead5ac624c4d3097a69d68470b986fd94655d52765df');manifest(fixture,'67a337ab1f629f82f445aaa2da948c85db44e0c7a959afba57590943f4e7869b')
 report=gui/'qa/build-1791153819143987946/report.json';check(report,'66c4a615937fc475712594f59ea8b17969837a26ea3f3eaa0de07fa38e2aab63');d=json.loads(report.read_text());assert d['passed']
 for name,digest in d['inputs'].items():
  check(gui/name,digest)
  if name not in ('assets/elm.js','assets/bar.js','assets/popup.js'):check(report.parent/'inputs'/name,digest)
 for name,digest in d['artifacts'].items():check(report.parent/name,digest)
 check(report.parent/'elm-host',d['binarySHA256'])
 for section in ('compilerDependencies','tools','linkedLibraries'):
  for p,v in d[section].items():check(p,v['sha256'] if isinstance(v,dict) else v)
 pair_path=core/'qa/build-pair-manifest.json';pair=json.loads(pair_path.read_text());assert pair['passed'];pins[str(pair_path.resolve())]=sha(pair_path)
 for name,digest in pair['files'].items():check(core/name,digest)
 for v in pair['nativePair'].values():check(v['path'],v['sha256'])
 for key in ('owningAcceptance','owningCoreComponent','producerEvidence','keyboardAcceptance'):check(pair[key],pair[key+'SHA256'])
 descriptor=core/'native-build-report.json';pins[str(descriptor)]=sha(descriptor);native=json.loads(descriptor.read_text());check(native['pluginBuildReport'],native['pluginBuildReportSHA256']);n=json.loads(Path(native['pluginBuildReport']).read_text());assert n['passed'] and n['core']['sha256']==pair['nativePair']['core']['sha256']
 for section in ('dependencies','linkedLibraries'):
  for p,digest in n[section].items():check(p,digest)
 grant=REPO/'implementation/elm-grant-retirement-native-v596/qa/native-1791146569027803533/report.json';q=json.loads(grant.read_text());assert q['passed'] and q['cleanupPassed'] and len(q['checks'])==42 and q['pair']==pair['nativePair'];pins[str(grant)]=sha(grant)
 for name,digest in q['artifacts'].items():check(grant.parent/name,digest)
 # Current component manifests authenticate exact build bytes; grant qualification
 # supplies owning retirement capability, not transfer of old GUI scenario results.
 return pins

def verify_profiles(root):
 fixture=REPO/'implementation/elm-recovery-delivery-current-fixture-v660';s=importlib.util.spec_from_file_location('prepared_current634relay',fixture/'relay/qa/relay.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 out=root/'qa/profile-binding';out.mkdir(mode=0o700);runtime=out/'runtime';runtime.mkdir(mode=0o700);control=out/'control';control.mkdir(mode=0o700);receipt_control=out/'receipt-control';receipt_control.mkdir(mode=0o700)
 a=out/'authority.json';a.write_text(json.dumps({'runtime':str(runtime),'instance':'prepared_current'}));a.chmod(0o600)
 r=out/'receipt.json';r.write_text(json.dumps({'authorityConfig':str(a),'controlDirectory':str(receipt_control),'incarnation':'16','effectOperation':'restore-geometry','selectorOrdinal':2}));r.chmod(0o600)
 common={'runtime':str(runtime),'instance':'prepared_current','controlDirectory':str(control)}
 broker=m.command_for(dict(common,profile='broker',authorityConfig=str(a)),REPO);receipt=m.command_for(dict(common,profile='receipt',receiptConfig=str(r)),REPO)
 assert broker[2]==str(REPO/'implementation/elm-recovery-delivery-integrated-gui-v640/qa/build-1791153819143987946/inputs/adapter/daemon.py')
 assert receipt[2]==str(fixture/'receipt/qa/broker-entrypoint.py')
 return {'broker':broker,'receipt':receipt,'profileConfigSHA256':{str(p):sha(p) for p in [a,r]},'scope':'Actual production command_for invoked; no child process or native endpoint launched'}
