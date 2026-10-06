import hashlib,json,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=r/'implementation/warlock-preview-provider-v70';parent=root.parent/'warlock-preview-provider-v69';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((root/'ANCESTRY.json').read_text());assert a['parentManifestSHA256']==sha(parent/'component-manifest.json')
for folder in ['src','native','adapter','assets']:
 for p in (parent/folder).glob('*'):
  if p.is_file() and p.name!='resume-enrollment-test.cpp':assert sha(root/folder/p.name)==sha(p),p
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
e=loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(r)),['PROGRESS70 preparation completed all source/ancestry corrections but checkpoint rejected absolute evidence paths; preserve script/error and emit correct relative checkpoint now. Production unchanged69; only actualoriginalCseed/request/refusedproof and sameElmrequestcounter history added to test, expectednativejob2 intact. FullGUI70build live28391. RunactualCproof thenowningnative; alloriginalfullreleasegates remainactive.'],'progress',[str((root/'ANCESTRY.json').relative_to(r)),str((parent/'component-manifest.json').relative_to(r))]);print(str(e))
