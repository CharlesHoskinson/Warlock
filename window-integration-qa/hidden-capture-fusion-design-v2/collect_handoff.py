import hashlib,json,os,stat
from pathlib import Path

HERE=Path(__file__).resolve().parent;QA=HERE.parent;V1=HERE.with_name('hidden-capture-fusion-design-v1')
def stamp(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mode':stat.S_IMODE(p.stat().st_mode)}
def main():
    sources={}
    def add(path,row=None):
        value=stamp(path)
        if row is not None:assert row==value
        if str(path) in sources:assert sources[str(path)]==value
        sources[str(path)]=value
    original=json.loads((V1/'source-handoff.json').read_text())
    for path,row in original['sources'].items():add(Path(path),row)
    add(V1/'source-handoff.json')
    for path in HERE.rglob('*'):
        if path.is_file():add(path)
    for name in ('hidden-capture-fusion-formal-selection-epochs-v1.json','restore-v6-actual-named-correction-v1/report.json','restore-v6-actual-named-correction-v1/named.log','run_restore_v6_named_correction_v1.py','thumbnail-v14-agent-formal-selection-audit-v1/report.json'):
        add(QA/name)
    formal=json.loads((HERE/'formal-before-runtime.json').read_text());output=json.loads((HERE/'output-replay.json').read_text())
    assert formal['result']=='pass' and formal['namedActuallyRun']==23 and output['result']=='pass' and len(output['cases'])==9
    for proof in (formal,output):
        for path,row in proof['sources'].items():add(Path(path),row)
    for check in formal['checks']:
        assert check['exitCode']==0
        add(Path(check['log']),{'sha256':check['sha256'],'mode':check['mode']})
    packet={'result':'proposal-ready','version':2,'sources':sources,'inputCount':len(sources),
        'predecessor':{'path':str(V1/'source-handoff.json'),**stamp(V1/'source-handoff.json')},
        'formal':{'namedActuallyRun':23,'samples':2000,'steps':100,'report':str(HERE/'formal-before-runtime.json')},
        'fileAvailabilityCasesActuallyRun':9,'retainedPixelMatrices':16,'retainedExactPixelComparisons':32,'pixelsNewlyRerun':False,
        'onlyV1PatchDelta':'Require both private thumbnail/composed outputs regular-file availability and size>=64 before first publication',
        'patch':{'path':str(HERE/'intended.patch'),**stamp(HERE/'intended.patch')},
        'originalV1WholeSourceInverseExact':True,'runtimeApplied':False,'ownedApplicationTestsExecuted':False,'nativeAccepted':False,
        'original38Accepted':False,'original34Accepted':False,'timingAcceptance':False,'campaignB14RemainsFailed':True,
        'rootV6Actual45NamedCorrectionIncluded':True,'falseNominalV1Default18CountAndBroadSelectorFailureRetained':True,
        'legacyStandaloneAndOriginalBudgetsUnchanged':True}
    for path,row in sources.items():assert stamp(Path(path))==row
    path=HERE/'source-handoff.json'
    with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(packet,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'result':packet['result'],'path':str(path),'sha256':stamp(path)['sha256'],'inputCount':len(sources),'patchSHA256':packet['patch']['sha256']}))
if __name__=='__main__':main()
