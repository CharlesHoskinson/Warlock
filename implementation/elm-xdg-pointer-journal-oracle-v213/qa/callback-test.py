import hashlib,importlib.util,json,os,resource,shlex,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
s=Path(__file__).resolve().parents[1];r=s.parents[1];fixture=r/'implementation/elm-geometry-xdg-hint-choice-fixture-v197';selected=json.loads((fixture/'client-build-report.json').read_text())['client'];build=Path(selected['buildReport']);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert sha(build)==selected['buildReportSHA256'];b=json.loads(build.read_text());assert b['passed']
inputs={}
for section in ('inputs','dependencies','tools','linkedLibraries'):
 for p,digest in b[section].items():assert sha(p)==digest,p;inputs[p]=digest
source=fixture/'native/xdg-origin-client.c';inputs[str(source)]=sha(source);inputs[str(s/'oracle.py')]=sha(s/'oracle.py');inputs[str(Path(__file__))]=sha(__file__)
out=s/'qa'/('callback-'+str(time.time_ns()));out.mkdir();shutil.copyfile(source,out/'xdg-origin-client.c')
(out/'callback.c').write_text('''#define main fixture_main
#include "xdg-origin-client.c"
#undef main
static unsigned connections;
struct wl_display *__wrap_wl_display_connect(const char *name){(void)name;++connections;return NULL;}
int main(void){
 struct client c={.surface=(struct wl_surface *)(uintptr_t)1};
 pointer_enter(&c,NULL,5,c.surface,4224,6208);
 pointer_button(&c,NULL,6,100,272,1);
 pointer_button(&c,NULL,7,101,272,0);
 pointer_enter(&c,NULL,8,(struct wl_surface *)(uintptr_t)2,4224,6208);
 pointer_button(&c,NULL,9,102,272,1);
 printf("{\\"connections\\":%u}\\n",connections);return connections?1:0;
}
''')
gen=build.parent/'generated';libs=shlex.split(subprocess.check_output(['/usr/bin/pkg-config','--cflags','--libs','wayland-client'],text=True));cmd=['/usr/bin/cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wl,-z,defs','-Wl,--wrap=wl_display_connect','-I'+str(gen),str(out/'callback.c'),str(gen/'xdg-shell-protocol.c'),*libs,'-o',str(out/'callback')]
result=subprocess.run(cmd,capture_output=True,text=True,timeout=30);(out/'build.stderr').write_text(result.stderr);assert result.returncode==0,result.stderr
p=subprocess.Popen([str(out/'callback')],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env={**os.environ,'WAYLAND_DISPLAY':'no-display-cpu-only'});stdout,stderr=p.communicate(timeout=5);assert p.returncode==0,stderr;(out/'callback.stdout').write_text(stdout);rows=[json.loads(line) for line in stdout.splitlines()];assert rows[-1]=={'connections':0};assert len(rows)==4 and rows[0]['event']=='pointer-enter';pair=rows[1:3]
spec=importlib.util.spec_from_file_location('oracle213',s/'oracle.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);proof=m.validate_pair(pair,pid=p.pid,after_sequence=rows[0]['sequence'],button=272,expected_local=[16.5,24.25]);assert not proof['physicalHardwareAccepted']
report={'passed':True,'scope':'Compiled actual197 pointer callbacks and213 strict decoder; no Wayland connection/native injection','nativeAcceptance':False,'processPID':p.pid,'proof':proof,'connections':0,'foreignPointerSuppressed':True,'buildCommand':cmd,'inputs':inputs,'artifacts':{str(f.relative_to(out)):sha(f) for f in out.rglob('*') if f.is_file()}};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'actualCallbacks':True,'connections':0}))
