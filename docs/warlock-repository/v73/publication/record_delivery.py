import json,pathlib,resource,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');base=pathlib.Path(__file__).parent;d=json.loads((base/'delivery.json').read_text());assert d['pushCompleted'] and d['ownedFiles']>=6464
v=json.loads(subprocess.check_output(['gh','repo','view','CharlesHoskinson/Warlock','--json','name,url,visibility'],text=True));assert v['visibility']=='PUBLIC';(base/'visibility.json').write_text(json.dumps(v,indent=2)+'\n')
observed=subprocess.check_output(['gh','api','repos/CharlesHoskinson/Warlock/branches/feature%2Felm','--jq','.commit.sha'],text=True).strip();assert observed==d['publishedCommit']
(base/'branch.json').write_text(json.dumps({'commit':observed,'verified':True},indent=2)+'\n')
report=json.loads((r/'docs/warlock-preview/v93/component-report106.json').read_text())
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
e=loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2','implementation/warlock-preview-provider-v106',['PROGRESS PUBLIC73 '+d['publishedCommit']+' verified '+str(d['ownedFiles'])+' exact owned blobs. Held GUI106 actual FD/GIO49+allocator40/two variants,compiled Elm/native ACK24/two normal exits,local14/22/373/three variants;current resource477+35/four,resource14/22/349/three,capture14/66/816/three,C10190/260/1041 and full95. Next real Core19 capture-resource protocol/native qualification, live-window binding detachment and renderer native tickets/WebKit. QualifiedGUI92/native128/core16/plugin18 and original full-release gates unchanged; no installed changes.'],'progress',['docs/warlock-preview/v93/component-report106.json','implementation/warlock-preview-provider-v106/component-manifest.json','docs/warlock-repository/v73/publication/delivery.json']);print(e)
