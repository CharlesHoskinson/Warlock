"""Actual tuple/source preflight only; fresh EOF reconnect QA never launched here."""
import ast,hashlib,importlib.util,json,resource,shutil,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];PARENT=REPO/'implementation/elm-geometry-staged-menu-reconnect-native-v83'
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
OUT=ROOT/'qa'/('preflight-'+str(time.time_ns()));OUT.mkdir();INPUT=OUT/'inputs';INPUT.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[ROOT/'candidate_host.py',ROOT/'upstream.json',ROOT/'qa/native.py',ROOT/'qa/client_evidence.py',ROOT/'README.md',ROOT/'qa/freeze.py',Path(__file__)]
rows={str(p.relative_to(ROOT)):sha(p) for p in files}
for p in files:
 dest=INPUT/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
checks=[];report={'passed':False,'scope':'QA EOF reconnect runner AST preservation and actual source/owning tuple preflight only; no GUI or reconnect acceptance','inputs':rows,'checks':checks}
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
def find(t,n):return next(x for x in ast.walk(t) if isinstance(x,ast.FunctionDef) and x.name==n)
def dump(n):return ast.dump(n,include_attributes=False)
try:
 before=ast.parse((PARENT/'qa/native.py').read_text());after=ast.parse((ROOT/'qa/native.py').read_text())
 for name in ['check','wait','frames','projection','incoming','effects','geometry','geometry_row','coherent','row','parent_pointer','open_menu','action','settle_menu']:
  check('original transition helper exact '+name,dump(find(before,name))==dump(find(after,name)))
 check('original client ACK/pixel helper byte exact',sha(ROOT/'qa/client_evidence.py')==sha(PARENT/'qa/client_evidence.py'))
 # The complete original post-reconnect assertion is retained verbatim.
 name='reconnectRenegotiatesPreservingSavedOriginNoReplay'
 def named(t):return next(x for x in ast.walk(t) if isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=='check' and x.args and isinstance(x.args[0],ast.Constant) and x.args[0].value==name)
 check('saved MAX lifetime/capability/no effect replay assertion unchanged',dump(named(before))==dump(named(after)))
 def calls(t,name):return [dump(x) for x in ast.walk(find(t,'run')) if isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id==name]
 check('all operation sequence calls unchanged',calls(before,'settle_menu')==calls(after,'settle_menu'))
 from collections import Counter
 def asserted(t):
  adapted={'reconnectExactCapturedBrokerAndRelayCommands','reconnectFreshActorFixedCommands'}
  return [dump(x) for x in ast.walk(find(t,'run')) if isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=='check' and not (x.args and isinstance(x.args[0],ast.Constant) and x.args[0].value in adapted)]
 check('all original operation/state/deadline assertion expressions retained',not (Counter(asserted(before))-Counter(asserted(after))))
 check('closed receipt actor command/config checks present',all(n in (ROOT/'qa/native.py').read_text() for n in ['reconnectExactCapturedBrokerAndRelayCommands','reconnectFreshActorFixedCommands']))
 check('full09 required without partial acceptance shortcut',"report['scenarios'].append('GEOMETRY-MENU-09')" in (ROOT/'qa/native.py').read_text() and 'partialScenarios' not in (ROOT/'qa/native.py').read_text())
 check('no SIGSTOP added',sum(isinstance(x,ast.Attribute) and x.attr=='SIGSTOP' for x in ast.walk(before))==sum(isinstance(x,ast.Attribute) and x.attr=='SIGSTOP' for x in ast.walk(after)))
 spec=importlib.util.spec_from_file_location('v96_native_preflight',ROOT/'qa/native.py');runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
 build,pair,pointer,fixture=runner.preflight();relay=runner.load_relay()
 check('actual staged CPU build and fresh pair selected',build['passed'] is True and pair['nativePair']['core']['sha256']=='f1430c86174efa5682c40545daa3c7d823e29943ef07f8c992da59a0641617ad')
 check('relay strict APIs present',all(callable(getattr(relay,k)) for k in ['actor_status','close_stdin','exit_status']))
 report['selectedTuple']={'pair':pair['nativePair'],'buildReport':str(runner.BUILD),'buildReportSHA256':runner.BUILD_HASH,'relayManifest':str(runner.RELAY/'qa/held-source-manifest.json'),'relayManifestSHA256':runner.RELAY_MANIFEST_HASH,'receiptManifest':str(runner.RECEIPT/'qa/held-source-manifest.json'),'receiptManifestSHA256':runner.RECEIPT_MANIFEST_HASH}
 for relative,digest in rows.items():check('source held '+relative,sha(ROOT/relative)==digest)
 report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not report['passed'])
