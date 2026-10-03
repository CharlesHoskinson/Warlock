from pathlib import Path
import hashlib,json,stat,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 require_qa_scope();before={str(p):sha(p)for p in B.iterdir()if p.is_file()and p.suffix in('.cpp','.hpp','.py')};prior=json.loads((B/'registry-product-negatives-build.json').read_text());core=['Lifetime.cpp','Popup.cpp','Seal.cpp','ProcessKernel.cpp','MappingDiagnostic.cpp','MappingWitness.cpp','MappingBatch.cpp','ProcessRegistry.cpp','moc_ProcessRelay.cpp','moc_ReloadRelay.cpp'];build=B/'process-build';flags=subprocess.check_output(['/usr/bin/pkg-config','--cflags','--libs','Qt6Core','Qt6Qml','Qt6Quick'],text=True).split();mocflags=[v for v in flags if not v.startswith('-l')]
 for n in core:assert sha(B/n)==prior['sources'][str(B/n)]
 for p,h in prior['dependencies'].items():assert sha(p)==h
 commands=[['/usr/lib/qt6/moc',*mocflags,str(B/'Provider.hpp'),'-o',str(B/'moc_Provider.cpp')],['/usr/lib/qt6/moc',*mocflags,str(B/'Provider.cpp'),'-o',str(B/'Provider.moc')]]
 extra=['NativeProcess.cpp','Provider.cpp','moc_Provider.cpp'];commands += [['/usr/bin/clang++','-std=c++23','-O2','-Wall','-Wextra','-Werror','-fPIC','-pthread','-MD','-MF',str(build/(n+'.d')),'-c',str(B/n),'-o',str(build/(n+'.o')),*mocflags]for n in extra];commands += [['/usr/bin/clang++','-shared','-pthread','-Wl,-z,defs,-z,nodelete',*[str(build/(n+'.o'))for n in core+extra],'-o',str(B/'libobjectlifetime-process.so'),*flags,'-ldl']];rows=[]
 for c in commands:
  r=subprocess.run(c,capture_output=True,text=True,timeout=120);rows.append(dict(command=c,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr))
  if r.returncode:break
 stable=all(sha(p)==h for p,h in before.items());good=len(rows)==len(commands)and all(r['exitCode']==0 for r in rows)and stable;dependencies={}
 if good:
  for n in core+extra:
   p=build/(n+'.d')
   for name in p.read_text().replace('\\\n',' ').split(':',1)[1].split():dependencies[name]={'sha256':sha(name),'mode':stat.S_IMODE(Path(name).stat().st_mode)}
 row=dict(result='pass'if good else'fail',sources=before,sourceUnchanged=stable,commands=rows,dependencies=dependencies,inheritedActualCoreBuild=prior,GUI=False,nativeLoaded=False,linkedNativeProcessAndRegistry=good,noUndefinedSymbols=True,nodeleteLinked=True)
 if good:row['binarySHA256']=sha(B/'libobjectlifetime-process.so')
 p=B/('production-module-build.json'if good else f'production-module-failure-{time.time_ns()}.json');p.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(result=row['result'],report=str(p))));return int(not good)
if __name__=='__main__':raise SystemExit(main())
