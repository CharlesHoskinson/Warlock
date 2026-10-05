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
 gui=REPO/'implementation/elm-focus-recovery-integrated-gui-v333';core=REPO/'implementation/elm-grant-retirement-runtime-v595';fixture=REPO/'implementation/elm-focus-recovery-current-fixture-v342'
 def source_hold(path,digest):
  check(path,digest);packet=json.loads(path.read_text());assert packet['passed'] and packet['selectedProduction']==str(gui.relative_to(REPO))
  names=[v['path'] for v in packet['files']];assert len(names)==len(set(names))
  for v in packet['files']:
   rel=Path(v['path']);assert not rel.is_absolute() and '..' not in rel.parts
   p=REPO/rel
   if 'symlink' in v:assert p.is_symlink() and os.readlink(p)==v['symlink']
   else:assert not p.is_symlink();check(p,v['sha256']);assert p.stat().st_size==v['size']
  return packet
 held=source_hold(REPO/'implementation/elm-focus-recovery-integrated-held-v340/acceptance-manifest.json','86d318a1e44007f3d8ac581cd2f0f364c981f1740fe0a93bdd6fc3d27b367912');assert held['currentNativeScopedChecks']==224
 cohort=source_hold(REPO/'implementation/elm-focus-recovery-current-fixture-held-v345/acceptance-manifest.json','85f37f8d8a71f2ab3820dfb00f603e2d10433c95d7e2e8a8848cf0b9c26a1bc4');assert cohort['nativeCurrentTotalScopedChecksWith340']==390
 fixture_packet=manifest(fixture,'18a3c9966f40360721ac2e1e68da71c396c54f597ef01740726a4a05164e8a0c')
 for rel,v in fixture_packet['special'].items():assert v['kind']=='symlink' and (fixture/rel).is_symlink() and os.readlink(fixture/rel)==v['target']
 report=gui/'qa/build-1791154674626733228/report.json';check(report,'efac8a808dd40e92d599a81db6070f827e3ec4cd613a122b168b4759247ea77b');d=json.loads(report.read_text());assert d['passed']
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
 fixture=REPO/'implementation/elm-focus-recovery-current-fixture-v342';s=importlib.util.spec_from_file_location('prepared_current634relay',fixture/'relay/qa/relay.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 out=root/'qa/profile-binding';out.mkdir(mode=0o700);runtime=out/'runtime';runtime.mkdir(mode=0o700);control=out/'control';control.mkdir(mode=0o700);receipt_control=out/'receipt-control';receipt_control.mkdir(mode=0o700)
 a=out/'authority.json';a.write_text(json.dumps({'runtime':str(runtime),'instance':'prepared_current'}));a.chmod(0o600)
 r=out/'receipt.json';r.write_text(json.dumps({'authorityConfig':str(a),'controlDirectory':str(receipt_control),'incarnation':'16','effectOperation':'restore-geometry','selectorOrdinal':2}));r.chmod(0o600)
 common={'runtime':str(runtime),'instance':'prepared_current','controlDirectory':str(control)}
 broker=m.command_for(dict(common,profile='broker',authorityConfig=str(a)),REPO);receipt=m.command_for(dict(common,profile='receipt',receiptConfig=str(r)),REPO)
 assert broker[2]==str(REPO/'implementation/elm-focus-recovery-integrated-gui-v333/qa/build-1791154674626733228/inputs/adapter/daemon.py')
 assert receipt[2]==str(fixture/'receipt/qa/broker-entrypoint.py')
 return {'broker':broker,'receipt':receipt,'profileConfigSHA256':{str(p):sha(p) for p in [a,r]},'scope':'Actual production command_for invoked; no child process or native endpoint launched'}
