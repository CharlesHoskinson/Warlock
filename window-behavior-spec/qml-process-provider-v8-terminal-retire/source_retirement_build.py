from pathlib import Path
import hashlib,json,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
A=B.with_name('qml-process-provider-v5-historical')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 require_qa_scope();prior=json.loads((A/'registry-product-negatives-build.json').read_text());assert prior['result']=='pass';units=['Lifetime.cpp','Popup.cpp','Seal.cpp','ProcessKernel.cpp','MappingDiagnostic.cpp','MappingWitness.cpp','MappingBatch.cpp','ProcessRegistry.cpp','moc_ProcessRelay.cpp','moc_ReloadRelay.cpp'];objects=[];reused={}
 for n in units:
  assert sha(A/n)==prior['sources'][str(A/n)] and (B/n).read_bytes()==(A/n).read_bytes();p=A/'process-build'/(n+'.o');objects.append(str(p));reused[str(p)]=sha(p)
 for p,h in prior['dependencies'].items():assert sha(p)==h
 before={str(p):sha(p)for p in B.iterdir()if p.is_file()and p.suffix in('.cpp','.hpp','.py')};flags=subprocess.check_output(['/usr/bin/pkg-config','--cflags','--libs','Qt6Core','Qt6Qml','Qt6Quick'],text=True).split();compileflags=[v for v in flags if not v.startswith('-l')];build=B/'process-build';obj=build/'source_retirement_cpu.o';dep=build/'source_retirement_cpu.d';commands=[['/usr/bin/clang++','-std=c++23','-O2','-Wall','-Wextra','-Werror','-fPIC','-pthread','-MD','-MF',str(dep),'-c',str(B/'cpu_registry_product_negatives.cpp'),'-o',str(obj),*compileflags],['/usr/bin/clang++','-pthread',*objects,str(obj),'-o',str(B/'cpu-registry-product-negatives'),*flags,'-ldl']];rows=[]
 for c in commands:
  r=subprocess.run(c,capture_output=True,text=True,timeout=120);rows.append(dict(command=c,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr))
  if r.returncode:break
 stable=all(sha(p)==h for p,h in before.items())and all(sha(p)==h for p,h in reused.items());good=len(rows)==2 and all(r['exitCode']==0 for r in rows)and stable;deps={}
 if good:
  for name in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():deps[name]=sha(name)
 row=dict(result='pass'if good else'fail',sources=before,sourceUnchanged=stable,reusedExactV5Objects=reused,inheritedCoreProofSHA256=sha(A/'registry-product-negatives-build.json'),commands=rows,dependencies=deps,GUI=False,productionRuntimeExactV5=True)
 if good:row['binarySHA256']=sha(B/'cpu-registry-product-negatives')
 p=B/('registry-product-negatives-build.json'if good else f'source-retirement-build-failure-{time.time_ns()}.json');p.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(result=row['result'],report=str(p))));return int(not good)
if __name__=='__main__':raise SystemExit(main())
