import json,pathlib,resource,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');base=pathlib.Path(__file__).parent;d=json.loads((base/'delivery.json').read_text());assert d['pushCompleted'] and d['ownedFiles']>=825
v=json.loads(subprocess.check_output(['gh','repo','view','CharlesHoskinson/Warlock','--json','name,url,visibility'],text=True));assert v['visibility']=='PUBLIC';(base/'visibility.json').write_text(json.dumps(v,indent=2)+'\n')
observed=subprocess.check_output(['gh','api','repos/CharlesHoskinson/Warlock/branches/feature%2Felm','--jq','.commit.sha'],text=True).strip();assert observed==d['publishedCommit']
(base/'branch.json').write_text(json.dumps({'commit':observed,'verified':True},indent=2)+'\n')
report=json.loads((r/'docs/warlock-preview/v93/component-report-combined-restart-204-207.json').read_text());assert report['passed'] and report['fourOperationBoundaryScenariosQualified'] and report['combinedControlledPreviewRestartQualified'] and not report['uncertainPreviewRetirementQualified']
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
e=loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2','implementation/warlock-client-provider-native-v204',['PROGRESS PUBLIC106 '+d['publishedCommit']+' verified '+str(d['ownedFiles'])+' exact owned blobs. '+report['scope']+' Next actual native preview-effect uncertainty and original-clock pressure/expiry; full GUI goal remains active.'],'progress',['docs/warlock-preview/v93/component-report-combined-restart-204-207.json','implementation/warlock-client-provider-native-v204/component-manifest.json','docs/warlock-repository/v106/publication/delivery.json']);print(e)
