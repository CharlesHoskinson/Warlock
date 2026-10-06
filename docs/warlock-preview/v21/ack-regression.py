"""Require the actual ACK envelope regression to fail its named host oracle."""
import hashlib,json,pathlib,resource,shlex,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
ROOT=pathlib.Path(__file__).parent;OUT=ROOT/('ack-regression-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
reports=list((REPO/'implementation/warlock-preview-provider-v27').glob('qa/build-*/report.json'));assert len(reports)==1
build=reports[0];built=json.loads(build.read_text());assert built['passed'];inputs=build.parent/'inputs'
source=inputs/'native/shared-host.c';assert sha(source)==built['inputs']['native/shared-host.c']
text=source.read_text();first=text.index('static JsonNode *imported_command_row(');last=text.index('\nstatic gboolean imported_commands(',first)
old='''static JsonNode *imported_command_row(JsonNode *root,JsonNode *row) {
    JsonNode *single=json_node_copy(root);JsonArray *one=json_array_new();
    json_array_add_element(one,json_node_copy(row));
    json_object_set_array_member(json_node_get_object(single),"entries",one);return single;
}'''
mutant=OUT/'shared-host.c';mutant.write_text(text[:first]+old+text[last:])
flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','gtk+-3.0','webkit2gtk-4.1','gtk-layer-shell-0','json-glib-1.0','gio-unix-2.0'],text=True))
objects=[build.parent/(x+'.o') for x in ['preview_uri.cpp','preview-uri-webkit.cpp','preview-provider-bootstrap.cpp','client-producer.cpp','imported-clients.cpp']]
r={'passed':False,'inputs':{str(build):sha(build),str(source):sha(source),**{str(p):sha(p) for p in objects}},'nativeAcceptance':False,'fullReleaseAccepted':False}
def run(name,command,timeout):
    result=subprocess.run(command,cwd=inputs,capture_output=True,text=True,timeout=timeout)
    (OUT/(name+'.stdout')).write_text(result.stdout);(OUT/(name+'.stderr')).write_text(result.stderr)
    r[name]={'command':command,'exitCode':result.returncode};return result
try:
    compileResult=run('compile',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','-I'+str(inputs/'native'),'-c',str(mutant),'-o',str(OUT/'host.o'),*flags],180);assert compileResult.returncode==0
    link=run('link',['g++',str(OUT/'host.o'),*map(str,objects),'-o',str(OUT/'elm-host'),*flags],180);assert link.returncode==0
    correct=run('correct',[str(build.parent/'elm-host'),'--self-test','-p','/host/imported-acknowledgement-isolation'],5);assert correct.returncode==0 and 'ok 1 /host/imported-acknowledgement-isolation' in correct.stdout
    unsafe=run('mutant',[str(OUT/'elm-host'),'--self-test','-p','/host/imported-acknowledgement-isolation'],5)
    assert unsafe.returncode!=0 and "'copy!=object' should be TRUE" in unsafe.stdout+unsafe.stderr
    r.update(passed=True,guard='Named actual host assertion rejects shared-object copy before dereferencing its invalidated original array; compiler failures or unrelated crashes do not qualify.')
except Exception as e:r['error']=repr(e)
r['artifacts']={p.name:sha(p) for p in OUT.iterdir() if p.is_file()}
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
