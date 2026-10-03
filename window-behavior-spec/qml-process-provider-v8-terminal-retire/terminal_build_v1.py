from pathlib import Path
import hashlib,json,os,stat,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 require_qa_scope();build=B/'terminal-build';build.mkdir(exist_ok=False);pre=build/'generated-preimages';pre.mkdir();flags=subprocess.check_output(['/usr/bin/pkg-config','--cflags','--libs','Qt6Core','Qt6Qml','Qt6Quick'],text=True).split();cf=[x for x in flags if not x.startswith('-l')]
 core=['Lifetime.cpp','Popup.cpp','Seal.cpp','ProcessKernel.cpp','MappingDiagnostic.cpp','MappingWitness.cpp','MappingBatch.cpp','ProcessRegistry.cpp','moc_ProcessRelay.cpp','moc_ReloadRelay.cpp'];module=core+['NativeProcess.cpp','Provider.cpp','moc_Provider.cpp'];rows=[];generation=[]
 for source,out in [('ProcessRelay.hpp','moc_ProcessRelay.cpp'),('ReloadRelay.hpp','moc_ReloadRelay.cpp'),('Provider.hpp','moc_Provider.cpp'),('Provider.cpp','Provider.moc'),('cpu_process_runtime.cpp','cpu_process_runtime.moc'),('retire_process_fixture.cpp','retire_process_fixture.moc')]:
  p=B/out
  if p.exists():(pre/out).write_bytes(p.read_bytes())
  c=['/usr/lib/qt6/moc',*cf,str(B/source),'-o',str(p)];r=subprocess.run(c,capture_output=True,text=True,timeout=120);generation.append(dict(command=c,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0,generation[-1]
 before={str(p):sha(p)for p in B.iterdir()if p.is_file()and p.suffix in('.cpp','.hpp','.py','.moc')};commands=[]
 for n in module+['cpu_registry_product_negatives.cpp','cpu_retire_product_disconnect.cpp','cpu_dso.cpp']:
  commands.append(['/usr/bin/clang++','-std=c++23','-O2','-Wall','-Wextra','-Werror','-fPIC','-pthread','-MD','-MF',str(build/(n+'.d')),'-c',str(B/n),'-o',str(build/(n+'.o')),*cf])
 def objects(names):return [str(build/(n+'.o'))for n in names]
 commands += [['/usr/bin/clang++','-shared','-pthread','-Wl,-z,defs,-z,nodelete',*objects(module),'-o',str(B/'libobjectlifetime-process-terminal.so'),*flags,'-ldl']]
 for unit,out in [('cpu_registry_product_negatives.cpp','cpu-terminal-product'),('cpu_retire_product_disconnect.cpp','cpu-terminal-disconnect')]:commands.append(['/usr/bin/clang++','-pthread',*objects(core+[unit]),'-o',str(B/out),*flags,'-ldl'])
 commands.append(['/usr/bin/clang++',*objects(['cpu_dso.cpp']),'-o',str(B/'cpu-terminal-dso'),*flags,'-ldl'])
 for i,c in enumerate(commands):
  r=subprocess.run(c,capture_output=True,text=True,timeout=120);rows.append(dict(command=c,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr));print(json.dumps({'buildStep':i+1,'total':len(commands),'exitCode':r.returncode}),flush=True)
  if r.returncode:break
 stable=all(sha(p)==h for p,h in before.items());good=stable and len(rows)==len(commands)and all(r['exitCode']==0 for r in rows);deps={};depfiles={}
 for p in sorted(build.glob('*.d')):
  depfiles[str(p)]={'sha256':sha(p),'mode':stat.S_IMODE(p.stat().st_mode)}
  for raw in p.read_text().replace('\\\n',' ').split(':',1)[1].split():
   for n in {Path(raw),Path(raw).resolve(strict=True)}:deps[str(n)]={'sha256':sha(n),'mode':stat.S_IMODE(n.stat().st_mode)}
 outputs=['libobjectlifetime-process-terminal.so','cpu-terminal-product','cpu-terminal-disconnect','cpu-terminal-dso'];row={'result':'pass'if good else'fail','sources':before,'sourceUnchanged':stable,'generationCommands':generation,'commands':rows,'dependencies':deps,'depfiles':depfiles,'objects':{str(p):{'sha256':sha(p),'mode':stat.S_IMODE(p.stat().st_mode)}for p in build.glob('*.o')},'tools':{str(Path(p).resolve()):sha(Path(p).resolve())for p in ['/usr/bin/clang++','/usr/lib/qt6/moc','/usr/bin/pkg-config','/usr/bin/ld']},'outputs':{str(B/n):sha(B/n)for n in outputs if(B/n).exists()},'GUI':False,'nativeLoaded':False,'currentSourcesBuilt':True,'reusedV7Objects':False}
 target=B/('terminal-module-build-v1.json'if good else f'terminal-build-failure-{time.time_ns()}.json');target.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps({'result':row['result'],'report':str(target)}));return int(not good)
if __name__=='__main__':raise SystemExit(main())
