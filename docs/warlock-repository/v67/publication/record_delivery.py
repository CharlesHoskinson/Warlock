import json,pathlib,resource,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');base=pathlib.Path(__file__).parent;d=json.loads((base/'delivery.json').read_text());assert d['pushCompleted'] and d['ownedFiles']>=777
v=json.loads(subprocess.check_output(['gh','repo','view','CharlesHoskinson/Warlock','--json','name,url,visibility'],text=True));assert v['visibility']=='PUBLIC';(base/'visibility.json').write_text(json.dumps(v,indent=2)+'\n')
observed=subprocess.check_output(['gh','api','repos/CharlesHoskinson/Warlock/branches/feature%2Felm','--jq','.commit.sha'],text=True).strip();assert observed==d['publishedCommit']
(base/'branch.json').write_text(json.dumps({'commit':observed,'verified':True},indent=2)+'\n')
report=json.loads((r/'docs/warlock-preview/v93/component-report95.json').read_text())
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
e=loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2','implementation/warlock-preview-provider-v95',['PROGRESS PUBLIC67 '+d['publishedCommit']+' verified '+str(d['ownedFiles'])+' exact owned blobs. HeldGUI95 inactive native control12selected/20traces/190states/3compiled mutants, JS10selected/22traces/389states/3JSvariants and64nativeMetadata+JS loss/retry/Unknown/order/backpressure/normalcleanup controls. Productionmodules unchanged; fullyqualifiedGUI92/native128 unchanged. Next receipt confirmation before native close, cleanup reservations before native admission, receiver reconciliation and actual WebKit activation. All original release gates remain.'],'progress',['docs/warlock-preview/v93/component-report95.json','implementation/warlock-preview-provider-v95/component-manifest.json','docs/warlock-repository/v67/publication/delivery.json']);print(e)
