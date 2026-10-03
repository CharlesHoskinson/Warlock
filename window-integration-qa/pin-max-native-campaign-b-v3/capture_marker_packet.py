"""Complete frozen failed-parent plus current source union; never native/freeze."""
from pathlib import Path
import sys,json,stat
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parent
P=B.with_name('pin-max-native-campaign-b-v2')
A=P.parent/'pin-maximized-native-v2'
sys.path.insert(0,str(A/'proposed'))
from closure_union import union
sys.path.insert(0,str(B))
from capture_packet import publish,meta

def inventory():
 parent=json.loads((P/'frozen-inputs.json').read_bytes())
 raw=P/'attempt-1'
 rawdirs=dict(inputs={},inputModes={},symlinks={},directoryModes={str(p):stat.S_IMODE(p.stat().st_mode)for p in [raw,*sorted(raw.rglob('*'))]if p.is_dir()and not p.is_symlink()})
 extras=[P/n for n in ['frozen-inputs.json','ROOT_NATIVE_GRANT.json','SOURCE_READY.json','SOURCE_READY-v2.json','SOURCE_INPUTS.json','SOURCE_INPUTS-v2.json','FINAL_HANDOFF.md']]
 extras.extend(p for p in sorted(raw.rglob('*'))if p.is_file()or p.is_symlink())
 extras.extend(P.parent/n for n in ['pin-max-native-b-v2-root-failure-v1.json','pin-max-campaign-b-promotion-root-review-v2.json'])
 audit=P.parent/'pin-max-native-b-v2-intent-marker-audit-v1'
 extras.extend(p for p in sorted(audit.rglob('*'))if p.is_file()or p.is_symlink())
 auditdirs=dict(inputs={},inputModes={},symlinks={},directoryModes={str(p):stat.S_IMODE(p.stat().st_mode)for p in [audit,*sorted(audit.rglob('*'))]if p.is_dir()and not p.is_symlink()})
 row=union(B,[parent,rawdirs,auditdirs],extras)
 assert all(row['inputs'].get(k)==v and row['inputModes'].get(k)==parent['inputModes'][k]for k,v in parent['inputs'].items())
 assert all(row['symlinks'].get(k)==v for k,v in parent['symlinks'].items())
 assert all(row['directoryModes'].get(k)==v for k,v in parent['directoryModes'].items())
 row['ancestralDescriptors']=[dict(path=str(P/'frozen-inputs.json'),**meta(P/'frozen-inputs.json'))]
 row['scope']='root-approved QA-only intent-marker oracle derivative; B01–B12 unaccepted; no native/freeze authority'
 row['retainedRawFailedAttempt']=str(raw)
 row['wholeFrozenParentInputs']=len(parent['inputs'])
 return row

if __name__=='__main__':
 row=inventory();publish(B/'SOURCE_INPUTS.json',row)
 ready=dict(schema=1,sourceOnly=True,nativeAuthorized=False,freezeAuthorized=False,locationOnly=False,parent=str(P),parentFrozen=meta(P/'frozen-inputs.json'),sourceInputsSHA256=meta(B/'SOURCE_INPUTS.json')['sha256'],pairSHA256=meta(B/'PAIR_READY.json')['sha256'],inputs=len(row['inputs']),symlinks=len(row['symlinks']),directoryModes=len(row['directoryModes']),wholeFrozenParentInputs=len(json.loads((P/'frozen-inputs.json').read_bytes())['inputs']),runtimeDelta='only approved B04/B05 exact intent-marker oracle; eighteen immediate mode/geometry fields conserved',CPU=19,original16CPUASTExact=True,newCPUTests=3,producerNamedFormal=14,producerTraces=2000,producerMaxSteps=100,formalBodiesAndProofsUnchanged=True,coreAndObserverUnchanged=True,original14Credit=False,fullCampaignBAccepted=False,fullParityAccepted=False,remaining=['fresh root source/freeze/grant and actual B01–B12','B03 full CLI','B07–09 presentation ROI','B11–12 third blocked peer','native full mode trajectory','B13–B24 masks/scroll/transfer/two outputs','B24 genuine trigger','full parity'])
 publish(B/'SOURCE_READY.json',ready)
 print(json.dumps(dict(sourceReadySHA256=meta(B/'SOURCE_READY.json')['sha256'],sourceInputsSHA256=ready['sourceInputsSHA256'],inputs=ready['inputs'],links=ready['symlinks'],dirs=ready['directoryModes'],sourceOnly=True)))
