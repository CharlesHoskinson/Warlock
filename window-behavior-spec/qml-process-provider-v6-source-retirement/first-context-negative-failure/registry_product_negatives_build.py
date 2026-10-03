from pathlib import Path
import hashlib,json,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 require_qa_scope();before={str(p):sha(p)for p in B.iterdir()if p.suffix in('.cpp','.hpp','.py')};flags=subprocess.check_output(['/usr/bin/pkg-config','--cflags','--libs','Qt6Core','Qt6Qml','Qt6Quick'],text=True).split();mocflags=[v for v in flags if not v.startswith('-l')];build=B/'process-build';build.mkdir(exist_ok=True)
 commands=[['/usr/lib/qt6/moc',*mocflags,str(B/n),'-o',str(B/output)]for n,output in [('ProcessRelay.hpp','moc_ProcessRelay.cpp'),('ReloadRelay.hpp','moc_ReloadRelay.cpp'),('cpu_process_runtime.cpp','cpu_process_runtime.moc')]]
 units=['Lifetime.cpp','Popup.cpp','Seal.cpp','ProcessKernel.cpp','MappingDiagnostic.cpp','MappingWitness.cpp','MappingBatch.cpp','ProcessRegistry.cpp','moc_ProcessRelay.cpp','moc_ReloadRelay.cpp','cpu_registry_product_negatives.cpp']
 commands += [['/usr/bin/clang++','-std=c++23','-O2','-Wall','-Wextra','-Werror','-fPIC','-pthread','-MD','-MF',str(build/(n+'.d')),'-c',str(B/n),'-o',str(build/(n+'.o')),*mocflags]for n in units]
 commands += [['/usr/bin/clang++','-pthread',*[str(build/(n+'.o'))for n in units],'-o',str(B/'cpu-registry-product-negatives'),*flags,'-ldl']]
 rows=[]
 for c in commands:
  r=subprocess.run(c,capture_output=True,text=True,timeout=120);rows.append(dict(command=c,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr))
  if r.returncode:break
 stable=all(sha(p)==h for p,h in before.items());good=len(rows)==len(commands)and all(r['exitCode']==0 for r in rows)and stable;row=dict(result='pass'if good else'fail',sourceUnchanged=stable,sources=before,commands=rows,GUI=False)
 if good:
  deps={}
  for p in build.glob('*.d'):
   for name in p.read_text().replace('\\\n',' ').split(':',1)[1].split():deps[name]=sha(name)
  row['dependencies']=deps;row['binarySHA256']=sha(B/'cpu-registry-product-negatives')
 p=B/('registry-product-negatives-build.json'if good else f'product-async-build-failure-{time.time_ns()}.json');p.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(result=row['result'],report=str(p))));return int(not good)
if __name__=='__main__':raise SystemExit(main())
