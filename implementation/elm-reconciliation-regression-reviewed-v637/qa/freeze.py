import ast,hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
menu=REPO/'implementation/elm-reconciliation-full-menu-v631'
report=menu/'qa/native-1791152528506709531/report.json';j=json.loads(report.read_text());assert j['passed'] and j['cleanupPassed'] and len(j['checks'])==89 and all(x['passed'] for x in j['checks'])
for n,d in j['artifacts'].items():assert sha(report.parent/n)==d,n
for n,d in j['inputs'].items():assert sha(n)==d,n
assert not j['privateHost'].get('remainingDescendants') and not j['privateHost'].get('cleanupErrors')
old=ast.parse((REPO/'implementation/elm-responsive-full-menu-v281/qa/native.py').read_text());new=ast.parse((menu/'qa/native.py').read_text())
for name in ['check','wait']:
 def calls(t):return [ast.dump(n,include_attributes=False) for n in ast.walk(t) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id==name]
 assert calls(old)==calls(new)
for name in ['check','wait','click']:
 def fn(t):return next(n for n in ast.walk(t) if isinstance(n,ast.FunctionDef) and n.name==name)
 assert ast.dump(fn(old),include_attributes=False)==ast.dump(fn(new),include_attributes=False)
files={};links={}
for root in [menu,REPO/'implementation/elm-reconciliation-capability-v632',REPO/'implementation/elm-reconciliation-focus-v633',ROOT]:
 for p in sorted(root.rglob('*')):
  if '__pycache__' in p.parts or 'elm-stuff' in p.parts or p.name=='component-manifest.json':continue
  rel=str(p.relative_to(REPO))
  if p.is_symlink():links[rel]=str(p.readlink())
  elif p.is_file():files[rel]={'sha256':sha(p),'size':p.stat().st_size}
parent=REPO/'implementation/elm-reconciliation-integrated-reviewed-v625/component-manifest.json'
out=ROOT/'component-manifest.json';assert not out.exists();out.write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'parent':str(parent.relative_to(REPO)),'parentSHA256':sha(parent),'nativeMenu89Passed':True,'nativeMenuReport':str(report.relative_to(REPO)),'capabilityFocusPreflightFailed':True,'capabilityFocusNativeLaunched':False,'full473NewTupleAccepted':False,'fullReleaseAccepted':False,'completedRequirementIds':[],'files':files,'symlinks':links},indent=2)+'\n');print(out)
