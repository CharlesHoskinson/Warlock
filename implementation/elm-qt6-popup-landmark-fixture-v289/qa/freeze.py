import hashlib,importlib.util,json,re,resource,stat,sys
from pathlib import Path
sys.path.insert(0,"/home/hoskinson/window-integration-qa")
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
manifest=ROOT/"component-manifest.json";assert not manifest.exists()
parent=REPO/"implementation/elm-qt6-role-journal-fixture-v250";ancestor=ROOT/"ancestor-component-manifest.json";assert sha(ancestor)=="c65966d9a136418a4b371278a554d3d830890f0d74b76950984857c0e4097983"
build=json.loads((ROOT/"client-build-report.json").read_text());assert build['passed'] is True and build['nativeAcceptance'] is False
external={str(parent/"component-manifest.json"):sha(parent/"component-manifest.json")}
for name,row in json.loads(ancestor.read_text())['files'].items():assert sha(parent/name)==row['sha256'];external[str(parent/name)]=row['sha256']
for name,row in build['sources'].items():assert sha(ROOT/name)==sha(row['capture'])==row['sha256']
for group in ['dependencies','tools','libraries']:
 for path,row in build[group].items():assert sha(path)==row['sha256'];external[path]=row['sha256']
assert sha(build['artifact']['path'])==build['artifact']['sha256']
for name in ['commands.hpp','private-runtime.h']:assert (ROOT/'native'/name).read_bytes()==(parent/'native'/name).read_bytes()
spec=importlib.util.spec_from_file_location('extractor',ROOT/'qa/lifetime-test.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
a=(parent/'native/qt-role-client.cpp').read_text();b=(ROOT/'native/qt-role-client.cpp').read_text();unchanged=[]
for name in re.findall(r'static [^\n{]*\b(\w+)\([^\n]*?\)\{',a):
 if name not in ['record','retire','execute']:
  assert module.extract(a,name)==module.extract(b,name),name;unchanged.append(name)
for start,end in [('class Landmark final:','static Role* roleWindow'),('class Observer final:','static bool currentRole')]:assert a[a.index(start):a.index(end)]==b[b.index(start):b.index(end)]
selected=['test-1791149874091237550','lifetime-1791149874090977176','popup-1791149872937719716']
for name in selected:
 r=json.loads((ROOT/'qa'/name/'report.json').read_text());assert r['passed'] is True and r['nativeAcceptance'] is False
 if 'sourceSHA256' in r:assert r['sourceSHA256']==sha(ROOT/'native/qt-role-client.cpp')
files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)} for p in sorted(ROOT.rglob('*')) if p.is_file()}
manifest.write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'qt06Accepted':False,'files':files,'externalFiles':external,'selectedReports':selected,'buildReport':str(ROOT/'client-build-report.json'),'artifact':build['artifact'],'unchangedFunctions':unchanged,'popupMarkerRGB':[255,0,255],'popupMarkerRectangle':[4,4,8,8]},indent=2)+'\n');print(json.dumps({'passed':True,'manifestSHA256':sha(manifest),'ownFiles':len(files),'externalFiles':len(external),'unchangedFunctions':len(unchanged)}))
