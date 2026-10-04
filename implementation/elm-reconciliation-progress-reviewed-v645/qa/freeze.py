import ast,hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
components={'elm-paged-history-archive-v629':'8b621c1ae04793b97f0038159b30d13c2a46ce0b721d3656b07505a17621160b','elm-recovery-delivery-integration-v630':'de086f609ef1f04c3a02cef438e4ab9b1629d3bad1ae011ccd5bec279142aac5','elm-reconciliation-current-fixture-v634':'110ec5b2cd0ee927d0808a9c8c6afd1371bdcc5a4cd3550eb0e1589226a23434','elm-delivery-recovery-review-v639':'a6aaa9ad7c079e112137f5cb96669d56b857b24e6d1fcf0986f138a97ee76961'}
for n,d in components.items():
 p=REPO/'implementation'/n/'component-manifest.json';assert sha(p)==d;j=json.loads(p.read_text());items=j['files'].items() if isinstance(j['files'],dict) else [(x['path'],x) for x in j['files']]
 for rel,v in items:
  path=(REPO if rel.startswith('implementation/') else p.parent)/rel
  if isinstance(v,str):assert sha(path)==v
  else:assert sha(path)==v['sha256'] and path.stat().st_size==v['size'],str(path)
reports=[]
for n,old,count in [('elm-reconciliation-capability-v635','elm-responsive-capability-v283',83),('elm-reconciliation-focus-v636','elm-responsive-focus-v284',83)]:
 p=REPO/'implementation'/n/'qa';report=next(p.glob('native-*/report.json'));j=json.loads(report.read_text());assert j['passed'] and j['cleanupPassed'] and len(j['checks'])==count and all(x['passed'] for x in j['checks'])
 for k,d in j['artifacts'].items():assert sha(report.parent/k)==d
 for k,d in j['inputs'].items():assert sha(k)==d
 assert not j['privateHost'].get('remainingDescendants') and not j['privateHost'].get('cleanupErrors')
 original=ast.parse((REPO/'implementation'/old/'qa/native.py').read_text());actual=ast.parse((p/'native.py').read_text())
 for name in ['check','wait']:
  def calls(t):return [ast.dump(x,include_attributes=False) for x in ast.walk(t) if isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id==name]
  assert calls(original)==calls(actual)
 for name in ['wait','click','check']:
  def fn(t):return next(x for x in ast.walk(t) if isinstance(x,ast.FunctionDef) and x.name==name)
  assert ast.dump(fn(original),include_attributes=False)==ast.dump(fn(actual),include_attributes=False)
 reports.append({'path':str(report.relative_to(REPO)),'sha256':sha(report),'checks':count,'passed':True,'cleanupPassed':True})
files={};links={}
roots=[*[REPO/'implementation'/n for n in components],REPO/'implementation/elm-reconciliation-capability-v635',REPO/'implementation/elm-reconciliation-focus-v636',ROOT]
for root in roots:
 for p in sorted(root.rglob('*')):
  if '__pycache__' in p.parts or 'elm-stuff' in p.parts:continue
  if p==ROOT/'component-manifest.json':continue
  rel=str(p.relative_to(REPO))
  if p.is_symlink():links[rel]=str(p.readlink())
  elif p.is_file():files[rel]={'sha256':sha(p),'size':p.stat().st_size}
parent=REPO/'implementation/elm-reconciliation-regression-reviewed-v638/component-manifest.json'
out=ROOT/'component-manifest.json';assert not out.exists();out.write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'parent':str(parent.relative_to(REPO)),'parentSHA256':sha(parent),'selectedProduction':'implementation/elm-reconciliation-startup-order-v626','nativeReports':reports,'originalNative135AlreadyQualified':True,'originalNativeMenu89AlreadyQualified':True,'currentScopedGeneralChecks':255,'full473NewTupleAccepted':False,'deliveryIntegrationCPUChecks':36,'deliveryRepeatHistoryDefectConfirmed':'RECOVERY-639-001','releaseDeliveryLossNativeAccepted':False,'scalableHistoryAccepted':False,'symbolicPagedArchiveNamedScenarios':32,'fullReleaseAccepted':False,'completedRequirementIds':[],'componentPins':components,'files':files,'symlinks':links},indent=2)+'\n');print(out)
