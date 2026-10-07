"""Preserve failed nominal count audit and account for original optional readonly polls."""
import ast,hashlib,json,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');base=repo/'docs/warlock-preview/v93';root=repo/'implementation/warlock-client-provider-native-v131';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=base/'freeze_native131.py';source=old.read_text();report=next(root.glob('qa/native-*/report.json'));d=json.loads(report.read_text());assert d['passed'] and d['cleanupPassed'] and d['priorNative130Retention']['passed'] and d['priorNative130Retention']['fixedOrderedControls']==2510
readonly={'styleDimPendingNativeReadonlyScope','styleAgainDimPendingNativeReadonlyScope','styleRestoreIntermediateReadonlyScope','styleCropDimIntermediateReadonlyScope'};polls=[row for row in d['checks'] if row['name'] in readonly];assert len(polls)==5 and all(row['passed'] for row in polls) and {row['name'] for row in polls}==readonly
failure=base/'native131-freeze-count-failure.json';assert not failure.exists();failure.write_text(json.dumps({'schema':1,'passed':False,'nativeCampaignPassed':True,'freezer':str(old),'freezerSHA256':sha(old),'nativeReport':str(report),'nativeReportSHA256':sha(report),'failedAssertion':'Nominal raw check total2519 assumed six optional readonly polls from native130; current original campaign has five, while every fixed control and actual allocator/deadline/normal-exit assertion passes.','originalFixedControlsRetained':2510,'newFixedRetentionControl':1,'actualAttemptControls':2,'actualOptionalReadonlyPolls':5,'rawChecks':2518,'nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
needle="assert len(proof['checks'])==2519+comparison126['current']['actualAttemptChecks']-2 and len(proof['ownedExitCodes'])==278+comparison126['current']['attempts']-1";assert source.count(needle)==1
source=source.replace(needle,"""# Original optional read-only polling can repeat while awaiting the same fixed
# transition. Audit actual polling rows rather than inventing a raw nominal count.
polls=[row for row in proof['checks'] if row['name'] in readonly]
assert {row['name'] for row in polls}==readonly and all(row['passed'] for row in polls)
assert len(proof['checks'])==2511+comparison126['current']['actualAttemptChecks']+len(polls)
assert len(proof['ownedExitCodes'])==278+comparison126['current']['attempts']-1""")
ast.parse(source);target=base/'freeze_native131_v2.py';assert not target.exists();target.write_text(source);print(target)
