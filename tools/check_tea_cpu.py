#!/usr/bin/env python3
"""Fixed owning Elm effect/decoder and stream-capacity CPU campaigns."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'window-integration-qa'))
from qa_launch import require_qa_scope, runtime_base
from check_elm_cpu import quint_toolchain
from qa_cpu import tea_inputs


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


BOOLEAN_WORKER = r'''
const fs=require('node:fs'),vm=require('node:vm');
const [file,name,output]=process.argv.slice(1);
const capacityNames=['publishedPinReachable','sixteenRequestsAdmitted','seventeenRequestsRefused','freshSavingLocallyUnsent','unknownReservationPreserved','mismatchedIdentityPreserved','noPartialReplay','everyFallbackBounded','requestlessDomainPreserved','request8192AsciiAdmitted','request8193AsciiRefused','request8192UnicodeAdmitted','request8193UnicodeRefused','whole131072UnicodeAdmitted','whole131073UnicodeCompacted','requestlessOverflowCompacted','unboundOverflowCompacted','missingBindingOverflowCompacted','refusalPreservesRegisteredBatchCount','refusalDoesNotAllocateRequest','freshActionAfterLocalRefusalAdmitted'];
const names={PinsReplay:['pinWritesOnce','doesNotClaimSaveBeforeReceipt','pinOrderConfirmed','reorderConfirmed','restartPreservesExactIdentitiesAndOrder','staleActionRejected','staleReceiptRejected','missingEntryCannotBePinned','boundaryReorderNoWrite','zeroWindowPinLaunchesOnce','unknownReceiptNeverWrites','currentPinReceiptRestoresSearchFocus','unknownReceiptKeepsRecoveryReachable'],PreviewPaintReplay:['OriginalAcquireWaitsForPaint','PaintForwardsExactOriginalJobAndDeadline','DuplicatePaintCannotReplayAcquire','ExactCancelRetiresUnsentAcquireImmediately','DifferentRequestCannotCancelPendingAcquire','DifferentBindingCannotCancelPendingAcquire','RepeatedPendingAcquireDoesNotMintAnotherTicket','OldPaintCannotBorrowFreshRequest','ReleaseAndAckNeverWaitForPaint','ForeignNumericExtraPaintCannotCapture']};
names.StreamCapacityReplay=capacityNames;
let done=false;
const report={passed:false,nativeAcceptance:false,releaseAccepted:false,module:name};
function save(){fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');}
const timer=setTimeout(()=>{if(!done){report.error='Missing outgoing fixture';save();process.exitCode=2;}},3000);
try {
 if(!names[name])throw Error('Unknown fixed boolean fixture');
 const sandbox={console,setTimeout,clearTimeout};vm.createContext(sandbox);
 vm.runInContext(fs.readFileSync(file,'utf8'),sandbox,{timeout:1500});
 sandbox.Elm[name].init({flags:null}).ports.outgoing.subscribe(raw=>{
  done=true;clearTimeout(timer);report.fixture=JSON.parse(JSON.stringify(raw));
  const checks=report.fixture.checks||{},actual=Object.keys(checks).sort(),expected=[...names[name]].sort();
  report.exactNamedBudget=JSON.stringify(actual)===JSON.stringify(expected);
  report.passed=report.exactNamedBudget&&expected.every(n=>checks[n]===true);
  save();process.exitCode=report.passed?0:1;
 });
}catch(error){done=true;clearTimeout(timer);report.error=String(error.stack||error);save();process.exitCode=2;}
'''


def main():
    capacity_only = sys.argv[1:] == ['--capacity']
    if sys.argv[1:] and not capacity_only:
        raise RuntimeError('Only the fixed --capacity mode is supported')
    scope = require_qa_scope()
    runtime_base()
    output = ROOT / '.warlock-contributor' / ('tea-cpu-' + str(time.time_ns()))
    output.mkdir(mode=0o700)
    report = {'schema': 1, 'requirement': 'ELM-ARC-003' if capacity_only else 'ELM-TEA-003', 'passed': False,
              'mode': 'stream-capacity' if capacity_only else 'effects-and-capacity',
              'scope': ('Actual owning Elm compiler and production register/refusal property fixture; no model sampling in this focused mode'
                        if capacity_only else 'Actual owning Elm compiler/replay and independent effect/decoder fixtures; sampled causal models'),
              'protectedScope': scope, 'originalAcceptance': False, 'nativeAcceptance': False,
              'releaseAccepted': False, 'commands': [], 'models': {}}
    work = output / 'work'
    home = output / 'elm-home'
    try:
        inputs = {name: digest(ROOT / name) for name in sorted(tea_inputs(ROOT))}
        report['inputs'] = inputs
        pin, cli = quint_toolchain()
        node = Path(pin['node']['path'])
        if digest(node) != pin['node']['sha256']:
            raise RuntimeError('Pinned Node interpreter differs')
        report['quintToolchain'] = pin
        report['pythonSHA256'] = digest(Path(sys.executable).resolve())
        held = ROOT / 'implementation/warlock-preview-provider-v143'
        spec = importlib.util.spec_from_file_location('tea_held_toolchain', held / 'qa/toolchain.py')
        toolchain = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(toolchain)
        compiler_pin = toolchain.verify()
        report['compiler'] = compiler_pin
        compiler = str(held / compiler_pin['compiler'])
        work.mkdir(mode=0o700)
        shutil.copytree(ROOT / 'implementation/warlock/src', work / 'src')
        shutil.copytree(held / compiler_pin['elmHome'], home)
        (work / 'qa').mkdir()
        config = json.loads((ROOT / 'implementation/warlock/elm.json').read_text())
        config['source-directories'] = ['src', 'qa']
        (work / 'elm.json').write_text(json.dumps(config))
        for name in inputs:
            if name.startswith('implementation/warlock/qa/'):
                shutil.copy2(ROOT / name, work / 'qa' / Path(name).name)
        env = dict(os.environ, ELM_HOME=str(home), NO_COLOR='1', PYTHONDONTWRITEBYTECODE='1')
        for name in ('NODE_OPTIONS', 'NODE_PATH', 'FORCE_COLOR'):
            env.pop(name, None)

        def run(name, arguments, timeout=120):
            toolchain.verify()
            try:
                result = subprocess.run([str(a) for a in arguments], cwd=work, env=env,
                                        capture_output=True, text=True, timeout=timeout)
            except subprocess.TimeoutExpired as error:
                def decoded(value):
                    return value.decode('utf-8', errors='replace') if isinstance(value, bytes) else (value or '')
                (output / (name + '.stdout')).write_text(decoded(error.stdout))
                (output / (name + '.stderr')).write_text(decoded(error.stderr))
                report['commands'].append({'name': name, 'argv': [str(a) for a in arguments],
                                           'exit': None, 'timeout': True, 'forcedCleanup': True})
                raise RuntimeError(name + ' timed out; partial logs retained') from error
            (output / (name + '.stdout')).write_text(result.stdout)
            (output / (name + '.stderr')).write_text(result.stderr)
            report['commands'].append({'name': name, 'argv': [str(a) for a in arguments],
                                       'exit': result.returncode, 'timeout': False, 'forcedCleanup': False})
            print(name, result.returncode, flush=True)
            toolchain.verify()
            if result.returncode != 0:
                raise RuntimeError(name + ' failed; retained stdout/stderr contain the result')
            return result.stdout

        run('compiler-version', [compiler, '--version'])
        run('node-version', [node, '--version'])
        for module in ('Main', 'Bar', 'Popup'):
            run('compile-' + module, [compiler, 'make', 'src/' + module + '.elm', '--optimize', '--output=' + str(output / (module + '.js'))])
        fixtures = [('StreamCapacityReplay', 'stream-capacity')] if capacity_only else [('PinsPendingReplay', 'pins-pending'), ('PinsReplay', 'legacy-pins'),
                    ('PreviewPaintReplay', 'preview-paint'), ('AuthorityTupleReplay', 'authority-tuple'),
                    ('ReceiptStateReplay', 'receipt-state'), ('StreamCapacityReplay', 'stream-capacity')]
        for module, name in fixtures:
            run('compile-' + name, [compiler, 'make', 'qa/' + module + '.elm', '--optimize', '--output=' + str(output / (name + '.js'))])

        for model in (() if capacity_only else ('pins-save-lifecycle', 'receipt-lifecycle')):
            model_report = {'directedTests': {}}
            report['models'][model] = model_report
            for filename in (model + '.qnt', model + '_test.qnt'):
                source = (work / 'qa' / filename).read_text()
                main_module = re.search(r'^\s*module\s+(\w+)', source, re.M).group(1)
                run(filename + '-typecheck', [node, cli, 'typecheck', 'qa/' + filename])
                tests = re.findall(r'^\s*run\s+(\w+)\s*=', source, re.M)
                if tests:
                    if len(tests) != len(set(tests)):
                        raise RuntimeError('Duplicate named model test')
                    selector = '^(' + '|'.join(re.escape(t) for t in tests) + ')$'
                    text = run(filename + '-directed', [node, cli, 'test', 'qa/' + filename, '--main=' + main_module,
                                                       '--match=' + selector, '--backend=typescript', '--verbosity=2'])
                    count = re.search(r'(\d+) passing', text)
                    if count is None or int(count.group(1)) != len(tests):
                        raise RuntimeError('Exact named model test budget not executed')
                    model_report['directedTests'][filename] = tests
            source = (work / 'qa' / (model + '.qnt')).read_text()
            main_module = re.search(r'^\s*module\s+(\w+)', source, re.M).group(1)
            witnesses = [name for name in re.findall(r'^\s*val\s+(\w+)\s*=', source, re.M)
                         if name.startswith('witness') or name.endswith('Witness')]
            if not witnesses:
                raise RuntimeError('Named model reachability witnesses required')
            text = run(model + '-safety', [node, cli, 'run', 'qa/' + model + '.qnt', '--main=' + main_module,
                                          '--backend=typescript', '--invariant=safety', '--witnesses', *witnesses,
                                          '--max-samples=10000', '--max-steps=50', '--seed=20261101', '--verbosity=1'], timeout=180)
            counts = {name: int(count) for name, count in re.findall(r'(\w+) was witnessed in (\d+) trace', text)}
            model_report['sampling'] = {'samples': 10000, 'maxSteps': 50, 'seed': 20261101, 'witnesses': counts}
            if set(counts) != set(witnesses) or any(n == 0 for n in counts.values()):
                raise RuntimeError('Model witness missing/zero; retain coverage gap')
        quint_toolchain()
        # Run unchanged boundary controls before the intentionally failing RED.
        for module, name in fixtures[1:] + fixtures[:1]:
            if module in ('PinsReplay', 'PreviewPaintReplay', 'StreamCapacityReplay'):
                run(name, [node, '-e', BOOLEAN_WORKER, output / (name + '.js'), module, output / (name + '.json')])
            else:
                run(name, [node, 'qa/' + name + '.cjs', output / (name + '.js'), output / (name + '.json')])
        if inputs != {name: digest(ROOT / name) for name in inputs}:
            raise RuntimeError('Reviewed input changed during check')
        if digest(node) != pin['node']['sha256'] or digest(Path(sys.executable).resolve()) != report['pythonSHA256']:
            raise RuntimeError('Development interpreter changed during check')
        report['passed'] = True
    except Exception as error:
        report['error'] = str(error)
    finally:
        try:
            if report.get('inputs'):
                report['inputsAfter'] = {}
                for name in report['inputs']:
                    path = ROOT / name
                    if path.is_symlink() or not path.is_file():
                        raise RuntimeError('Reviewed regular input replaced: ' + name)
                    report['inputsAfter'][name] = digest(path)
                report['inputsUnchanged'] = report['inputsAfter'] == report['inputs']
                if not report['inputsUnchanged']:
                    raise RuntimeError('Reviewed source changed, including on failing campaign')
            if 'toolchain' in locals():
                toolchain.verify()
            if 'pin' in locals():
                quint_toolchain()
                if digest(Path(pin['node']['path'])) != pin['node']['sha256']:
                    raise RuntimeError('Pinned Node changed')
            if report.get('pythonSHA256') and digest(Path(sys.executable).resolve()) != report['pythonSHA256']:
                raise RuntimeError('Python interpreter changed')
        except Exception as error:
            report['passed'] = False
            report['postcheckError'] = str(error)
        # Retain the exact staged source/model/fixture copy as well as logs.
        report['artifacts'] = {p.name: digest(p) for p in output.glob('*.js')}
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        shutil.rmtree(home, ignore_errors=True)
        print(json.dumps({'passed': report['passed'], 'report': str(output / 'report.json'), 'error': report.get('error')}), flush=True)
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
