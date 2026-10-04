import hashlib,json,os,pathlib,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
from toolchain import verify
ROOT=pathlib.Path(__file__).resolve().parents[1];PARENT=ROOT.parent/'elm-focus-recovery-integrated-gui-v333'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
t=verify();r=json.loads((ROOT/'qa/provenance-report.json').read_text());assert r['passed'] and r['newPublicAssertions']==51 and r['provenanceGuardFixtures']==8 and all(v['byteIdentical'] for v in r['sameProgramComparisons'].values())
for n,h in r['productionSourceHashes'].items():assert sha(ROOT/n)==h and sha(PARENT/n)==h
b=json.loads(pathlib.Path(r['buildReport']).read_text());p=json.loads(pathlib.Path(r['publicReport']).read_text());assert b['passed'] and p['passed'] and len(p['checks'])==51 and all(v['beforeAfterVerified'] for v in b['elmToolchainBeforeAfterChecks']+p['elmToolchainBeforeAfterChecks'])
for n,row in t['heldFiles'].items():assert sha(ROOT/n)==row['sha256']
assert sha(ROOT/'qa/ancestry/build333-missing-elm-inventory.json')==sha(PARENT/'qa/build-1791154674626733228/report.json')
rows=[];links={}
for f in sorted(ROOT.rglob('*')):
 if f.is_symlink():links[str(f.relative_to(ROOT))]=os.readlink(f)
 elif f.is_file() and f not in [ROOT/'component-manifest.json',ROOT/'qa/freeze-receipt.json',ROOT/'qa/protected-freeze.log']:rows.append({'path':str(f.relative_to(ROOT)),'sha256':sha(f),'size':f.stat().st_size,'mode':oct(f.stat().st_mode & 0o777)})
m=ROOT/'component-manifest.json';m.write_text(json.dumps({'sourceHeld':True,'passed':True,'sameProgramAs333':True,'compilerSHA256':r['compilerSHA256'],'heldCompilerPackageCacheFiles':111,'dependencyPackages':7,'publicAssertions':51,'provenanceGuardFixtures':8,'buildBeforeAfterCommands':r['buildBeforeAfterCommands'],'publicBeforeAfterCommands':r['publicBeforeAfterCommands'],'selectedBuildReport':r['buildReport'],'selectedPublicReport':r['publicReport'],'nativeAcceptance':False,'fullReleaseAccepted':False,'files':rows,'intentionalUnsafeGuardFixtureSymlinks':links},indent=2)+'\n');out={'passed':True,'files':len(rows),'manifestSHA256':sha(m),'sameProgramAs333':True,'nativeAcceptance':False};(ROOT/'qa/freeze-receipt.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
