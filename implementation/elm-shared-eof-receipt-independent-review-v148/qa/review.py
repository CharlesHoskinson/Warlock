"""Independent held-source/invariant acquisition review; never starts a backend."""
import ast,hashlib,importlib.util,json,os,resource,shutil,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];SOURCE=REPO/'implementation/elm-shared-eof-receipt-fixture-v148';OUT=ROOT/'qa'/('review-'+str(time.time_ns()));OUT.mkdir();checks=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
def node(p,name):return ast.dump(next(n for n in ast.parse(p.read_text()).body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name),include_attributes=False)
report={'passed':False,'nativeAcceptance':False,'full08Accepted':False,'full09Accepted':False,'full10Accepted':False,'scope':'Independent immutable fixture source/pin/AST/import-only review; no child, socket, receipt settlement or native action','checks':checks}
try:
 manifest=SOURCE/'component-manifest.json';check('expected reviewed fixture manifest',sha(manifest)=='daf8e357930c9326c20b01c8b8adc1482c166364b3d10b62159584946a81eba2');m=json.loads(manifest.read_text());check('held integrity and narrow native scope',m['sourceHeld'] is True and m['evidenceIntegrityPassed'] is True and all(m[k] is False for k in ['nativeAcceptance','full08Accepted','full09Accepted','full10Accepted']))
 for relative,row in m['files'].items():
  path=SOURCE/relative;check('held file '+relative,not path.is_symlink() and path.is_file() and path.stat().st_size==row['size'] and sha(path)==row['sha256'])
 for path,row in m['externalClosure'].items():check('held owning external closure '+path,Path(path).stat().st_size==row['size'] and sha(path)==row['sha256'])
 for rel in ['qa/backend.py','qa/relay.py','qa/wrapper.py','qa/broker-entrypoint.py','backend-pin.json','fixture-source-pin.json','component-manifest.json']:
  target=OUT/'inputs'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(SOURCE/rel,target)
 pin=json.loads((SOURCE/'backend-pin.json').read_text());check('fixed final145 frozen manifest',pin['componentManifestSHA256']=='65d6252dcd0d4b90ece6d67982e88b31bc010796b44c66483b0398ecc9d42fd8');check('fixed13 actual captured broker dependencies',len(pin['adapterFiles'])==13 and all(sha(Path(pin['adapterDirectory'])/name)==row['sha256'] and sha(row['source'])==row['sha256'] for name,row in pin['adapterFiles'].items()))
 sys.path.insert(0,str(SOURCE/'qa'));spec=importlib.util.spec_from_file_location('fixture_source_backend_review',SOURCE/'qa/backend.py');backend=importlib.util.module_from_spec(spec);spec.loader.exec_module(backend)
 verified=backend.verify_backend();check('actual verified backend fixed source',verified==Path(pin['adapterDirectory'])/'daemon.py');loaded=backend.load_backend();check('actual source-only broker imports pinned daemon',Path(loaded.__file__).resolve()==verified.resolve() and callable(loaded.main) and callable(loaded.send));check('current delivery writer bounded and unpoisoned',loaded.OUTPUT_SECONDS==3 and loaded.output_writer.poisoned is False)
 relay=SOURCE/'qa/relay.py';original=REPO/'implementation/elm-geometry-broker-eof-deadline-v92/qa/relay.py'
 for name in ['pump','actor_status','exit_status','close_stdin','directory','read_private','decode']:check('unchanged exact V92 AST '+name,node(relay,name)==node(original,name))
 wrapper=SOURCE/'qa/wrapper.py';old=REPO/'implementation/elm-geometry-receipt-selector-v82/qa/wrapper.py'
 for name in ['ReceiptHold','supervise','write_release','main']:check('unchanged exact V82 AST '+name,node(wrapper,name)==node(old,name))
 check('unchanged fixed receipt entrypoint bytes',sha(SOURCE/'qa/broker-entrypoint.py')==sha(old.with_name('broker-entrypoint.py')))
 for name,row in m['reports'].items():
  j=json.loads(Path(row['path']).read_text());check('selected distinct CPU report '+name,sha(row['path'])==row['sha256'] and j['passed'] is True)
 report.update(passed=True,manifestSHA256=sha(manifest),checkedFiles=len(m['files']),sourceSHA256=sha(Path(__file__)),limitations=['Tuple336 and exact144 backend only; current380 runtime requires fresh binding','Historical100 real receipt bytes only; no current native Pending settlement','Relay/hold source review does not qualify actual EOF/notifications/receipt release or six-second native scenario'])
except Exception as error:report['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not report['passed'])
