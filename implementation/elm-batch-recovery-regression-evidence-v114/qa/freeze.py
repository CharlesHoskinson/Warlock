"""Freeze exact full semantic regression and current host adapter evidence."""
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
REG=REPO/'implementation/elm-shared-batch-semantic-regressions-v108'
HOST=REPO/'implementation/elm-geometry-current-private-host-links-v112'
SEM=REG/'semantic/qa/replay-1791110787029714375/report.json'
POST=REG/'post-close/qa/replay-1791110820482726038/report.json'
PREFLIGHT=HOST/'qa/preflight-1791110830508333771/report.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify_artifacts(path,data):
    for relative,expected in data['artifacts'].items():
        p=path.parent/relative
        assert not p.is_symlink() and p.resolve().is_relative_to(path.parent.resolve()) and sha(p)==expected,str(p)
def main():
    out=ROOT/'qa'/('freeze-'+str(time.time_ns()));out.mkdir()
    result={'passed':False,'nativeAcceptance':False,'fullRoadmapAccepted':False}
    try:
        sem=json.loads(SEM.read_text());post=json.loads(POST.read_text());host=json.loads(PREFLIGHT.read_text())
        assert sem['passed'] and post['passed'] and host['passed']
        assert sem['sourceInputs']==post['sourceInputs'] and sem['sourceRoot']==post['sourceRoot']
        assert [sem['stagedSuites'][k]['checks'] for k in ['menu','geometry','refresh']]==[78,53,21]
        assert all(row['passed'] for row in sem['stagedSuites'].values())
        assert post['postCloseChecks']['checks']==59 and post['postCloseChecks']['passed']
        assert len(host['checks'])==23 and all(row['passed'] for row in host['checks'])
        for relative,expected in sem['sourceInputs'].items():assert sha(Path(sem['sourceRoot'])/relative)==expected,relative
        for report in [SEM,POST,PREFLIGHT]:verify_artifacts(report,json.loads(report.read_text()))
        for path,expected in host['inputs'].items():assert sha(Path(path))==expected,path
        for row in json.loads((HOST/'parent-failure.json').read_text())['files']:assert sha(Path(row['path']))==row['sha256']
        paths=set([SEM,POST,PREFLIGHT,Path(__file__)])
        for base in [REG,HOST]:
            for path in base.rglob('*'):
                if path.is_file() and not path.is_symlink():paths.add(path)
        paths.update(Path(sem['sourceRoot'])/rel for rel in sem['sourceInputs'])
        inventory=[{'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size} for p in sorted(paths)]
        packet={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'fullRoadmapAccepted':False,
                'scope':'Actual shared recovery production semantic regressions211 and current private host closure23; no disposition-specific or native acceptance',
                'semanticChecks':211,'hostPreflightChecks':23,'productionRoot':sem['sourceRoot'],'tuple':host['tuple'],
                'originalImmediateDispatchDiagnosticsRetained':sem['originalSuites'],
                'reports':[{'path':str(p.relative_to(REPO)),'sha256':sha(p)} for p in [SEM,POST,PREFLIGHT]],'files':inventory}
        (ROOT/'component-manifest.json').write_text(json.dumps(packet,indent=2)+'\n')
        result.update(passed=True,files=len(inventory),semanticChecks=211,hostPreflightChecks=23)
    except Exception as error:result['error']=repr(error)
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),**result}));return not result['passed']
if __name__=='__main__':raise SystemExit(main())
