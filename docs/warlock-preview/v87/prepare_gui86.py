"""Fresh source for one validated all-native actor retirement transaction."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');p=r/'implementation/warlock-preview-provider-v85';t=r/'implementation/warlock-preview-provider-v86'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
m=p/'component-manifest.json';d=json.loads(m.read_text());assert d['passed'] and d['sourceHeld']
for rel,row in d['files'].items():assert sha(p/rel)==row['sha256'],rel
assert not t.exists()
def ignore(path,names):
 if pathlib.Path(path)==p:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==p/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(p,t,ignore=ignore)
(t/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(p),'parentManifestSHA256':sha(m),
 'purpose':'Atomic native Retired-certified actor removal after exact physical/backend/terminal ACK retirement, across explicit C membership, frames/intents, Coordinator, Broker, original receiver and ReceiptDelivery. Nonreused serial frontier refuses old absent entries; stage new C membership until actual native admission. Integrate typed Elm settlement/control barriers before host activation; all original gates/ordinary eligibility remain.',
 'nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(t.relative_to(r)),
 ['PROGRESS native124 terminalPASS2463/277normal/core16/plugin18/currentGUI85, unchanged strict lock guard/original deadlines fixed parent same-inode writer; freeze55891 terminal. PUBLIC60 03582f63/receipt70c6f9. Fresh GUI86 owned atomic all-native actor retirement and typed Elm settlement/queued-control integration, preserving original physical/journal/counter/receiver/clock obligations. Next native all-map code, selected/coupled Quint/refinement/whole build, exact Elm barrier and actual >256window turnover; full release and ordinary eligibility remain open.'],
 'progress',[str((t/'ANCESTRY.json').relative_to(r))]))
