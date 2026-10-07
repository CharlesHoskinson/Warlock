"""Exercise shipped hook commands without installing a client or touching its config."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PLUGIN = Path(__file__).resolve().parents[1]
ENV = {key: value for key, value in os.environ.items()
       if not key.startswith(('GIT_', 'GROK_', 'CLAUDE_', 'PLUGIN_'))}
ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1')


class HostCommandTests(unittest.TestCase):
    def commands(self):
        for name in ('hooks/hooks.json', 'hooks/codex.json'):
            data = json.loads((PLUGIN / name).read_text())
            for event, entries in data['hooks'].items():
                for entry in entries:
                    for hook in entry['hooks']:
                        yield event, hook['command']

    def test_missing_or_pruned_plugin_never_blocks_prompt(self):
        for event, command in self.commands():
            for root in ('', '/nonexistent/warlock-plugin-cache'):
                with self.subTest(event=event, root=root, command=command):
                    env = dict(ENV, CLAUDE_PLUGIN_ROOT=root, PLUGIN_ROOT=root)
                    proc = subprocess.run(['/bin/sh', '-c', command], env=env,
                                          input=json.dumps({'hook_event_name': event}),
                                          capture_output=True, text=True, timeout=10)
                    self.assertEqual(proc.returncode, 0)
                    self.assertEqual(proc.stdout, '')

    def test_local_plugin_with_spaces_and_unrelated_project_is_silent(self):
        with tempfile.TemporaryDirectory(prefix='warlock plugin with spaces ') as folder:
            link = Path(folder) / 'plugin'
            link.symlink_to(PLUGIN, target_is_directory=True)
            for event, command in self.commands():
                with self.subTest(event=event, command=command):
                    env = dict(ENV, CLAUDE_PLUGIN_ROOT=str(link), PLUGIN_ROOT=str(link))
                    proc = subprocess.run(['/bin/sh', '-c', command], env=env,
                                          input=json.dumps({'hook_event_name': event, 'cwd': folder}),
                                          capture_output=True, text=True, timeout=10)
                    self.assertEqual(proc.returncode, 0, proc.stderr)
                    self.assertEqual(proc.stdout, '')

    def test_malformed_payload_and_stop_cannot_deny(self):
        for payload in ('{broken', 'null', json.dumps({'hook_event_name': 'Stop', 'cwd': '/tmp'})):
            proc = subprocess.run([sys.executable, '-B', str(PLUGIN / 'scripts/session_hook.py')],
                                  env=ENV, input=payload, capture_output=True, text=True, timeout=10)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(proc.stdout, '')

    def test_passive_grok_hook_does_not_run_checker(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in ('docs/warlock-build-loop/v2/STATE.json', 'docs/elm-roadmap/requirements.json'):
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text('{}')
            proc = subprocess.run([sys.executable, '-B', str(PLUGIN / 'scripts/session_hook.py')],
                                  env=dict(ENV, GROK_HOOK_EVENT='SessionStart'),
                                  input=json.dumps({'hookEventName': 'SessionStart', 'workspaceRoot': folder}),
                                  capture_output=True, text=True, timeout=10)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(proc.stdout, '')


if __name__ == '__main__':
    unittest.main()
