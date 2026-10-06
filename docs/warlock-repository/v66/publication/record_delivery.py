import json,pathlib,resource,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');base=pathlib.Path(__file__).parent;d=json.loads((base/'delivery.json').read_text());assert d['pushCompleted'] and d['ownedFiles']>1000
v=json.loads(subprocess.check_output(['gh','repo','view','CharlesHoskinson/Warlock','--json','name,url,visibility'],text=True));assert v['visibility']=='PUBLIC';(base/'visibility.json').write_text(json.dumps(v,indent=2)+'\n')
observed=subprocess.check_output(['gh','api','repos/CharlesHoskinson/Warlock/branches/feature%2Felm','--jq','.commit.sha'],text=True).strip();assert observed==d['publishedCommit']
(base/'branch.json').write_text(json.dumps({'commit':observed,'verified':True},indent=2)+'\n')
report=json.loads((r/'docs/warlock-preview/v93/component-report94.json').read_text())
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
e=loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2','implementation/warlock-preview-provider-v94',['PROGRESS PUBLIC66 '+d['publishedCommit']+' verified '+str(d['ownedFiles'])+' exact owned blobs. HeldGUI94 fairpoll full95/identicalElm/45 controls/nativeElm54/Csocket50/Q10selected/22actualC++traces/427states/3compiledMutants and original9068aggregate/14467channel/280synthetic. FullyqualifiedGUI92/native128 stays unchanged. Next fresh bounded reliable outgoing control/retry/ACK/nativecleanupreservation/reload contract before actual WebKit activation. All original release gates remain.'],'progress',['docs/warlock-preview/v93/component-report94.json','implementation/warlock-preview-provider-v94/component-manifest.json','docs/warlock-repository/v66/publication/delivery.json']);print(e)
