"""Replay actual frozen V1 native protocol frames through compiled V2 code.
Historical wire compatibility evidence only; not new native execution acceptance.
"""
import hashlib
import json
import resource
import shutil
import subprocess
import time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
V1 = REPO/'implementation/elm-context-menu-v1'
LOG = V1/'qa/native-1791068940107201096/native-evidence/elm-webview.log'
OUT = ROOT/'qa'/('historical-'+str(time.time_ns()))
OUT.mkdir()
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
report = {'passed':False, 'scope':'Previously accepted native frames replayed through current compiled Elm; no new native GUI acceptance'}
try:
    manifest = json.loads((V1/'qa/implementation-manifest.json').read_text())
    assert sha(LOG) == manifest['files'][str(LOG.relative_to(V1))]
    build_path = sorted((ROOT/'qa').glob('replay-*/report.json'))[-1]
    build = json.loads(build_path.read_text())
    assert build['passed']
    for relative,digest in build['inputs'].items():
        assert sha(ROOT/relative) == digest, 'Source changed: '+relative
    for source,name in [(LOG,'native.log'),(build_path.parent/'router.js','router.js'),(ROOT/'qa/router.cjs','router.cjs'),(Path(__file__),'historical.py')]:
        shutil.copy2(source,OUT/name)
    commands=[]
    receipts=[]
    projections=[]
    for line in LOG.read_text().splitlines():
        if line.startswith('frontend-request: '):
            frame=json.loads(line.split(': ',1)[1])
            if frame['kind']=='window-effect': commands.append(frame)
        if line.startswith('backend-frame: '):
            frame=json.loads(line.split(': ',1)[1])
            if frame['kind']=='effect-outcome': receipts.append(frame)
            if frame['kind']=='action-projection': projections.append(frame)
    assert len(commands)==len(receipts)==2
    steps=[]
    expected=[]
    for index,(command,receipt) in enumerate(zip(commands,receipts)):
        native=command['binding']; context=command['intent']['context']; incarnation=command['intent']['incarnation']
        projection=next(p for p in projections if p['binding']==native and p['context']==context)
        row=next(w for w in projection['scene']['windows'] if w['incarnation']==incarnation)
        provider={'protocolVersion':1,'providerId':'1','capabilityGeneration':'1',
            'binding':{**native,'revision':context['revision'],'outputId':'1','outputGeneration':context['output']},
            'target':{'lifetime':native['lifetime'],'session':native['session'],'incarnation':incarnation},
            'title':row['label'],'capabilities':['restore','minimize'],
            'items':[{'id':'1','label':'Restore','enabled':row['minimized'],'action':{'kind':'restore'}},
                     {'id':'2','label':'Minimize','enabled':not row['minimized'],'action':{'kind':'minimize'}}]}
        steps.append({'op':'open','provider':provider})
        expected.append({'at':len(steps)-1,'value':{'registry':0,'outstanding':0,'error':None,'menu':{'status':'ready'}}})
        steps.append({'op':'activate','index':1 if command['intent']['operation']=='minimize' else 0,'command':command})
        expected.append({'at':len(steps)-1,'value':{'registry':1,'outstanding':1,'commands':index+1,'error':None,'menu':{'status':'pending'}}})
        steps.append({'op':'receipt','frame':json.dumps(receipt)})
        expected.append({'at':len(steps)-1,'value':{'registry':0,'outstanding':0,'commands':index+1,'error':None,'menu':None}})
    fixtures={'traces':[{'id':'actual-native-minimize-restore-frames','steps':steps,'expect':expected}]}
    (OUT/'fixtures.json').write_text(json.dumps(fixtures,indent=2)+'\n')
    command=['node',str(OUT/'router.cjs'),str(OUT/'router.js'),str(OUT/'fixtures.json'),str(OUT/'checks.json')]
    result=subprocess.run(command,capture_output=True,text=True,timeout=30)
    (OUT/'stdout').write_text(result.stdout);(OUT/'stderr').write_text(result.stderr)
    assert result.returncode==0,result.stderr
    checks=json.loads((OUT/'checks.json').read_text())
    assert checks['passed']
    report.update(passed=True,checks=checks['checks'],nativeCommands=2,nativeReceipts=2,
        sourceLogSHA256=sha(LOG),buildReportSHA256=sha(build_path),buildReport=str(build_path.relative_to(ROOT)),
        command=command,exitCode=result.returncode)
except Exception as error: report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}))
raise SystemExit(not report['passed'])
