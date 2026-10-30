"""Protected retained-log parser checks; no GUI or original acceptance."""
import hashlib
import importlib.util
import json
import random
import re
import resource
import sys
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path('/home/charles/Warlock')
LOG = Path('/home/charles/window-integration-qa/warlock-window-feedback-1793230156693216294/warlock.log')
COLLECTOR = HERE.parent/'taskbar-qa/measured_inspection.py'
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path, name):
    raw = path.read_bytes()
    m = importlib.util.module_from_spec(importlib.util.spec_from_loader(name, loader=None))
    m.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), m.__dict__)
    return m
def main():
    sys.path.insert(0, str(ROOT/'window-integration-qa'))
    from qa_launch import require_qa_scope
    scope = require_qa_scope()
    assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
    assert sha(COLLECTOR) == '559775d3a39c14b1cea2b5747773665a4817c5b9850d08afc4782d2919a11f9e'
    paths = [Path(__file__), HERE/'popup_join.py', HERE/'runner.py', HERE/'branch.txt', COLLECTOR, LOG]
    inputs = {str(p): sha(p) for p in paths}
    report = dict(passed=False, scope=scope, checks=[], inputs=inputs, seed=20261030,
                  nativeAcceptance=False, releaseAccepted=False,
                  limits='Actual retained log positive; in-memory event mutations and seeded stale acknowledgements are parser checks, not new native observations.')
    def check(name, value):
        report['checks'].append(dict(name=name, passed=bool(value)))
        if not value:
            raise AssertionError(name)
    try:
        parser = load(HERE/'popup_join.py', 'pin_join_checks')
        collector = load(COLLECTOR, 'pin_collector_checks')
        runner = load(HERE/'runner.py', 'pin_runner_source_checks')
        source = runner.compose()
        (HERE/'composed-source-only.py').write_text(source)
        check('All exact composition anchors and Python syntax valid', bool(compile(source, str(HERE/'composed-source-only.py'), 'exec')))
        check('No stopped keyboard menu opener in selected branch', "key(127)" not in (HERE/'branch.txt').read_text())
        raw = LOG.read_text()
        lines = raw.splitlines()
        candidate = None
        # Find an actual complete coherent popup/bar/model frame. Do not modify
        # the retained positive log or fabricate its publication or lease.
        for end, line in enumerate(lines):
            if not line.startswith('surface-report: origin=popup '):
                continue
            text = '\n'.join(lines[:end+1])+'\n'
            body = json.loads(line.split(' ', 2)[2])['body']
            projection = collector.Collector().read(text)
            result = parser.join(text, body, projection, '2', native_bar_epochs=collector.native_bar_epochs)
            if result:
                candidate = text, body, projection, result
                break
        check('Actual retained popup frame has exact object join', candidate is not None)
        text, body, projection, result = candidate
        report['retainedFrame'] = dict(endLine=len(text.splitlines()), join=result,
                                       logSHA256=inputs[str(LOG)], body=body, projection=projection)
        check('Retained configured global box matches actual recorded popup', result['rect'] == [50, 56, 700, 420])
        def joined(value=text, b=body, p=projection):
            return parser.join(value, b, p, '2', native_bar_epochs=collector.native_bar_epochs)
        popup, xdg, surface, parent = (result[k] for k in ['popup', 'xdg', 'surface', 'parent'])
        check('Missing exact parent assignment refused', joined(re.sub(r'^.*zwlr_layer_surface_v1[#@]'+parent+r'\.get_popup\(xdg_popup[#@]'+popup+r'\).*\n', '', text, flags=re.M)) is None)
        check('Missing exact xdg acknowledgement refused', joined(re.sub(r'^.*xdg_surface[#@]'+xdg+r'\.ack_configure\(.*\n', '', text, flags=re.M)) is None)
        check('Missing host geometry callback refused', joined(re.sub(r'^surface-configured:.*\n', '', text, flags=re.M)) is None)
        check('Destroyed popup refused', joined(text+'xdg_popup#'+popup+'.destroy()\n') is None)
        check('Destroyed and reused wl_surface epoch refused', joined(text+'wl_surface#'+surface+'.destroy()\nwl_compositor#5.create_surface(new id wl_surface#'+surface+')\n') is None)
        check('Destroyed parent layer refused', joined(text+'zwlr_layer_surface_v1#'+parent+'.destroy()\n') is None)
        check('Closed host lease refused', joined(text+'surface-popup-closed: lease='+body['lease']+'\n') is None)
        check('Stale body publication refused', joined(b={**body, 'publication': '999999'}) is None)
        check('Wrong body lease refused', joined(b={**body, 'lease': '999999'}) is None)
        check('Wrong native menu incarnation refused', joined(p={**projection, 'mode': 'menu', 'menu': {'incarnation': 'foreign'}}) is None)
        check('Closed projection refused', joined(p={**projection, 'mode': 'closed'}) is None)
        event = 'xdg_popup#'+popup+'.configure(50, 56, 700, 420)\n'
        configure = 'xdg_surface#'+xdg+'.configure(9999)\nxdg_surface#'+xdg+'.ack_configure(9999)\n'
        check('Second same-size configure without fresh host callback refused', joined(text+event+configure) is None)
        fresh = text+event+'surface-configured: lease='+body['lease']+' rectKnown=0 gdkWidth=700 gdkHeight=420\n'+configure
        check('Fresh exact host callback and acknowledgement restore same-size join', joined(fresh) is not None)
        foreign = ('wl_compositor#5.create_surface(new id wl_surface#9001)\n'
                   'xdg_wm_base#35.get_xdg_surface(new id xdg_surface#9002, wl_surface#9001)\n'
                   'xdg_surface#9002.get_popup(new id xdg_popup#9003, nil, xdg_positioner#9004)\n'
                   'zwlr_layer_surface_v1#'+parent+'.get_popup(xdg_popup#9003)\n')
        check('Ambiguous live popup refused', joined(text+foreign) is None)
        rng = random.Random(report['seed'])
        report['staleSerials'] = []
        for i in range(16):
            serial = rng.randrange(10000, 1000000)
            mutated = fresh+'xdg_surface#'+xdg+'.configure('+str(serial)+')\nxdg_surface#'+xdg+'.ack_configure(9999)\n'
            check('Seeded stale acknowledgement '+str(i), joined(mutated) is None)
            report['staleSerials'].append(serial)
        for path, value in inputs.items():
            check('Observed source unchanged '+Path(path).name, sha(Path(path)) == value)
        report['passed'] = True
    except Exception as error:
        report.update(error=repr(error), traceback=traceback.format_exc())
    (HERE/'parser-check-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(passed=report['passed'], checks=len(report['checks']), report=str(HERE/'parser-check-report.json'), error=report.get('error'))))
    return 0 if report['passed'] else 1
if __name__ == '__main__':
    sys.exit(main())
