from pathlib import Path
import hashlib,json,os,stat,subprocess
B=Path(__file__).resolve().parent
A=Path('/home/hoskinson/window-integration-qa/pin-native-qa-v1/source-ready-inputs.json')
V1=Path('/home/hoskinson/window-behavior-spec/qml-object-lifetime-v1')
CPU=B/'cpu-evidence-1790937826358427656/report.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 inherited=json.loads(A.read_text());inputs={};modes={};links={};mismatch=[]
 # Retain installed runtime/tool closure; predecessor product packets are separate immutable authorities.
 for name,h in inherited['inputs'].items():
  if name.startswith(('/home/hoskinson/window-integration-qa/','/home/hoskinson/window-behavior-spec/')):continue
  p=Path(name)
  if not p.is_file()or sha(p)!=h or stat.S_IMODE(p.stat().st_mode)!=inherited['inputModes'][name]:mismatch.append(name)
  else:inputs[name]=h;modes[name]=inherited['inputModes'][name]
 for name,target in inherited['symlinks'].items():
  if name.startswith(('/home/hoskinson/window-integration-qa/','/home/hoskinson/window-behavior-spec/')):continue
  if not Path(name).is_symlink()or os.readlink(name)!=target:mismatch.append(name)
  else:links[name]=target
 def add(p):
  p=Path(os.path.abspath(p))
  for parent in [p,*p.parents]:
   if parent.is_symlink():links[str(parent)]=os.readlink(parent)
  resolved=p.resolve(strict=True)
  for q in {p,resolved}:
   if q.is_file()and not q.is_symlink():inputs[str(q)]=sha(q);modes[str(q)]=stat.S_IMODE(q.stat().st_mode)
 for p in B.rglob('*'):
  if p.is_file()and '__pycache__'not in p.parts and 'build'not in p.parts and p.name not in ('source-ready.json','source-ready-inputs.json'):add(p)
 for p in V1.rglob('*'):
  if p.is_file()and '__pycache__'not in p.parts:add(p)
 for name in ('qa_run.py','qa_launch.py'):add('/home/hoskinson/window-integration-qa/'+name)
 build=json.loads((B/'build-report.json').read_text())
 for p in build['perTranslationUnitDependencies']:add(p)
 elf=[B/'libobjectlifetime.so',B/'cpu-registry',B/'cpu-dso',Path('/usr/bin/clang++'),Path('/usr/lib/qt6/moc'),Path('/usr/bin/python3'),Path('/usr/bin/quickshell')]
 ldd=[]
 for p in elf:
  add(p);r=subprocess.run(['/usr/bin/ldd',str(p)],capture_output=True,text=True,timeout=30)
  if r.returncode:raise ValueError('Actual ELF loader closure refused '+str(p))
  ldd.append(dict(path=str(p),stdout=r.stdout,stderr=r.stderr))
  for line in r.stdout.splitlines():
   for word in line.split():
    if word.startswith('/'):add(word)
 proof=json.loads(CPU.read_text());good=not mismatch and proof['result']=='pass'and proof['sourceUnchanged']and build['result']=='pass'and build['sourceUnchanged']
 for p,v in proof['sources'].items():
  if sha(p)!=v['sha256']or stat.S_IMODE(Path(p).stat().st_mode)!=v['mode']:good=False;mismatch.append(p)
 packet=dict(inputs=inputs,inputModes=modes,symlinks=links,inheritedInstalledClosure=dict(path=str(A),sha256=sha(A)),formalPredecessor=dict(path=str(V1/'formal-review-ready.json'),sha256=sha(V1/'formal-review-ready.json')),cpuEvidence=dict(path=str(CPU),sha256=sha(CPU)),elf=ldd,nativeLaunch=False,mainChanges=False)
 path=B/'source-ready-inputs.json';path.write_text(json.dumps(packet,indent=2)+'\n')
 row=dict(result='source-ready'if good else'fail',packet=str(path),packetSHA256=sha(path),inputs=len(inputs),modes=len(modes),links=len(links),mismatch=mismatch,CPUChecks=215,CPUCases=10,formalNamedCases=29,GUI=False,nativeLaunch=False,rootReviewPending=True,wholePinCampaignReady=False,popupRuntimeImplemented=False,ProcessRegistryImplemented=False,batchConsumerAccepted=False,frozen=False)
 (B/'source-ready.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row));return int(not good)
if __name__=='__main__':raise SystemExit(main())
