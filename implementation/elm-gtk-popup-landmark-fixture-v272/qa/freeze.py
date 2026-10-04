"""Freeze compiled actual popup fixture and callback/lifetime evidence."""
import hashlib,importlib.util,json,re,resource,stat,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
ancestor=ROOT/'ancestor-component-manifest.json';assert sha(ancestor)=='32f0cc1aff70793ef9cc2d1bc76508806500a5be34df386696d5db4aa5cc4758'
parent=REPO/'implementation/elm-gtk-sibling-role-fixture-v253';old=json.loads(ancestor.read_text())
assert sha(parent/'native/gtk-role-client.c')==old['files']['native/gtk-role-client.c']['sha256']
assert (ROOT/'native/commands.h').read_bytes()==(parent/'native/commands.h').read_bytes()
spec=importlib.util.spec_from_file_location('callbacks',ROOT/'qa/callback-test.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
before=(parent/'native/gtk-role-client.c').read_text();after=(ROOT/'native/gtk-role-client.c').read_text()
names=re.findall(r'static [^\n{]+\b(\w+)\([^\n]*?\)\{',before)
unchanged=[]
for name in names:
 if name not in ['record','close_role','popover_clicked','execute']:
  assert module.extract(before,name)==module.extract(after,name),name
  unchanged.append(name)
buildpath=ROOT/'client-build-report.json';build=json.loads(buildpath.read_text());assert build['passed'] and not build['nativeAcceptance']
external={str(parent/'component-manifest.json'):sha(parent/'component-manifest.json'),str(parent/'native/gtk-role-client.c'):sha(parent/'native/gtk-role-client.c')}
for filename,row in build['sources'].items():assert sha(ROOT/filename)==row['sha256'] and sha(row['capture'])==row['sha256']
for section in ['tools','dependencies','libraries']:
 for filename,row in build[section].items():assert sha(filename)==row['sha256'];external[filename]=row['sha256']
assert sha(build['artifact']['path'])==build['artifact']['sha256']
selected=['test-1791146397496709165','callbacks-1791146503355529671','lifecycle-1791146397498062343','popup-1791146503047786823']
for label in selected:
 report=json.loads((ROOT/'qa'/label/'report.json').read_text());assert report['passed'] and not report['nativeAcceptance']
 if 'sourceSHA256' in report:assert report['sourceSHA256']==sha(ROOT/'native/gtk-role-client.c')
manifest=ROOT/'component-manifest.json';assert not manifest.exists()
files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)} for p in sorted(ROOT.rglob('*')) if p.is_file()}
manifest.write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'gtk06Accepted':False,'scope':'Actual GTK popup button/area landmark construction and guarded callbacks; native input/pixels unlaunched','files':files,'externalFiles':external,'buildReport':str(buildpath),'artifact':build['artifact'],'selectedReports':selected,'unchangedFunctions':unchanged,'popupMarkerRGB':[255,0,255],'popupMarkerRectangle':[4,4,8,8]},indent=2)+'\n')
print(json.dumps({'passed':True,'manifestSHA256':sha(manifest),'ownFiles':len(files),'externalFiles':len(external),'unchangedFunctions':len(unchanged)}))
