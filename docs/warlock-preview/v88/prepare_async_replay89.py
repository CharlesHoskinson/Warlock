"""Current compiled asynchronous sibling-retirement replay and preserved ancestor failure."""
import json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=r/'implementation/warlock-preview-provider-v89'
s=(root/'qa/elm-retirement-check.py').read_text().replace('elm-retirement-check-','retirement-async-check-').replace('elm-retirement-replay.js','retirement-async-replay.js').replace('Actual optimized immutable Elm retirement ownership/readiness/anti-replay','Actual optimized immutable Elm independently delivered sibling retirement')
(root/'qa/retirement-async-check.py').write_text(s)
old=next(root.glob('qa/retirement-async-ancestor88-*/report.json'));d=json.loads(old.read_text());assert not d['passed'] and 'Exact delayed completion' in d['error']
target=r/'docs/warlock-preview/v88'/old.parent.name;assert not target.exists();shutil.copytree(old.parent,target)
