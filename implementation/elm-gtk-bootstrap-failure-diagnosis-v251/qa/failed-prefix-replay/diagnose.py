import hashlib, json, re, resource, sys, time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
r = Path(__file__).resolve().parents[1]
owner = r.parent / 'elm-gtk-role-native-v238'
failed = owner / 'qa/native-1791141503469881852'
sys.path.insert(0, str(owner / 'qa'))
from protocol import Trace, CALL
raw_path = failed / 'native-evidence/gtk-role-client/wayland.log'
raw = raw_path.read_bytes()
parsed = Trace(raw)
assert len(parsed.calls) == 0
prefix = re.compile(r'^\[(\d{2}):(\d{2}):(\d{2})\.(\d{6})\] \{[^{}\r\n]{1,128}\} ')
lines, changed = [], 0
for line in raw.decode().splitlines(True):
    m = prefix.match(line)
    if m:
        line = '[0.000] ' + line[m.end():]
        changed += 1
    lines.append(line)
diagnostic = ''.join(lines).encode()
replayed = Trace(diagnostic)
assert len(replayed.calls) > 0
roles = {}
for role, surface in [('A', 42), ('C', 71)]:
    roles[role] = replayed.role(role=role, pid=3188779, surface_id=surface)
    assert roles[role]['ack']['index'] > roles[role]['configure']['index']
    assert roles[role]['lastCommitIndex'] > roles[role]['ack']['index']
report = json.loads((failed / 'report.json').read_text())
unexpected = report['cleanup']['unexpectedInnerDescendants']
bus = report['cleanup']['privateBus']
assert len(unexpected) == 10 and all(row['pgid'] == bus['pgid'] for row in unexpected)
bus_log = failed / 'native-evidence/privateBus.log'
log = bus_log.read_text()
assert "pid=3188779" in log and "org.freedesktop.portal.Desktop" in log
out = r / 'qa' / ('diagnose-' + str(time.time_ns()))
out.mkdir()
(out / 'diagnostic-prefix-normalized.log').write_bytes(diagnostic)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
result = {'passed': True, 'nativeAcceptance': False, 'scope': 'Immutable actual failure replay; prefix normalization only for diagnosis, no production parser adoption', 'rawCallsMatched': len(parsed.calls), 'normalizedCallsMatched': len(replayed.calls), 'prefixesNormalized': changed, 'roles': roles, 'unexpectedDescendants': unexpected, 'privateBus': bus, 'evidenceSources': {str(p): {'sha256': sha(p), 'size': p.stat().st_size} for p in [raw_path, bus_log, failed / 'report.json', owner / 'qa/protocol.py']}, 'limits': ['No pixels/input/modal campaign passed', 'Activation log identifies some services; full ten-process identities absent from preserved census', 'No main desktop access inferred or excluded solely by this parser diagnosis']}
(out / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
print(str(out / 'report.json'))
