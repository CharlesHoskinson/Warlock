from pathlib import Path
import hashlib,json,os,stat,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent;Q=Path('/home/hoskinson/window-integration-qa');W=B.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 require_qa_scope();inputs={};modes={};links={};mismatch=[]
 def add(p):
  p=Path(os.path.abspath(p))
  for a in (p,*p.parents):
   if a.is_symlink():links[str(a)]=os.readlink(a)
  resolved=p.resolve(strict=True)
  for q in {p,resolved}:
   if q.is_file()and not q.is_symlink():inputs[str(q)]=sha(q);modes[str(q)]=stat.S_IMODE(q.stat().st_mode)
 def packet(p):
  add(p);r=json.loads(Path(p).read_text())
  for n,h in r['inputs'].items():
   mode=r.get('inputModes',{}).get(n)if isinstance(h,str)else h['mode'];wanted=h if isinstance(h,str)else h['sha256'];f=Path(n)
   if sha(f)!=wanted or stat.S_IMODE(f.stat().st_mode)!=mode:mismatch.append(n)
   add(f)
  for n,t in r.get('symlinks',r.get('links',{})).items():
   if not Path(n).is_symlink()or os.readlink(n)!=t:mismatch.append(n)
   links[n]=t
 packet(W/'qml-object-lifetime-v5-popup/source-ready-inputs.json')
 for p in B.iterdir():
  if p.is_file()and(p.suffix in('.cpp','.hpp','.py','.md','.qnt','.json')or p.name in('qmldir','Provider.moc','libobjectlifetime-process.so','cpu-product-capture','cpu-registry-product-negatives','cpu-source-aliases'))and not p.name.startswith('scoped-source-checkpoint'):add(p)
 for directory in ('before-scoped-runtime','first-scoped-fast-positive-source','first-context-negative-failure','context-diagnostic-baseline-failure'):
  for p in (B/directory).iterdir():
   if p.is_file():add(p)
 for n in ('production-module-build.json','registry-product-negatives-build.json'):
  row=json.loads((B/n).read_text());assert row['result']=='pass'
  if n=='production-module-build.json':assert all(sha(p)==h for p,h in row['sources'].items())
  for p,h in row['dependencies'].items():
   wanted=h['sha256']if isinstance(h,dict)else h;assert sha(p)==wanted;add(p)
 for rel in ('process-parser-pointer-root-semantics-review-v1.json','process-async-current-witness-root-review-v1.json','process-current-witness-root-model-review-v1.json','mapping-source-scope-v4-root-source-review-v1.json','process-callback-rearm-root-source-review-v1.json','popup-v5-root-source-review-v1.json'):add(Q/rel)
 for rel in ('process-callback-thread-v2-rearm','mapping-source-scope-v4','mapping-current-witness-v3-async'):
  for p in (W/rel).iterdir():
   if p.is_file():add(p)
 for n in ('qa_run.py','qa_launch.py'):add(Q/n)
 for p in (W/'pin-lifetime-v3/frontend').glob('*.py'):add(p)
 loader=[]
 for n in ('libobjectlifetime-process.so','cpu-product-capture','cpu-registry-product-negatives','cpu-source-aliases'):
  p=B/n;r=subprocess.run(['/usr/bin/ldd',str(p)],capture_output=True,text=True,timeout=30);assert r.returncode==0;loader.append(dict(path=str(p),stdout=r.stdout,stderr=r.stderr));add(p)
  for word in r.stdout.split():
   if word.startswith('/'):add(word)
 out=B/'scoped-source-checkpoint-inputs.json';out.write_text(json.dumps(dict(inputs=inputs,inputModes=modes,symlinks=links,loader=loader,GUI=False,nativeReady=False,frozen=False,fullCampaignInventoryRetained=True),indent=2)+'\n')
 row=dict(result='source-checkpoint'if not mismatch else'fail',packet=str(out),packetSHA256=sha(out),inputs=len(inputs),modes=len(modes),links=len(links),mismatch=mismatch,GUI=False,frozen=False,nativeReady=False,actualUnchangedFastHelperPositiveRetained=True,actualRegistryPositiveNegativeScenarios=7,reliabilityAccepted=False,pendingProductionResultRetirementNegatives=True)
 (B/'scoped-source-checkpoint.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row));return int(bool(mismatch))
if __name__=='__main__':raise SystemExit(main())
