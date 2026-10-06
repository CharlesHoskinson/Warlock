"""Extend the verified native observation freeze to actual current C/socket facts."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
text=(repo/'docs/warlock-preview/v83/freeze_native121.py').read_text()
text=text.replace('native121','native122').replace('warlock-client-provider-native-v121','warlock-client-provider-native-v122').replace('warlock-preview-provider-v81','warlock-preview-provider-v84').replace('docs/warlock-preview/v83/','docs/warlock-preview/v84/')
marker='files={}\n';assert text.count(marker)==1
extra='''typed=proof['typedNativeRetirementEvidence'];assert proof['typedNativeRetirementObservationBoundedQualified'] and typed['normalExit'] and typed['complete']['passed'] and not typed['complete']['actorTurnoverAccepted']
facts=typed['observations'];assert [row['state'] for row in facts]==['Active','Active','Retired','Active']
assert facts[0]['subject']==facts[2]['subject'] and facts[1]['subject']==facts[3]['subject'] and facts[0]['subject']!=facts[1]['subject']
assert all(row['kind']=='native-incarnation-retirement' and row['binding']==facts[0]['binding'] and row['clock']==facts[0]['binding']['lifetime'] for row in facts)
assert all(int(b['sequence'])>int(a['sequence']) and int(b['now'])>=int(a['now']) and int(b['issuedThrough'])>=int(a['issuedThrough']) for a,b in zip(facts,facts[1:]))
assert all(int(row['subject'])<=int(row['issuedThrough']) for row in facts)
prior121=json.loads(pathlib.Path(preflight['retainedNative121Report']).read_text());comparison121=audit.compare(prior121,proof,stable)
assert any(row['name']=='allPriorNative121FixedOrderedAndActualRetryAssertionsRetained' and row['passed'] and row['evidence']==comparison121 for row in proof['checks'])
for field in ['retirementDecoderReport','retirementCReport']:
 current=pathlib.Path(gui[field]);checked=json.loads(current.read_text());assert checked['passed']
 for rel,value in checked['inputs'].items():assert sha(provider.parent/rel)==value,rel
 for rel,value in checked['artifacts'].items():assert sha(current.parent/rel)==value,rel
'''
text=text.replace(marker,extra+marker)
text=text.replace("'nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)","'typedNativeRetirementObservationBoundedQualified':True,'prior121FixedOrderedControls':comparison121['fixedOrderedControls'],'typedNativeRetirementEvidence':typed,'nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)")
text=text.replace("'nativeIncarnationRetirementObservationBoundedQualified':True,'actorTurnoverAccepted':False", "'nativeIncarnationRetirementObservationBoundedQualified':True,'typedNativeRetirementObservationBoundedQualified':True,'typedNativeRetirementEvidence':typed,'prior121FixedOrderedControls':comparison121['fixedOrderedControls'],'typedDecoderScenarios':13,'typedDecoderTraces':25,'typedDecoderStates':439,'unsafeDecoderMutants':3,'retirementCChecks':96,'actorTurnoverAccepted':False")
start=text.index(" 'next':");end=text.index("}\n(repo/",start)
text=text[:start]+" 'next':'Commit/publish exact held failedGUI83/passedGUI84/native122 evidence. Fresh GUI85 replaces vector index identities with bounded active membership and nonreused monotonic entry serials, full build66449 running. Integrate atomic proof-safe physical/journal/receiver/Coordinator/Broker/ledger/C retirement and exact Elm settlement facts, then actual more-than256 window turnover; ordinary capture and all original release gates remain.'"+text[end:]
start=text.index(" ['PROGRESS native122");end=text.index(",\n 'progress'",start)
text=text[:start]+" ['PROGRESS native122 exact core16/plugin18/currentGUI84 PASS '+str(len(proof['checks']))+'/'+str(len(proof['ownedExitCodes']))+'normalclean. Real owning C/bootstrap/socket/ImportedClients typed Active/Retired/liveNeighbor observations, native clocks/cursors/frontier and original untouched reservations/exact final journal ACKs; all original121 fixed gates and actual allocator trials verified. Current GUI84 full95/all original suites/decoder13/25/439states/3mutants/C96 pass; failed83 held. PUBLIC59 ba21f432 source83e294 and receipt70d888. Fresh GUI85 serial registry/fullcompile66449, then atomic actor/history retirement beyond256 and all original release gates; main desktop/drafts preserved, no full release claim.']"+text[end:]
ast.parse(text);target=pathlib.Path(__file__).parent/'freeze_native122.py';assert not target.exists();target.write_text(text);print(target)
