"""Independently replay completed proof/closure; preserve the failed outer driver."""
from pathlib import Path
import hashlib,json,os,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(path,row):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'w')as out:json.dump(row,out,indent=2);out.write('\n')
scope=require_qa_scope();proof=json.loads((B/'offline-checkpoint.json').read_text())
assert (proof['pythonTests'],proof['quintNamedScenarios'],proof['quintModels'])==(324,227,24)
assert proof['sourceUnchangedDuringProof']is True and len(proof['checks'])==73 and all(r['exitCode']==0 for r in proof['checks'])
assert all(sha(name)==digest for name,digest in proof['sourceSHA256'].items())
from collect_reduced_validation import collect,verify
old=json.loads((B/'source-ready-v18.json').read_text());verify(old);current=collect()
assert all(current['inputs'].get(name)==digest and current['inputModes'][name]==old['inputModes'][name]for name,digest in old['inputs'].items())
assert all(current['links'].get(name)==target for name,target in old['links'].items())
witnesses={name:dict(sha256=digest,mode=current['inputModes'][name])for name,digest in current['inputs'].items()if Path(name).is_relative_to(B)}
save(B/'source-ready-v18-v2.json',current)
verify(current)
row=dict(result='pass independent completed proof and closure replay',scope=scope,offlineSHA256=sha(B/'offline-checkpoint.json'),originalSourceReadySHA256=sha(B/'source-ready-v18.json'),currentSourceReadySHA256=sha(B/'source-ready-v18-v2.json'),checks=dict(actual324Python227Named24ModelsCompleted=True,all73ActualCommandsExit0=True,allOriginalProofSourcesExact=True,entireOriginalReadyBytesModesLinksExact=True,currentFullClosureExact=True),sourceWitnesses=witnesses,counts=dict(inputs=len(current['inputs']),modes=len(current['inputModes']),links=len(current['links'])),retainedOuterDriverResult='fail AttributeError after successful offline proof and source collection; no successful outer-driver exit inferred',nativeLaunch=False,mainChanged=False,fullNativeReducedParityAccepted=False)
save(B/'final-reduced-gate-checkpoint-v2.json',row);print(json.dumps({k:v for k,v in row.items()if k!='sourceWitnesses'}))
