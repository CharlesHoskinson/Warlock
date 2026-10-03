"""Frozen production taskbar packaging; imports never contact a desktop.

The production widget has an absolute accessibility import. Its copied bytes
stay unchanged; the actual original import is separately frozen and its native
mapping must be checked at runtime. No writable user catalogs are linked.
"""
from pathlib import Path
import hashlib
import json
import os
import shutil
import stat
import sys

QA = Path('/home/hoskinson/window-integration-qa')
sys.path.insert(0, str(QA))
from qa_launch import require_qa_scope, verify_runtime, verify_parent

B = Path(__file__).resolve().parent
OWNER = Path('/home/hoskinson')
SHELL = Path('/usr/share/omarchy/shell')
PLUGIN = OWNER / '.config/omarchy/plugins/hoskinson.windows'
ACCESSIBILITY = OWNER / '.local/share/hypr-window-controls/qml/WindowAccessibilityV4'
HELPERS = ('hypr-taskbar', 'hypr-desktop', 'hypr-windowctl',
           'hypr-windowctl-core', 'hypr-window-motion', 'hypr-window-preview',
           'hypr-window-family', 'hypr-snap-groups', 'hypr-window-menu')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def regular(path):
    info = Path(path).lstat()
    if not stat.S_ISREG(info.st_mode):
        raise ValueError('Explicit regular source required: ' + str(path))
    return info


def shell_config(manifests):
    ids = sorted({m['id'] for m in manifests})
    if 'omarchy.bar' not in ids:
        raise ValueError('Production bar manifest missing')
    return {'version': 1, 'idle': {'screensaver': 0, 'lock': 0},
            'bar': {'id': 'omarchy.bar', 'position': 'top',
                    'transparent': False, 'layout': {
                        'left': [{'id': 'hoskinson.windows'}],
                        'center': [], 'right': []}},
            'plugins': [],
            # First-party infrastructure is enabled implicitly. Disable every
            # unrelated manifest, including lock/polkit/idle/background/media.
            'disabledPlugins': [i for i in ids if i != 'omarchy.bar']}


def build_payload():
    target = B / 'payload'
    target.mkdir(mode=0o700)  # Fresh packet only; never update retained payload.
    rows = []

    def copy(source, relative):
        info = regular(source)
        data = Path(source).read_bytes()
        before = sha(source)
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with destination.open('xb') as stream:
            stream.write(data)
        destination.chmod(0o700 if info.st_mode & 0o111 else 0o600)
        if sha(source) != before or sha(destination) != before:
            raise ValueError('Source changed during copy: ' + str(source))
        rows.append({'source': str(source), 'relative': str(relative),
                     'sha256': before, 'executable': bool(info.st_mode & 0o111)})

    manifests = []
    for source in sorted(SHELL.rglob('*')):
        if source.is_symlink():
            raise ValueError('Unexpected packaged shell link: ' + str(source))
        if source.is_file():
            copy(source, Path('omarchy/shell') / source.relative_to(SHELL))
            if source.name == 'manifest.json' or source.name.endswith('.manifest.json'):
                manifests.append(json.loads(source.read_text()))
    launcher_link = Path('/usr/share/omarchy/bin/omarchy-shell')
    if not launcher_link.is_symlink() or os.readlink(launcher_link) != '/usr/bin/omarchy-shell':
        raise ValueError('Packaged launcher link differs from reviewed source')
    copy(Path('/usr/bin/omarchy-shell'), Path('omarchy/bin/omarchy-shell'))
    copy(PLUGIN / 'manifest.json', Path('home/.config/omarchy/plugins/hoskinson.windows/manifest.json'))
    for source in sorted((PLUGIN / 'widget_v65').iterdir()):
        copy(source, Path('home/.config/omarchy/plugins/hoskinson.windows/widget_v65') / source.name)
    for name in HELPERS:
        copy(OWNER / '.local/bin' / name, Path('home/.local/bin') / name)
    copy(OWNER / '.local/share/hypr-window-controls/window_state.py',
         Path('home/.local/share/hypr-window-controls/window_state.py'))
    for source in sorted(ACCESSIBILITY.iterdir()):
        copy(source, Path('retained-accessibility') / source.name)
    # Theme files are resolved snapshots, not links into the original home.
    theme = OWNER / '.local/state/omarchy/current/theme'
    for name in ('colors.toml', 'shell.toml'):
        source = theme / name
        if source.exists():
            copy(source.resolve(), Path('home/.local/state/omarchy/current/theme') / name)
    config = shell_config(manifests)
    generated = {}

    def generate(relative, value):
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        data = (json.dumps(value, indent=2) + '\n').encode()
        with path.open('xb') as stream:
            stream.write(data)
        path.chmod(0o600)
        generated[str(relative)] = sha(path)

    generate(Path('omarchy/config/omarchy/shell.json'), config)
    generate(Path('home/.config/omarchy/shell.json'), config)
    generate(Path('home/.config/omarchy/taskbar-pins.json'), [])
    generate(Path('home/.config/omarchy/taskbar-settings.json'),
             {'combineMode': 'always', 'desktopScope': 'all', 'displayMode': 'all'})
    descriptor = {'copies': rows, 'generated': generated,
                  'externalSymlinks': {str(launcher_link): '/usr/bin/omarchy-shell'},
                  'absoluteAccessibilityImports': {
                      str(p): sha(p) for p in ACCESSIBILITY.iterdir()},
                  'config': config, 'nativeLaunch': False,
                  'mainFilesWritten': False, 'widgetModified': False}
    with (B / 'payload-manifest.json').open('x') as stream:
        json.dump(descriptor, stream, indent=2); stream.write('\n')
    return descriptor


def verify_payload():
    descriptor = json.loads((B / 'payload-manifest.json').read_text())
    for row in descriptor['copies']:
        source = Path(row['source']); target = B / 'payload' / row['relative']
        regular(source); regular(target)
        if sha(source) != row['sha256'] or sha(target) != row['sha256']:
            raise ValueError('Frozen production shell input changed: ' + str(source))
    for name, digest in descriptor['generated'].items():
        path = B / 'payload' / name
        regular(path)
        if sha(path) != digest:
            raise ValueError('Frozen private config changed: ' + str(path))
    for name, target in descriptor['externalSymlinks'].items():
        if not Path(name).is_symlink() or os.readlink(name) != target:
            raise ValueError('Frozen packaged launcher link changed: ' + name)
    for name, digest in descriptor['absoluteAccessibilityImports'].items():
        regular(name)
        if sha(name) != digest:
            raise ValueError('Actual absolute accessibility import changed: ' + name)
    return descriptor


def prepare_home(private_env, compositor_pid=None, compositor_start=None):
    """Only an already live selected QA compositor may materialize a home."""
    require_qa_scope()
    runtime = verify_runtime(private_env['XDG_RUNTIME_DIR'])
    parent = verify_parent(private_env)
    if not Path(parent['path']).parent.samefile(runtime):
        raise ValueError('Shell display must be inside the selected private runtime')
    if parent['pid'] != compositor_pid or compositor_start is None:
        raise ValueError('Shell display peer must be the selected compositor')
    process = Path('/proc') / str(compositor_pid)
    if process.stat().st_uid != os.getuid() or process.joinpath('stat').read_text().rsplit(')', 1)[1].split()[19] != str(compositor_start):
        raise ValueError('Selected compositor PID/start changed before shell home copy')
    if not private_env.get('HYPRLAND_INSTANCE_SIGNATURE') or not private_env.get('DBUS_SESSION_BUS_ADDRESS', '').startswith('unix:path=' + str(runtime) + '/'):
        raise ValueError('Explicit private compositor and bus required')
    verify_payload()
    home = runtime / 'taskbar-home'
    shutil.copytree(B / 'payload/home', home)
    for name in ('cache', 'data', 'config', 'state'):
        (home / ('xdg-' + name)).mkdir(mode=0o700)
    # The production shell and helpers intentionally use HOME-relative paths;
    # keep XDG locations aligned rather than inventing a second config scheme.
    env = {k: v for k, v in private_env.items()
           if not k.startswith('HYPR_WINDOWCTL_') and k not in
           ('DISPLAY', 'XAUTHORITY', 'WAYLAND_SOCKET', 'QT_QPA_PLATFORMTHEME',
            'QS_CONFIG_PATH', 'QS_CONFIG_NAME', 'QS_MANIFEST')}
    env.update(HOME=str(home), OMARCHY_PATH=str(B / 'payload/omarchy'),
               XDG_CONFIG_HOME=str(home / '.config'),
               XDG_DATA_HOME=str(home / '.local/share'),
               XDG_STATE_HOME=str(home / '.local/state'),
               XDG_CACHE_HOME=str(home / 'xdg-cache'),
               PATH=str(home / '.local/bin') + ':' + str(B / 'payload/omarchy/bin') + ':/usr/bin',
               QT_QPA_PLATFORM='wayland', GSETTINGS_BACKEND='memory',
               GDK_DEBUG='no-portals', GIO_USE_VFS='local',
               PYTHONDONTWRITEBYTECODE='1')
    return env


if __name__ == '__main__':
    result = build_payload() if sys.argv[1:] == ['--build'] else verify_payload()
    print(json.dumps({'productionCopies': len(result['copies']),
                      'privateGeneratedConfigs': len(result['generated']),
                      'nativeLaunch': False, 'widgetModified': False}))
