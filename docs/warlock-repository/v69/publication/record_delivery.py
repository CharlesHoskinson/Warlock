import json,pathlib,resource,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');base=pathlib.Path(__file__).parent;d=json.loads((base/'delivery.json').read_text());assert d['pushCompleted'] and d['ownedFiles']>=4638
v=json.loads(subprocess.check_output(['gh','repo','view','CharlesHoskinson/Warlock','--json','name,url,visibility'],text=True));assert v['visibility']=='PUBLIC';(base/'visibility.json').write_text(json.dumps(v,indent=2)+'\n')
observed=subprocess.check_output(['gh','api','repos/CharlesHoskinson/Warlock/branches/feature%2Felm','--jq','.commit.sha'],text=True).strip();assert observed==d['publishedCommit']
(base/'branch.json').write_text(json.dumps({'commit':observed,'verified':True},indent=2)+'\n')
report=json.loads((r/'docs/warlock-preview/v93/component-report99.json').read_text())
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
e=loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2','implementation/warlock-preview-provider-v99',['PROGRESS PUBLIC69 '+d['publishedCommit']+' verified '+str(d['ownedFiles'])+' exact owned blobs. Held97 native reservations11/23/397/four +64controls; held98 admission13/21/189/four and retainedlateOffer counterexample; held99 controlled decoder14/22/174/four +44unchangedlegacycontrols +69compiledElm/NativeBroker/realURI/Nativebank controls,25ACKretries no neweffect. Syntheticfacts/fixturebytes only; no WebKit/capture/actor-hostclose/native-release claim. Next actualcontrolledprovider admission/tickets/physical release/reconciliation/outbox integration. FullqualifiedGUI92/native128 originalgatesunchanged.'],'progress',['docs/warlock-preview/v93/component-report99.json','implementation/warlock-preview-provider-v99/component-manifest.json','docs/warlock-repository/v69/publication/delivery.json']);print(e)
