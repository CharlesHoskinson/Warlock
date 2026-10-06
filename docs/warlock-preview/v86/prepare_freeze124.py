"""Prepare current serial-registry native freeze, retaining the lock fixture race."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
text=(repo/'docs/warlock-preview/v85/freeze_native123.py').read_text().replace('native123','native124').replace('warlock-client-provider-native-v123','warlock-client-provider-native-v124').replace('docs/warlock-preview/v85/','docs/warlock-preview/v86/')
marker='files={}\n';assert text.count(marker)==1
extra="lockRace=pathlib.Path(preflight['lockControlRaceReport']);race=json.loads(lockRace.read_text());assert race['passed'] and race['evidence'][0]['reproducedOriginalUnlinkedReaderRefusal'] and race['evidence'][1]['stableIdentityPublisherAccepted']\nfor name,value in race['inputs'].items():assert sha(pathlib.Path(name))==value,name\nfor name,value in race['artifacts'].items():assert sha(lockRace.parent/name)==value,name\nfailed123=pathlib.Path(preflight['retainedFailedLockControlRace']);failure=json.loads(failed123.read_text());assert not failure['passed'] and failure['cleanupPassed'] and [row['name'] for row in failure['checks'] if not row['passed']]==['guiSessionLockFixtureNormalExitAfterUnlock']\nassert [(row['name'],row['exitCode']) for row in failure['ownedExitCodes'] if row['exitCode']!=0]==[('gui-lock',1)]\n"
text=text.replace(marker,extra+marker)
text=text.replace("'boundedCSerialRegistryQualified':True", "'boundedCSerialRegistryQualified':True,'lockControlRaceReport':str(lockRace),'retainedFailedNative123Report':str(failed123)")
text=text.replace('Commit/publish exact held GUI85/native124 serial-registry source/evidence and PUBLIC60 receipt70c6f9.', 'Commit/publish exact held GUI85/failednative123/passednative124 serial-registry source/evidence, deterministic unchanged C lock guard race proof and PUBLIC60 receipt70c6f9.')
text=text.replace('bounded explicit C subject membership and monotonic nonreused serials qualify on current full Elm/native host,', 'bounded explicit C subject membership and monotonic nonreused serials qualify on current full Elm/native host; failed123 lock guard race preserved, parent same-inode publisher passes unchanged strict helper and original deadlines,')
ast.parse(text);target=pathlib.Path(__file__).parent/'freeze_native124.py';assert not target.exists();target.write_text(text);print(target)
