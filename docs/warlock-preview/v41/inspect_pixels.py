import pathlib,resource,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path(__file__).resolve().parent;d=r/'pixel-pairs';p=subprocess.run(['g++','-std=c++20','-O2','-Wall','-Wextra','-Werror',str(r/'pixel-pairs.cpp'),'-lpng','-o',str(d)],capture_output=True,text=True);assert p.returncode==0,p.stderr
base=r.parents[2]/'implementation/warlock-client-provider-native-v62/qa/native-1791269530323836731/private-evidence'
for tag in ['half','opaque']:
 p=subprocess.run([str(d),str(base/('config-opacity-'+tag+'.png')),str(base/('config-opacity-'+tag+'-native-output.png'))],capture_output=True,text=True);assert p.returncode==0,p.stderr;(r/('pairs-'+tag+'.txt')).write_text(p.stdout);print(tag,sorted(p.stdout.splitlines(),key=lambda line:int(line.split()[0]),reverse=True)[:12])
