"""Build native attention/navigation authority against the unchanged owning ABI.

Frozen capture/policy dependencies are referenced by hash; no copied lineage.
This report proves compilation/closure only. Actual native journeys are separate.
"""
import hashlib,json,os,pathlib,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope()
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
PRIOR=REPO/'implementation/warlock-family-style-crop-capture-v19/qa/build-1791342038926680323'
HELD=PRIOR.parents[1]
OUT=ROOT/'qa/runs'/('native-authority-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
r={'passed':False,'nativeAcceptance':False,'installed':False,'protectedScope':scope,'commands':[],
   'scope':'Changed native pointer ownership observation/effect guards and navigation authority TU against unchanged owning core/capture inputs; strict strong-symbol closure; native acceptance separate'}
def run(name,args):
 p=subprocess.run(args,capture_output=True,text=True,timeout=180)
 (OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr)
 r['commands'].append({'name':name,'command':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 if p.returncode:raise RuntimeError(p.stderr[-4000:])
 return p.stdout
try:
 prior=json.loads((PRIOR/'report.json').read_text());assert prior['passed'] and sha(prior['binary'])==prior['binarySHA256']
 # Every previously compiled dependency and library remains exact, including
 # retained native policy headers and the owning core's exported ABI.
 preserved={**prior['dependencies'],**prior['linkedLibraries'],**prior['tools']}
 for p,h in preserved.items():assert sha(p)==h,p
 core=prior['core'];assert sha(core['path'])==core['sha256']
 old_core=dict(core);focus_core=None;header_prefix=None
 focus_path=ROOT/'qa/current-focus-core.json'
 if focus_path.exists():
  focus=json.loads(focus_path.read_text());focus_report=REPO/focus['report']
  assert sha(focus_report)==focus['reportSHA256'];focus_core=json.loads(focus_report.read_text())
  assert focus_core['passed'] and focus_core['existingPublicHeadersUnchanged'] and focus_core['existingObjectLayoutsUnchanged']
  assert sha(ROOT/'native/core/SeatManager.cpp')==focus_core['sourceSHA256']
  owning=pathlib.Path(old_core['path']).parent
  original_core=json.loads((owning/'report.json').read_text())
  assert focus_core['owningHeaders']==original_core['owningHeaders']
  header_prefix=(str(owning/'owning-headers'),str(focus_report.parent/'owning-headers'))
  for rel,h in focus_core['owningHeaders'].items():assert sha(pathlib.Path(header_prefix[1])/rel)==h
  core={'path':focus_core['binary'],'sha256':focus_core['binarySHA256']};assert sha(core['path'])==core['sha256']
 pin_path=ROOT/'qa/current-pin-core.json'
 if pin_path.exists():
  pin=json.loads(pin_path.read_text());pin_report=REPO/pin['report'];assert sha(pin_report)==pin['reportSHA256'];pin_core=json.loads(pin_report.read_text())
  assert pin_core['passed'] and pin_core['existingPublicHeadersUnchanged'] and pin_core['existingObjectLayoutsUnchanged'] and sha(ROOT/'native/core/ConfigActions.cpp')==pin_core['sourceSHA256']
  assert pin_core['ancestor']=={'report':str(focus_report),'reportSHA256':sha(focus_report)} and pin_core['owningHeaders']==focus_core['owningHeaders']
  header_prefix=(header_prefix[0],str(pin_report.parent/'owning-headers'));core={'path':pin_core['binary'],'sha256':pin_core['binarySHA256']};assert sha(core['path'])==core['sha256']
 scene_pointer=ROOT/'qa/current-scene-core.json'
 scene_meta=json.loads(scene_pointer.read_text()) if scene_pointer.exists() else None
 scene_record=json.loads((REPO/scene_meta['report']).read_text()) if scene_meta else None
 max_path=ROOT/'qa/current-max-core.json'
 if max_path.exists():
  maximum=json.loads(max_path.read_text());max_report=REPO/maximum['report'];assert sha(max_report)==maximum['reportSHA256'];max_core=json.loads(max_report.read_text())
  assert max_core['passed'] and max_core['existingPublicHeadersUnchanged'] and max_core['existingObjectLayoutsUnchanged'] and sha(ROOT/'native/core/FullscreenController.cpp')==max_core['sourceSHA256'] and all(sha((max_report.parent/'owning-headers'/('src/desktop/state/ViewHitTester.cpp' if p=='native/core/ViewHitTester.cpp' else 'src/desktop/view/Window.cpp')) if scene_record and p in ('native/core/ViewHitTester.cpp','native/core/Window.cpp') else ROOT/p)==h for p,h in max_core['sourceHashes'].items())
  assert max_core['ancestor']=={'report':str(pin_report),'reportSHA256':sha(pin_report)} and max_core['owningHeaders']==pin_core['owningHeaders']
  header_prefix=(header_prefix[0],str(max_report.parent/'owning-headers'));core={'path':max_core['binary'],'sha256':max_core['binarySHA256']};assert sha(core['path'])==core['sha256']
 if scene_record:
  scene_report=REPO/scene_meta['report'];assert sha(scene_report)==scene_meta['reportSHA256']
  assert scene_record['passed'] and scene_record['existingPublicHeadersUnchanged'] and scene_record['existingObjectLayoutsUnchanged'] and scene_record['existingStrongExportsPreserved']
  expected_ancestor={'report':str(max_report),'reportSHA256':sha(max_report)}
  scene_base=scene_record
  seen_ancestors=set()
  while scene_base['ancestor']!=expected_ancestor:
   child=scene_base;parent_path=pathlib.Path(child['ancestor']['report'])
   assert str(parent_path) not in seen_ancestors and len(seen_ancestors)<2;seen_ancestors.add(str(parent_path))
   assert sha(parent_path)==child['ancestor']['reportSHA256']
   scene_base=json.loads(parent_path.read_text());assert scene_base['passed'] and sha(scene_base['binary'])==scene_base['binarySHA256']
   assert scene_base['existingPublicHeadersUnchanged'] and scene_base['existingObjectLayoutsUnchanged'] and scene_base['existingStrongExportsPreserved']
   assert child['owningHeaders']==scene_base['owningHeaders']
   changes=set(child.get('changedSources',['native/core/KeybindManager.cpp','native/core/GestureKeyPolicy.hpp']))
   assert changes in ({'native/core/KeybindManager.cpp','native/core/GestureKeyPolicy.hpp'},{'native/core/Window.cpp','native/core/CaptionGesturePolicy.hpp'})
   assert set(child['sourceHashes'])==set(scene_base['sourceHashes'])|changes
   assert all(child['sourceHashes'][p]==h for p,h in scene_base['sourceHashes'].items() if p not in changes)
   assert all(sha(p)==h for p,h in {**scene_base['dependencies'],**scene_base['linkDependencies']}.items())
  assert 'native/core/Window.cpp' in scene_record['sourceHashes'] or sha(ROOT/'native/core/Window.cpp')==max_core['sourceHashes']['native/core/Window.cpp']
  assert scene_base['ancestor']==expected_ancestor and scene_record['owningHeaders']==max_core['owningHeaders']
  assert all(sha(ROOT/p)==h for p,h in scene_record['sourceHashes'].items())
  assert all(sha(p)==h for p,h in scene_record['dependencies'].items()) and all(sha(p)==h for p,h in scene_record['linkDependencies'].items())
  header_prefix=(header_prefix[0],str(scene_report.parent/'owning-headers'));core={'path':scene_record['binary'],'sha256':scene_record['binarySHA256']};assert sha(core['path'])==core['sha256']
 source=OUT/'inputs/native';source.mkdir(parents=True)
 inputs={}
 for name in ('authority.cpp','navigation-modal.hpp','geometry-effects.inc','snap-placement.inc','transfer-workspace.inc','motion-profile.inc','picker-preview.inc','picker-probe-table.hpp','capture-fd-server.inc','geometry.inc','shortcut-bindings.inc'):
  p=ROOT/'native'/name;inputs['native/'+name]=sha(p);shutil.copyfile(p,source/name)
 if scene_record:
  p=ROOT/'native/core/CommittedScene.hpp';inputs['native/core/CommittedScene.hpp']=sha(p);(source/'core').mkdir();shutil.copyfile(p,source/'core/CommittedScene.hpp')
  p=ROOT/'native/core/ModalRecipient.hpp';inputs['native/core/ModalRecipient.hpp']=sha(p);shutil.copyfile(p,source/'core/ModalRecipient.hpp')
 command=next(c['command'] for c in prior['commands'] if c['name']=='compile').copy()
 for i,arg in enumerate(command):
  if arg==str(PRIOR/'inputs/native/authority.cpp'):command[i]=str(source/'authority.cpp')
  elif i and command[i-1]=='-o':command[i]=str(OUT/'elm-window-geometry-authority.so')
  elif i and command[i-1]=='-MF':command[i]=str(OUT/'authority.d')
  elif header_prefix and arg.startswith('-I'+header_prefix[0]):command[i]='-I'+header_prefix[1]+arg[len('-I'+header_prefix[0]):]
 command[1:1]=['-I'+str(PRIOR/'inputs/native')]
 run('navigation-authority-compile',command)
 binary=OUT/'elm-window-geometry-authority.so'
 deps=shlex.split((OUT/'authority.d').read_text().replace('\\\n',' ').split(':',1)[1])
 dependencies={str(pathlib.Path(p).resolve()):sha(p) for p in deps}
 for p,h in dependencies.items():
  if p.startswith(str(source)):
   assert pathlib.Path(p).name in ('ModalRecipient.hpp','CommittedScene.hpp','authority.cpp','navigation-modal.hpp','geometry-effects.inc','snap-placement.inc','transfer-workspace.inc','motion-profile.inc','picker-preview.inc','picker-probe-table.hpp','capture-fd-server.inc','geometry.inc','shortcut-bindings.inc')
  else:
   inherited=header_prefix[0]+p[len(header_prefix[1]):] if header_prefix and p.startswith(header_prefix[1]+'/') else p
   recorded=preserved.get(inherited)
   verified_header=focus_core and '/owning-headers/' in p and focus_core['owningHeaders'].get(p.split('/owning-headers/',1)[1])==h
   assert recorded==h or (recorded is None and verified_header),('Unrecorded or changed inherited dependency',p)
 exports=set()
 for command_row in prior['commands']:
  if not command_row['name'].startswith('provider-symbols-'):continue
  path=PRIOR/(command_row['name']+'.stdout');assert sha(path)==prior['artifacts'][path.name]
  provider=command_row['command'][-1];assert sha(provider)==(old_core['sha256'] if provider==old_core['path'] else prior['linkedLibraries'][provider])
  symbols=run('current-core-exports',['nm','-D','--defined-only',core['path']]) if focus_core and provider==old_core['path'] else path.read_text()
  for line in symbols.splitlines():
   words=line.split()
   if len(words)>=3:
    symbol=words[-1].replace('@@','@');exports.add(symbol);exports.add(symbol.split('@')[0])
 missing=[]
 for line in run('plugin-undefined',['nm','-D','--undefined-only',str(binary)]).splitlines():
  words=line.split()
  if len(words)==2 and words[0]=='U' and words[1] not in exports:missing.append(words[1])
 assert not missing,missing
 for rel,h in inputs.items():assert sha(ROOT/rel)==h
 for p,h in preserved.items():assert sha(p)==h,p
 assert sha(core['path'])==core['sha256']
 r.update(passed=True,inputs=inputs,dependencies=dependencies,inheritedBuild=str(PRIOR/'report.json'),
          inheritedBuildSHA256=sha(PRIOR/'report.json'),core=core,binary=str(binary),binarySHA256=sha(binary),missingSymbols=missing,
          focusCoreReport=focus if focus_core else None)
except Exception as e:r['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
