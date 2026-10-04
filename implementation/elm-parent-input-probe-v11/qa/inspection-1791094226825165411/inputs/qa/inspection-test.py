"""External CPU oracles for actual fixture receipt inspection; no GUI evidence."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import shutil
import time

assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1), 'Use protected qa_run.py'
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'qa' / ('inspection-' + str(time.time_ns()))
OUT.mkdir()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


inputs = [Path(__file__).resolve(), ROOT / 'qa/fixture-inspection.py', ROOT / 'fixture.py']
hashes = {str(p.relative_to(ROOT)): sha(p) for p in inputs}
for path in inputs:
    dest = OUT / 'inputs' / path.relative_to(ROOT)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dest)
    dest.chmod(0o444)
spec = importlib.util.spec_from_file_location('actual_inspector', OUT / 'inputs/qa/fixture-inspection.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
checks = []


def check(name, run):
    try:
        run()
        checks.append({'name': name, 'passed': True})
    except Exception as error:
        checks.append({'name': name, 'passed': False, 'error': repr(error)})


def expect_equal(actual, expected):
    assert actual == expected, (actual, expected)


def rejected(run):
    try:
        value = run()
    except (ValueError, KeyError, TypeError):
        return
    assert value == [], ('Unexpected admitted malformed receipt', value)


# Deliberately independent identities: EventBox's above-child input GDK window
# (900) differs from its drawing window (400); typed ownership is independently
# witnessed by the fixture. Raw gpointer diagnostics are not authority.
# These are labeled synthetic CPU inputs, never native delivery observations.
base = {'schema': 1, 'sequence': 1, 'pid': 1234, 'title': 'ELM-PARENT-INPUT-PROBE',
        'fixtureWindowId': 'ordinary-1', 'eventRecipient': 'parent-input-recipient',
        'kind': 'button-press', 'counts': {'enter': 1, 'motion': 1, 'button-press': 1, 'button-release': 0},
        'geometry': {'mapped': True, 'realized': True, 'scaleFactor': 1,
                     'recipientAllocation': {'x': 0, 'y': 0, 'width': 240, 'height': 160},
                     'windowAllocation': {'width': 240, 'height': 160},
                     'gdkWindowReference': '400', 'displayType': 'GdkWaylandDisplay'},
        'signalRecipient': 'parent-input-recipient', 'gdkEventWidget': 'parent-input-recipient',
        'eventWidgetIsRecipient': True, 'signalWidgetIsRecipient': True,
        'eventWindowIsOwned': True, 'eventWindowOwnerReference': '500',
        'recipientNativeReference': '500', 'eventWindowOwnerIsRecipient': True,
        'eventWindowReference': '900', 'x': 20.0, 'y': 30.0, 'button': 1, 'sendEvent': False}
client = {'pid': 1234, 'title': 'ELM-PARENT-INPUT-PROBE', 'address': '0xabc',
          'at': [100, 80], 'size': [240, 160]}


def observation(records=None):
    return {'records': copy.deepcopy(records if records is not None else [base])}


def deliveries(record):
    return module.delivered_since(observation([record]), 0, 'button-press', [20, 30], 2, 1)


check('DistinctInputAndDrawingWindowWithExactWidgetOwnerAccepted',
      lambda: expect_equal(deliveries(base), [base]))
for field, value, name in (
    ('eventWidgetIsRecipient', False, 'SameWidgetNameCannotSpoofActualWidgetIdentity'),
    ('signalWidgetIsRecipient', False, 'SameSignalNameCannotSpoofActualSignalWidget'),
    ('eventWindowIsOwned', False, 'MatchingRawPointerCannotOverrideWrongTypedWindowOwner'),
    ('eventWidgetIsRecipient', None, 'MissingTypedActualWidgetRejected'),
    ('signalWidgetIsRecipient', None, 'MissingTypedSignalWidgetRejected'),
    ('eventWindowIsOwned', None, 'MissingTypedWindowOwnershipRejected'),
    ('eventWindowIsOwned', 1, 'IntegerCannotStandInForWindowOwnershipBoolean'),
    ('eventWidgetIsRecipient', 1, 'IntegerCannotStandInForWidgetIdentityBoolean'),
    ('signalRecipient', 'unrelated-widget', 'DifferentSignalRecipientRejected'),
    ('gdkEventWidget', 'unrelated-widget', 'DifferentEventWidgetRejected'),
    ('eventWindowReference', None, 'MissingActualGdkEventWindowRejected'),
):
    record = copy.deepcopy(base)
    record[field] = value
    check(name, lambda record=record: rejected(lambda: deliveries(record)))
for value, name in ((40.0, 'WrongCoordinateCannotCountAsExpectedReceipt'),
                    (float('nan'), 'NonfiniteCoordinateCannotCountAsExpectedReceipt'),
                    (float('inf'), 'InfiniteCoordinateCannotCountAsExpectedReceipt')):
    record = copy.deepcopy(base)
    record['x'] = value
    check(name, lambda record=record: rejected(lambda: deliveries(record)))
diagnostic = copy.deepcopy(base)
diagnostic['eventWindowOwnerReference'] = '501'
diagnostic['eventWindowOwnerIsRecipient'] = False
check('RawGpointerDiagnosticsDoNotOverrideTypedOwnershipWitness',
      lambda: expect_equal(deliveries(diagnostic), [diagnostic]))
record = copy.deepcopy(base)
record['button'] = 3
check('DifferentButtonDoesNotCountAsExpectedPress', lambda: expect_equal(deliveries(record), []))
check('OldSequenceCannotCountAsNewDelivery', lambda: expect_equal(
    module.delivered_since(observation(), 1, 'button-press', [20, 30], button=1), []))
second = copy.deepcopy(base)
second['sequence'] = 2
check('DuplicateDeliveredPressesRemainVisibleForRunnerCountOracle', lambda: expect_equal(
    len(module.delivered_since(observation([base, second]), 0, 'button-press', [20, 30], button=1)), 2))

path = OUT / 'external-receipts.jsonl'
path.write_text(json.dumps(base) + '\n')
check('NativePidTitleAddressAndActualAllocationJoin', lambda: expect_equal(
    module.inspect(path, [client])['address'], '0xabc'))
check('UnrelatedNativePidDoesNotJoin', lambda: expect_equal(
    module.inspect(path, [{**client, 'pid': 2345}]), None))
check('StaleNativeSizeDoesNotJoin', lambda: expect_equal(
    module.inspect(path, [{**client, 'size': [320, 240]}]), None))
check('AmbiguousNativeWindowJoinRejected', lambda: rejected(
    lambda: module.inspect(path, [client, {**client, 'address': '0xdef'}])))
partial = OUT / 'partial-receipts.jsonl'
partial.write_text(json.dumps(base) + '\n' + '{"sequence":2')
check('IncompleteFinalWriteWaitsForNextObservation', lambda: expect_equal(module.receipts(partial), [base]))

observed = {'at': [100, 80], 'size': [240, 160]}
for monitor, expected, name in (
    ({'width': 800, 'height': 600, 'scale': 1, 'x': 0, 'y': 0}, [120.0, 110.0], 'IdentityModeParentCoordinates'),
    ({'width': 640, 'height': 480, 'scale': 1, 'x': 0, 'y': 0}, [150.0, 137.5], 'ShrunkChildParentCoordinates'),
    ({'width': 960, 'height': 640, 'scale': 2, 'x': 0, 'y': 0}, [200.0, 206.25], 'ScaledChildUsesLogicalExtent'),
):
    check(name, lambda monitor=monitor, expected=expected: expect_equal(
        module.parent_point(observed, [20, 30], monitor, [800, 600]), expected))
check('OffsetMonitorOriginExcludedFromLocalParentCoordinates', lambda: expect_equal(
    module.parent_point({'at': [300, -20], 'size': [240, 160]}, [20, 30],
                        {'width': 960, 'height': 640, 'scale': 2, 'x': 200, 'y': -100}, [800, 600]), [200.0, 206.25]))
check('RotationRejectedInsteadOfInventedMapping', lambda: rejected(lambda: module.parent_point(
    observed, [20, 30], {'width': 960, 'height': 640, 'scale': 2, 'x': 0, 'y': 0, 'transform': 1}, [800, 600])))
check('OutsideAllocatedWidgetPointRejected', lambda: rejected(lambda: module.parent_point(
    observed, [240, 30], {'width': 800, 'height': 600, 'scale': 1, 'x': 0, 'y': 0}, [800, 600])))
for rel, value in hashes.items():
    check('SourcePreserved:' + rel, lambda rel=rel, value=value: expect_equal(
        (sha(ROOT / rel), sha(OUT / 'inputs' / rel)), (value, value)))
report = {'passed': all(item['passed'] for item in checks), 'nativeAcceptance': False,
          'scope': 'Actual inspection helper CPU tests on independent synthetic external receipts; no GTK/native delivery',
          'inputs': hashes, 'checks': checks, 'checkCount': len(checks)}
(OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(OUT / 'report.json', flush=True)
print('checks', len(checks), 'failed', sum(not item['passed'] for item in checks), flush=True)
raise SystemExit(not report['passed'])
