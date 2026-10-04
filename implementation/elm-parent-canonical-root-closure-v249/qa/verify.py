"""Root verification of frozen canonical parent fixture and independent review."""
import hashlib,json,resource,stat,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
PINS={'elm-parent-keyboard-canonical-observer-v247':'ea7dc366dda3ab5d7a9ec5efb5c3984915a585673a7da10372fafaf76c45a3f5','elm-parent-canonical-isolation-review-v248':'b65967ce43decd7aebc57bda15b48ee1f4800d7788276feea43a0f084db765b4'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
out=ROOT/'qa'/('verify-'+str(time.time_ns()));out.mkdir()
report={'passed':False,'nativeAcceptance':False,'fullGoalAccepted':False,'inputs':{},'verifiedFiles':0,'symlinks':0}
try:
 for name,digest in PINS.items():
  root=ROOT.parent/name;path=root/'component-manifest.json'
  assert sha(path)==digest,name
  report['inputs'][str(path)]=digest
  data=json.loads(path.read_text());assert data['sourceHeld'] is True and data['nativeAcceptance'] is False
  for section,base in [('files',root),('externalFiles',None)]:
   for name,row in data.get(section,{}).items():
    p=base/name if base else Path(name)
    assert p.is_file() and (base is None or not p.is_symlink()),str(p)
    assert sha(p)==row['sha256'] and p.stat().st_size==row['size'],str(p)
    if 'mode' in row:assert stat.S_IMODE(p.stat().st_mode)==row['mode'],str(p)
    report['verifiedFiles']+=1
  for name,target in data.get('symlinks',{}).items():
   p=root/name;assert p.is_symlink() and str(p.readlink())==target,str(p)
   report['symlinks']+=1
 owner=ROOT.parent/'elm-parent-keyboard-canonical-observer-v247'
 review=ROOT.parent/'elm-parent-canonical-isolation-review-v248'
 data=json.loads((review/'component-manifest.json').read_text())
 assert data['ownerManifestSHA256']==PINS[owner.name]
 reviewed=json.loads((review/data['verificationReport']).read_text())
 assert reviewed['passed'] is True and reviewed['guardChecks']==29
 build=json.loads((owner/'parent-probe-build-report.json').read_text())
 assert sha(Path(build['buildReport']))==build['buildReportSHA256']
 assert json.loads(Path(build['buildReport']).read_text())['passed'] is True
 report['descriptorSHA256']=sha(owner/'parent-probe-build-report.json')
 report['passed']=True
except BaseException as error:report['error']=repr(error)
finally:
 report['verifierSHA256']=sha(Path(__file__))
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json')
raise SystemExit(0 if report['passed'] else 1)
