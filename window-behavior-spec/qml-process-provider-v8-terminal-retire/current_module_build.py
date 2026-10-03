from pathlib import Path
import hashlib,json,stat,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent;A=B.with_name('qml-process-provider-v5-historical')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 require_qa_scope();prior=json.loads((A/'registry-product-negatives-build.json').read_text());assert prior['result']=='pass';core=['Lifetime.cpp','Popup.cpp','Seal.cpp','ProcessKernel.cpp','MappingDiagnostic.cpp','MappingWitness.cpp','MappingBatch.cpp','ProcessRegistry.cpp','moc_ProcessRelay.cpp','moc_ReloadRelay.cpp'];objects=[];reused={}
 for n in core:
  assert sha(A/n)==prior['sources'][str(A/n)] and (A/n).read_bytes()==(B/n).read_bytes();p=A/'process-build'/(n+'.o');reused[str(p)]=sha(p);objects.append(str(p))
 for p,h in prior['dependencies'].items():assert sha(p)==h
 flags=subprocess.check_output(['/usr/bin/pkg-config','--cflags','--libs','Qt6Core','Qt6Qml','Qt6Quick'],text=True).split();compileflags=[v for v in flags if not v.startswith('-l')];generated={str(B/n):sha(B/n) for n in ['moc_Provider.cpp','Provider.moc']};immutableBefore={str(p):sha(p)for p in B.iterdir()if p.is_file()and p.suffix in('.cpp','.hpp','.py')and p.name not in('moc_Provider.cpp','Provider.moc')};generation=[]
 for source,destination in [('Provider.hpp','moc_Provider.cpp'),('Provider.cpp','Provider.moc')]:
  c=['/usr/lib/qt6/moc',*compileflags,str(B/source),'-o',str(B/destination)];r=subprocess.run(c,capture_output=True,text=True,timeout=120);generation.append(dict(command=c,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0
 assert all(sha(p)==h for p,h in immutableBefore.items());before={str(p):sha(p)for p in B.iterdir()if p.is_file()and p.suffix in('.cpp','.hpp','.py','.moc')};build=B/'process-build';extra=['NativeProcess.cpp','Provider.cpp','moc_Provider.cpp'];commands=[['/usr/bin/clang++','-std=c++23','-O2','-Wall','-Wextra','-Werror','-fPIC','-pthread','-MD','-MF',str(build/(n+'.d')),'-c',str(B/n),'-o',str(build/(n+'.o')),*compileflags]for n in extra];commands += [['/usr/bin/clang++','-shared','-pthread','-Wl,-z,defs,-z,nodelete',*objects,*[str(build/(n+'.o'))for n in extra],'-o',str(B/'libobjectlifetime-process.so'),*flags,'-ldl'],['/usr/bin/clang++','-std=c++23','-O2','-Wall','-Wextra','-Werror','-fPIC','-pthread','-MD','-MF',str(build/'current_cpu_dso.d'),str(B/'cpu_dso.cpp'),'-o',str(B/'cpu-dso-current'),*flags,'-ldl']];rows=[]
 for c in commands:
  r=subprocess.run(c,capture_output=True,text=True,timeout=120);rows.append(dict(command=c,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr))
  if r.returncode:break
 stable=all(sha(p)==h for p,h in before.items())and all(sha(p)==h for p,h in reused.items());good=len(rows)==len(commands)and all(r['exitCode']==0 for r in rows)and stable;dependencies={}
 if good:
  dpaths=[A/'process-build'/(n+'.d')for n in core]+[build/(n+'.d')for n in extra]+[build/'current_cpu_dso.d']
  for p in dpaths:
   for name in p.read_text().replace('\\\n',' ').split(':',1)[1].split():dependencies[name]={'sha256':sha(name),'mode':stat.S_IMODE(Path(name).stat().st_mode)}
 row=dict(result='pass'if good else'fail',sources=before,sourceUnchanged=stable,reusedExactV5Objects=reused,inheritedCoreProofPath=str(A/'registry-product-negatives-build.json'),inheritedCoreProofSHA256=sha(A/'registry-product-negatives-build.json'),generationCommands=generation,generatedPreimages=generated,generatedAfter={p:sha(p)for p in generated},commands=rows,dependencies=dependencies,GUI=False,linkedNativeProcessAndRegistry=good,nodeleteLinked=True,noUndefinedSymbols=True,loaded=False)
 if good:row.update(binarySHA256=sha(B/'libobjectlifetime-process.so'),cpuDSOSHA256=sha(B/'cpu-dso-current'))
 p=B/('production-module-current-build.json'if good else f'production-current-build-failure-{time.time_ns()}.json');p.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(result=row['result'],report=str(p))));return int(not good)
if __name__=='__main__':raise SystemExit(main())
