import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parent=REPO/'implementation/elm-stable-publication-qualified-v526/qa/slice-manifest.json';assert sha(parent)=='70421e459a6cce9284a133170cd47f5b80d9feb47435d1601f36ca0eaa6ab40e';held=json.loads(parent.read_text())
for row in held['files']:assert sha(REPO/row['path'])==row['sha256']
source=REPO/'implementation/elm-surface-publication-trace-v532';base=REPO/'implementation/elm-stable-surface-publication-v521'
changes=[]
for section in ['src','native','adapter','assets']:
 for p in (source/section).glob('*'):
  if p.is_file() and sha(p)!=sha(base/p.relative_to(source)):changes.append(str(p.relative_to(source)))
assert set(changes)=={'native/shared-host.c','native/shared-context.h'}
for rel,begin,end in [('native/shared-host.c','    if (qa_exit && kind && (g_str_equal(kind,"view-commit")','    if (qa_exit && kind && g_str_equal(kind,"surface-report")'),('native/shared-context.h','    if (qa_exit && (event->type==GDK_BUTTON_PRESS','    if(event->type==GDK_KEY_PRESS && ((GdkEventKey *)event)->keyval==GDK_KEY_Escape)')]:
 text=(source/rel).read_text();start=text.index(begin);finish=text.index(end,start);assert text[:start]+text[finish:]==(base/rel).read_text()
files=[];links=[];reports=[];native=[]
for number in [528,529,530,532,533,534]:
 directory=next((REPO/'implementation').glob('*v'+str(number)))
 for p in sorted(directory.rglob('*')):
  if '__pycache__' in p.parts or 'elm-stuff' in p.parts:continue
  if p.is_symlink():links.append({'path':str(p.relative_to(REPO)),'target':str(p.readlink())});continue
  if not p.is_file():continue
  files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
  if p.name!='report.json' or any(x in p.relative_to(directory).parts for x in ['inputs','native-evidence']):continue
  j=json.loads(p.read_text());assert j['passed'];reports.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'passed':True})
  for rel,digest in j.get('artifacts',{}).items():assert sha(p.parent/rel)==digest
  if p.parent.name.startswith('native-'):
   expected={529:161,530:57,533:89}[number];assert len(j['checks'])==expected and all(c['passed'] for c in j['checks']) and j['cleanupPassed'] and not j['mainDesktopActions'];assert j['pair']==held['nativePair'];native.append({'path':str(p.relative_to(REPO)),'checks':expected,'diagnostic':number==533,'buildReport':j['buildReport']})
assert len(native)==3
production=[r for r in native if not r['diagnostic']];assert sum(r['checks'] for r in production)==218
original=REPO/held['nativeReports'][0];j=json.loads(original.read_text());assert j['passed'] and len(j['checks'])==89 and j['cleanupPassed'] and j['buildReport']==production[0]['buildReport']==production[1]['buildReport'];assert j['pair']==held['nativePair']
analysis=REPO/'implementation/elm-surface-publication-trace-analysis-v534/qa/report.json';a=json.loads(analysis.read_text());assert a['passed'] and a['bridgeInputCount']==99 and a['pointerProofCount']==40 and len(a['correlatedPointerContexts'])==11 and a['decoderNegativeControls']==5;assert sha(Path(a['nativeReport']))==a['nativeReportSHA256'] and sha(Path(a['log']))==a['logSHA256']
for p in [Path(__file__).resolve(),ROOT/'HANDOFF.md']:files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
result={'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'source':'implementation/elm-stable-surface-publication-v521','diagnosticSource':str(source.relative_to(REPO)),'parentManifest':str(parent),'parentManifestSHA256':sha(parent),'nativeAcceptance':True,'newProductionNativeChecks':218,'coherentProductionNativeChecks':307,'diagnosticNativeChecks':89,'nativeReports':native,'nativePair':held['nativePair'],'files':files,'symlinks':links,'reports':reports,'diagnosticAnalysis':str(analysis.relative_to(REPO)),'pointerRaceCausallyResolved':False,'fullReleaseAccepted':False,'completedRequirementIds':[]}
p=ROOT/'qa/slice-manifest.json';assert not p.exists();p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':True,'files':len(files),'reports':len(reports),'newProductionChecks':218,'coherentProductionChecks':307,'diagnosticChecks':89,'manifestSHA256':sha(p)}))
