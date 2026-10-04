"""Original unchanged compatibility and proposed profile guard CPU experiment."""
import hashlib,json,resource,shlex,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
OUT=ROOT/'qa'/('experiment-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
origin=json.loads((ROOT/'origin.json').read_text());OLD=Path(origin['source'])
for rel,w in origin['files'].items():assert sha(OLD/rel)==w,rel
assert sha(ROOT/'qa/projection-test.cpp')==origin['files']['qa/projection-test.cpp']
owner=REPO/'implementation/elm-parent-first-anchor-pair-v90/qa/build-1791107369559431070/report.json'
pair=json.loads(owner.read_text());library=Path('/usr/lib/libhyprutils.so.0.14.2');assert sha(library)==pair['linkedLibraries'][str(library)]
for rel in ['candidate/ProspectiveGeometry.hpp','qa/projection-test.cpp','qa/effective-test.cpp','qa/test.py','spec/REQUIREMENTS.md','origin.json']:
 p=ROOT/rel;target=OUT/'inputs'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
report={'passed':False,'scope':'EXPERIMENTAL proposed fixed-integer-axis guard only; no native, model, wire or broad policy acceptance','nativeAcceptance':False,'modelAcceptance':False,'policyAcceptance':False,'inputs':{rel:sha(ROOT/rel) for rel in ['candidate/ProspectiveGeometry.hpp','qa/projection-test.cpp','qa/effective-test.cpp','qa/test.py','spec/REQUIREMENTS.md','origin.json']},'runs':{}}
try:
 candidate=(ROOT/'candidate/ProspectiveGeometry.hpp').read_text();legacy=(OLD/'candidate/ProspectiveGeometry.hpp').read_text()
 guard='''    if(!variableConfigureAxis(input.raw.minimum.x,input.raw.maximum.x,input.layout.minimum.x,input.layout.maximum.x) ||
       !variableConfigureAxis(input.raw.minimum.y,input.raw.maximum.y,input.layout.minimum.y,input.layout.maximum.y))return std::nullopt;
'''
 assert candidate.count(guard)==1
 variants=[('original1710',legacy,'projection-test.cpp',0),('experimental1710',candidate,'projection-test.cpp',0),('effective-cases',candidate,'effective-test.cpp',0),
 ('unsafe-no-effective-guard',candidate.replace(guard,''),'effective-test.cpp',1),
 ('unsafe-singleton-allowed',candidate.replace('return lower<upper;','return lower<=upper;'),'effective-test.cpp',1),
 ('unsafe-ceil-real-layout-minimum',candidate.replace('std::floor(layoutMinimum)','std::ceil(layoutMinimum)'),'effective-test.cpp',1),
 ('unsafe-raw-upper-compares-real',candidate.replace('axis(configure.x,input.raw.minimum.x','axis(real.w,input.raw.minimum.x'),'effective-test.cpp',1)]
 for name,header,test,expected in variants:
  area=OUT/name;(area/'candidate').mkdir(parents=True);(area/'qa').mkdir()
  (area/'candidate/ProspectiveGeometry.hpp').write_text(header);shutil.copy2(OUT/'inputs/qa'/test,area/'qa'/test)
  binary=area/'test';command=['c++','-std=c++23','-O2','-Wall','-Wextra','-Werror','-MD','-MF',str(area/'dependencies.d'),str(area/'qa'/test),str(library),'-o',str(binary)]
  result=subprocess.run(command,capture_output=True,text=True,timeout=30);(area/'compile.stdout').write_text(result.stdout);(area/'compile.stderr').write_text(result.stderr);assert result.returncode==0,result.stderr
  result=subprocess.run([str(binary)],capture_output=True,text=True,timeout=3);(area/'checks.stdout').write_text(result.stdout);(area/'checks.stderr').write_text(result.stderr)
  report['runs'][name]={'exitCode':result.returncode,'expectedExitCode':expected,'command':command,'failedCases':[line[5:] for line in result.stdout.splitlines() if line.startswith('FAIL ')]}
  if name.endswith('1710'):
   if result.returncode==0:report['runs'][name]['checks']=int(result.stdout.split(': ')[1]);assert report['runs'][name]['checks']==1710
  else:report['runs'][name]['checks']=sum(line.startswith(('PASS ','FAIL ')) for line in result.stdout.splitlines())
  assert result.returncode==expected,name+' compatibility/experiment mismatch'
  if name=='effective-cases':
   deps=shlex.split((area/'dependencies.d').read_text().replace('\\\n',' ').split(':',1)[1])
   report['dependencies']={p:sha(Path(p)) for p in deps}
   for p,w in report['dependencies'].items():
    if '/hyprutils/' in p:assert w==pair['dependencies'][p],p
   linked=subprocess.check_output(['ldd',str(binary)],text=True);(area/'linked.stdout').write_text(linked)
   report['linkedLibraries']={p:sha(Path(p)) for line in linked.splitlines() for p in line.split() if p.startswith('/')}
 report['owningMath']={'report':str(owner),'reportSHA256':sha(owner),'library':str(library),'librarySHA256':sha(library)}
 assert sha(library)==pair['linkedLibraries'][str(library)]
 report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
