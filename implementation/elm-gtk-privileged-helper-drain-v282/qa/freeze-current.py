"""Freeze actual current source/CPU evidence, retain all predecessor failures."""
import hashlib,json,resource,stat,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
from preflight import verify,sha
from private_bus import Activations
ROOT=Path(__file__).resolve().parents[1];manifest=ROOT/'component-manifest.json';assert not manifest.exists()
host,core,fixture,observer,probe,external=verify()
selected=['preflight-1791149240251225713', 'private-bus-1791149240345972359', 'activation-1791149240096585639', 'bus-deadline-1791149240396444568', 'bus-journal-1791149240351611621', 'overlay-1791149240400510962', 'wire-1791149240172371936', 'post-retirement-1791149240216244358', 'rapid-reap-1791149240040435924', 'reap-body-1791149240175274215', 'placement-1791149240156834140', 'cleanup-regression-1791149240265200447', 'credentials-1791149240136630797', 'outcomes-1791149240009616152', 'drain-1791149240032075778']
for name in selected:
 path=ROOT/'qa'/name/'report.json';data=json.loads(path.read_text());assert data['passed'] is True
 for filename,expected in data.get('inputs',{}).items():
  assert sha(filename)==expected,filename
  if not Path(filename).is_relative_to(ROOT):external[filename]=expected
failure=ROOT.parents[1]/'implementation/elm-gtk-bootstrap-wire-v252/qa/private-bus-1791144211835016883/report.json';data=json.loads(failure.read_text());assert data['passed'] and data['callerRefusedFallback']
overlay=json.loads((ROOT/'qa/overlay-1791149240400510962/report.json').read_text())
for row in overlay['services']:
 for filename,digest in [(row['source'],row['sourceSHA256']),(row['argv'][0],row['binarySHA256'])]:assert sha(filename)==digest;external[filename]=digest
external['/usr/share/dbus-1/session.conf']=sha('/usr/share/dbus-1/session.conf')
# Configuration includes retain original absolute paths; bind every current file.
for folder in ['/usr/share/dbus-1/session.d','/etc/dbus-1/session.d']:
 for path in Path(folder).rglob('*'):
  if path.is_file():external[str(path)]=sha(path)
for filename in ['/etc/dbus-1/session.conf','/etc/dbus-1/session-local.conf']:
 path=Path(filename)
 if path.is_file():external[filename]=sha(path)
# Bind actual Python/Gio import closure and actual currently loaded libraries.
for module in list(sys.modules.values()):
 filename=getattr(module,'__file__',None)
 if filename and Path(filename).is_file() and not Path(filename).is_relative_to(ROOT):external[filename]=sha(filename)
for line in Path('/proc/self/maps').read_text().splitlines():
 parts=line.split(maxsplit=5)
 if len(parts)==6 and parts[5].startswith('/') and Path(parts[5]).is_file():external[parts[5]]=sha(parts[5])
files={}
for path in sorted(ROOT.rglob('*')):
 if path.is_file():files[str(path.relative_to(ROOT))]={'sha256':sha(path),'size':path.stat().st_size,'mode':stat.S_IMODE(path.stat().st_mode)}
packet={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'fullCampaignPassed':False,'scope':'Privileged helper wait-only policy, per-child signal error isolation, bounded phase drain with terminal/error conservation; failed276 preserved; native source unlaunched','files':files,'externalFiles':external,'selectedCPUReports':[str(ROOT/'qa'/n/'report.json') for n in selected],'actualCallerFallbackRefusal':str(failure),'historicalNativeFailure':str(ROOT.parents[1]/'implementation/elm-gtk-role-native-v238/qa/native-1791141503469881852/report.json'),'sourceNativeTuple':'historical470/plugin471/AQ155; safe244/246/247','selectedNativeTuple':{'core':core['binary'],'coreSHA256':core['sha256'],'authority':core['plugin'],'observer':{'path':observer['binary'],'sha256':observer['binarySHA256']},'gtk':fixture['artifact'],'parentInput':probe},'remainingScenarios':['GTK01','GTK02','GTK03','GTK04','GTK05','GTK06','GTK07','GTK08'],'continuousCommitPresentationGateQualified':False,'invocation':'python3 -B implementation/elm-build-loop-v1/loop.py native --runner '+str(ROOT/'qa/native.py')+' -- --diagnostic-bootstrap'}
ancestor=ROOT/'ancestor-component-manifest.json';assert sha(ancestor)=='95aecc9e6c640cc762f2776c6ad87c33edb82f6f926f546d4f6575f8875a5a32'
parent=ROOT.parents[1]/'implementation/elm-gtk-activation-credentials-fix-v276'
for name,row in json.loads(ancestor.read_text())['files'].items():assert sha(parent/name)==row['sha256'];external[str(parent/name)]=row['sha256']
external[str(parent/'component-manifest.json')]=sha(parent/'component-manifest.json')
review=ROOT.parents[1]/'implementation/elm-gtk-privileged-drain-failure-v281';review_manifest=review/'component-manifest.json'
assert sha(review_manifest)=='c70c1bf8c76c71f69300e5fa580454ff8ed017a0c675600a033699e2aba7b968'
external[str(review_manifest)]=sha(review_manifest)
for name,row in json.loads(review_manifest.read_text())['files'].items():assert sha(review/name)==row['sha256'];external[str(review/name)]=row['sha256']
for name,row in json.loads(review_manifest.read_text())['externalFiles'].items():
 expected=row['sha256'] if isinstance(row,dict) else row
 assert sha(name)==expected;external[name]=expected
for name,row in files.items():assert sha(ROOT/name)==row['sha256']
for filename,expected in external.items():assert sha(filename)==expected,filename
manifest.write_text(json.dumps(packet,indent=2)+'\n');print(json.dumps({'passed':True,'manifest':str(manifest),'sha256':sha(manifest),'ownFiles':len(files),'externalFiles':len(external),'nativeAcceptance':False}))
