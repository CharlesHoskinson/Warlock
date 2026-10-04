import hashlib,json,resource,shlex,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];OWNER=REPO/'implementation/maximized-stack-v1/native-core-v2';PRIOR=REPO/'implementation/elm-core-seat-focus-restoration-v450/build-1791131758410759196';SOURCE=REPO/'implementation/elm-xdg-origin-render-input-v468/candidate'
OUT=ROOT/('compile-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parent=REPO/'implementation/elm-xdg-coordinate-design-held-v465/qa/slice-manifest.json';assert sha(parent)=='f72ae292632c0e1903a0eb3e0741adb266a546b5cae3835847c2ff5d462d3943'
for e in json.loads(parent.read_text())['files']:assert sha(REPO/e['path'])==e['sha256']
j=json.loads((PRIOR/'report.json').read_text());assert j['passed'];headers=j['owningHeaders'];assert len(headers)==694;tree=OUT/'owning-headers'
for rel,digest in headers.items():
 p=PRIOR/'owning-headers'/rel;assert sha(p)==digest;q=tree/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
db=OWNER/'build/compile_commands.json';entries=json.loads(db.read_text());sources=['src/render/pass/SurfacePassElement.cpp','src/render/ElementRenderer.cpp','src/desktop/state/ViewHitTester.cpp'];report={'passed':False,'nativeAcceptance':False,'scope':'Actual changed full-surface render/UV and inverse-input owning translation units; no core link or native correction acceptance','owningReport':str(PRIOR/'report.json'),'owningReportSHA256':sha(PRIOR/'report.json'),'owningHeaders':headers,'compileDatabaseSHA256':sha(db),'translationUnits':[]}
try:
 for rel in sources:
  source=SOURCE/rel;dest=tree/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest);original=OWNER/rel;entry=next(e for e in entries if Path(e['file'])==original);args=shlex.split(entry['command']);cmd=[];i=0
  while i<len(args):
   a=args[i]
   if a in ['-o','-include']:i+=2;continue
   if a=='-c':i+=1;continue
   if a==str(original):i+=1;continue
   if a.startswith('-I'+str(OWNER)) and '/build/' not in a and '/subprojects/' not in a:a='-I'+str(tree)+a[len('-I'+str(OWNER)):]
   cmd.append(a);i+=1
  stem=Path(rel).name;obj=OUT/(stem+'.o');dep=OUT/(stem+'.d');cmd+=['-MD','-MF',str(dep),'-o',str(obj),'-c',str(dest)]
  row={'source':str(source),'sourceSHA256':sha(source),'command':cmd};report['translationUnits'].append(row);result=subprocess.run(cmd,cwd=OWNER/'build',capture_output=True,timeout=240);(OUT/(stem+'.stdout')).write_bytes(result.stdout);(OUT/(stem+'.stderr')).write_bytes(result.stderr);row['exitCode']=result.returncode;assert result.returncode==0,stem
  names=shlex.split(dep.read_text().replace(chr(92)+chr(10),' ').split(':',1)[1]);deps={str((Path(n) if Path(n).is_absolute() else OWNER/'build'/n).resolve()):sha((Path(n) if Path(n).is_absolute() else OWNER/'build'/n).resolve()) for n in names};assert not any(n.startswith('/usr/include/hyprland') for n in deps)
  row.update(object=str(obj),objectSHA256=sha(obj),dependencies=deps);assert sha(source)==sha(dest)==row['sourceSHA256'];print(stem+' compiled',flush=True)
 for rel,digest in headers.items():assert sha(tree/rel)==digest
 report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
