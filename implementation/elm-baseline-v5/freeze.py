"""Read original collectors as data; never import or execute native campaigns."""
import ast
import hashlib
import json
import resource
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT = HERE / 'ledger.json'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return (ROOT / path).read_bytes()


def text_expr(node, bindings):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        return bindings[node.id]
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return text_expr(node.left, bindings) + text_expr(node.right, bindings)
    raise ValueError(ast.dump(node))


def collector(filename, route):
    path = 'window-integration-qa/family-preparation-thumbnail-v14/' + filename
    source = read(path).decode()
    tree = ast.parse(source)
    calls = sorted((n for n in ast.walk(tree) if isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Name) and n.func.id == 'check'),
                   key=lambda n: n.lineno)
    cases = []
    counts = Counter()
    for call in calls:
        line = call.lineno
        if filename == 'native_integration.py':
            bindings = {376: [{'operation': x} for x in ('minimize', 'restore')],
                        401: [{'operation': x} for x in ('minimize', 'restore', 'minimize', 'restore')],
                        522: [{'operation': x} for x in ('minimize', 'restore')],
                        525: [{'operation': x} for x in ('minimize', 'restore')],
                        625: [{'name': x} for x in ('owner', 'child', 'nested')]}.get(line, [{}])
        else:
            if route == 'closed-peer' and line in (447, 448):
                continue
            if route == 'compatible' and line in (442, 444, 445):
                continue
            bindings = {140: [{'operation': 'minimize'}],
                        165: [{'operation': 'restore'}],
                        299: [{'name': x} for x in ('owner', 'child', 'nested')]}.get(line, [{}])
        for binding in bindings:
            name = text_expr(call.args[0], binding)
            counts[name] += 1
            cases.append({'originalName': name, 'nameOccurrence': counts[name],
                          'sourcePath': path, 'sourceLine': line, 'bindings': binding,
                          'originalAssertionSource': ast.get_source_segment(source, call),
                          'originalAssertionAST': ast.dump(call, include_attributes=False),
                          'elmNativeAcceptance': 'pending'})
    expected = 38 if filename == 'native_integration.py' else (34 if route == 'closed-peer' else 33)
    assert len(cases) == expected
    return {'route': route, 'sourcePath': path, 'sourceSHA256': digest(read(path)),
            'staticCheckSites': len(calls), 'expandedChecks': len(cases), 'cases': cases,
            'timingSource': [{'line': n.lineno, 'source': ast.get_source_segment(source, n)}
                for n in ast.walk(tree) if isinstance(n, ast.Call) and
                ((isinstance(n.func, ast.Name) and n.func.id in ('wait', 'monotonic', 'sleep'))
                 or any(k.arg == 'timeout' for k in n.keywords))]}


def build():
    roots = ['window-integration-qa/family-preparation-thumbnail-v14',
             'window-integration-qa/toolkit-held-matrix-v9',
             'window-behavior-spec/pin-maximized-native-policy-v1-design']
    inventory = {}
    for folder in roots:
        for path in sorted((ROOT / folder).rglob('*')):
            if path.is_file() and not path.is_symlink():
                inventory[str(path.relative_to(ROOT))] = digest(path.read_bytes())
    matrix = json.loads(read(roots[1] + '/matrix.json'))
    held = [{'originalVariant': variant, 'originalCase': case, 'elmNativeAcceptance': 'pending'}
            for variant in matrix['variants'] for case in matrix['casesPerVariant']]
    assert len(held) == matrix['totalVariantCases'] == 52
    pin = json.loads(read(roots[2] + '/cases.json'))
    assert [c['id'] for c in pin] == [f'B{i:02d}' for i in range(1, 25)]
    return {'schemaVersion': 1, 'scope': 'S01 inherited campaign discovery; not native acceptance',
            'requirementsSHA256': digest(read('docs/elm-roadmap/requirements.json')),
            'sourceInventory': inventory,
            'restore': collector('native_integration.py', 'baseline'),
            'faultClosedPeer': collector('native_faults.py', 'closed-peer'),
            'faultCompatible': collector('native_faults.py', 'compatible'),
            'held': held, 'pinOriginalCases': pin,
            'ordering': 'Collector source order; repeated names retain occurrence. Not a runtime trace.',
            'blockingMissingEvidence': [
                'Elm-native campaign adapters with exact owning core/plugin pairing are not implemented.',
                'Restore original two-second completion deadline requires its service-side timing origin and derivative binding; harness wait bounds do not replace it.',
                'Fault acceptance requires a fresh accepted 38-check restore baseline; inherited baseline failed.',
                '34 fault checks describes closed-peer route; compatible route has 33. Route counts do not alter original assertions.',
                'Held X11 routes require explicitly enabled, validated private Xwayland; Wayland cannot substitute.',
                'Pin B13–B24 have original definitions but lack complete native collectors.',
                'Popup/process, MAX renderer and remaining inherited campaigns still require full ledger discovery.',
                'Owner/verifier, product integration inventory and performance budgets remain open S01/S02 gates.'
            ]}


def main():
    assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1), 'Use protected qa_run.py'
    ledger = build()
    encoded = (json.dumps(ledger, indent=2, sort_keys=True) + '\n').encode()
    if sys.argv[1:] == ['--freeze']:
        assert not OUT.exists(), 'Frozen ledger exists; use a fresh derivative'
        OUT.write_bytes(encoded)
    else:
        assert not sys.argv[1:]
        assert OUT.read_bytes() == encoded, 'Original sources, identities, timing or frozen ledger changed'
    print(json.dumps({'passed': True, 'restore': 38, 'faultClosedPeer': 34,
                      'faultCompatible': 33, 'held': 52, 'pin': 24,
                      'sourceFiles': len(ledger['sourceInventory']),
                      'nativeAcceptance': False, 'ledgerSHA256': digest(encoded)}))


if __name__ == '__main__':
    main()
