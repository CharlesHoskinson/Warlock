from pathlib import Path
import hashlib,json,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 require_qa_scope();prior=json.loads((B/'registry-product-negatives-build.json').read_text());allowed={'cpu_registry_product_negatives.cpp','registry_negative_incremental.py'};units=['Lifetime.cpp','Popup.cpp','Seal.cpp','ProcessKernel.cpp','MappingDiagnostic.cpp','MappingWitness.cpp','MappingBatch.cpp','ProcessRegistry.cpp','moc_ProcessRelay.cpp','moc_ReloadRelay.cpp','cpu_registry_product_negatives.cpp'];build=B/'process-build';before={str(p):sha(p)for p in B.iterdir()if p.is_file()and p.suffix in('.cpp','.hpp','.py')}
 for n in units[:-1]:assert sha(B/n)==prior['sources'][str(B/n)]
 # Every prior production header and tool source remains exact; only CPU test can change.
 for p,h in prior['sources'].items():
  if Path(p).name not in allowed:assert sha(p)==h
 flags=subprocess.check_output(['/usr/bin/pkg-config','--cflags','--libs','Qt6Core','Qt6Qml','Qt6Quick'],text=True).split();mocflags=[v for v in flags if not v.startswith('-l')];commands=[['/usr/bin/clang++','-std=c++23','-O2','-Wall','-Wextra','-Werror','-fPIC','-pthread','-MD','-MF',str(build/'cpu_registry_product_negatives.cpp.d'),'-c',str(B/'cpu_registry_product_negatives.cpp'),'-o',str(build/'cpu_registry_product_negatives.cpp.o'),*mocflags],['/usr/bin/clang++','-pthread',*[str(build/(n+'.o'))for n in units],'-o',str(B/'cpu-registry-product-negatives'),*flags,'-ldl']];rows=[]
 for c in commands:
  r=subprocess.run(c,capture_output=True,text=True,timeout=120);rows.append(dict(command=c,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr))
  if r.returncode:break
 good=len(rows)==2 and all(r['exitCode']==0 for r in rows)and all(sha(p)==h for p,h in before.items());deps={}
 if good:
  for p in build.glob('*.d'):
   for name in p.read_text().replace('\\\n',' ').split(':',1)[1].split():deps[name]=sha(name)
 row=dict(result='pass'if good else'fail',sourceUnchanged=all(sha(p)==h for p,h in before.items()),sources=before,commands=rows,dependencies=deps,binarySHA256=sha(B/'cpu-registry-product-negatives')if good else None,GUI=False,inheritedProductionBuild=prior,onlyCPUNegativeChanged=True)
 p=B/('registry-product-negatives-build.json'if good else f'registry-incremental-failure-{time.time_ns()}.json');p.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(result=row['result'],report=str(p))));return int(not good)
if __name__=='__main__':raise SystemExit(main())
