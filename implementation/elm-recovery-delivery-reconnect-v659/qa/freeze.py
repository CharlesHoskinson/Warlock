"""Freeze prepared runner source and CPU evidence; no native launches."""
import ast,hashlib,json,os,resource,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not (ROOT/'component-manifest.json').exists()
geometric=ROOT.name.endswith('v658');ancestor=REPO/'implementation'/('elm-responsive-geometry-v288' if geometric else 'elm-responsive-reconnect-v293')
old=(ancestor/'qa/native.py').read_text();actual=(ROOT/'qa/native.py').read_text()
def calls(t,name):return [ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(t)) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id==name]
assert calls(old,'check')==calls(actual,'check');assert calls(old,'wait')==calls(actual,'wait')
if geometric:
 p=Path(json.loads((ROOT/'qa/preflight-result.json').read_text())['report']);d=json.loads(p.read_text());assert d['passed'];identity=list((ROOT/'qa').glob('identity-*/report.json'));assert len(identity)==1;assert json.loads(identity[0].read_text())['passed'];reports=[p,*identity]
 # All run scenario assertions retain exact AST; only input inventory path changes.
 a=next(n for n in ast.walk(ast.parse(old)) if isinstance(n,ast.FunctionDef) and n.name=='run');b=next(n for n in ast.walk(ast.parse(actual)) if isinstance(n,ast.FunctionDef) and n.name=='run')
 asserts=lambda t:[ast.dump(n,include_attributes=False) for n in ast.walk(t) if isinstance(n,ast.Assert)]
 assert asserts(a)==asserts(b)
else:
 p=ROOT/'qa/preflight.json';d=json.loads(p.read_text());assert d['passed'];reports=[p]
 # Full scenario program differs only in authorized source tuple literals.
 expected=old.replace('elm-picker-ready-runtime-v239','elm-grant-retirement-runtime-v595').replace('elm-responsive-surfaces-gui-v278','elm-recovery-delivery-integrated-gui-v640').replace('elm-responsive-broker-fixture-v292','elm-recovery-delivery-current-fixture-v660').replace('build-1791147765154709569','build-1791153819143987946')
 assert ast.dump(ast.parse(expected),include_attributes=False)==ast.dump(ast.parse(actual),include_attributes=False)
for name,digest in d['inputs'].items():assert sha(name)==digest,name
files={};special={}
for base,dirs,names in os.walk(ROOT,followlinks=False):
 dirs[:]=[x for x in dirs if x not in ('elm-stuff','__pycache__')]
 for name in names:
  p=Path(base)/name;rel=str(p.relative_to(ROOT))
  if p.is_symlink():special[rel]={'kind':'symlink','target':os.readlink(p)}
  elif p.is_file():files[rel]={'sha256':sha(p),'size':p.stat().st_size}
  else:special[rel]={'kind':'runtime-special'}
manifest={'schema':1,'component':ROOT.name,'sourceHeld':True,'readyForRootNative':True,'nativeLaunched':False,'nativeAcceptance':False,'releaseAcceptance':False,'originalScenarioCount':161 if geometric else 57,'ancestor':str(ancestor.relative_to(REPO)),'ancestorRunnerSHA256':sha(ancestor/'qa/native.py'),'selectedProduction':'implementation/elm-recovery-delivery-integrated-gui-v640','fixtureManifestSHA256':'67a337ab1f629f82f445aaa2da948c85db44e0c7a959afba57590943f4e7869b','preparedReports':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in reports],'owningPair':d.get('pair',json.loads((REPO/'implementation/elm-grant-retirement-runtime-v595/qa/build-pair-manifest.json').read_text())['nativePair']),'files':dict(sorted(files.items())),'special':special,'completedRequirementIds':[],'scope':'Prepared runner source/oracle/CPU closure only; native execution belongs to root serial lane'}
p=ROOT/'component-manifest.json';p.write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'manifest':str(p),'sha256':sha(p),'files':len(files),'nativeAcceptance':False}))
