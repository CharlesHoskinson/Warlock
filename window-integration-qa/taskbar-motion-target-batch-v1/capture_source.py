from pathlib import Path
import hashlib,json,os,stat,subprocess,re
from check_source import check
B=Path(__file__).resolve().parent
P=Path('/home/hoskinson/window-integration-qa/pin-native-qa-v1/source-ready-inputs.json')
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def capture():
 assert not(B/'source-ready-inputs.json').exists(),'already captured; preserve packet'
 check()
 report=json.loads((B/'offline-report.json').read_text());assert report['result']=='pass'and report['sourceUnchanged']
 for path,h in report['sourceSHA256'].items():assert digest(path)==h,'offline source changed: '+path
 inherited=json.loads(P.read_text())
 for path,h in inherited['inputs'].items():
  assert digest(path)==h,'inherited source changed: '+path
  assert stat.S_IMODE(Path(path).stat().st_mode)==inherited['inputModes'][path],'inherited mode changed: '+path
 for path,target in inherited['symlinks'].items():assert Path(path).is_symlink()and os.readlink(path)==target,'inherited link changed: '+path
 inputs=dict(inherited['inputs']);modes=dict(inherited['inputModes']);links=dict(inherited['symlinks'])
 def add(path):
  p=Path(path)
  assert p.is_absolute()and p.exists(),'missing dependency: '+str(p)
  # Preserve every lexical path component that is a symlink and the resolved file.
  for candidate in list(reversed(p.parents))+[p]:
   if candidate.is_symlink():links[str(candidate)]=os.readlink(candidate)
  inputs[str(p)]=digest(p);modes[str(p)]=stat.S_IMODE(p.stat().st_mode)
  resolved=p.resolve()
  if resolved!=p:inputs[str(resolved)]=digest(resolved);modes[str(resolved)]=stat.S_IMODE(resolved.stat().st_mode)
 for p in B.rglob('*'):
  if p.is_file()and '__pycache__'not in p.parts and p.name not in('source-ready.json','source-ready-inputs.json'):add(p)
 add(P);add('/usr/bin/clang++');add('/usr/bin/pkg-config');add('/usr/bin/ldd')
 dependencies=(B/'test-qjs.d').read_text().replace('\\\n',' ').split(':',1)[1].split()
 for path in dependencies:add(path)
 runtime=subprocess.run(['/usr/bin/ldd',str(B/'test-qjs')],capture_output=True,text=True,check=True)
 for path in re.findall(r'(/[^\s()]+)',runtime.stdout):add(path)
 packet=dict(inputs=inputs,inputModes=modes,symlinks=links,inheritedPinPacket=dict(path=str(P),sha256=digest(P)),scope='source-only batch motion-target candidate; root pairing/review/native pending',sourceReview=check(),nativeLaunch=False,mainChanges=False,GUIAccepted=False,latencyAccepted=False)
 out=B/'source-ready-inputs.json'
 with out.open('x')as f:json.dump(packet,f,indent=2);f.write('\n')
 ready=dict(result='source-ready',packet=str(out),packetSHA256=digest(out),inputs=len(inputs),modes=len(modes),links=len(links),formalNamed=12,formalTraces=2000,formalSteps=100,actualQJSEngineAssertions=39,singleTargetExact=True,rootReviewPending=True,frozen=False,nativeLaunch=False,GUIAccepted=False,latencyAccepted=False)
 with(B/'source-ready.json').open('x')as f:json.dump(ready,f,indent=2);f.write('\n')
 print(json.dumps(ready))
if __name__=='__main__':capture()
