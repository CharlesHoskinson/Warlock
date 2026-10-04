"""Replay explicit Quint ITF events through source-extracted production fragments."""
import hashlib
import json
from pathlib import Path
import resource
import shutil
import subprocess
import time

assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
ROOT = Path(__file__).resolve().parents[1]
IMPL = ROOT.parent
AQ = IMPL / 'elm-nested-input-status-v30'
CORE = IMPL / 'elm-core-parent-position-v31'
MODEL = IMPL / 'elm-parent-position-model-v37/qa/model-1791099188929216528'
OUT = ROOT / 'qa' / ('replay-' + str(time.time_ns()))
OUT.mkdir()
paths = [Path(__file__), ROOT / 'template.cpp', MODEL / 'report.json', MODEL / 'parent.qnt',
         AQ / 'candidate/src/backend/Wayland.cpp', AQ / 'candidate/src/backend/NestedLifecycle.hpp',
         AQ / 'candidate/src/backend/NestedPresentation.hpp', AQ / 'candidate/src/backend/BufferDimensions.hpp',
         AQ / 'candidate/include/aquamarine/input/ParentInput.hpp',
         CORE / 'candidate/src/pointer/PointerManager.cpp', CORE / 'candidate/src/pointer/ParentNormalizedPosition.hpp']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def body(text, marker):
    start = text.index(marker)
    brace = text.index('{', start)
    depth = 1
    end = brace + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end], text[brace + 1:end - 1]


def decode(value):
    if isinstance(value, dict):
        if '#bigint' in value:
            return int(value['#bigint'])
        return {k: decode(v) for k, v in value.items() if not k.startswith('#')}
    if isinstance(value, list):
        return [decode(v) for v in value]
    return value


report = {'passed': False, 'nativeAcceptance': False,
          'scope': 'Selected Quint traces versus actual parent routing/query fragments with typed ownership/monitor mocks; renderer, transport, general clamp and full program excluded',
          'inputs': {}, 'commands': []}


def run(name, command, expected=0):
    p = subprocess.run(command, text=True, capture_output=True, timeout=60)
    (OUT / (name + '.stdout')).write_text(p.stdout)
    (OUT / (name + '.stderr')).write_text(p.stderr)
    report['commands'].append({'command': command, 'exitCode': p.returncode, 'expected': expected})
    assert p.returncode == expected, p.stderr or p.stdout
    return p.stdout


try:
    model = json.loads((MODEL / 'report.json').read_text())
    assert model['passed'] and model['executedNamedScenarios'] == 19
    for rel, digest in model['artifacts'].items():
        assert sha(MODEL / rel) == digest, rel
    trace_paths = sorted(MODEL.glob('named-*.itf.json'))
    assert len(trace_paths) == 19
    paths.extend(trace_paths)
    report['inputs'] = {str(p): sha(p) for p in paths}
    traces = [{'name': p.name, 'states': [decode(s['s']) for s in json.loads(p.read_text())['states']]} for p in trace_paths]
    (OUT / 'traces.json').write_text(json.dumps(traces, indent=2) + '\n')
    text = (CORE / 'candidate/src/pointer/PointerManager.cpp').read_text()
    aq_text = (AQ / 'candidate/src/backend/Wayland.cpp').read_text()
    a = aq_text.index('Aquamarine::ParentInputStatus Aquamarine::parentPointerInputStatus')
    b = aq_text.index('Aquamarine::CWaylandPointer::~CWaylandPointer()', a)
    state_a = text.index('namespace {\nstruct ParentPointerPosition')
    state_b = text.index('UP<CPointerManager>&', state_a)
    warp_text = body(text, 'void CPointerManager::warpAbsolute(')[0]
    projection_a = warp_text.index('    const auto parentPosition = parentPositionFor(this);')
    projection_b = warp_text.index('    onCursorMoved();', projection_a)
    parts = {
        'PRODUCTION_QUERY': aq_text[a:b],
        'PRODUCTION_STATE': text[state_a:state_b],
        'PRODUCTION_WARP_TO': body(text, 'void CPointerManager::warpTo(')[0],
        'PRODUCTION_OUTPUT_PROJECTION': warp_text[projection_a:projection_b],
        'PRODUCTION_LAYOUT': body(text, 'void CPointerManager::onMonitorLayoutChange()')[0],
        'PRODUCTION_DETACH': body(text, 'void CPointerManager::detachPointer(')[0],
        'PRODUCTION_DISPATCH': body(text, 'listener->motionAbsolute = aqPointer->events.warp.listen(')[1],
    }
    source = (ROOT / 'template.cpp').read_text()
    for name, fragment in parts.items():
        assert source.count('// ' + name) == 1
        source = source.replace('// ' + name, fragment)
    (OUT / 'extracted-fragments.json').write_text(json.dumps(parts, indent=2) + '\n')
    (OUT / 'replay.cpp').write_text(source)
    flags = ['c++', '-std=c++23', '-O2', '-Wall', '-Wextra', '-Werror',
             '-I' + str(AQ / 'candidate/src/backend'), '-I' + str(AQ / 'candidate/include'),
             '-I' + str(CORE / 'candidate/src/pointer')]
    run('compile', [*flags, str(OUT / 'replay.cpp'), '-o', str(OUT / 'replay')])
    result = run('replay', [str(OUT / 'replay'), str(OUT / 'traces.json')])
    states = int(result.split('states: ')[1])
    assert states == sum(len(t['states']) for t in traces)
    # The comparison must reject actual routing changes, independently of model mutation controls.
    mutants = [
        ('origin', 'm_pointerPos = *parentPoint;', 'm_pointerPos = Vector2D{parentPoint->x - mappedArea.x,parentPoint->y};'),
        ('readiness', 'return focused && focused.get() == output && mappingReady(focused.get());',
         'return focused && mappingReady(focused.get());'),
        ('superseding', 'parentPositionFor(this)->clear();\n    damageIfSoftware();', 'damageIfSoftware();'),
    ]
    for name, before, after in mutants:
        assert source.count(before) == 1
        cpp = OUT / (name + '.cpp')
        cpp.write_text(source.replace(before, after))
        run(name + '-compile', [*flags, str(cpp), '-o', str(OUT / name)])
        run(name + '-rejected', [str(OUT / name), str(OUT / 'traces.json')], expected=1)
    for path, digest in report['inputs'].items():
        assert sha(path) == digest, path
    report.update(passed=True, traces=len(traces), states=states, mutantsRejected=3,
                  comparedFields=['anchor output', 'normalized point', 'routed warp count', 'forwarded/superseding logical coordinates'])
except Exception as error:
    report['error'] = repr(error)
report['artifacts'] = {str(p.relative_to(OUT)): sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'passed': report['passed'], 'report': str(OUT / 'report.json'), 'error': report.get('error')}))
raise SystemExit(not report['passed'])
