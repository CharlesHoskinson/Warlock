"""Real GDK enum/event objects exercise the extracted receipt function, no GUI."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import resource
import shutil
import time

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk, Gtk

assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1), 'Use protected qa_run.py'
ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT.parents[1] / 'implementation/elm-parent-input-probe-v12/fixture.py'
OUT = ROOT / 'qa' / ('event-kind-' + str(time.time_ns()))
OUT.mkdir()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


inputs = {str(path): sha(path) for path in (ROOT / 'fixture.py', Path(__file__).resolve(), PARENT)}
for index, path in enumerate(inputs):
    dest = OUT / 'inputs' / (str(index) + '-' + Path(path).name)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dest)
    dest.chmod(0o444)
checks = []


def check(name, fn):
    try:
        fn()
        checks.append({'name': name, 'passed': True})
    except Exception as error:
        checks.append({'name': name, 'passed': False, 'error': repr(error)})


def eq(actual, expected):
    assert actual == expected, (actual, expected)


source = (ROOT / 'fixture.py').read_text()
tree = ast.parse(source)
compile(source, str(ROOT / 'fixture.py'), 'exec')
delivery = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'delivered')
normalized = copy.deepcopy(tree)
for node in ast.walk(normalized):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'log':
        node.keywords = [keyword for keyword in node.keywords if keyword.arg not in ('eventType', 'eventTypeNick')]
check('OriginalFixtureAstUnchangedExceptTwoReceiptFields', lambda: eq(
    ast.dump(normalized, include_attributes=False), ast.dump(ast.parse(PARENT.read_text()), include_attributes=False)))


class Recipient:
    def get_name(self):
        return 'parent-input-recipient'

    def get_window(self):
        return None


# Stand-in widget has no native window. Actual GDK Event objects and actual
# Gtk.get_event_widget are used; this exercises logging, not native ownership.
recipient = Recipient()
captured = []
counts = {'enter': 0, 'motion': 0, 'button-press': 0, 'button-release': 0}
env = {'Gtk': Gtk, 'recipient': recipient, 'counts': counts,
       'log': lambda kind, **fields: captured.append({'kind': kind, **fields})}
exec(compile(ast.Module(body=[delivery], type_ignores=[]), str(ROOT / 'fixture.py') + ':delivered', 'exec'), env)
for event_type, value, nick, kind in (
    (Gdk.EventType.BUTTON_PRESS, 4, 'button-press', 'button-press'),
    (Gdk.EventType.DOUBLE_BUTTON_PRESS, 5, '2button-press', 'button-press'),
    (Gdk.EventType.TRIPLE_BUTTON_PRESS, 6, '3button-press', 'button-press'),
    (Gdk.EventType.BUTTON_RELEASE, 7, 'button-release', 'button-release'),
    (Gdk.EventType.MOTION_NOTIFY, 3, 'motion-notify', 'motion'),
    (Gdk.EventType.ENTER_NOTIFY, 10, 'enter-notify', 'enter'),
):
    def witness(event_type=event_type, value=value, nick=nick, kind=kind):
        eq((int(event_type), event_type.value_nick), (value, nick))
        event = Gdk.Event.new(event_type)
        event.x, event.y, event.time = 20, 30, 55
        if kind.startswith('button-'):
            event.button = 1
        before = len(captured)
        eq(env['delivered'](recipient, event, kind), False)
        eq(len(captured), before + 1)
        record = captured[-1]
        eq((record['eventType'], record['eventTypeNick'], record['kind']), (value, nick, kind))
        eq((record['x'], record['y'], record['eventTime']), (20.0, 30.0, 55))
        eq(record['button'], 1 if kind.startswith('button-') else None)
    check('ActualGdkEnumAndExtractedReceipt:' + nick, witness)
check('DoubleAndTriplePressReceiptsNotDroppedOrRemovedFromOriginalCount', lambda: eq(counts['button-press'], 3))
check('AllOriginalRecipientCountsPreserved', lambda: eq(
    counts, {'enter': 1, 'motion': 1, 'button-press': 3, 'button-release': 1}))
check('PhysicalPress4DistinguishableFromDouble5AndTriple6', lambda: eq(
    [event['eventType'] for event in captured if event['kind'] == 'button-press'], [4, 5, 6]))
check('PhysicalRelease7RemainsSeparateReceipt', lambda: eq(
    [event['eventType'] for event in captured if event['kind'] == 'button-release'], [7]))
for path, digest in inputs.items():
    check('OriginalInputPreserved:' + path, lambda path=path, digest=digest: eq(sha(path), digest))
report = {'passed': all(item['passed'] for item in checks), 'nativeAcceptance': False,
          'scope': 'Real GDK3 enum and allocated Event CPU witnesses; extracted actual receipt function; no native event delivery',
          'inputs': inputs, 'checks': checks, 'checkCount': len(checks), 'receipts': captured}
(OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(OUT / 'report.json', flush=True)
print('checks', len(checks), 'failed', sum(not item['passed'] for item in checks), flush=True)
raise SystemExit(not report['passed'])
