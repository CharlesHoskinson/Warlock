import hashlib,json,resource,shlex,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];OWNER=REPO/'implementation/maximized-stack-v1/native-core-v2';PRIOR=REPO/'implementation/elm-core-xdg-origin-projection-v470/build-1791134095830955197'
OUT=ROOT/('compile-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
j=json.loads((PRIOR/'report.json').read_text());assert j['passed'];headers=j['owningHeaders'];assert len(headers)==694;tree=OUT/'owning-headers'
for rel,digest in headers.items():
 p=PRIOR/'owning-headers'/rel;assert sha(p)==digest;q=tree/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
source=REPO/'implementation/elm-keyboardless-focus-source-v200/candidate/src/managers/SeatManager.cpp';dest=tree/'src/managers/SeatManager.cpp';shutil.copy2(source,dest);original=OWNER/'src/managers/SeatManager.cpp';db=OWNER/'build/compile_commands.json';entry=next(e for e in json.loads(db.read_text()) if Path(e['file'])==original);args=shlex.split(entry['command']);cmd=[];i=0
while i<len(args):
 a=args[i]
 if a in ['-o','-include']:i+=2;continue
 if a=='-c':i+=1;continue
 if a==str(original):i+=1;continue
 if a.startswith('-I'+str(OWNER)) and '/build/' not in a and '/subprojects/' not in a:a='-I'+str(tree)+a[len('-I'+str(OWNER)):]
 cmd.append(a);i+=1
obj=OUT/'SeatManager.cpp.o';dep=OUT/'SeatManager.cpp.d';cmd+=['-MD','-MF',str(dep),'-o',str(obj),'-c',str(dest)]
r={'passed':False,'nativeAcceptance':False,'scope':'Full actual changed SeatManager translation unit against694 exact owning core470 headers; no compositor link/plugin ABI or native correction acceptance','source':str(source),'sourceSHA256':sha(source),'owningReport':str(PRIOR/'report.json'),'owningReportSHA256':sha(PRIOR/'report.json'),'owningHeaders':headers,'compileDatabaseSHA256':sha(db),'command':cmd}
try:
 result=subprocess.run(cmd,cwd=OWNER/'build',capture_output=True,timeout=240);(OUT/'compile.stdout').write_bytes(result.stdout);(OUT/'compile.stderr').write_bytes(result.stderr);r['exitCode']=result.returncode;assert result.returncode==0
 names=shlex.split(dep.read_text().replace(chr(92)+chr(10),' ').split(':',1)[1]);dependencies={str((Path(n) if Path(n).is_absolute() else OWNER/'build'/n).resolve()):sha((Path(n) if Path(n).is_absolute() else OWNER/'build'/n).resolve()) for n in names};assert not any(n.startswith('/usr/include/hyprland') for n in dependencies)
 for rel,digest in headers.items():assert sha(tree/rel)==digest
 assert sha(source)==sha(dest)==r['sourceSHA256'];r.update(passed=True,object=str(obj),objectSHA256=sha(obj),dependencies=dependencies)
except Exception as error:r['error']=repr(error)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
