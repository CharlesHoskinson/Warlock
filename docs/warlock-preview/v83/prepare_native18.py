"""Derive plugin18: factual permanent incarnation retirement, no actor erasure."""
import ast, hashlib, json, pathlib, resource, shutil, sys
sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
repo = pathlib.Path('/home/hoskinson/omarchy-windows-parity')
parent = repo / 'implementation/warlock-family-style-crop-capture-v17'
target = repo / 'implementation/warlock-family-style-crop-capture-v18'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
manifest = parent / 'component-manifest.json'
held = json.loads(manifest.read_text())
assert held['sourceHeld'] and held['evidenceIntegrityPassed'] and not target.exists()
for name, row in held['files'].items():
    if row['kind'] == 'file':
        assert sha(parent / name) == row['sha256'], name
def ignore(path, names):
    return [name for name in names if name in {'component-manifest.json', 'native-build-report.json', 'ANCESTRY.json', '__pycache__'} or (pathlib.Path(path) == parent / 'qa' and name.startswith('build-'))]
shutil.copytree(parent, target, ignore=ignore)
header = target / 'native/incarnation-retirement.hpp'
shutil.copy2(repo / 'docs/warlock-preview/v83/incarnation-retirement.hpp', header)
path = target / 'native/authority.cpp'
text = path.read_text()
text = '#include "incarnation-retirement.hpp"\n' + text
marker = 'uint64_t retirementSequence=0;'
assert text.count(marker) == 1
text = text.replace(marker, marker + '\nuint64_t incarnationRetirementSequence=0;')
marker = 'grantRegistry=std::make_unique<Elm::GrantRetirement::Registry>(lifetime);retirementSequence=0;'
assert text.count(marker) == 1
text = text.replace(marker, marker + 'incarnationRetirementSequence=0;')
marker = '        } else if ((operation=="binding-retire-request" || operation=="binding-retirement-state-request")'
assert text.count(marker) == 1
text = text.replace(marker, (repo / 'docs/warlock-preview/v83/incarnation-retirement.inc').read_text() + marker)
path.write_text(text)
spec = target / 'SPEC.md'
spec.write_text(spec.read_text() + '''

## Permanent native incarnation retirement observation

Add an authenticated preview-incarnation-retirement-state-request with exact
caller binding, positive requestId and subjectIncarnation. Validate the original
PID/start grant; return protocol1 state Active/Retired/Future, same binding/request/
subject, native clock/now, independent monotonic sequence and issuance frontier.
Owned members remain Active even when minimized, suspended or unmapped. A positive
absent incarnation at or below the lifetime frontier is permanently Retired:
native birth never reuses ids and refuses overflow. Future is never Retired.

This only observes native membership. It does not retire independent capture
exports, mappings, readers, backend locks, Broker proofs or actor history, enable
ordinary capture, change Elm policy, or qualify full/native release acceptance.
Preserve every existing owning ABI/core source, capture route and original oracle.
''')
upstream_path = target / 'upstream.json'
upstream = json.loads(upstream_path.read_text())
previous_sources = dict(upstream['sourceFiles'])
upstream.update(parent=str(parent), parentDescriptorSHA256=sha(parent / 'native-build-report.json'),
    parentSourceFiles={name: sha(parent / name) for name in previous_sources},
    sourceFiles={name: sha(target / name) for name in [*previous_sources, 'native/incarnation-retirement.hpp']},
    change='Add authenticated factual native permanent incarnation retirement observation from current owner membership and monotonic issued frontier. Existing generated backdrop/render/capture/FD semantics unchanged; no actor removal or ordinary eligibility acceptance.')
upstream_path.write_text(json.dumps(upstream, indent=2) + '\n')
ast.parse((target / 'qa/build.py').read_text())
(target / 'ANCESTRY.json').write_text(json.dumps({'owner': 'f6779148-8f5d-4bdf-8a0f-044184e486f2',
    'parent': str(parent), 'parentManifestSHA256': sha(manifest),
    'requirements': 'openspec/changes/warlock-preview-actor-retirement',
    'purpose': 'First actor-turnover prerequisite: authenticated native permanent incarnation retirement observation only. Owning core16 source unchanged; no erasure of independent backend/physical/journal obligations. Current provider81/native118 qualification remains separate.',
    'nativeAcceptance': False, 'fullReleaseAccepted': False}, indent=2) + '\n')
sys.path.insert(0, str(repo / 'implementation/elm-build-loop-v1'))
import loop
print(loop.write_checkpoint(repo, 'f6779148-8f5d-4bdf-8a0f-044184e486f2', str(target.relative_to(repo)),
    ['PROGRESS native118/GUI81 held2467/284normal/all2429stable116 thirdlease resume/image/ACK/drain; publication58 underway. Fresh native18 owned: authenticated permanent incarnation retirement state from native membership/issued frontier, no physical/history erasure or eligibility change. Next compile actual module, selected coupled state/decoder checks, full owning-ABI native qualification. Then integrate bounded atomic actor turnover; original full release gates active.'],
    'progress', [str((target / 'ANCESTRY.json').relative_to(repo))]))
