"""Compile and exercise actual private controller delivery boundary under protection."""
import hashlib,json,resource,shlex,subprocess,sys,time,traceback
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).parent;REPO=ROOT.parents[2];GUI=REPO/'implementation/warlock-preview-provider-v48';OUT=ROOT/('controller-check-v3-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'passed':False,'scope':scope,'nativeAcceptance':False,'fullReleaseAccepted':False,'commands':[],'inputs':{}}
try:
 bp=next(GUI.glob('qa/build-*/report.json'));b=json.loads(bp.read_text());assert b['passed']
 for rel,h in b['inputs'].items():assert sha(GUI/rel)==h,rel
 deps=[Path(__file__),ROOT/'controller-delay-test_v2.c',bp]
 deps += [Path(p) for p in b['compilerDependencies']]
 objects=[bp.parent/(name+'.o') for name in ['preview_uri.cpp','preview_icons.cpp','preview-uri-webkit.cpp','preview-provider-bootstrap.cpp','client-producer.cpp','imported-clients.cpp']]
 deps += objects
 report['inputs']={str(p):sha(p) for p in deps}
 flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','gtk+-3.0','webkit2gtk-4.1','gtk-layer-shell-0','json-glib-1.0','gio-unix-2.0'],text=True))
 cmds=[('compile',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations',str(ROOT/'controller-delay-test_v2.c'),*map(str,objects),*flags,'-lstdc++','-o',str(OUT/'controller-delay-test')]),('controls',[str(OUT/'controller-delay-test')])]
 for name,argv in cmds:
  p=subprocess.run(argv,capture_output=True,text=True,timeout=180);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'argv':argv,'exitCode':p.returncode});assert p.returncode==0,p.stderr or p.stdout
 report['evidence']=json.loads(next(l.split(': ',1)[1] for l in (line.removeprefix('# ') for line in p.stdout.splitlines()) if l.startswith('controller-delay-result: ')));assert report['evidence']['passed'] and report['evidence']['checks']==22
 assert all(sha(Path(p))==h for p,h in report['inputs'].items());report['passed']=True
except Exception as e:report.update(error=repr(e),traceback=traceback.format_exc())
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
