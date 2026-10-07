import json,pathlib,resource,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');base=pathlib.Path(__file__).parent;d=json.loads((base/'delivery.json').read_text());assert d['pushCompleted'] and d['ownedFiles']>=2213
v=json.loads(subprocess.check_output(['gh','repo','view','CharlesHoskinson/Warlock','--json','name,url,visibility'],text=True));assert v['visibility']=='PUBLIC';(base/'visibility.json').write_text(json.dumps(v,indent=2)+'\n')
observed=subprocess.check_output(['gh','api','repos/CharlesHoskinson/Warlock/branches/feature%2Felm','--jq','.commit.sha'],text=True).strip();assert observed==d['publishedCommit']
(base/'branch.json').write_text(json.dumps({'commit':observed,'verified':True},indent=2)+'\n')
report=json.loads((r/'docs/warlock-preview/v93/component-report111.json').read_text())
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
e=loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2','implementation/warlock-preview-provider-v111',['PROGRESS PUBLIC80 '+d['publishedCommit']+' verified '+str(d['ownedFiles'])+' exact owned blobs. GUI111 inactive native-issued renderer outbox C93/protocol47/Quint14/26 actualJS traces/463 states/200 samples/six variants/full97 retains original96. Two Active subject realms share Native grant and strict native barriers. Three fixture failures retained. Parent110 product byte-identical. Native130 current110 legacy2518/278/full cleanup remains bounded baseline. Next native ticket/prefix reload recovery and typed realm/actual WebKit/Core activation. Original full release gates open; no installed changes.'],'progress',['docs/warlock-preview/v93/component-report111.json','implementation/warlock-preview-provider-v111/component-manifest.json','docs/warlock-repository/v80/publication/delivery.json']);print(e)
