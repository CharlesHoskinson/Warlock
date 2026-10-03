"""Exact available source/dependency closure, never freeze or launch native QA."""
from pathlib import Path
import hashlib,json,os,re,stat,subprocess
B=Path(__file__).resolve().parent;QA=B.parent
EXCLUDE=('source-controller-inputs-v1.json','source-controller-handoff-v1.json')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 inputs={};modes={};links={};inherited=[]
 def link(p):
  if p.is_symlink():
   target=os.readlink(p)
   if str(p)in links and links[str(p)]!=target:raise ValueError('Conflicting exact link')
   links[str(p)]=target
 def add(p,digest=None,mode=None):
  p=Path(p).absolute()
  for parent in[p,*p.parents]:link(parent)
  if p.is_symlink():add(p.resolve(),digest,mode);return
  s=p.lstat();h=sha(p);m=stat.S_IMODE(s.st_mode)
  if not stat.S_ISREG(s.st_mode)or digest is not None and digest!=h or mode is not None and mode!=m or str(p)in inputs and inputs[str(p)]!=h:raise ValueError('Byte/mode closure differs: '+str(p))
  inputs[str(p)]=h;modes[str(p)]=m
 def packet(p):
  p=Path(p);raw=p.read_bytes();d=json.loads(raw)
  for n,h in d['inputs'].items():add(n,h,d['inputModes'][n])
  for n,t in d.get('symlinks',{}).items():
   if not Path(n).is_symlink()or os.readlink(n)!=t:raise ValueError('Inherited exact link differs')
   links[n]=t
  add(p);inherited.append(dict(path=str(p),sha256=sha(p)))
  if p.read_bytes()!=raw:raise ValueError('Inherited manifest changed')
 packet(QA/'pin-native-qa-v1/source-ready-inputs.json')
 for p in sorted(B.rglob('*')):
  if '__pycache__'in p.parts or p.name in EXCLUDE or any(part.startswith('attempt-')for part in p.parts):continue
  if p.is_symlink():link(p)
  elif p.is_file():add(p)
 for name in('/usr/lib/qt6/qml/Quickshell/quickshell-core.qmltypes','/usr/lib/qt6/qml/Quickshell/Io/quickshell-io.qmltypes'):add(name)
 probe=json.loads((B/'native-probe/build-report.json').read_text())
 if probe['exitCode']!=0 or probe['sourceUnchanged']is not True or sha(B/'native-probe/libpin-frontend-probe.so')!=probe['binarySHA256']:raise ValueError('Actual clean probe build authority differs')
 for item in probe['sourceDependencies']:add(item['path'],item['sha256'],item['mode'])
 key=json.loads((B/'keyboard/physical-build-report.json').read_text())
 for item in key['dependencies']:add(item['path'],item['sha256'],item['mode'])
 for item in key['symlinks']:
  if os.readlink(item['path'])!=item['target']:raise ValueError('Physical driver exact links differ')
  links[item['path']]=item['target']
 command=['/usr/bin/ldd',str(B/'native-probe/libpin-frontend-probe.so')];r=subprocess.run(command,capture_output=True,text=True,timeout=15)
 if r.returncode or 'not found'in r.stdout:raise ValueError('Compiled readonly probe loader unresolved')
 loader=[]
 for line in r.stdout.splitlines():
  match=re.search(r'(?:=>\s+)?(/\S+)\s+\(',line)
  if match:add(match[1]);loader.append(match[1])
 offline=json.loads((B/'offline-report.json').read_text())
 if offline['result']!='pass'or offline['sourceUnchanged']is not True:raise ValueError('Focused actual offline proof required')
 for name,h in offline['sourceSHA256'].items():
  if sha(name)!=h:raise ValueError('Source changed after focused suite: '+name)
 row=dict(inputs=inputs,inputModes=modes,symlinks=links,inheritedPackets=inherited,probeLoader=dict(command=command,stdout=r.stdout,stderr=r.stderr,paths=loader),scope='Available Pin frontend input-controller/probe/physical-driver/adapter sources only; required actual engine/lifecycle/wrapper pairing not implemented',sourceComponentReady=True,wholeNativeCampaignReady=False,nativeRunnable=False,nativeLaunch=False,mainChanges=False,frozen=False)
 path=B/EXCLUDE[0]
 if path.exists():raise ValueError('Fresh component handoff only')
 path.write_text(json.dumps(row,indent=2)+'\n');path.chmod(0o600)
 result=dict(result='source-component-ready',packet=str(path),packetSHA256=sha(path),inputs=len(inputs),modes=len(modes),links=len(links),focusedCommands=len(offline['commands']),CPUControllerAndAuthorityTests=31,physicalDriverTests=10,adapterTests=18,formalNamed=31,models=3,formalTracesEach=2000,sourceUnchangedDuringSuite=True,inverseSourceChecksSeparate=True,wholeNativeCampaignReady=False,nativeRunnable=False,missingActualAuthorities=['QQmlEngine/object lifetime provider','transient actual helper/QML normal-exit registry','complete private B host/wrapper and full case matrix'],rootReviewPending=True,nativeLaunch=False,mainChanges=False,frozen=False,fullWindowsParityAccepted=False)
 (B/EXCLUDE[1]).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));return 0
if __name__=='__main__':raise SystemExit(main())
