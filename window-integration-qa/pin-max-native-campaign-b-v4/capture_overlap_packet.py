"""Full frozen failedBv3/current overlap source union; never freeze/native."""
from pathlib import Path
import sys,json,stat
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parent
P=B.with_name('pin-max-native-campaign-b-v3')
A=P.parent/'pin-maximized-native-v2'
sys.path.insert(0,str(A/'proposed'))
from closure_union import union
sys.path.insert(0,str(B))
from capture_packet import publish,meta

def inventory():
 parent=json.loads((P/'frozen-inputs.json').read_bytes())
 raw=P/'attempt-1';audit=P.parent/'pin-max-native-b-v3-overlap-audit-v1'
 def dirrow(root):return dict(inputs={},inputModes={},symlinks={},directoryModes={str(p):stat.S_IMODE(p.stat().st_mode)for p in [root,*sorted(root.rglob('*'))]if p.is_dir()and not p.is_symlink()})
 extras=[P/n for n in ['frozen-inputs.json','ROOT_NATIVE_GRANT.json','SOURCE_READY.json','SOURCE_INPUTS.json','FINAL_HANDOFF.md']]
 extras.extend(p for root in [raw,audit]for p in sorted(root.rglob('*'))if p.is_file()or p.is_symlink())
 extras.append(P.parent/'pin-max-native-b-v3-root-failure-v1.json')
 row=union(B,[parent,dirrow(raw),dirrow(audit)],extras)
 assert all(row['inputs'].get(k)==v and row['inputModes'].get(k)==parent['inputModes'][k]for k,v in parent['inputs'].items())
 assert all(row['symlinks'].get(k)==v for k,v in parent['symlinks'].items())
 assert all(row['directoryModes'].get(k)==v for k,v in parent['directoryModes'].items())
 row['ancestralDescriptors']=[dict(path=str(P/'frozen-inputs.json'),**meta(P/'frozen-inputs.json'))]
 row['scope']='approved current Qt/native peer-button overlap operand; no product/native/freeze authority'
 row['retainedRawFailedAttempt']=str(raw);row['wholeFrozenParentInputs']=len(parent['inputs'])
 return row
if __name__=='__main__':
 row=inventory();publish(B/'SOURCE_INPUTS.json',row)
 ready=dict(schema=1,sourceOnly=True,nativeAuthorized=False,freezeAuthorized=False,parent=str(P),parentFrozen=meta(P/'frozen-inputs.json'),sourceInputsSHA256=meta(B/'SOURCE_INPUTS.json')['sha256'],pairSHA256=meta(B/'PAIR_READY.json')['sha256'],inputs=len(row['inputs']),symlinks=len(row['symlinks']),directoryModes=len(row['directoryModes']),wholeFrozenParentInputs=row['wholeFrozenParentInputs'],runtimeDelta="sole overlap operand self.qt_box(actor,'peer',peer)",allOriginal19TestsExact=True,inheritedCPU=19,newWholeBodyCPU=4,producerNamedFormal=14,producerTraces=2000,producerMaxSteps=100,formalBodiesAndProofsUnchanged=True,coreAndObserverUnchanged=True,original14Credit=False,fullCampaignBAccepted=False,fullParityAccepted=False,remaining=['fresh source review/freeze/grant and actual B01–B12','CLI/ROI/third blocked peer/native full mode trajectory','B13–B24 masks/scroll/transfer/two outputs','B24 genuine trigger','full parity'])
 publish(B/'SOURCE_READY.json',ready)
 print(json.dumps(dict(readySHA256=meta(B/'SOURCE_READY.json')['sha256'],inputsSHA256=ready['sourceInputsSHA256'],inputs=ready['inputs'],links=ready['symlinks'],dirs=ready['directoryModes'],nativeExecuted=False)))
