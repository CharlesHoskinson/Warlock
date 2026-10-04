"""Hold reviewed types-only proposal; does not approve or qualify model logic."""
import hashlib
import json
import re
import resource
from pathlib import Path

assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
root = Path(__file__).resolve().parents[1]
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
source = root / 'spec/constraints-sketch.qnt'
expected = '6fdc0a0c95dd10d2a33172e409a3c0fd440598b825288bf037249720035b7d51'
assert sha(source) == expected
assert not re.search(r'^\s*(?:action|def|pure\s+def|val|run)\s', source.read_text(), re.MULTILINE)
directory = root / 'qa/typecheck-1791123837485517527'
report = json.loads((directory / 'report.json').read_text())
assert report['passed'] is True and report['sourceSHA256'] == expected
assert sha(directory / 'constraints-sketch.qnt') == expected
files = []
for p in sorted(root.rglob('*')):
    assert not p.is_symlink(), p
    if p.is_file():
        files.append(dict(path=str(p), size=p.stat().st_size, sha256=sha(p)))
destination = root / 'proposal-hold.json'
assert not destination.exists()
destination.write_text(json.dumps(dict(scope='Reviewed types-only proposal; explicit approval pending, no logic/model/native/release acceptance', sketchSHA256=expected, logicApproved=False, modelAcceptance=False, nativeAcceptance=False, files=files), indent=2) + '\n')
print(json.dumps(dict(held=True, files=len(files), manifestSHA256=sha(destination))))
