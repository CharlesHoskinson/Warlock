import hashlib,json,os,stat
from pathlib import Path

HERE=Path(__file__).resolve().parent;QA=HERE.parent
def stamp(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mode':stat.S_IMODE(p.stat().st_mode)}
def main():
    formal=json.loads((HERE/'formal-complete.json').read_text());pixel=json.loads((HERE/'pixel-replay.json').read_text());mapping=json.loads((HERE/'intended-source-map.json').read_text())
    assert formal['result']=='pass' and formal['named']==18 and pixel['result']=='pass' and mapping['completeInverseExact'] and not mapping['applied']
    sources={str(p):stamp(p) for p in HERE.rglob('*') if p.is_file()}
    evidence=[QA/'thumbnail-v14-agent-causal-replay-v1/replay.py',QA/'thumbnail-v14-agent-causal-replay-v1/report.json',QA/'thumbnail-v14-agent-formal-selection-audit-v1/audit.py',QA/'thumbnail-v14-agent-formal-selection-audit-v1/report.json',QA/'restore-v6-actual-named-correction-v1/report.json',QA/'restore-v6-actual-named-correction-v1/named.log',QA/'run_restore_v6_named_correction_v1.py',QA/'thumbnail-v14-root-failure-audit-v1.json']
    sources.update({str(p):stamp(p)for p in evidence})
    for report in (QA/'thumbnail-v14-agent-causal-replay-v1/report.json',QA/'thumbnail-v14-agent-formal-selection-audit-v1/report.json'):
        for p,row in json.loads(report.read_text())['sources'].items():
            assert stamp(Path(p))==row
            if p in sources:assert sources[p]==row
            sources[p]=row
    for p,row in formal['sources'].items():assert stamp(Path(p))==row
    row={'result':'proposal-ready','sources':sources,'inputCount':len(sources),'formal':{'namedActuallyRun':18,'samples':2000,'steps':100,'report':str(HERE/'formal-complete.json')},'pixels':{'matrices':16,'exactComparisons':32,'report':str(HERE/'pixel-replay.json')},'intendedPatch':str(HERE/'intended.patch'),'intendedPatchSHA256':stamp(HERE/'intended.patch')['sha256'],'runtimeApplied':False,'ownedApplicationTestsExecuted':False,'nativeAccepted':False,'original38Accepted':False,'original34Accepted':False,'timingAcceptance':False,'campaignB14RemainsFailed':True,'newNativeGrant':False}
    path=HERE/'source-handoff.json'
    with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'result':row['result'],'path':str(path),'sha256':stamp(path)['sha256'],'inputCount':len(sources),'patchSHA256':row['intendedPatchSHA256']}))
if __name__=='__main__':main()
