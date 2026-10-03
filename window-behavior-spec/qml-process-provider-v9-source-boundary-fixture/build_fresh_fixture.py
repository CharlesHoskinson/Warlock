from pathlib import Path
import hashlib,json,os,stat,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
V=Path('/home/hoskinson/window-behavior-spec/qml-process-provider-v8-terminal-retire')
Q=Path('/home/hoskinson/window-integration-qa')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin(p):return {'sha256':sha(p),'mode':stat.S_IMODE(Path(p).stat().st_mode)}
def main():
 require_qa_scope()
 handoff=Q/'process-disconnect-fixture-v3-evidence-source-handoff-v1.json';grant=Q/'process-disconnect-fixture-v3-root-source-grant-v1.json'
 assert sha(grant)=='f1e808e2995f04988da7847317a300bd6fe02bba074ffef7f7e88b3465c0c642'
 ancestor=json.loads(handoff.read_text());assert all(sha(p)==h and stat.S_IMODE(Path(p).stat().st_mode)==ancestor['inputModes'][p]for p,h in ancestor['inputs'].items())
 for f in ['cpu_retire_product_disconnect.cpp','retire_process_fixture.cpp','terminal_product_once.py']:
  assert (B/f).read_bytes()==(Path(ancestor['proposalRoot'])/f).read_bytes()
 inheritedPath=V/'terminal-module-build-v1.json';inherited=json.loads(inheritedPath.read_text());assert inherited['result']=='pass'
 core=['Lifetime.cpp','Popup.cpp','Seal.cpp','ProcessKernel.cpp','MappingDiagnostic.cpp','MappingWitness.cpp','MappingBatch.cpp','ProcessRegistry.cpp','moc_ProcessRelay.cpp','moc_ReloadRelay.cpp']
 reused={};reusedDepfiles={};reusedDependencies={}
 for unit in core:
  assert sha(V/unit)==inherited['sources'][str(V/unit)]
  obj=V/'terminal-build'/(unit+'.o');dep=V/'terminal-build'/(unit+'.d')
  assert pin(obj)==inherited['objects'][str(obj)] and pin(dep)==inherited['depfiles'][str(dep)]
  reused[str(obj)]=pin(obj);reusedDepfiles[str(dep)]=pin(dep)
  for raw in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
   for path in {Path(raw),Path(raw).resolve(strict=True)}:
    assert pin(path)==inherited['dependencies'][str(path)];reusedDependencies[str(path)]=pin(path)
 for p,h in inherited['tools'].items():assert sha(p)==h
 flags=subprocess.check_output(['/usr/bin/pkg-config','--cflags','--libs','Qt6Core','Qt6Qml','Qt6Quick'],text=True).split();cf=[x for x in flags if not x.startswith('-l')]
 build=B/'fixture-build';build.mkdir(exist_ok=False)
 c1=['/usr/lib/qt6/moc',*cf,str(B/'retire_process_fixture.cpp'),'-o',str(B/'retire_process_fixture.moc')]
 unit=B/'cpu_retire_product_disconnect.cpp';obj=build/'cpu_retire_product_disconnect.cpp.o';dep=build/'cpu_retire_product_disconnect.cpp.d';output=B/'cpu-terminal-disconnect'
 commands=[c1,['/usr/bin/clang++','-std=c++23','-O2','-Wall','-Wextra','-Werror','-fPIC','-pthread','-MD','-MF',str(dep),'-c',str(unit),'-o',str(obj),*cf],['/usr/bin/clang++','-pthread',*list(reused),str(obj),'-o',str(output),*flags,'-ldl']]
 sources={str(p):sha(p)for p in B.iterdir()if p.is_file()and p.suffix in ['.cpp','.hpp','.py']};rows=[]
 for i,command in enumerate(commands):
  r=subprocess.run(command,capture_output=True,text=True,timeout=120);rows.append({'command':command,'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr});print(json.dumps({'step':i+1,'exitCode':r.returncode}),flush=True)
  if r.returncode:break
 good=len(rows)==3 and all(r['exitCode']==0 for r in rows)and all(sha(p)==h for p,h in sources.items());dependencies={}
 if dep.exists():
  for raw in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
   for p in {Path(raw),Path(raw).resolve(strict=True)}:dependencies[str(p)]=pin(p)
 row={'result':'pass'if good else'fail','sources':sources,'sourceModes':{p:stat.S_IMODE(Path(p).stat().st_mode)for p in sources},'commands':rows,'outputs':{str(output):sha(output)}if output.exists()else{},'outputModes':{str(output):stat.S_IMODE(output.stat().st_mode)}if output.exists()else{},'generatedMoc':pin(B/'retire_process_fixture.moc')if(B/'retire_process_fixture.moc').exists()else None,'currentObject':{str(obj):pin(obj)}if obj.exists()else{},'currentDepfile':{str(dep):pin(dep)}if dep.exists()else{},'dependencies':dependencies,'reusedObjects':reused,'reusedDepfiles':reusedDepfiles,'reusedDependencies':reusedDependencies,'reusedCoreUnitBodies':{str(V/u):pin(V/u)for u in core},'reusedBuildDescriptor':{'path':str(inheritedPath),**pin(inheritedPath)},'toolImages':{str(Path(p).resolve(strict=True)):pin(Path(p).resolve(strict=True))for p in ['/usr/bin/clang++','/usr/lib/qt6/moc','/usr/bin/pkg-config','/usr/bin/ld']},'all1257ReviewedInputsExact':True,'ancestor':{'path':str(handoff),**pin(handoff)},'rootGrant':{'path':str(grant),**pin(grant)},'wholeModuleRebuilt':False,'productionChanged':False,'GUI':False}
 report=B/'terminal-module-build-v1.json';report.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps({'result':row['result'],'report':str(report)}));return int(not good)
if __name__=='__main__':raise SystemExit(main())
