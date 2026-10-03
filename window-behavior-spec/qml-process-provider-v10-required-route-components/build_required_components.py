from pathlib import Path
import hashlib,json,stat,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent;V=Path('/home/hoskinson/window-behavior-spec/qml-process-provider-v8-terminal-retire');Q=Path('/home/hoskinson/window-integration-qa')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin(p):return {'sha256':sha(p),'mode':stat.S_IMODE(Path(p).stat().st_mode)}
def main():
 require_qa_scope();handoff=Q/'process-terminal-required-routes-source-proposal-handoff-v1.json';grant=Q/'process-terminal-required-routes-root-source-grant-v1.json';assert sha(grant)=='ce92e155b1f4371e279835d20c76c9457d51065e0f55fad9716c67873c483b1c';ancestor=json.loads(handoff.read_text());assert all(sha(p)==h and stat.S_IMODE(Path(p).stat().st_mode)==ancestor['inputModes'][p]for p,h in ancestor['inputs'].items())
 for p in Path(ancestor['proposalRoot']).iterdir():assert (B/p.name).read_bytes()==p.read_bytes(),p
 inheritedPath=V/'terminal-module-build-v1.json';inherited=json.loads(inheritedPath.read_text());assert inherited['result']=='pass'
 core=['Lifetime.cpp','Popup.cpp','Seal.cpp','ProcessKernel.cpp','MappingDiagnostic.cpp','MappingWitness.cpp','MappingBatch.cpp','ProcessRegistry.cpp','moc_ProcessRelay.cpp','moc_ReloadRelay.cpp'];reused={};reusedDepfiles={};reusedDependencies={}
 for unit in core:
  assert sha(V/unit)==inherited['sources'][str(V/unit)];obj=V/'terminal-build'/(unit+'.o');dep=V/'terminal-build'/(unit+'.d');assert pin(obj)==inherited['objects'][str(obj)]and pin(dep)==inherited['depfiles'][str(dep)];reused[str(obj)]=pin(obj);reusedDepfiles[str(dep)]=pin(dep)
  for raw in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
   for p in {Path(raw),Path(raw).resolve(strict=True)}:assert pin(p)==inherited['dependencies'][str(p)];reusedDependencies[str(p)]=pin(p)
 for p,h in inherited['tools'].items():assert sha(p)==h
 module=V/'libobjectlifetime-process-terminal.so';assert sha(module)==inherited['outputs'][str(module)]
 flags=subprocess.check_output(['/usr/bin/pkg-config','--cflags','--libs','Qt6Core','Qt6Qml','Qt6Quick'],text=True).split();cf=[x for x in flags if not x.startswith('-l')];build=B/'component-build';build.mkdir(exist_ok=False)
 sources={str(p):sha(p)for p in B.iterdir()if p.is_file()and p.suffix in ['.cpp','.hpp','.py']};commands=[]
 for source,out in [('retire_process_fixture.cpp','retire_process_fixture.moc'),('cpu_typed_retire_adapter.hpp','moc_cpu_typed_retire_adapter.cpp')]:commands.append(['/usr/lib/qt6/moc',*cf,str(B/source),'-o',str(B/out)])
 units=['cpu_terminal_required_routes.cpp','moc_cpu_typed_retire_adapter.cpp','cpu_public_provider_retire_refusal.cpp','cpu_final_admission_primitive.cpp']
 for unit in units:commands.append(['/usr/bin/clang++','-std=c++23','-O2','-Wall','-Wextra','-Werror','-fPIC','-pthread','-MD','-MF',str(build/(unit+'.d')),'-c',str(B/unit),'-o',str(build/(unit+'.o')),*cf])
 def objs(names):return [str(build/(n+'.o'))for n in names]
 commands.append(['/usr/bin/clang++','-pthread',*list(reused),*objs(units[:2]),'-o',str(B/'cpu-terminal-required-routes'),*flags,'-ldl'])
 for unit,out in [(units[2],'cpu-public-provider-retire-refusal'),(units[3],'cpu-final-admission-primitive')]:commands.append(['/usr/bin/clang++','-pthread',*objs([unit]),'-o',str(B/out),*flags,'-ldl'])
 rows=[]
 for i,command in enumerate(commands):
  r=subprocess.run(command,capture_output=True,text=True,timeout=120);rows.append({'command':command,'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr});print(json.dumps({'step':i+1,'total':len(commands),'exitCode':r.returncode}),flush=True)
  if r.returncode:break
 good=len(rows)==len(commands)and all(r['exitCode']==0 for r in rows)and all(sha(p)==h for p,h in sources.items());dependencies={};depfiles={}
 for dep in build.glob('*.d'):
  depfiles[str(dep)]=pin(dep)
  for raw in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
   for p in {Path(raw),Path(raw).resolve(strict=True)}:dependencies[str(p)]=pin(p)
 outputs={str(B/n):sha(B/n)for n in ['cpu-terminal-required-routes','cpu-public-provider-retire-refusal','cpu-final-admission-primitive']if(B/n).exists()}
 row={'result':'pass'if good else'fail','sources':sources,'sourceModes':{p:stat.S_IMODE(Path(p).stat().st_mode)for p in sources},'commands':rows,'outputs':outputs,'outputModes':{p:stat.S_IMODE(Path(p).stat().st_mode)for p in outputs},'currentObjects':{str(p):pin(p)for p in build.glob('*.o')},'depfiles':depfiles,'dependencies':dependencies,'generatedMoc':{str(B/n):pin(B/n)for n in ['retire_process_fixture.moc','moc_cpu_typed_retire_adapter.cpp']if(B/n).exists()},'reusedObjects':reused,'reusedDepfiles':reusedDepfiles,'reusedDependencies':reusedDependencies,'reusedCoreUnitBodies':{str(V/u):pin(V/u)for u in core},'reusedBuildDescriptor':{'path':str(inheritedPath),**pin(inheritedPath)},'reusedCurrentProviderModule':{'path':str(module),**pin(module)},'toolImages':{str(Path(p).resolve()):pin(Path(p).resolve())for p in ['/usr/bin/clang++','/usr/lib/qt6/moc','/usr/bin/pkg-config','/usr/bin/ld']},'all1438ReviewedInputsExact':True,'ancestor':{'path':str(handoff),**pin(handoff)},'rootGrant':{'path':str(grant),**pin(grant)},'wholeModuleRebuilt':False,'productionChanged':False,'GUI':False}
 report=B/'terminal-module-build-v1.json';report.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps({'result':row['result'],'report':str(report)}));return int(not good)
if __name__=='__main__':raise SystemExit(main())
