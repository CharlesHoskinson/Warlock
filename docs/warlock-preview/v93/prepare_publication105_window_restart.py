"""Prepare exact owned publication of current main-window restart qualification."""
import ast,json,pathlib,re,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');out=repo/'docs/warlock-repository/v105/publication';assert not out.exists()
base='4e5774fd8433275d2d80e189221510e479fee247';local='26ae1e8eda0e9c6ceef47457e7479589478fbd1c';previous='884a5d7afc7a73bc475379a81e5dd3272659b975';oldbase='0ddc454b739f0a8dce50530d661a8b2e86551ca7'
components=[(f'warlock-client-provider-native-v{v}',v>=198) for v in range(195,202)]+[('warlock-window-restart-supervisor-v1',True)]
minimum=0
for name,passed in components:
 held=json.loads((repo/'implementation'/name/'component-manifest.json').read_text());assert held['sourceHeld'] and held['passed']==passed;minimum+=len(held['files'])
held=json.loads((repo/'docs/warlock-preview/v93/component-report-window-restart-198-201.json').read_text())
assert held['passed'] and held['fourOperationBoundaryScenariosQualified'] and held['fullBuildCommands']==119
out.mkdir(parents=True);prior=repo/'docs/warlock-repository/v104/publication'
def put(name,text):ast.parse(text);(out/name).write_text(text)
text=(prior/'publish.py').read_text().replace(oldbase,base).replace('3a25f38c155bcf60fd27110a9a0190a3be418d65..',previous+'..')
allowed=('docs/warlock-preview/v93/','docs/warlock-repository/v104/publication/','docs/warlock-repository/v105/publication/',*(f'implementation/{name}/' for name,_ in components),'openspec/changes/warlock-preview-actor-retirement/tasks.md','openspec/changes/warlock-preview-actor-retirement/specs/preview-actors/spec.md')
a=text.index('allowed=');b=text.index('\nassert all',a);text=text[:a]+'allowed='+repr(allowed)+text[b:]
a=text.index(' qualification=');b=text.index('\n published=',a)
qualification=" qualification=json.loads((REPO/'docs/warlock-preview/v93/component-report-window-restart-198-201.json').read_text());assert qualification['passed'] and qualification['fourOperationBoundaryScenariosQualified'] and qualification['actualWindowCommandRestartQualified'] and qualification['actualWindowCommandDurableUnknownQualified'] and qualification['historicalUnknownPreserved'] and qualification['automaticUnknownReplayCount']==0 and qualification['nativeAuthorityResets']==0 and qualification['fullBuildCommands']==119 and qualification['privateSessionCleanupPassed'] and not qualification['combinedControlledPreviewRestartQualified'] and not qualification['wholeHostRestartQualified'] and not qualification['nativeAcceptance'] and not qualification['fullReleaseAccepted']\n assert [qualification['reports']['native'+str(v)]['checks'] for v in range(198,202)]==[63,61,63,61]"
title='Qualify durable window commands across native restart'
text=text[:a]+qualification+'\n message='+repr(title+'\n\n'+held['scope'])+'\n'+text[b:];put('publish.py',text)
text=(prior/'record_delivery.py').read_text();a=text.index('report=json.loads(');b=text.index('\nsys.path.insert',a)
text=text[:a]+"report=json.loads((r/'docs/warlock-preview/v93/component-report-window-restart-198-201.json').read_text());assert report['passed'] and report['fourOperationBoundaryScenariosQualified'] and not report['combinedControlledPreviewRestartQualified']"+text[b:]
text,n=re.subn(r"d\['ownedFiles'\]>=\d+","d['ownedFiles']>="+str(minimum),text);assert n==1
a=text.index('e=loop.write_checkpoint(')
text=text[:a]+"e=loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2','implementation/warlock-client-provider-native-v198',['PROGRESS PUBLIC105 '+d['publishedCommit']+' verified '+str(d['ownedFiles'])+' exact owned blobs. '+report['scope']+' Next combined controlled-preview strict retirement/window-command durable Unknown/whole-host restart, actual native uncertainty and original full-release gates; goal remains active.'],'progress',['docs/warlock-preview/v93/component-report-window-restart-198-201.json','implementation/warlock-client-provider-native-v198/component-manifest.json','docs/warlock-repository/v105/publication/delivery.json']);print(e)\n";put('record_delivery.py',text)
text=(prior/'commit_receipt.py').read_text().replace(oldbase,base).replace('Record public shared renderer native drain repair','Record public durable window restart qualification')
text,n=re.subn(r"d\['ownedFiles'\]>=\d+","d['ownedFiles']>="+str(minimum),text);assert n==1;put('commit_receipt.py',text)
text=(repo/'docs/warlock-preview/v93/commit_gui143_shared_process_drain.py').read_text().replace('0549a14782f04c155beda4191068dbaf1910730c',local).replace('Drain native custody before shared renderer recovery',title).replace('Commit exact held GUI119 ordered visual custody and owned publication preparation.','Commit exact held main-window restart proof and owned publication preparation.')
a=text.index('for name,passed in ');b=text.index(':\n root=',a);text=text[:a]+'for name,passed in '+repr(components)+text[b:]
a=text.index('for base in [');b=text.index(':\n for p in',a);text=text[:a]+"for base in [r/'docs/warlock-preview/v93',r/'docs/warlock-repository/v105/publication']"+text[b:]
p=repo/'docs/warlock-preview/v93/commit_window_restart_198_201.py';assert not p.exists();ast.parse(text);p.write_text(text)
print(json.dumps({'publication':str(out),'minimumOwnedFiles':minimum,'qualification':held['scope']}))
