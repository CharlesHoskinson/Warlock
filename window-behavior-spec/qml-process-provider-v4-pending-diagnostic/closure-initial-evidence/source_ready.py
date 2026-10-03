from pathlib import Path
import hashlib,json,os,stat,subprocess
B=Path(__file__).resolve().parent
CPU=B/'cpu-evidence-1790941731153845687/report.json'
PREDECESSORS=B/'reviewed-predecessors.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 inputs={};modes={};links={};mismatch=[]
 def add(p):
  p=Path(os.path.abspath(p))
  for q in (p,*p.parents):
   if q.is_symlink():links[str(q)]=os.readlink(q)
  resolved=p.resolve(strict=True)
  for q in {p,resolved}:
   if q.is_file()and not q.is_symlink():inputs[str(q)]=sha(q);modes[str(q)]=stat.S_IMODE(q.stat().st_mode)
 def verifyPacket(p):
  packet=json.loads(p.read_text());add(p)
  for name,row in packet.get('inputs',{}).items():
   digest=row if isinstance(row,str)else row['sha256'];mode=packet.get('inputModes',{}).get(name)if isinstance(row,str)else row['mode']
   q=Path(name)
   if not q.is_file()or sha(q)!=digest or stat.S_IMODE(q.stat().st_mode)!=mode:mismatch.append(name)
   else:inputs[name]=digest;modes[name]=mode
  for name,target in packet.get('symlinks',packet.get('links',{})).items():
   if not Path(name).is_symlink()or os.readlink(name)!=target:mismatch.append(name)
   else:links[name]=target
 predecessors=json.loads(PREDECESSORS.read_text())
 for row in predecessors.values():
  p=Path(row['path'])
  if sha(p)!=row['sha256']:mismatch.append(str(p))
  if row is predecessors['rootReview']:add(p)
  else:verifyPacket(p)
 verifyPacket(Path('/home/hoskinson/window-behavior-spec/qml-pin-popup-lifetime-v1/formal-review-inputs.json'))
 for p in B.rglob('*'):
  if p.is_file()and '__pycache__'not in p.parts and 'build'not in p.parts and p.name not in ('source-ready.json','source-ready-inputs.json'):add(p)
 for name in ('qa_run.py','qa_launch.py'):add('/home/hoskinson/window-integration-qa/'+name)
 build=json.loads((B/'build-report.json').read_text());proof=json.loads(CPU.read_text())
 good=not mismatch and proof['result']=='pass'and proof['sourceUnchanged']and build['result']=='pass'and build['sourceUnchanged']
 for name,row in {**build['perTranslationUnitDependencies'],**proof['sources']}.items():
  if sha(name)!=row['sha256']or stat.S_IMODE(Path(name).stat().st_mode)!=row['mode']:mismatch.append(name);good=False
  add(name)
 for name,digest in build['sourceSHA256'].items():
  if sha(name)!=digest:mismatch.append(name);good=False
 for name,digest in build['binarySHA256'].items():
  if sha(B/name)!=digest:mismatch.append(str(B/name));good=False
 elf=[B/n for n in ('libobjectlifetime.so','cpu-registry','cpu-dso','cpu-popup-runtime')]+[Path(n)for n in ('/usr/bin/clang++','/usr/lib/qt6/moc','/usr/bin/python3','/usr/bin/quickshell')]
 loader=[]
 for p in elf:
  add(p);r=subprocess.run(['/usr/bin/ldd',str(p)],capture_output=True,text=True,timeout=30)
  if r.returncode:raise ValueError('Actual ELF loader closure refused '+str(p))
  loader.append(dict(path=str(p),stdout=r.stdout,stderr=r.stderr))
  for line in r.stdout.splitlines():
   for word in line.split():
    if word.startswith('/'):add(word)
 checks=sum(json.loads(row['stdout'])['checks']for row in proof['rows'])
 packet=dict(inputs=inputs,inputModes=modes,symlinks=links,reviewedPredecessors=predecessors,cpuEvidence=dict(path=str(CPU),sha256=sha(CPU)),elf=loader,GUI=False,nativeLaunch=False,mainChanges=False,sourceComponentOnly=True)
 path=B/'source-ready-inputs.json';path.write_text(json.dumps(packet,indent=2)+'\n')
 row=dict(result='source-ready'if good else'fail',packet=str(path),packetSHA256=sha(path),inputs=len(inputs),modes=len(modes),links=len(links),mismatch=mismatch,CPUChecks=checks,CPUCases=len(proof['rows']),popupCPUChecks=json.loads(next(row['stdout']for row in proof['rows']if row['mode']=='actual-popup-runtime'))['checks'],formalBaseNamed=29,formalPopupInitialNamed=35,formalPopupContextNamed=44,formalRandomTracesEach=2000,formalSteps=100,GUI=False,nativeLaunch=False,rootReviewPending=True,installedQSPopupAccepted=False,wholePinCampaignReady=False,ProcessRegistryImplemented=False,batchConsumerAccepted=False,frozen=False)
 (B/'source-ready.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row));return int(not good)
if __name__=='__main__':raise SystemExit(main())
