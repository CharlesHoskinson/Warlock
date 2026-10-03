from pathlib import Path
import hashlib,json,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parents[1]
Q=Path('/home/hoskinson/window-integration-qa')
V=Path('/home/hoskinson/window-behavior-spec/qml-process-provider-v7-fault-projection')
P=Path('/home/hoskinson/window-behavior-spec/pin-lifetime-v3/frontend')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    require_qa_scope()
    proofs={}
    for name,count in [('formal-conservation-before-runtime.json',41),('formal-hint-v2-before-runtime.json',49)]:
        p=B/name;r=json.loads(p.read_text());assert r['result']=='pass'
        for path,entry in r['inputs'].items():
            t=Path(path);assert sha(t)==entry['sha256']and stat.S_IMODE(t.stat().st_mode)==entry['mode'],path
        assert f'{count} passing' in r['commands'][0]['stdout']
        assert all(c['exitCode']==0 for c in r['commands'])
        proofs[name]={'sha256':sha(p),'named':count,'traces':2000,'steps':100,'actualRuntimeProof':False}
    inverse=json.loads((B/'proposal/source-inverses.json').read_text());assert inverse['result']=='pass'and all(inverse['checks'].values())
    files=set(p for p in B.rglob('*')if p.is_file())
    files.update(Path(p)for p in inverse['inputs'])
    lineage={
        'original35Model':Q/'process-terminal-retire-v1-model-handoff.json',
        'V7Ready':V/'current-source-ready.json',
        'V7ReadyInputs':V/'current-source-ready-inputs.json',
        'V7CurrentBuild':V/'production-module-current-build.json',
        'V7BuildCompanion':Q/'process-current-v7-build-provenance-v1/build-provenance-companion.json',
        'V7RootReview':Q/'process-current-v7-root-source-review-v1.json',
        'helperRootHandoff':Q/'pin-helper-v1-root-source-handoff-v1.json',
        'retainedReliabilityAttribution':Path('/home/hoskinson/window-behavior-spec/process-reliability-diagnosis-v1/retained-attribution.json'),
    }
    files.update(lineage.values());files.update(P/x for x in ['pin_helper.py','pin_capture.py','pin_config.py'])
    for p in files:assert p.is_file()and not p.is_symlink(),p
    inputs={str(p):sha(p)for p in sorted(files)};modes={str(p):stat.S_IMODE(p.stat().st_mode)for p in sorted(files)}
    result={
        'schema':'process-terminal-retire-source-proposal-v1','status':'source-proposal-ready',
        'inputs':inputs,'inputModes':modes,'proofs':proofs,
        'lineage':{k:{'path':str(v),'sha256':sha(v),'mode':stat.S_IMODE(v.stat().st_mode)}for k,v in lineage.items()},
        'desiredSources':str(B/'proposal/desired'),'unappliedDiffs':str(B/'proposal/diffs'),
        'mapping':str(B/'proposal/REVIEW.md'),'sourceReconstruction':str(B/'proposal/source-inverses.json'),
        'existingSameCommandArmBodyExact':True,'original35Retained':True,
        'runtimeApplied':False,'compiled':False,'helpersLaunched':False,'nativeReady':False,
        'GUI':False,'installedQS':False,'reliabilityAccepted':False,
        'requiresSourceReviewBeforeApplication':True,
        'remaining':['actual proposed C++/QML compilation and Registry/kernel tests','typed public Qt number and queued QObject/lease signal semantics','visible retirement-refusal feedback integration','one bounded varied reliability campaign retaining every failure','actual root-owned private QS/frontend/input proof'],
    }
    target=Q/'process-terminal-retire-v2-source-proposal-handoff-v1.json'
    assert not target.exists(),'Preserve existing handoff; choose a new packet name.'
    target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'packet':str(target),'sha256':sha(target),'inputs':len(inputs),'models':[41,49],'runtimeApplied':False}))
if __name__=='__main__':main()
