import hashlib,json,resource,shlex,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];OUT=ROOT/'qa'/('local-unsent-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
report={'passed':False,'nativeAcceptance':False,'releaseAcceptance':False,'inputs':{},'commands':[],'scope':'Actual compiled shared controller and unchanged actual C preflight certificate; dedicated Pending-only local terminal, no native receipt or replay. CPU only; Combined V121 attach correction/operation refusal tested; current shared native integration remains open'}
inputs=OUT/'inputs'
for directory in ['src','native','qa']:
 for p in (ROOT/directory).glob('*'):
  if p.is_file():
   dest=inputs/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);report['inputs'][str(p.relative_to(ROOT))]=sha(p)
for name in ['elm.json','upstream.json','README.md']:
 shutil.copy2(ROOT/name,inputs/name);report['inputs'][name]=sha(ROOT/name)
evidence=REPO/'implementation/elm-menu-retirement-native-forensics-v94/qa/native-evidence.json';shutil.copy2(evidence,inputs/'qa/native-evidence.json');report['recordedEvidenceSHA256']=sha(evidence)
source=(inputs/'native/shared-host.c').read_text()
# Exact contiguous actual production snippets; host.c is included intact by probe.
header=source[source.index('typedef struct {'):source.index('static GPtrArray *output_views;')]
header+='static guint64 topology_revision;\n'
header+=source[source.index('static JsonNode *scope_packet('):source.index('static OutputView *scope_lookup(')]
header+=source[source.index('static JsonNode *shared_batch_certificate('):source.index('static void shared_batch_notify(')]
(inputs/'qa/actual-shared-helpers.h').write_text(header);report['actualExtractedHelperSHA256']=sha(inputs/'qa/actual-shared-helpers.h')
def run(name,argv):
 p=subprocess.run(argv,cwd=inputs,capture_output=True,text=True,timeout=180);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'argv':argv,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr[-7000:];return p.stdout
try:
 ancestor=ROOT.parents[1]/'implementation/elm-shared-batch-disposition-v104';held=ancestor/'qa/held-source-manifest.json';assert sha(held)=='5e120bdb350c664897f14ff0ebdf25e857fe37aa2cd8819d3be02ef2f7bfd21e'
 run('worker-compile',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/BatchReplay.elm','--output='+str(OUT/'worker.js')])
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gtk+-3.0','webkit2gtk-4.1','gtk-layer-shell-0','json-glib-1.0','gio-unix-2.0']))
 run('actual-host-helper-compile',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','-MD','-MF',str(OUT/'probe.d'),'qa/disposition-probe.c','-o',str(OUT/'probe'),*flags])
 run('compiled-local-unsent',['node',str(inputs/'qa/disposition.cjs'),str(OUT/'worker.js'),str(inputs/'qa/native-evidence.json'),str(OUT/'probe'),str(OUT/'checks.json')])
 result=json.loads((OUT/'checks.json').read_text());assert result['passed'];report['checks']=result['checks'];report['passed']=True
 run('compiled-deferred-attach',['node',str(inputs/'qa/deferred-attach.cjs'),str(OUT/'worker.js'),str(inputs/'qa/native-evidence.json'),str(OUT/'probe'),str(OUT/'deferred-checks.json')])
 deferred=json.loads((OUT/'deferred-checks.json').read_text());assert deferred['passed'];report['checks']+=deferred['checks']
 run('actual-main-compile',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Main.elm','--optimize','--output='+str(OUT/'main.js')])
 for module in ['Bar','Popup']:
  run('actual-'+module+'-compile',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/'+module+'.elm','--optimize','--output='+str(OUT/(module+'.js'))])
 deps=shlex.split((OUT/'probe.d').read_text().replace('\\\n',' ').split(':',1)[1]);report['compilerDependencies']={str((inputs/p).resolve()):sha((inputs/p).resolve()) for p in deps}
 for relative,wanted in report['inputs'].items():assert sha(ROOT/relative)==wanted
except Exception as error:report['passed']=False;report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and 'elm-stuff' not in p.parts}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
