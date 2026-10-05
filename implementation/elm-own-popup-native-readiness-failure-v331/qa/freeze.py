import hashlib,json,os,resource,shutil,time
from pathlib import Path
import sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT.parent/'elm-own-popup-native-diagnostic-v325'
RUN=SOURCE/'qa/native-1791158297819510551'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
out=ROOT/'qa'/('freeze-'+str(time.time_ns()));out.mkdir()
r={'passed':False,'nativeAcceptance':False,'ownBlockerGrantQualified':False,'scope':'Freeze actual failed bootstrap selector; exact core/plugin runtime maps qualified only, no popup query/GTK02/window effect'}
try:
    manifest=SOURCE/'component-manifest.json';assert sha(manifest)=='ed55e341e1ff82fe2198733d9a6b0c89b496d53f5d7ef11d4935988d998f4496'
    m=json.loads(manifest.read_bytes());external={str(manifest):sha(manifest)}
    for name,row in m['files'].items():
        p=SOURCE/name;assert sha(p)==row['sha256'];external[str(p)]=sha(p)
    for name,h in m['externalFiles'].items():assert sha(name)==h;external[name]=h
    d=json.loads((RUN/'report.json').read_bytes())
    assert d['passed'] is False and d['nativeAcceptance'] is False
    assert d['cleanupPassed'] and not d.get('failureCleanupError') and not d['cleanup']['cleanupErrors'] and d['cleanup']['remainingDescendants']==[]
    assert 'Original absolute six-second stage deadline' in d['error'] and 'point(host_log,boot)' in d['traceback']
    assert [x['name'] for x in d['checks']]==['load-exact-authority','load-exact-observer','actual-private-parent-module-map'] and all(x['passed'] for x in d['checks'])
    assert d['processMaps']['mappedLibraryCount']==171 and len(d['processMaps']['requiredArtifacts'])==4
    for name,h in d['artifacts'].items():assert sha(RUN/name)==h
    assert 'wholeGrab' not in d and 'stage' not in d
    lines=(RUN/'native-evidence/elm-webview.log').read_text().splitlines()
    reports=[json.loads(l.split(' ',2)[2]) for l in lines if l.startswith('surface-report: origin=bar ')]
    latest=reports[-1];buttons=latest['body']['buttons'];enabled=[b for b in buttons if b['id'].startswith('group:') and b['disabled'] is False and b['width']>0 and b['height']>0]
    assert len(enabled)==1 and not any(b['id'].startswith('bar:group:') for b in buttons)
    inspection=[json.loads(l[len('surface-inspection: '):]) for l in lines if l.startswith('surface-inspection: ')]
    matching=[x for x in inspection if x['publication']==latest['body']['publication'] and x['lease']==latest['body']['lease'] and x['body']['phase']=='Coherent']
    assert matching and any(g['domId']==enabled[0]['id'] for g in matching[-1]['body']['groups'])
    effects=[json.loads(l[len('frontend-request: '):]) for l in lines if l.startswith('frontend-request: ')]
    assert not any(x.get('kind')=='window-effect' for x in effects)
    assert 'backend-exit: waited=1 normal=1 code=0' in lines
    shutil.copytree(RUN,ROOT/'observed-run')
    r.update(passed=True,failedNativeReport=sha(RUN/'report.json'),nativeLoadChecks=3,mappedLibraryCount=171,cleanupPassed=True,selectorObservation={'publication':latest['body']['publication'],'lease':latest['body']['lease'],'button':enabled[0]},external=external)
except Exception as e:r['error']=repr(e)
(out/'report.json').write_text(json.dumps(r,indent=2)+'\n')
if r['passed']:
    own={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='component-manifest.json'}
    (ROOT/'component-manifest.json').write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'ownBlockerGrantQualified':False,'scope':r['scope'],'files':own,'externalFiles':r['external'],'freezeReport':str(out/'report.json')},indent=2)+'\n')
print(json.dumps({'passed':r['passed'],'report':str(out/'report.json'),'manifestSHA256':sha(ROOT/'component-manifest.json') if r['passed'] else None,'error':r.get('error')}));raise SystemExit(not r['passed'])
