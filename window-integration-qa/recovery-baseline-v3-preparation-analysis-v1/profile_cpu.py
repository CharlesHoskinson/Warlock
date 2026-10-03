"""Actual frozen V19 CPU job phases; no compositor, client or GUI connection."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time

SOURCE = Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-family-query-v19')
sys.path.insert(0, str(SOURCE))
from helper_supervisor import Keeper
from owned_commands import OwnedCommands
from service_runtime import RuntimeLease, JournalStore


class ProfiledKeeper(Keeper):
    def __init__(self, *args, **kwargs):
        self.phases = []
        super().__init__(*args, **kwargs)

    def phase(self, name, function, *args, **kwargs):
        begin = time.monotonic_ns()
        try:
            return function(*args, **kwargs)
        finally:
            self.phases.append({'phase': name, 'beginNs': begin,
                                'endNs': time.monotonic_ns()})

    def register(self, *args, **kwargs):
        return self.phase('register', super().register, *args, **kwargs)

    def released(self, *args, **kwargs):
        return self.phase('released', super().released, *args, **kwargs)

    def complete(self, *args, **kwargs):
        return self.phase('complete', super().complete, *args, **kwargs)


def main():
    original_affinity = sorted(os.sched_getaffinity(0))
    os.sched_setaffinity(0, {original_affinity[0]})
    with tempfile.TemporaryDirectory(prefix='v19-cpu-profile-') as raw:
        root = Path(raw)
        env = dict(os.environ, XDG_RUNTIME_DIR=raw,
                   HYPRLAND_INSTANCE_SIGNATURE='cpu-profile-no-compositor',
                   WAYLAND_DISPLAY='never-connect')
        lease = RuntimeLease(root, env['HYPRLAND_INSTANCE_SIGNATURE'])
        store = JournalStore(root, lease.session)
        serial = 0
        def persist(ownership):
            nonlocal serial
            lease.verify()
            serial += 1
            store.write({'version': 1, 'session': lease.session,
                         'snapshot': serial, 'scenes': [], 'pending': [],
                         'helperOwnership': deepcopy(ownership)})
        keeper = ProfiledKeeper(root, env, persist)
        rows = []
        try:
            commands = OwnedCommands(keeper, env, actor=1)
            for _ in range(24):
                start = time.monotonic_ns()
                offset = len(keeper.phases)
                result = commands.run(['/usr/bin/cat'], input='CPU query\n',
                                      text=True, capture_output=True,
                                      check=True, timeout=2)
                end = time.monotonic_ns()
                assert result.stdout == 'CPU query\n'
                rows.append({'beginNs': start, 'endNs': end,
                             'elapsedMs': (end-start)/1e6,
                             'keeperPhases': keeper.phases[offset:]})
            keeper.stop()
            terminal = keeper.read_terminal()
            assert terminal['normalStop'] is True
            assert len(terminal['jobs']) == len(rows)
            assert all(j['normalCompletion'] and j['groupEmpty']
                       for j in terminal['jobs'])
            result = {'cpuOnly': True, 'nativeLaunch': False,
                      'nativeLatencyCauseClaimed': False,
                      'singleCpuAffinity': original_affinity[0],
                      'nativeCgroupQuotaReproduced': False,
                      'sourceManifestSHA256': hashlib.sha256(
                          (SOURCE/'manifest-family-query-v19.json').read_bytes()).hexdigest(),
                      'runtimeSources': {n: hashlib.sha256((SOURCE/n).read_bytes()).hexdigest()
                                         for n in ['helper_supervisor.py', 'helper_keeper.py',
                                                   'owned_launch.py', 'owned_commands.py',
                                                   'service_runtime.py']},
                      'count': len(rows), 'rows': rows,
                      'sumMs': sum(r['elapsedMs'] for r in rows),
                      'meanMs': sum(r['elapsedMs'] for r in rows)/len(rows),
                      'journalPublications': serial,
                      'normalKeeperStop': terminal['normalStop']}
            Path(__file__).with_name('cpu-profile-result.json').write_text(
                json.dumps(result, indent=2)+'\n')
            print(json.dumps({k: result[k] for k in ['count', 'sumMs', 'meanMs',
                                                   'journalPublications', 'normalKeeperStop']}))
        finally:
            if not keeper.closed:
                keeper.detach()
                keeper.process.wait(timeout=5)
                keeper.process.stderr.close()
            lease.close()


if __name__ == '__main__':
    main()
