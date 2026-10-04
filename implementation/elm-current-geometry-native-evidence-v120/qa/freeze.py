"""Freeze exact current-tuple geometry qualification with its bounded scope."""
import hashlib,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
CANDIDATE=REPO/'implementation/elm-geometry-current-host-native-v118'
REPORT=CANDIDATE/'qa/native-1791111444682157633/report.json'
ANCESTOR=REPO/'implementation/elm-geometry-monitor-native-regression-v79/qa/native-1791107523831396904/report.json'
OUT=ROOT/'qa'/('freeze-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
result={'passed':False,'fullRoadmapAccepted':False}
try:
    d=json.loads(REPORT.read_text());old=json.loads(ANCESTOR.read_text())
    assert old['passed'] and d['passed'] and d['cleanupPassed']
    assert len(old['checks'])==96 and len(d['checks'])==98 and all(row['passed'] for row in d['checks'])
    additions={'normalGeometryClientExitBeforePluginUnload','nativeGeometryClientsEmptyBeforePluginUnload'}
    assert [r['name'] for r in d['checks'] if r['name'] not in additions]==[r['name'] for r in old['checks']]
    assert len([r for r in d['checks'] if 'actualInteriorPixelsMatchSelectedConfigure' in r['name']])==7
    core=d['privateHost']['privateCore'];aq=d['privateHost']['privateAquamarine']
    assert core['sha256']=='3e02556699f1e1667a88ace26f656ee380fce8a39b20d405a3f0d2757c65cd73'
    assert aq['mappedVerified'] and aq['mappedFiles']=={aq['path']:'b7431f7036d28ed1f87a1aec9374a7700a2ebb9e819a707f0e8368a87cfcff97'}
    for absolute,expected in d['inputs'].items():assert sha(Path(absolute))==expected,absolute
    for relative,expected in d['artifacts'].items():
        p=REPORT.parent/relative
        assert not p.is_symlink() and p.resolve().is_relative_to(REPORT.parent.resolve()) and sha(p)==expected,relative
    held=CANDIDATE/'qa/held-source-manifest.json';h=json.loads(held.read_text())
    assert h['sourceHeld'] and h['evidenceIntegrityPassed']
    for relative,row in h['files'].items():assert sha(CANDIDATE/relative)==row['sha256'] and (CANDIDATE/relative).stat().st_size==row['size'],relative
    paths=set([REPORT,ANCESTOR,held,Path(__file__)])
    paths.update(REPORT.parent/relative for relative in d['artifacts'])
    paths.update(CANDIDATE/relative for relative in h['files'])
    inventory=[{'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size} for p in sorted(paths)]
    packet={'sourceHeld':True,'evidenceIntegrityPassed':True,'boundedNativeGeometryAccepted':True,
            'originalGeometryChecks':96,'additionalCleanupChecks':2,'pixelCheckpoints':7,
            'cleanupPassed':True,'fullMenuAccepted':False,'sharedRecoveryAccepted':False,'fullRoadmapAccepted':False,
            'scope':'Exact original native geometry campaign on core89/plugin90/AQ105 through current reviewed facade; no Elm/menu/shared recovery acceptance',
            'nativeReport':str(REPORT),'nativeReportSHA256':sha(REPORT),'tuple':{'core':core,'aquamarine':aq,'pluginSHA256':d['pluginSHA256']},'files':inventory}
    (ROOT/'component-manifest.json').write_text(json.dumps(packet,indent=2)+'\n')
    result.update(passed=True,files=len(paths),boundedNativeGeometryAccepted=True)
except Exception as error:result['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'report':str(OUT/'report.json'),**result}));raise SystemExit(not result['passed'])
