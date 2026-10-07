import json,pathlib,resource,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');base=pathlib.Path(__file__).parent;d=json.loads((base/'delivery.json').read_text());assert d['pushCompleted'] and d['ownedFiles']>=10076
v=json.loads(subprocess.check_output(['gh','repo','view','CharlesHoskinson/Warlock','--json','name,url,visibility'],text=True));assert v['visibility']=='PUBLIC';(base/'visibility.json').write_text(json.dumps(v,indent=2)+'\n')
observed=subprocess.check_output(['gh','api','repos/CharlesHoskinson/Warlock/branches/feature%2Felm','--jq','.commit.sha'],text=True).strip();assert observed==d['publishedCommit']
(base/'branch.json').write_text(json.dumps({'commit':observed,'verified':True},indent=2)+'\n')
report=json.loads((r/'docs/warlock-preview/v93/component-report105.json').read_text())
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
e=loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2','implementation/warlock-preview-provider-v105',['PROGRESS PUBLIC72 '+d['publishedCommit']+' verified '+str(d['ownedFiles'])+' exact owned blobs. Held104 capture intent/adoption and held105/plugin19 scoped resource/C recovery477+35/four variants,14/22/349/three resource model,original capture14/66/816/three,controlled C10190/260/1041,95 full host and core16/plugin19 compile. Actual adopted-FD/readers reconciliation, native Core registry/capture, live-window binding detachment and renderer native tickets/WebKit remain open. RuntimeGUI92/native128/core16/plugin18 and original gates unchanged.'],'progress',['docs/warlock-preview/v93/component-report105.json','implementation/warlock-preview-provider-v105/component-manifest.json','docs/warlock-repository/v72/publication/delivery.json']);print(e)
