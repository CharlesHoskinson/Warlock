import hashlib,json,resource,shlex,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];OUT=ROOT/'qa'/('disposition-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
report={'passed':False,'nativeAcceptance':False,'releaseAcceptance':False,'inputs':{},'commands':[],'scope':'Actual compiled shared controller registration and actual native preflight/certificate with recorded retirement ordering, hostile/mixed/uncertainty CPU cases'}
inputs=OUT/'inputs'
for directory in ['src','native','qa']:
 for p in (ROOT/directory).glob('*'):
  if p.is_file():
   dest=inputs/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);report['inputs'][str(p.relative_to(ROOT))]=sha(p)
shutil.copy2(ROOT/'elm.json',inputs/'elm.json');report['inputs']['elm.json']=sha(ROOT/'elm.json')
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
 run('worker-compile',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/BatchReplay.elm','--output='+str(OUT/'worker.js')])
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gtk+-3.0','webkit2gtk-4.1','gtk-layer-shell-0','json-glib-1.0','gio-unix-2.0']))
 run('actual-host-helper-compile',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','-MD','-MF',str(OUT/'probe.d'),'qa/disposition-probe.c','-o',str(OUT/'probe'),*flags])
 run('compiled-shared-disposition',['node',str(inputs/'qa/disposition.cjs'),str(OUT/'worker.js'),str(inputs/'qa/native-evidence.json'),str(OUT/'probe'),str(OUT/'checks.json')])
 result=json.loads((OUT/'checks.json').read_text());assert result['passed'];report['checks']=result['checks'];report['passed']=True
 deps=shlex.split((OUT/'probe.d').read_text().replace('\\\n',' ').split(':',1)[1]);report['compilerDependencies']={str((inputs/p).resolve()):sha((inputs/p).resolve()) for p in deps}
 for relative,wanted in report['inputs'].items():assert sha(ROOT/relative)==wanted
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and 'elm-stuff' not in p.parts}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
