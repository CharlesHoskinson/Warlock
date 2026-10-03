from pathlib import Path
import hashlib,json,os,stat,subprocess,sys,difflib
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent;W=B.parent;Q=Path('/home/hoskinson/window-integration-qa')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 require_qa_scope();inputs={};modes={};links={};mismatch=[];antecedents=[]
 def add(p):
  p=Path(os.path.abspath(p))
  for a in (p,*p.parents):
   if a.is_symlink():links[str(a)]=os.readlink(a)
  resolved=p.resolve(strict=True)
  for f in {p,resolved}:
   if f.is_file()and not f.is_symlink():inputs[str(f)]=sha(f);modes[str(f)]=stat.S_IMODE(f.stat().st_mode)
 def packet(p):
  add(p);r=json.loads(Path(p).read_text());antecedents.append({'path':str(p),'sha256':sha(p)})
  for n,h in r['inputs'].items():
   wanted=h if isinstance(h,str)else h['sha256'];mode=r.get('inputModes',{}).get(n)if isinstance(h,str)else h['mode'];f=Path(n)
   if sha(f)!=wanted or stat.S_IMODE(f.stat().st_mode)!=mode:mismatch.append(n)
   add(f)
  for n,t in r.get('symlinks',{}).items():
   if not Path(n).is_symlink()or os.readlink(n)!=t:mismatch.append(n)
   links[n]=t
 packet(W/'qml-process-provider-v3-scoped/scoped-source-checkpoint-inputs.json');packet(Q/'process-historical-v5-runtime-cpu-handoff-v1.json')
 for directory in ('mapping-device-semantics-v1','process-historical-closure-v1','process-fault-projection-v1'):
  for p in (W/directory).rglob('*'):
   if p.is_file():add(p)
 for p in B.iterdir():
  if p.is_file()and not p.name.startswith('current-source-ready')and(p.suffix in('.cpp','.hpp','.py','.md','.qnt','.json','.moc')or p.name in('qmldir','libobjectlifetime-process.so','cpu-dso-current','cpu-registry-product-negatives')):add(p)
 for p in (B/'module-loader-eight-char-runtime-failure').rglob('*'):
  if p.is_file():add(p)
 builds=[]
 for stage,name in [('qml-process-provider-v5-historical','registry-product-negatives-build.json'),('qml-process-provider-v6-source-retirement','production-module-current-build.json'),('qml-process-provider-v7-fault-projection','registry-product-negatives-build.json'),('qml-process-provider-v7-fault-projection','production-module-current-build.json')]:
  p=W/stage/name;r=json.loads(p.read_text());assert r['result']=='pass';add(p);builds.append({'path':str(p),'sha256':sha(p)})
  for field in ('sources','dependencies','reusedExactObjects','reusedExactV5Objects','reusedObjectSources'):
   for n,h in r.get(field,{}).items():
    wanted=h['sha256']if isinstance(h,dict)else h;assert sha(n)==wanted;add(n)
 for stage in ('qml-process-provider-v5-historical','qml-process-provider-v6-source-retirement'):
  for n in ('ProcessRegistry.cpp','ProcessRegistry.hpp','cpu_registry_product_negatives.cpp','registry_product_once.py','registry-product-negatives-build.json','production-module-current-build.json','CURRENT_RUNTIME_MAPPING.md'):
   p=W/stage/n
   if p.is_file():add(p)
 for review in ('process-scoped-v3-source-handoff-v1.json','process-historical-closure-root-design-review-v1.json','popup-v5-root-source-review-v1.json','process-parser-pointer-root-semantics-review-v1.json','process-async-current-witness-root-review-v1.json','mapping-source-scope-v4-root-source-review-v1.json','process-callback-rearm-root-source-review-v1.json'):add(Q/review)
 diffDir=Q/'process-current-v7-runtime-diff-v1';diffDir.mkdir(exist_ok=False)
 old=W/'qml-process-provider-v6-source-retirement';same=[];deltas=[]
 for p in sorted(B.glob('*.cpp'))+sorted(B.glob('*.hpp')):
  a=old/p.name
  if not a.is_file():continue
  if a.read_bytes()==p.read_bytes():same.append(p.name)
  else:
   output=diffDir/(p.name+'.diff');output.write_text(''.join(difflib.unified_diff(a.read_text().splitlines(True),p.read_text().splitlines(True),fromfile=str(a),tofile=str(p))));add(output);deltas.append(p.name)
 assert deltas==['ProcessRegistry.cpp','cpu_registry_product_negatives.cpp'];before=(old/'ProcessRegistry.cpp').read_text();after=(B/'ProcessRegistry.cpp').read_text();a=after.index('void ProcessRegistry::callback(');z=after.index('void ProcessRegistry::event(',a);part=after[a:z];assert part.count('r->fault=true;r->kernel=false;r->accepted=false;r->normalLife=false;')==2;inverse=after[:a]+part.replace('r->fault=true;r->kernel=false;r->accepted=false;r->normalLife=false;','r->fault=true;r->accepted=false;r->normalLife=false;')+after[z:];assert inverse==before
 loader=[]
 for n in ('libobjectlifetime-process.so','cpu-registry-product-negatives','cpu-dso-current'):
  p=B/n;r=subprocess.run(['/usr/bin/ldd',str(p)],capture_output=True,text=True,timeout=30);assert r.returncode==0;loader.append({'path':str(p),'stdout':r.stdout,'stderr':r.stderr});add(p)
  for word in r.stdout.split():
   if word.startswith('/'):add(word)
 proofs=[W/'qml-process-provider-v5-historical'/n for n in ('registry-product-pending-retire-1790974246678344905.json','registry-product-pending-context-retire-1790974253595577130.json','registry-product-duplicate-worker-notification-1790974260445873733.json')]+[W/'qml-process-provider-v6-source-retirement/registry-product-pending-source-retire-1790975291137135450.json',B/'registry-product-duplicate-eof-1790975786956516094.json',B/'production-module-current-lifecycle-1790975899053128801.json'];evidence=[]
 for p in proofs:
  r=json.loads(p.read_text());assert r['result']=='pass';add(p);evidence.append({'path':str(p),'sha256':sha(p)})
 source=B/'current-source-ready-inputs.json';source.write_text(json.dumps(dict(inputs=inputs,inputModes=modes,symlinks=links,loader=loader,antecedents=antecedents,builds=builds,actualEvidence=evidence,currentLibrary=str(B/'libobjectlifetime-process.so'),currentLibrarySHA256=sha(B/'libobjectlifetime-process.so'),currentRuntimeDeltaFiles=deltas,unchangedCPPHeaders=same,twoFaultAssignmentsSourceInverseExact=True,GUI=False,frozen=False,nativeReady=False,reliabilityAccepted=False),indent=2)+'\n')
 report=dict(result='source-ready'if not mismatch else'fail',packet=str(source),packetSHA256=sha(source),inputs=len(inputs),modes=len(modes),links=len(links),mismatch=mismatch,currentLibrarySHA256=sha(B/'libobjectlifetime-process.so'),actualEvidence=evidence,rootSourceReviewPending=True,GUI=False,frozen=False,nativeReady=False,reliabilityAccepted=False,actualChangedCommandReuseAccepted=False,actualInstalledQSProcessAccepted=False,pastBaselineFailureCauseUnknown=True)
 (B/'current-source-ready.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));return int(bool(mismatch))
if __name__=='__main__':raise SystemExit(main())
