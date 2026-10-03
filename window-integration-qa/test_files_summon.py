#!/usr/bin/env python3
"""Run the installed Files launcher with isolated command endpoints.

Checks backend ordering, identity forwarding, minimized retargeting, rejection
propagation, and preservation of unrelated special views. No real app is opened.
"""
import json
import os
from pathlib import Path
import subprocess
import tempfile

LAUNCHER = Path.home() / '.local/bin/omarchy-files'
SHIM = '''#!/usr/bin/env python3
import json,os,sys
from pathlib import Path
name=Path(sys.argv[0]).name;args=sys.argv[1:]
state=json.loads(Path(os.environ['FILES_SUMMON_CASE']).read_text())
with Path(os.environ['FILES_SUMMON_LOG']).open('a') as stream:
 stream.write(json.dumps([name,*args])+'\\n')
if name=='qs':sys.exit(0)
if name=='pgrep':print(123);sys.exit(0)
if name=='hyprctl':
 if args==['-j','clients']:
  print(json.dumps([dict(address='0xaaa',pid=123,title='Files',stableId=state.get('identity','abc'),workspace=dict(name=state['workspace']))]))
 elif args==['-j','monitors']:
  print(json.dumps([dict(focused=True,activeWorkspace=dict(name=state.get('current','1')),specialWorkspace=dict(name='special:unrelated'))]))
 else:sys.exit(91)
 sys.exit(0)
if name in ('hypr-desktops','hypr-windowctl'):
 assert args[-2:]==['abc','123'],args
 sys.exit(state.get('failMove',0) if name=='hypr-desktops' else state.get('failRestore',0))
sys.exit(92)
'''


def case(root, name, workspace, expected, status=0, **options):
    state = root / 'case.json'
    log = root / 'calls.jsonl'
    state.write_text(json.dumps(dict(workspace=workspace, **options)))
    log.write_text('')
    env = dict(os.environ, PATH=str(root / 'bin') + ':' + os.environ['PATH'],
               FILES_SUMMON_CASE=str(state), FILES_SUMMON_LOG=str(log))
    result = subprocess.run(['bash', str(LAUNCHER), 'home'], env=env,
                            text=True, capture_output=True, timeout=6)
    calls = [json.loads(line) for line in log.read_text().splitlines()]
    actions = [call for call in calls if call[0] in ('hypr-desktops', 'hypr-windowctl')]
    assert result.returncode == status, (name, result.returncode, result.stderr)
    assert actions == expected, (name, actions, expected)
    assert not any(call[0] == 'hyprctl' and 'dispatch' in call for call in calls), name


def main():
    restore = ['hypr-windowctl', 'restore', '0xaaa', 'abc', '123']
    move = ['hypr-desktops', 'move', '0xaaa', '1', 'abc', '123']
    with tempfile.TemporaryDirectory(prefix='files-summon-qa-') as directory:
        root = Path(directory)
        (root / 'bin').mkdir()
        shim = root / 'shim'
        shim.write_text(SHIM)
        shim.chmod(0o755)
        for name in ('qs', 'pgrep', 'hyprctl', 'hypr-windowctl', 'hypr-desktops'):
            (root / 'bin' / name).symlink_to(shim)
        case(root, 'visible here', '1', [restore])
        case(root, 'visible elsewhere', '2', [move, restore])
        case(root, 'minimized retarget', 'special:win-minimized', [move, restore])
        case(root, 'legacy recovery', 'special:scratchpad', [restore, move, restore])
        case(root, 'retarget rejects changed identity', 'special:win-minimized', [move], 3, failMove=3)
        case(root, 'restore rejection propagated', '1', [restore], 3, failRestore=3)
        case(root, 'missing stable identity', '1', [], 1, identity='')
        case(root, 'invalid destination', '1', [], 1, current='special:unrelated')
    print('Installed Files launcher: 8 backend/identity/special-view checks PASS')


if __name__ == '__main__': main()
