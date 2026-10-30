"""Protected real current-composition release selection and refusals."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import traceback

ROOT = Path('/home/charles/Warlock')
HERE = Path(__file__).resolve().parent
LOCK = HERE.parent/'current-native-capture-1793334328418274792/native-lock.json'
DIGEST = 'a04cea52dfbca05c21420c4b2705e75278d46640a9ebc81fe9aa4672005346ac'
sys.path.insert(0, str(ROOT/'implementation/warlock/adapter'))
import release_builder as builder
import release_tuple

def main():
    scope = builder.require_scope()
    sources = [Path(__file__), ROOT/'implementation/warlock/adapter/release_tuple.py', ROOT/'implementation/warlock/adapter/current_native.py']
    inputs = {str(p): builder.sha(p) for p in sources}
    report = dict(passed=False, scope=scope, sources=inputs, checks=[], nativeAcceptance=False,
                  releaseAccepted=False, limits='Production tuple selection and declared metadata mutations only. No compiler, native load or two-build comparison.')
    def check(name, value):
        report['checks'].append(dict(name=name, passed=bool(value)))
        if not value:
            raise AssertionError(name)
    def select(path, digest):
        files = {}
        add = lambda p, role, expected=None: builder.add(files, p, role, expected)
        selected = release_tuple.capture(ROOT, path, digest, add, builder.read, builder.sha)
        return selected, files
    def rejects(name, path, digest):
        try:
            select(path, digest)
        except (ValueError, OSError, builder.ChangedInput) as error:
            report['checks'].append(dict(name=name, passed=True, error=str(error), errorType=type(error).__name__))
        else:
            check(name, False)
    try:
        lock = builder.read(LOCK)
        previous = sys.modules.get('current_build')
        (pair, aliases, reference), files = select(LOCK, DIGEST)
        check('Actual current composition selects exact native artifacts', pair == {
            role: {k: lock['slots'][slot][k] for k in ['path', 'sha256']}
            for role, slot in [('core', 'core'), ('plugin', 'authority'), ('aquamarine', 'aquamarine')]})
        check('All nineteen current runtime assets retain exact hashes', reference['assets'] == {'assets/'+p: h for p, h in lock['assets']['files'].items()} and len(reference['assets']) == 19)
        check('Every composition input retains its recorded digest', all(files[p]['sha256'] == h for p, h in lock['inputs'].items()))
        check('Current selected host identity retained', reference['hostSHA256'] == lock['slots']['host']['sha256'])
        aq = lock['slots']['aquamarine']
        check('Owning loader alias retained', aliases == {Path(aq['sonameAlias']).name: aq['aliasTarget']})
        check('Source and release provenance limits remain explicit', reference['nativeAcceptance'] is False and reference['historicalBinaryReproduction'] is False and 'core and Aquamarine' in reference['missingObservation'])
        check('Temporary validator module binding restored', sys.modules.get('current_build') is previous)
        report['selection'] = dict(nativePair=pair, aliases=aliases, reference=reference, inputCount=len(files))
        rejects('Wrong outer reviewed digest refused', LOCK, '0'*64)
        def mutate(name, change):
            data = copy.deepcopy(lock)
            change(data)
            path = HERE/('selection-'+str(len(report['checks']))+'.json')
            path.write_text(json.dumps(data, indent=2)+'\n')
            rejects(name, path, builder.sha(path))
        mutate('Unknown schema refused', lambda d: d.update(schema=99))
        mutate('Unknown tuple kind refused', lambda d: d.update(kind='unknown'))
        mutate('Missing inputs becomes structured refusal', lambda d: d.pop('inputs'))
        mutate('Malformed inputs becomes structured refusal', lambda d: d.update(inputs=[]))
        mutate('Missing frontend becomes structured refusal', lambda d: d.pop('frontend'))
        mutate('Raised native acceptance refused', lambda d: d.update(nativeAcceptance=True))
        module = str(ROOT/'implementation/warlock/adapter/current_native.py')
        mutate('Wrong validator module digest refused', lambda d: d['inputs'].update({module: '0'*64}))
        mutate('Wrong historical adapter role refused', lambda d: d['adapterChanges'][str(ROOT/'implementation/warlock/adapter/release_tuple.py')].update(old='0'*64))
        mutate('Wrong runtime asset digest refused', lambda d: d['assets']['files'].update({'popup-adapter.js': '0'*64}))
        nonobject = HERE/'selection-nonobject.json'
        nonobject.write_text('[]\n')
        rejects('Nonobject tuple becomes structured refusal', nonobject, builder.sha(nonobject))
        old = HERE.parent/'current-native-capture-1793324986522396247/native-lock.json'
        rejects('Stale pre-adapter composition lock refused', old, 'ba97d48eaa4f8c093c63f4b6b6e46d9d2ad602f95ffae16cda226af550d8bcd0')
        check('Original reviewed selection still succeeds', select(LOCK, DIGEST)[0] == (pair, aliases, reference))
        for name, digest in inputs.items():
            check('Executed source unchanged '+Path(name).name, builder.sha(name) == digest)
        report['passed'] = True
    except Exception as error:
        report.update(error=repr(error), traceback=traceback.format_exc())
    (HERE/'selection-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(passed=report['passed'], checks=len(report['checks']), report=str(HERE/'selection-report.json'), error=report.get('error'))))
    return 0 if report['passed'] else 1
if __name__ == '__main__':
    sys.exit(main())
