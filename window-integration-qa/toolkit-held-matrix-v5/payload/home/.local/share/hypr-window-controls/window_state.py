"""Window desktop ownership shared by the taskbar and Alt+Tab."""
import json
import os
from pathlib import Path
import re
import subprocess


def enrich_families(windows):
    """Merge one native snapshot only when address, PID and stable identity agree."""
    try:
        native = json.loads(subprocess.check_output(['hyprctl', 'repl', 'print(hl.plugin.hyprbars.window_families())'], text=True, stderr=subprocess.DEVNULL, timeout=3))
        records = {w['address']: w for w in native if isinstance(w, dict)}
    except (OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError):
        return windows
    for window in windows:
        record = records.get(window.get('address'))
        if record and record.get('pid') == window.get('pid') and record.get('stableId') == window.get('stableId'):
            window.update({k: record.get(k) for k in ['parent', 'parentStableId', 'modal']})
    return windows


def family_root(window, windows):
    lookup = {w.get('address'): w for w in windows}
    visited = set()
    while window.get('address') not in visited:
        visited.add(window.get('address'))
        parent = lookup.get(window.get('parent'))
        if not parent or not window.get('parentStableId') or window['parentStableId'] != parent.get('stableId'):
            break
        window = parent
    return window


def family_members(window, windows):
    root = family_root(window, windows)
    members = [w for w in windows if w.get('mapped', True) and family_root(w, windows).get('address') == root.get('address')]
    return sorted(members, key=lambda w: (w.get('address') != root.get('address'), w.get('focusHistoryID', 999)))


def family_focus(window, windows):
    """Follow modal descendants; independent transient windows keep their focus."""
    visited = set()
    while window.get('address') not in visited:
        visited.add(window.get('address'))
        children = [w for w in windows if w.get('mapped', True) and w.get('modal') and w.get('parent') == window.get('address') and w.get('parentStableId') == window.get('stableId')]
        if not children: break
        window = min(children, key=lambda w: w.get('focusHistoryID', 999))
    return window


def saved_window_state(window, runtime=None):
    runtime = Path(runtime or os.getenv('XDG_RUNTIME_DIR', Path.home() / '.cache'))
    address = str(window.get('address', ''))
    if not re.fullmatch(r'0x[0-9a-fA-F]+', address):
        return None
    try:
        fields = (runtime / 'hypr-windowctl' / address).read_text().split()
        if len(fields) < 2 or not fields[0].isdigit():
            return None
        if len(fields) > 2 and fields[2] != str(window.get('stableId', '')):
            return None
        return fields[0], fields[1] == '1'
    except OSError:
        return None


def desktop_owner(window, runtime=None):
    workspace = str(window.get('workspace', {}).get('name', ''))
    if workspace == 'special:win-minimized':
        saved = saved_window_state(window, runtime)
        return saved if saved else ('', False)
    return (workspace, bool(window.get('pinned'))) if workspace.isdigit() else ('', False)


def monitor_owner(window, monitors, workspaces, runtime=None):
    """Hidden workspace placement is storage, not a window's display owner."""
    if window.get('workspace', {}).get('name') != 'special:win-minimized':
        return window.get('monitor', -1)
    home, _ = desktop_owner(window, runtime)
    monitor_ids = {m.get('id') for m in monitors}
    for workspace in workspaces:
        if str(workspace.get('name')) == home and workspace.get('monitorID') in monitor_ids:
            return workspace['monitorID']
    runtime = Path(runtime or os.getenv('XDG_RUNTIME_DIR', Path.home() / '.cache'))
    address = str(window.get('address', ''))
    if home and re.fullmatch(r'0x[0-9a-fA-F]+', address):
        try:
            saved = json.loads((runtime / 'hypr-windowctl' / (address + '.monitor.json')).read_text())
            if (saved.get('homeWorkspace') == home and saved.get('pid') == window.get('pid')
                    and saved.get('stableId') == window.get('stableId')):
                for monitor in monitors:
                    if monitor.get('name') == saved.get('monitorName'):
                        return monitor['id']
        except (OSError, ValueError, AttributeError):
            pass
    # Legacy state or a disconnected output falls back to the compositor's
    # current placement, then the focused display if no placement survives.
    if window.get('monitor') in monitor_ids:
        return window['monitor']
    return next((m['id'] for m in monitors if m.get('focused')), monitors[0]['id'] if monitors else -1)


def scope_settings(path=None):
    path = Path(path or Path.home() / '.config/omarchy/taskbar-settings.json')
    try:
        data = json.loads(path.read_text())
        return data if isinstance(data, dict) else {}
    except (ValueError, OSError):
        return {}


def switcher_candidates(windows, workspace, scope='current', runtime=None):
    windows = enrich_families(windows)
    candidates = []
    for window in sorted(windows, key=lambda w: w.get('focusHistoryID', 999)):
        if family_focus(window, windows).get('address') != window.get('address'):
            continue
        owner, pinned = desktop_owner(window, runtime)
        if window.get('mapped', True) and owner and (scope == 'all' or owner == str(workspace) or pinned):
            candidates.append({'address': window['address'], 'title': window.get('title', ''),
                               'class': window.get('class', ''), 'homeWorkspace': owner,
                               'pid':window.get('pid'), 'stableId':window.get('stableId','')})
    return candidates
