"""Actual v1 draft wrapper replay. No subprocess, native load or GUI."""
import sys,json,hashlib,os
from pathlib import Path
base=Path(__file__).resolve().parent.parent/'production-maintenance-v1'
sys.path.insert(0,str(base))
from maintenance import Maintenance,Identity
identity=Identity('abc_1_2',123,456,7,8)
artifact=dict(nativeAccepted=True,productionAccepted=True,privateProbeAbsent=True,sha256='a'*64,packageID='same-artifact',library=os.path.expanduser('~/.local/lib/omarchy-a11y-same-artifact.so'))
current=['old-plugin'];calls=[]
def transport(command,environment):
 calls.append(dict(command=command,plugin=current[0]))
 if command[3]=='repl' and 'identity()' in command[-1]:
  # Correct old identity reply; then a new instance of identical artifact loads.
  current[0]='new-plugin';return json.dumps(dict(instance=identity.signature,packageID=artifact['packageID']))
 if command[3]=='repl':return json.dumps(dict(instance=identity.signature,packageID=artifact['packageID'],ready=True))
 return 'ok'
manager=Maintenance(identity,artifact,lambda:identity,lambda row:None,transport)
manager.unload()
assert calls[0]['plugin']=='old-plugin' and calls[1]['plugin']=='new-plugin' and calls[2]['plugin']=='new-plugin'
r=dict(kind='actual v1 draft wrapper source replay; no native/product claim',counterexample=True,sourceSHA256=hashlib.sha256((base/'maintenance.py').read_bytes()).hexdigest(),sameCompositor=True,sameArtifact=True,staleIdentityRetiredNewPlugin=True,calls=calls,GUI=False,mainTouched=False)
(Path(__file__).resolve().parent/'incarnation-counterexample.json').write_text(json.dumps(r,indent=2)+'\n')
print('v1 draft incarnation counterexample confirmed')
