"""Prepare the unchanged native freeze checks for the current entry registry."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
text=(repo/'docs/warlock-preview/v84/freeze_native122.py').read_text()
text=text.replace('native122','native123').replace('warlock-client-provider-native-v122','warlock-client-provider-native-v123').replace('warlock-preview-provider-v84','warlock-preview-provider-v85').replace('docs/warlock-preview/v84/','docs/warlock-preview/v85/')
marker='files={}\n';assert text.count(marker)==1
extra="prior122=json.loads(pathlib.Path(preflight['retainedNative122Report']).read_text());comparison122=audit.compare(prior122,proof,stable)\nassert any(row['name']=='allPriorNative122FixedOrderedAndActualRetryAssertionsRetained' and row['passed'] and row['evidence']==comparison122 for row in proof['checks'])\n"
text=text.replace(marker,extra+marker)
text=text.replace("'prior121FixedOrderedControls':comparison121['fixedOrderedControls']", "'prior121FixedOrderedControls':comparison121['fixedOrderedControls'],'prior122FixedOrderedControls':comparison122['fixedOrderedControls'],'boundedCSerialRegistryQualified':True")
start=text.index(" 'next':");end=text.index("}\n(repo/",start)
text=text[:start]+" 'next':'Commit/publish exact held GUI85/native123 serial-registry source/evidence and PUBLIC60 receipt70c6f9. Implement one validated physical/journal/receiver/Coordinator/Broker/intent/C membership retirement transaction with exact Elm settlement and queued-control barriers; retire only native permanent Retired subjects, retain live neighbor floors and compact nonreused serial frontier. Qualify actual more-than256 windows and original replay/ownership/exhaustion cases; ordinary capture and all original release gates remain.'"+text[end:]
start=text.index(" ['PROGRESS native123");end=text.index(",\n 'progress'",start)
text=text[:start]+" ['PROGRESS native123 same core16/plugin18/currentGUI85 PASS '+str(len(proof['checks']))+'/'+str(len(proof['ownedExitCodes']))+'normalclean; bounded explicit C subject membership and monotonic nonreused serials qualify on current full Elm/native host, original122 fixed ordered runtime gates and real allocator trials unchanged. Current full95/original regressions/decoder13/25/439states/3mutants/C96 and real own typed C/socket Active/Retired/liveNeighbor/terminal ACKs pass. PUBLIC60 03582f63 exact8175 ownerblobs, receipt70c6f9 local. Next atomic multi-owner/Elm settlement retirement and actual turnover beyond256; ordinary capture and all original GUI release gates remain, main desktop/drafts preserved; no fullrelease claim.']"+text[end:]
ast.parse(text);target=pathlib.Path(__file__).parent/'freeze_native123.py';assert not target.exists();target.write_text(text);print(target)
