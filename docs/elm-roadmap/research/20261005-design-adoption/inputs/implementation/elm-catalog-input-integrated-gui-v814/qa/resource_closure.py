import hashlib,json,pathlib,re,subprocess,sys,time,shlex
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
r=pathlib.Path(__file__).resolve().parents[1];o=r/'qa'/('resource-closure-'+str(time.time_ns()));o.mkdir();source=r/'native/host.c';s=source.read_text();a=s[s.index('static const char *asset_name('):];a=a[:a.index('\n}\n')+3];c='#include <glib.h>\n#include <stdio.h>\n'+a+'\nint main(int argc,char **argv){for(int i=1;i<argc;i++){if(!asset_name(argv[i]))return 1;puts(asset_name(argv[i]));}return 0;}\n';(o/'actual.c').write_text(c)
rows=[]
def call(name,cmd,expected):
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=30);(o/(name+'.log')).write_text(p.stdout+p.stderr);rows.append({'name':name,'command':cmd,'exitCode':p.returncode,'expectedExitCode':expected});assert p.returncode==expected,(name,p.stderr);return p
flags=call('flags',['pkg-config','--cflags','--libs','glib-2.0'],0).stdout;binary=o/'closure';call('compile',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(o/'actual.c'),'-o',str(binary),*shlex.split(flags)],0)
refs={};uris=[]
for name in ('index.html','bar.html','popup.html'):
 p=r/'assets'/name;resources=re.findall(r'(?:src|href)="([^"]+)"',p.read_text());refs[name]=resources
 for rel in resources:assert (r/'assets'/rel).is_file();uris.append('elm-shell://app/'+rel)
call('all-three-HTML-resource-closure',[str(binary),*uris],0);call('QA-recorder-not-production-allowlisted',[str(binary),'elm-shell://app/event-fields.js'],1)
report={'passed':True,'actualAssetFunctionCompiled':True,'resources':refs,'commands':rows,'sourceHeld':source.read_text()==s,'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'nativeLaunched':False,'nativeEngineLoadingProved':False};(o/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(o/'report.json')
