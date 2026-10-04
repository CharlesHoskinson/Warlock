import hashlib,json,pathlib,resource,shlex,subprocess,sys,time,re
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('domains-build-'+str(time.time_ns()));OUT.mkdir();source=OUT/'qt-domains.cpp';source.write_bytes((ROOT/'native/qt-domains.cpp').read_bytes());report={'passed':False,'nativeAcceptance':False}
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
try:
 flags=shlex.split(subprocess.check_output(['/usr/bin/pkg-config','--cflags','--libs','Qt6Gui','Qt6GuiPrivate','xkbcommon'],text=True));binary=OUT/'qt-domains';command=['/usr/bin/c++','-std=c++17','-O2','-Wall','-Wextra','-Werror','-MD','-MF',str(OUT/'deps.d'),str(source),'-o',str(binary),*flags];p=subprocess.run(command,capture_output=True,timeout=45);(OUT/'compile.stderr').write_bytes(p.stderr);assert p.returncode==0
 constants=json.loads(subprocess.check_output([str(binary)],timeout=3));assert constants['qtVersion']=='6.11.2';assert constants['constants']['leftButton']>0
 ldd=subprocess.check_output(['/usr/bin/ldd',str(binary)],text=True,timeout=3);(OUT/'ldd.txt').write_text(ldd)
 paths=shlex.split((OUT/'deps.d').read_text().split(':',1)[1].replace('\\\n',' '));libs=re.findall(r'(?:=>\s+|^\s*)(/[^\s]+)',ldd,re.M)
 report.update(passed=True,compileCommand=command,dependencies={str(pathlib.Path(p).resolve()):sha(p) for p in paths},libraries={p:sha(p) for p in libs},tools={p:sha(p) for p in ['/usr/bin/c++','/usr/bin/pkg-config','/usr/bin/ldd']},constants=constants,binary=str(binary),binarySHA256=sha(binary),sourceSHA256=sha(source))
finally:
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json')
 if report['passed']:(ROOT/'qt-domains-build-report.json').write_text(json.dumps({'report':str(OUT/'report.json'),'sha256':sha(OUT/'report.json'),'binary':report['binary'],'binarySHA256':report['binarySHA256'],'constants':report['constants']['constants']},indent=2)+'\n')
