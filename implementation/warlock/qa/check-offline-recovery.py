"""Protected offline recovery model and actual profile/CLI observations."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import os
import signal
import stat
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'qa/runs' / ('offline-recovery-' + str(time.time_ns()))
OUT.mkdir(parents=True)

def command(name, argv):
    result = subprocess.run(argv, text=True, capture_output=True, timeout=180)
    (OUT / (name + '.stdout')).write_text(result.stdout)
    (OUT / (name + '.stderr')).write_text(result.stderr)
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout

spec = ROOT / 'qa/offline-recovery.qnt'
tests = ROOT / 'qa/offline-recovery_test.qnt'
command('typecheck', ['quint', 'typecheck', str(tests)])
command('named', ['quint', 'test', str(tests), '--backend=typescript',
    '--match=^(initialPredecessorTest|failedHostRollbackTest|damagedCandidateDoesNotBlockRecoveryTest|activeHostCannotSwitchTest|missingPriorCannotRollbackTest|privateStagingNeverChangesSelectionTest|stagingCrashKeepsOldPreferencesTest|unknownCannotStartOrReplayTest|readReconcilesUnknownTest|repeatedRollbackIsNoOpTest)$',
    '--max-samples=1', '--seed=79601'])
output = command('sampled-safety', ['quint', 'run', str(spec), '--backend=typescript',
    '--invariants=safety', '--witnesses', 'predecessorStarted',
    'failedHostRecovered', 'damagedCandidateRecovered',
    'uncertainSelectionObserved', 'stagingCrashRetainsCandidate',
    '--max-samples=1000', '--max-steps=30', '--seed=79602'])
import re
witnesses = {name: int(count) for name, count in re.findall(
    r'(\w+) was witnessed in (\d+) trace', output)}
assert len(witnesses) == 5 and all(witnesses.values()), output
report = {'passed': True, 'scope': 'Executable recovery profile initialization.',
    'modelSHA256': hashlib.sha256(spec.read_bytes()).hexdigest(),
    'witnessCounts': witnesses,
    'nativeAcceptance': False, 'fullReleaseAccepted': False}
if sys.argv[1:] != ['--model-only']:
    assert not sys.argv[1:], 'Unknown check mode'
    sys.path.insert(0, str(ROOT / 'adapter'))
    import recovery_profile as recovery
    from shell_preferences import Store as SettingsStore
    from shortcut_preferences import Store as ShortcutsStore
    from motion_preferences import Store as MotionStore
    from taskbar_preferences import Store as PinsStore
    checks = []
    def check(name, value):
        assert value, name
        checks.append(name)
    def refuses(name, fn):
        try:
            fn()
        except (recovery.Refused, OSError, ValueError):
            checks.append(name)
            return
        raise AssertionError(name)
    source = OUT / 'source-state'
    source.mkdir(mode=0o700)
    settings = SettingsStore(str(source)); old = settings.read()
    status, saved = settings.save({**old, 'values': {**old['values'], 'theme': 'dawn',
        'textScale': 150, 'effectsOff': True}})
    check('SeedValidatedAppearance', status == 'Saved')
    shortcuts = ShortcutsStore(str(source)); old = shortcuts.read()
    status, approved = shortcuts.save({**old, 'choices': {
        'applications': 'alternate', 'system': 'default', 'notifications': 'keep'}})
    check('SeedExplicitShortcutDecisions', status == 'Saved')
    motion = MotionStore(str(source)); old = motion.read()
    check('SeedMotion', motion.save({**old, 'override': 'reduced'})[0] == 'Saved')
    pins = PinsStore(str(source)); old = pins.read()
    check('SeedPins', pins.save({**old, 'identities': ['warlock-editor', 'warlock-peer']})[0] == 'Saved')
    baseline = {name: (source / 'warlock' / name).read_bytes() for name in recovery.PREFERENCES}
    executable = '/usr/bin/python3'
    events = OUT / 'host-events.jsonl'
    fixture = OUT / 'profile-host.py'
    fixture.write_text('''import json,os,pathlib,sys,time
sys.path.insert(0,sys.argv[1])
from shell_preferences import Store
from shortcut_preferences import Store as Shortcuts
from motion_preferences import Store as Motion
from taskbar_preferences import Store as Pins
role=sys.argv[2]
store=Store(); appearance=store.read()
with open(sys.argv[3],'a') as stream:
 stream.write(json.dumps({'role':role,'pid':os.getpid(),'appearance':appearance,
  'shortcuts':Shortcuts().read(),'motion':Motion().read(),'pins':Pins().read(),
  'stateHome':os.environ['XDG_STATE_HOME']})+'\\n');stream.flush()
if role=='candidate':
 status,value=store.save({**appearance,'values':{**appearance['values'],'theme':'high-contrast'}})
 assert status=='Saved'
 sys.exit(17)
if role=='hold':
 print('ready',flush=True)
 time.sleep(30)
''')
    def desc(role, path=fixture):
        return {'schema': 1, 'argv': [executable, '-B', str(path),
            str(ROOT / 'adapter'), role, str(events)], 'cwd': str(OUT),
            'files': {executable: recovery.artifact_sha(executable),
                      str(path): recovery.artifact_sha(str(path))}}
    predecessor, candidate = desc('predecessor'), desc('candidate')
    tool = str(ROOT / 'adapter/recovery_profile.py')
    for name, value in [('predecessor', predecessor), ('candidate', candidate)]:
        (OUT / (name + '.json')).write_text(json.dumps(value))
    profile = OUT / 'profile'
    def cli(operation, *args, expected=0, target=profile):
        result = subprocess.run([executable, '-B', tool, '--profile', str(target),
            operation, *args], text=True, capture_output=True, timeout=10)
        row = {'operation': operation, 'exitCode': result.returncode,
               'stdout': result.stdout, 'stderr': result.stderr}
        report.setdefault('cli', []).append(row)
        assert result.returncode == expected, row
        return json.loads(result.stdout)
    prepared = cli('prepare', '--predecessor', str(OUT / 'predecessor.json'),
        '--candidate', str(OUT / 'candidate.json'), '--source-state', str(source))
    check('PrepareRetainsPredecessorWithoutLaunching', prepared['route'] == 'predecessor'
          and not events.exists())
    check('SourcePreferencesRemainByteExact', all((source / 'warlock' / name).read_bytes() == body
          for name, body in baseline.items()))
    check('OnlyPreferencesCopiedNoRequestJournal', set((profile / 'baseline').iterdir()) ==
          {profile / 'baseline' / name for name in recovery.PREFERENCES})
    check('PrivateProfileAndCopies', all(stat.S_IMODE(p.stat().st_mode) ==
          (0o700 if p.is_dir() else 0o600) for p in profile.rglob('*')))
    before = (profile / 'selection.json').read_bytes()
    check('StatusDoesNotChangeSelection', cli('status')['route'] == 'predecessor'
          and (profile / 'selection.json').read_bytes() == before)
    check('ExplicitActivationSelectsCandidate', cli('activate')['route'] == 'candidate')
    observed = cli('run', expected=17)
    check('ActualManagedCandidateFailed', observed['route'] == 'candidate' and observed['exitCode'] == 17)
    check('CandidateHasItsOwnSavedPreferences', SettingsStore(str(profile / 'candidate-state')).read()['values']['theme'] == 'high-contrast')
    broken = profile / 'candidate-state/warlock/settings.json'
    broken.write_text('{"schema":99,"preserved":"future schema"}')
    broken_before = broken.read_bytes()
    candidate_only = OUT / 'candidate-only.txt'; candidate_only.write_text('retained artifact')
    candidate['files'][str(candidate_only)] = recovery.artifact_sha(str(candidate_only))
    # Retain an independently prepared profile for the missing-candidate drill.
    candidate_profile = recovery.Profile(OUT / 'missing-candidate-profile')
    candidate_profile.prepare(predecessor, candidate, str(source))
    candidate_profile.activate(); candidate_only.unlink()
    recovered_missing = candidate_profile.rollback()
    check('MissingCandidateResourceDoesNotBlockRollback', recovered_missing['status'] == 'Recovered')
    recovered = cli('rollback')
    restored_home = profile / recovered['stateHome']
    check('FailedHostNotContactedOrRestartedByRollback', recovered['status'] == 'Recovered'
          and len(events.read_text().splitlines()) == 1)
    check('AllCompatiblePreferenceBytesRestoredAtomically', all(
          (restored_home / 'warlock' / name).read_bytes() == body for name, body in baseline.items()))
    check('InvalidCandidateStatePreserved', broken.read_bytes() == broken_before)
    selection = (profile / 'selection.json').read_bytes()
    check('RepeatedRollbackDoesNotResetOrReplay', cli('rollback')['status'] == 'Unchanged'
          and (profile / 'selection.json').read_bytes() == selection
          and len(events.read_text().splitlines()) == 1)
    check('ActualPredecessorStartsWithoutCandidate', cli('run')['route'] == 'predecessor')
    restored = json.loads(events.read_text().splitlines()[-1])
    check('PredecessorReadsApprovedPreferences', restored['appearance'] == saved
          and restored['shortcuts'] == approved and restored['motion']['override'] == 'reduced'
          and restored['pins']['identities'] == ['warlock-editor', 'warlock-peer'])
    # Real managed child holds the profile lock, unlike a mocked host-liveness flag.
    hold = recovery.Profile(OUT / 'held-profile')
    hold.prepare(desc('hold'), desc('hold'), str(source)); hold.activate()
    held_log = (OUT / 'held-host.stdout').open('w')
    managed = subprocess.Popen([executable, '-B', tool, '--profile', str(hold.path), 'run'],
                               stdout=held_log, stderr=subprocess.STDOUT)
    try:
        deadline = time.monotonic() + 5
        while 'ready' not in (OUT / 'held-host.stdout').read_text():
            assert managed.poll() is None and time.monotonic() < deadline
            time.sleep(0.02)
        refuses('LiveManagedHostCannotRollback', hold.rollback)
        refuses('LiveManagedHostCannotActivate', hold.activate)
        refuses('SecondManagedHostCannotStart', hold.run)
        check('ReadOnlyStatusWorksWhileHostRuns', hold.status()['route'] == 'candidate')
    finally:
        managed.send_signal(signal.SIGTERM)
        managed.wait(timeout=8); held_log.close()
    check('OwnedManagedHostAndGroupRetired', managed.returncode == 130)
    check('RecoveryAfterOwnedHostStops', hold.rollback()['status'] == 'Recovered')
    lost = recovery.Profile(OUT / 'manager-loss-profile')
    lost.prepare(desc('hold'), desc('hold'), str(source)); lost.activate()
    lost_log = (OUT / 'lost-manager.stdout').open('w')
    manager = subprocess.Popen([executable, '-B', tool, '--profile', str(lost.path), 'run'],
        stdout=lost_log, stderr=subprocess.STDOUT)
    child_pid = None
    try:
        deadline = time.monotonic() + 5
        while 'ready' not in (OUT / 'lost-manager.stdout').read_text():
            assert manager.poll() is None and time.monotonic() < deadline
            time.sleep(0.02)
        child_pid = json.loads(events.read_text().splitlines()[-1])['pid']
        manager.kill(); manager.wait(timeout=5)
        check('ManagerLossLeavesActualChildAlive', Path('/proc', str(child_pid)).exists())
        refuses('LiveChildKeepsLockAfterManagerLoss', lost.rollback)
        refuses('ManagerLossCannotStartCompetingHost', lost.run)
    finally:
        if manager.poll() is None:
            manager.terminate(); manager.wait(timeout=8)
        if child_pid is not None and Path('/proc', str(child_pid)).exists():
            os.kill(child_pid, signal.SIGTERM)
        lost_log.close()
    deadline = time.monotonic() + 5
    while True:
        try:
            result = lost.rollback()
            break
        except recovery.Refused:
            assert time.monotonic() < deadline
            time.sleep(0.02)
    check('RollbackAfterActualOrphanHostExit', result['status'] == 'Recovered')
    # Fault injection checks the actual publication boundary, not a fake model file.
    fault = recovery.Profile(OUT / 'fault-profile')
    fault.prepare(predecessor, predecessor, str(source)); fault.activate()
    old_selection = (fault.path / 'selection.json').read_bytes()
    with patch('recovery_profile.os.rename', side_effect=OSError('before rename')):
        refuses('PreRenameFailureIsRefused', fault.rollback)
    check('PreRenameFailurePreservesCandidateSelection', (fault.path / 'selection.json').read_bytes() == old_selection)
    real_fsync = os.fsync
    root_inode = fault.path.stat().st_ino
    def sync_fault(fd):
        if stat.S_ISDIR(os.fstat(fd).st_mode) and os.fstat(fd).st_ino == root_inode:
            raise OSError('selection directory sync lost')
        return real_fsync(fd)
    unknown = False
    with patch('recovery_profile.os.fsync', side_effect=sync_fault):
        try:
            fault.rollback()
        except recovery.CommitUnknown:
            unknown = True
    check('PostRenameFailureIsUnknown', unknown)
    check('ReadReconcilesUnknownWithoutLaunching', fault.status()['route'] == 'predecessor')
    check('ReconciledRollbackDoesNotRepeat', fault.rollback()['status'] == 'Unchanged')
    damaged = recovery.Profile(OUT / 'damaged-prior-profile')
    damaged.prepare(predecessor, predecessor, str(source)); damaged.activate()
    prior_path = damaged.path / 'baseline/settings.json'
    prior_path.write_text('{}')
    before = (damaged.path / 'selection.json').read_bytes()
    refuses('ChangedBaselineCannotRecover', damaged.rollback)
    check('ChangedBaselineKeepsCandidateSelected', (damaged.path / 'selection.json').read_bytes() == before)
    symlink = OUT / 'linked-profile'; symlink.symlink_to(profile, target_is_directory=True)
    refuses('SymlinkProfileRefused', lambda: recovery.Profile(symlink).status())
    refuses('ExistingProfileCannotBeOverwritten', lambda: recovery.Profile(profile).prepare(predecessor, predecessor, str(source)))
    source_before = (source / 'warlock/settings.json').read_bytes()
    (source / 'warlock/settings.json').write_text('{"schema":999,"future":true}')
    refuses('UnknownSourceSchemaPreserved', lambda: recovery.Profile(OUT / 'future-profile').prepare(predecessor, predecessor, str(source)))
    check('UnknownSourceRemainsUntouched', (source / 'warlock/settings.json').read_text() == '{"schema":999,"future":true}'
          and not (OUT / 'future-profile').exists())
    (source / 'warlock/settings.json').write_bytes(source_before)
    report.update(scope='Production offline profile/CLI and real managed local child processes; no native GUI predecessor or independent release qualification.',
                  checks=checks, modelNamedTests=10,
                  sourceHashes={str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in [ROOT / 'adapter/recovery_profile.py', spec, tests]},
                  missingObservations=['Actual predecessor shell pixels/input and surviving application drafts on the exact native tuple.',
                    'Full reproducible release package/dependency inventory and main-session deployment/rollback drill.',
                    'Independent original-scenario review.'])
(OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'passed': True, 'report': str(OUT / 'report.json')}))
