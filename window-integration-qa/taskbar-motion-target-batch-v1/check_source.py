from pathlib import Path
import hashlib,json,re
B=Path(__file__).resolve().parent
BASE=Path('/home/hoskinson/window-behavior-spec/pin-lifetime-v3/frontend/widget_v66')
def function(source,name):
 start=re.search(r'^ +function '+re.escape(name)+r'\(',source,re.M).start()
 brace=source.index('{',start);level=1;i=brace+1
 while level:
  if source[i]=='{':level+=1
  elif source[i]=='}':level-=1
  i+=1
 return source[start:i]
def check():
 old=(BASE/'Windows.qml').read_text();new=(B/'widget_v67/Windows.qml').read_text()
 for name in ('motionTarget','motionTargetFor'):
  assert function(old,name)==function(new,name),name
 reconstructed=new.replace('import "MotionTargets.js" as MotionTargets\n','',1).replace('  readonly property double motionWidgetGeneration: MotionTargets.allocateGeneration()\n','',1).replace('          readonly property double motionDelegateGeneration: MotionTargets.allocateGeneration()\n','',1)
 for name in ('motionTargets','motionTargetObservation'):
  reconstructed=reconstructed.replace(function(reconstructed,name)+'\n','',1)
 assert reconstructed==old,'full inverse source reconstruction'
 rows=json.loads((B/'inherited-source.json').read_text())['inputs']
 for path,h in rows.items():
  p=Path(path);assert hashlib.sha256(p.read_bytes()).hexdigest()==h,'parent changed'
  if p.name!='Windows.qml':assert (B/'widget_v67'/p.relative_to(BASE)).read_bytes()==p.read_bytes(),'other frontend changed'
 assert function(new,'motionTargets').index('MotionTargets.decode(encoded)')<function(new,'motionTargets').index('moduleWidgets')
 return dict(result='pass',singleTargetExact=True,delegateExact=True,fullInverseReconstruction=True,otherFrontendExact=True,parentUnchanged=True,nativeExecuted=False)
if __name__=='__main__':print(json.dumps(check()))
