import ast,hashlib,json,os,resource,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
manifest=ROOT/'component-manifest.json';assert not manifest.exists()
reports=['receipt/qa/hold-1791155158880813917/report.json','receipt/qa/selector-1791155191421448306/report.json','relay/qa/test-1791155191604949339/report.json','qa/binding-1791155191986582375/report.json'];expected=[45,52,19,45]
for rel,count in zip(reports,expected):
 d=json.loads((ROOT/rel).read_text());assert d['passed'] and len(d['checks'])==count and all(x['passed'] for x in d['checks'])
 input_root=ROOT/'receipt' if rel.startswith('receipt/') else ROOT
 for name,digest in d.get('inputs',{}).items():assert sha(input_root/name)==digest
for rel in ['relay/qa/relay.py','relay/qa/test.py']:
 assert sha(ROOT/rel)==sha(ROOT/'relay/qa/test-1791155191604949339/inputs'/Path(rel).relative_to('relay'))
held=json.loads((ROOT/'receipt/qa/held-source-manifest.json').read_text())
for rel,v in held['files'].items():assert sha(ROOT/'receipt'/rel)==v['sha256']
ancestor=REPO/'implementation/elm-reconciliation-current-fixture-v634'
old=ast.parse((ancestor/'receipt/qa/test.py').read_text());new=ast.parse((ROOT/'receipt/qa/test.py').read_text())
calls=lambda tree:[ast.dump(n,include_attributes=False) for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='check']
assert calls(old)==calls(new),'Original45 receipt assertions changed'
parent=REPO/'implementation/elm-recovery-delivery-current-fixture-v654/component-manifest.json';assert sha(parent)=='be2f7b794c7149109256be31e960f0a146867611b7dd4e19a6d2f38b7335649e'
files={};special={}
for base,dirs,names in os.walk(ROOT,followlinks=False):
 dirs[:]=[x for x in dirs if x not in ('elm-stuff','__pycache__')]
 for name in names:
  p=Path(base)/name;rel=str(p.relative_to(ROOT))
  if p.is_symlink():special[rel]={'kind':'symlink','target':os.readlink(p)}
  elif p.is_file():files[rel]={'sha256':sha(p),'size':p.stat().st_size}
  else:special[rel]={'kind':'runtime-special'}
d={'schema':1,'component':ROOT.name,'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'fullRelease':False,'backendRoot':str(REPO/'implementation/elm-recovery-delivery-integrated-gui-v640/qa/build-1791153819143987946/inputs/adapter'),'backendComponentManifestSHA256':'f09652e1b61b5850d9efead5ac624c4d3097a69d68470b986fd94655d52765df','relay':'relay/qa/relay.py','receipt':'receipt/qa/broker-entrypoint.py','receiptSourceManifestSHA256':sha(ROOT/'receipt/qa/held-source-manifest.json'),'profiles':['broker','receipt'],'originalChecks':159,'additionalStale626Checks':2,'finalChecks':161,'reports':[{'path':r,'sha256':sha(ROOT/r),'checks':c} for r,c in zip(reports,expected)],'files':dict(sorted(files.items())),'special':special,'failedParentManifest':str(parent.relative_to(REPO)),'failedParentSHA256':sha(parent),'CPUHarnessReadinessAmendment':'held.json plus actual host-refresh before injection under same2s readiness deadline; original assertions/watchdog/subprocess timeouts unchanged','scope':'Current640 captured backend binding and inherited QA controls only; no native acceptance'}
manifest.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'manifest':str(manifest),'sha256':sha(manifest),'files':len(files),'checks':161}))
