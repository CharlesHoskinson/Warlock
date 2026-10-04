"""Bind header consumers to actual compiled ancestor objects, including patched sources."""
import collections,hashlib,json,resource,shlex,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[2];OWNER=REPO/'implementation/maximized-stack-v1/native-core-v2';PRIOR=REPO/'implementation/elm-window-geometry-map-state-v28/core/build-1791098117250155855'
BUILD=ROOT/'build-1791101053270682069/report.json';OUT=ROOT/'qa'/('consumer-audit-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
r={'passed':False,'nativeAcceptance':False,'scope':'Actual ancestor object/source dependency closure for changed XDG header; no GUI'}
origins={'FocusState.cpp':'elm-minimize-lifecycle-v14/build-1791060004170871924','ViewHitTester.cpp':'elm-input-hit-v23/build-1791066816123172452','Window.cpp':'elm-window-geometry-map-state-v28/core/build-1791098117250155855','FullscreenController.cpp':'elm-window-geometry-map-state-v28/core/build-1791098117250155855','InputManager.cpp':'elm-minimize-lifecycle-v14/build-1791060004170871924','Monitor.cpp':'elm-native-buffer-size-v7/build-1791090562611157328','XDGShell.cpp':'elm-window-geometry-map-state-v28/core/build-1791098117250155855','ElementRenderer.cpp':'elm-surface-facts-v20/build-1791065974847738580','Renderer.cpp':'elm-surface-facts-v20/build-1791065974847738580','WindowPolicy.cpp':'elm-minimize-lifecycle-v14/build-1791060004170871924'}
try:
 build=json.loads(BUILD.read_text());assert build['passed'] and len(build['rebuiltArchiveMembers'])==17
 old=json.loads((PRIOR/'new-archive-payloads.json').read_text());by=collections.defaultdict(list)
 for row in old:by[row['name']].append(row['sha256'])
 db=OWNER/'build/compile_commands.json';rows=json.loads(db.read_text());groups=collections.defaultdict(list)
 for row in rows:
  if row['output'].startswith('CMakeFiles/hyprland_lib.dir/') and row['output'].endswith('.o'):groups[Path(row['output']).name].append(row)
 target=(OWNER/'src/protocols/XDGShell.hpp').resolve();inventories={};consumers=[];patched=[];duplicates=[]
 def consume(path):
  names=shlex.split(path.read_text().replace(chr(92)+chr(10),' ').split(':',1)[1]);paths={(Path(p) if Path(p).is_absolute() else OWNER/'build'/p).resolve() for p in names};inventories[str(path)]=sha(path);return target in paths
 for member,hashes in by.items():
  group=groups[member]
  if len(group)>1 or len(hashes)>1:
   assert sorted(sha(OWNER/'build'/row['output']) for row in group)==sorted(hashes),member
   duplicates.append({'member':member,'orderedAncestorPayloadHashes':hashes,'owningObjects':[{'path':str(OWNER/'build'/row['output']),'sha256':sha(OWNER/'build'/row['output'])} for row in group]})
   for row in group:
    if consume(OWNER/'build'/(row['output']+'.d')):consumers.append(row['output'])
   continue
  assert len(hashes)==1
  is_changed=not group or sha(OWNER/'build'/group[0]['output'])!=hashes[0]
  if is_changed:
   stem=member.removesuffix('.o');assert stem in origins,member
   origin=REPO/'implementation'/origins[stem];obj=origin/member;assert sha(obj)==hashes[0],member
   report=origin/'report.json';packet=json.loads(report.read_text());assert packet['passed']
   dep=origin/(stem+'.d');uses=consume(dep)
   source_row=next(c for c in packet['commands'] if '-c' in c['command'] and c['command'][c['command'].index('-o')+1]==str(obj));source=Path(source_row['command'][source_row['command'].index('-c')+1]);assert source.is_file()
   inv=packet.get('sources') or packet.get('inputs');key=str(source.relative_to(origin/'inputs'));assert sha(source)==inv[key]
   patched.append({'member':member,'report':str(report),'reportSHA256':sha(report),'object':str(obj),'objectSHA256':sha(obj),'source':str(source),'sourceSHA256':sha(source),'dependency':str(dep),'dependencySHA256':sha(dep),'consumesHeader':uses})
   if uses:assert group,member;consumers.append(group[0]['output'])
  else:
   assert len(group)==1,member
   if consume(OWNER/'build'/(group[0]['output']+'.d')):consumers.append(group[0]['output'])
 actual={Path(p).name for p in consumers};assert actual==set(build['rebuiltArchiveMembers']),{'missing':sorted(actual-set(build['rebuiltArchiveMembers'])),'extra':sorted(set(build['rebuiltArchiveMembers'])-actual)}
 assert len(patched)==10 and len(actual)==17
 for path,wanted in inventories.items():assert sha(path)==wanted,path
 r.update(passed=True,buildReport=str(BUILD),buildReportSHA256=sha(BUILD),patchedObjects=patched,duplicateBasenameGroups=duplicates,dependencyInventories=inventories,actualConsumerMembers=sorted(actual),rawUnmodifiedObjectClosure=True,unaffectedPatchedMembers=[row['member'] for row in patched if not row['consumesHeader']],inputs={str(Path(__file__)):sha(__file__),str(db):sha(db),str(PRIOR/'new-archive-payloads.json'):sha(PRIOR/'new-archive-payloads.json')})
except Exception as error:r['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}),flush=True);raise SystemExit(not r['passed'])
