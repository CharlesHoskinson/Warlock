"""Add final root failure audit without replacing first capture descriptors."""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parent
sys.path.insert(0,str(B))
import capture_packet as initial
V2=Path('/home/hoskinson/window-integration-qa/pin-maximized-native-v2')
sys.path.insert(0,str(V2/'proposed'))
from closure_union import union
AUDIT=V2.parent/'pin-max-campaign-b-prehost-root-failure-v1.json'
CORRECTION=V2.parent/'root-lua-dispatch-interpretation-correction-v1.json'
def inventory():
 row=initial.inventory();row=union(B,[row],[AUDIT,CORRECTION]);row['rootDispatchCorrection']=dict(path=str(CORRECTION),**initial.meta(CORRECTION));row['rootFailureAudit']=dict(path=str(AUDIT),**initial.meta(AUDIT));return row
if __name__=='__main__':
 row=inventory();initial.publish(B/'SOURCE_INPUTS-v2.json',row)
 ready=json.loads((B/'SOURCE_READY.json').read_bytes());ready.update(finalSourceInputs=str(B/'SOURCE_INPUTS-v2.json'),sourceInputsSHA256=initial.meta(B/'SOURCE_INPUTS-v2.json')['sha256'],inputs=len(row['inputs']),symlinks=len(row['symlinks']),directoryModes=len(row['directoryModes']),retainedFirstReady=dict(path=str(B/'SOURCE_READY.json'),**initial.meta(B/'SOURCE_READY.json')),rootFailureAudit=row['rootFailureAudit'],freshHostOutputLocationPreflight='promotion_preflight.py before root native host',mechanicalCPUChecks=5)
 initial.publish(B/'SOURCE_READY-v2.json',ready)
 print(json.dumps(dict(sourceReady=str(B/'SOURCE_READY-v2.json'),readySHA256=initial.meta(B/'SOURCE_READY-v2.json')['sha256'],inputsSHA256=ready['sourceInputsSHA256'],inputs=ready['inputs'],links=ready['symlinks'],dirs=ready['directoryModes'],nativeLaunched=False)))
