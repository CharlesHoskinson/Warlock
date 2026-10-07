"""Prepare exact owned publication of the bounded combined recovery proof."""
import ast,json,pathlib,re,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');out=r/'docs/warlock-repository/v106/publication';assert not out.exists()
base='8c752ff31fe63308b31b6fd374e8e1f24de04062';local='5066a6494230abae859b1ffaeb93c8751fa40d27';previous='b341185be47894ef3da6363ba88b525b50d88af9';oldbase='4e5774fd8433275d2d80e189221510e479fee247'
components=[(f'warlock-client-provider-native-v{v}',v>=204) for v in range(202,208)]+[('warlock-window-restart-supervisor-v2',True),('warlock-combined-recovery-model-v1',True)]
minimum=0
for name,passed in components:
 d=json.loads((r/'implementation'/name/'component-manifest.json').read_text());assert d['sourceHeld'] and d['passed']==passed;minimum+=len(d['files'])
path='docs/warlock-preview/v93/component-report-combined-restart-204-207.json';held=json.loads((r/path).read_text())
assert held['passed'] and held['combinedControlledPreviewRestartQualified'] and held['fullBuildCommands']==119
prior=r/'docs/warlock-repository/v105/publication';out.mkdir(parents=True)
def put(name,s):ast.parse(s);(out/name).write_text(s)
s=(prior/'publish.py').read_text().replace(oldbase,base).replace('884a5d7afc7a73bc475379a81e5dd3272659b975..',previous+'..')
allowed=('docs/warlock-preview/v93/','docs/warlock-repository/v105/publication/','docs/warlock-repository/v106/publication/',*(f'implementation/{name}/' for name,_ in components),'openspec/changes/warlock-preview-actor-retirement/tasks.md','openspec/changes/warlock-preview-actor-retirement/specs/preview-actors/spec.md')
a=s.index('allowed=');b=s.index('\nassert all',a);s=s[:a]+'allowed='+repr(allowed)+s[b:]
a=s.index(' qualification=');b=s.index('\n published=',a)
qual=" qualification=json.loads((REPO/"+repr(path)+").read_text());assert qualification['passed'] and qualification['fourOperationBoundaryScenariosQualified'] and qualification['combinedControlledPreviewRestartQualified'] and qualification['originalReaderAndStrictNativeCloseBeforeGTKRecovery'] and qualification['actualWindowCommandRestartQualified'] and qualification['actualWindowCommandDurableUnknownQualified'] and qualification['historicalUnknownPreserved'] and qualification['automaticUnknownReplayCount']==0 and qualification['nativeAuthorityResets']==0 and qualification['fullBuildCommands']==119 and qualification['privateSessionCleanupPassed'] and qualification['namedModelScenarios']==14 and qualification['invariantSamples']==200 and qualification['coupledActualStages']==14 and qualification['supervisorNegativeChecks']==7 and not qualification['uncertainPreviewRetirementQualified'] and not qualification['popupDismissalFocusRestorationQualified'] and not qualification['wholeHostRestartQualified'] and not qualification['nativeAcceptance'] and not qualification['fullReleaseAccepted']\n assert [qualification['reports']['native'+str(v)]['checks'] for v in range(204,208)]==[102,101,99,104]"
title='Qualify combined preview retirement and durable window restart'
s=s[:a]+qual+'\n message='+repr(title+'\n\n'+held['scope'])+'\n'+s[b:];put('publish.py',s)
s=(prior/'record_delivery.py').read_text();a=s.index('report=json.loads(');b=s.index('\nsys.path.insert',a)
s=s[:a]+"report=json.loads((r/"+repr(path)+").read_text());assert report['passed'] and report['fourOperationBoundaryScenariosQualified'] and report['combinedControlledPreviewRestartQualified'] and not report['uncertainPreviewRetirementQualified']"+s[b:]
s,n=re.subn(r"d\['ownedFiles'\]>=\d+","d['ownedFiles']>="+str(minimum),s);assert n==1
a=s.index('e=loop.write_checkpoint(')
s=s[:a]+"e=loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2','implementation/warlock-client-provider-native-v204',['PROGRESS PUBLIC106 '+d['publishedCommit']+' verified '+str(d['ownedFiles'])+' exact owned blobs. '+report['scope']+' Next actual native preview-effect uncertainty and original-clock pressure/expiry; full GUI goal remains active.'],'progress',["+repr(path)+",'implementation/warlock-client-provider-native-v204/component-manifest.json','docs/warlock-repository/v106/publication/delivery.json']);print(e)\n";put('record_delivery.py',s)
s=(prior/'commit_receipt.py').read_text().replace(oldbase,base).replace('Record public durable window restart qualification','Record public combined recovery qualification')
s,n=re.subn(r"d\['ownedFiles'\]>=\d+","d['ownedFiles']>="+str(minimum),s);assert n==1;put('commit_receipt.py',s)
s=(r/'docs/warlock-preview/v93/commit_window_restart_198_201.py').read_text().replace('26ae1e8eda0e9c6ceef47457e7479589478fbd1c',local).replace('Qualify durable window commands across native restart',title).replace('Commit exact held main-window restart proof and owned publication preparation.','Commit exact held combined recovery proof and owned publication preparation.')
a=s.index('for name,passed in ');b=s.index(':\n root=',a);s=s[:a]+'for name,passed in '+repr(components)+s[b:]
s=s.replace("r/'docs/warlock-repository/v105/publication'","r/'docs/warlock-repository/v106/publication'")
p=r/'docs/warlock-preview/v93/commit_combined_restart_204_207.py';assert not p.exists();ast.parse(s);p.write_text(s)
print(json.dumps({'publication':str(out),'minimumOwnedFiles':minimum,'scope':held['scope']}))
