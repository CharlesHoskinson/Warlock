"""Prepare publication58 over verified public57; no unrelated worker paths."""
import ast, json, pathlib, resource, sys
sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
repo = pathlib.Path('/home/hoskinson/omarchy-windows-parity')
report = json.loads((repo / 'docs/warlock-preview/v82/report.json').read_text())
assert report['passed'] and report['sameHostThirdLeaseResumeImageACKQualified']
out = repo / 'docs/warlock-repository/v58/publication'
assert not out.exists()
out.mkdir(parents=True)
text = (repo / 'docs/warlock-repository/v57/publication/publish.py').read_text()
text = text.replace("BASE='498df7d93c334137711c87de7915a7e936ba2074'", "BASE='5d78ac5941d2639b1ea84fb3d2459441dfbecadc'")
text = text.replace('d62345012d19181d05b2c1c97eabd5461413c807..', '269ec84e9c0cce199363b400127f6a1d61769985..')
allowed = ('docs/warlock-preview/v82/', 'docs/warlock-repository/v57/publication/',
    'docs/warlock-repository/v58/publication/', 'openspec/changes/warlock-preview-next-resume/',
    'openspec/changes/warlock-preview-actor-retirement/', 'implementation/warlock-preview-provider-v81/',
    'implementation/warlock-client-provider-native-v117/', 'implementation/warlock-client-provider-native-v118/')
start = text.index('allowed=(')
end = text.index('\nassert all', start)
text = text[:start] + 'allowed=' + repr(allowed) + text[end:]
start = text.index(' qualification=')
end = text.index('\n published=', start)
message = 'Resume expired waiting previews on a later picker lease\n\nAdmit a distinct later unissued resume only after native expiry and exact original physical and terminal retirement, retaining owner/incarnation/clock and request floor. Require strictly later publication and lease, keep one bounded predecessor, and preserve same-stamp cutoffs. Full95 build and all eleven original regression suites pass. New resume tests pass13 selected Quint cases,29 actual helper/Broker traces,605 state comparisons,three unsafe native mutants,22 retirement/receiver C guards and C50/optimized Elm30 wire controls. Native118 verifies a third real pointer picker lease in the same GUI host: original waiting resume expires without losing job1, fresh native2s request2 loads its owned image and settles exact ACK with zero physical/journal obligations. All2429 stable116 controls are retained;2467 native checks and284 normal exits pass. Preserve failed117 fixture evidence. Add proposed EARS/OpenSpec requirements for bounded actor retirement. Native/full release, ordinary eligible capture, actor turnover, AT/hardware and all original release gates remain open.\n'
qualification = " qualification=json.loads((REPO/'docs/warlock-preview/v82/report.json').read_text());assert qualification['passed'] and qualification['nextResumeStates']==605 and qualification['nextResumeScenarios']==13 and qualification['nativeCControls']==50 and qualification['elmWireControls']==30 and qualification['sameHostThirdLeaseResumeImageACKQualified'] and qualification['prior116StableControls']==2429 and not qualification['nativeAcceptance'] and not qualification['fullReleaseAccepted']\n message=" + repr(message) + '\n'
text = text[:start] + qualification + text[end:]
ast.parse(text)
(out / 'publish.py').write_text(text)
text = (repo / 'docs/warlock-repository/v57/publication/record_delivery.py').read_text()
text = text.replace('docs/warlock-preview/v81', 'docs/warlock-preview/v82').replace('warlock-client-provider-native-v116', 'warlock-client-provider-native-v118').replace('warlock-preview-provider-v80', 'warlock-preview-provider-v81').replace('warlock-repository/v57', 'warlock-repository/v58')
start = text.index("['PROGRESS PUBLIC exactowner publication57 ")
end = text.index(",'progress'", start)
note = "['PROGRESS PUBLIC exactowner publication58 '+d['publishedCommit']+' verified '+str(d['ownedFiles'])+' blobs. Held GUI81 full95/original11/newresume13/29/605states/3mutants/guards22/C50Elm30; native118 '+str(report['nativeChecks'])+'/'+str(report['normalOwnedExits'])+'normalclean actual samehost third picker lease/request2/fresh native2s/ownedimage/exactACK/physicaljournaldrain, all2429stable116 retained. Failed117 typed trigger projection fixture preserved. Next actual native incarnation retirement then bounded actor turnover and ordinary eligible capture; all original release gates active. Main desktop/drafts/foreignchanges preserved; no fullreleaseclaim.']"
text = text[:start] + note + text[end:]
ast.parse(text)
(out / 'record_delivery.py').write_text(text)
# Exact owned commit uses the same raw-byte verification and bounded path batches.
text = (repo / 'docs/warlock-preview/v81/commit_owned.py').read_text()
text = text.replace('735eadfd6bec2e6c9a6cdd153336f857b6f203e6', '50f5e2305d512eead83cda64b0502ef55e25f388')
text = text.replace("[('warlock-preview-provider-v80',True),('warlock-client-provider-native-v115',False),('warlock-client-provider-native-v116',True)]", "[('warlock-preview-provider-v81',True),('warlock-client-provider-native-v117',False),('warlock-client-provider-native-v118',True)]")
old = "[r/'docs/warlock-preview/v80',r/'docs/warlock-preview/v81',r/'docs/warlock-repository/v57/publication',r/'openspec/changes/warlock-preview-unissued-priority']"
new = "[r/'docs/warlock-preview/v82',r/'docs/warlock-repository/v58/publication',r/'openspec/changes/warlock-preview-next-resume',r/'openspec/changes/warlock-preview-actor-retirement']"
assert old in text
text = text.replace(old, new)
text = text.replace('Qualify later preview enrollment and unissued priority in the native GUI', 'Qualify expired waiting preview resumes across native picker leases')
text = text.replace('Commit exact held GUI80/native115/116 and owned publication preparation.', 'Commit exact held GUI81/failed117/passed118 and owned publication preparation.')
ast.parse(text)
(repo / 'docs/warlock-preview/v82/commit_owned.py').write_text(text)
print(out)
