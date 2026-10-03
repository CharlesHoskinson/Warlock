from pathlib import Path
import hashlib,json,stat,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent;A=B.with_name('qml-process-provider-v6-source-retirement');C=B.with_name('qml-process-provider-v5-historical')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 require_qa_scope();prior=json.loads((A/'production-module-current-build.json').read_text());current=json.loads((B/'registry-product-negatives-build.json').read_text());assert prior['result']=='pass' and current['result']=='pass';sources={};objects={};deps={}
 core=['Lifetime.cpp','Popup.cpp','Seal.cpp','ProcessKernel.cpp','MappingDiagnostic.cpp','MappingWitness.cpp','MappingBatch.cpp','moc_ProcessRelay.cpp','moc_ReloadRelay.cpp'];extra=['NativeProcess.cpp','Provider.cpp','moc_Provider.cpp'];units=[(C,n)for n in core]+[(A,n)for n in extra]+[(B,'ProcessRegistry.cpp')]
 for directory,n in units:
  assert (directory/n).read_bytes()==(B/n).read_bytes();p=directory/'process-build'/(n+'.o');objects[str(p)]=sha(p);sources[str(directory/n)]=sha(directory/n);dep=directory/'process-build'/(n+'.d')
  for name in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():deps[name]={'sha256':sha(name),'mode':stat.S_IMODE(Path(name).stat().st_mode)}
 for p,h in current['sources'].items():assert sha(p)==h
 for p,h in prior['sources'].items():assert sha(p)==h
 for p,h in prior['dependencies'].items():assert sha(p)==h['sha256']
 for p,h in current['dependencies'].items():assert sha(p)==h
 before={str(p):sha(p)for p in B.iterdir()if p.is_file()and p.suffix in('.cpp','.hpp','.py','.moc')};flags=subprocess.check_output(['/usr/bin/pkg-config','--cflags','--libs','Qt6Core','Qt6Qml','Qt6Quick'],text=True).split();command=['/usr/bin/clang++','-shared','-pthread','-Wl,-z,defs,-z,nodelete',*objects,'-o',str(B/'libobjectlifetime-process.so'),*flags,'-ldl'];r=subprocess.run(command,capture_output=True,text=True,timeout=120);stable=all(sha(p)==h for p,h in before.items())and all(sha(p)==h for p,h in objects.items());good=r.returncode==0 and stable;row=dict(result='pass'if good else'fail',sources=before,reusedExactObjects=objects,reusedObjectSources=sources,sourceUnchanged=stable,commands=[dict(command=command,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr)],dependencies=deps,GUI=False,linkedNativeProcessAndRegistry=good,loaded=False,nodeleteLinked=True,noUndefinedSymbols=True,inheritedV6ModuleProofSHA256=sha(A/'production-module-current-build.json'),currentActualCoreProofSHA256=sha(B/'registry-product-negatives-build.json'))
 if good:row.update(binarySHA256=sha(B/'libobjectlifetime-process.so'),cpuDSOSHA256=sha(B/'cpu-dso-current'))
 path=B/('production-module-current-build.json'if good else f'production-relink-failure-{time.time_ns()}.json');path.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(result=row['result'],report=str(path))));return int(not good)
if __name__=='__main__':raise SystemExit(main())
