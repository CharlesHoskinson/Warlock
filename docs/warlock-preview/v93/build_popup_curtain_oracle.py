"""Build and retain independent region decoder through protected CPU QA."""
import hashlib,json,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
base=pathlib.Path(__file__).parent;out=base/('curtain-oracle-build-'+str(time.time_ns()));out.mkdir();source=base/'popup-curtain-oracle.cpp';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest();shutil.copy2(source,out/source.name)
r={'passed':False,'inputs':{str(source):sha(source)},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Independent bounded PNG region decoder build and checks against previously held actual output/renderer snapshots. This does not qualify an actual native curtain, geometry, frame, negative control or physical reveal.'}
def run(name,args):
 p=subprocess.run(args,capture_output=True,text=True,timeout=120);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);r['commands'].append({'name':name,'args':args,'exitCode':p.returncode});assert p.returncode==0,p.stderr;return p.stdout
try:
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','libpng']));run('build',['g++','-std=c++20','-O2','-Wall','-Wextra','-Werror','-MD','-MF',str(out/'oracle.d'),str(out/source.name),'-o',str(out/'popup-curtain-oracle'),*flags])
 native=base.parents[2]/'implementation/warlock-client-provider-native-v137/qa/native-controlled-1791384978375197831/private-evidence'
 for name,image,region in [('closed-output',native/'controlled-wayland-output.png',[58,96,684,364]),('rendered-source',native/'controlled-webkit.png',[8,48,684,364])]:
  r['inputs'][str(image)]=sha(image);pixels=json.loads(run(name,[str(out/'popup-curtain-oracle'),str(image),*map(str,region)]));r[name]=pixels
 assert r['closed-output']['red']==0 and r['closed-output']['green']==0 and r['rendered-source']['red']==19200
 deps=shlex.split((out/'oracle.d').read_text().replace('\\\n',' ').split(':',1)[1]);r['compilerDependencies']={str(pathlib.Path(p).absolute()):sha(p) for p in sorted(set(deps))}
 libs=run('libraries',['ldd',str(out/'popup-curtain-oracle')]);r['linkedLibraries']={}
 for line in libs.splitlines():
  fields=line.split();p=fields[fields.index('=>')+1] if '=>' in fields else fields[0] if fields else ''
  if p.startswith('/'):r['linkedLibraries'][p]=sha(p)
 r['tools']={shutil.which(name):sha(shutil.which(name)) for name in ['g++','pkg-config','ldd']};assert all(sha(p)==h for p,h in r['inputs'].items());r['passed']=True
except Exception as error:r['error']=repr(error)
r['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(out/'report.json'),'error':r.get('error','')}));sys.exit(not r['passed'])
