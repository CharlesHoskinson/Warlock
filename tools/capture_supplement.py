#!/usr/bin/python3
"""Preserve additional work discovered outside the initial source roots."""
import json
from pathlib import Path
import capture_snapshot

REPO = capture_snapshot.REPO
HOME_ROOT = capture_snapshot.HOME_ROOT

def main():
    entries = []
    relatives = [
        '.local/bin/brave-browser', '.local/lib/brave-launcher',
        '.local/share/applications/brave-browser.desktop',
        '.local/share/applications/omarchy-files.desktop',
        '.local/bin/sudo-askpass', '.local/bin/sudo-askpass.pinentry',
        '.config/omarchy/extensions',
        '.config/omarchy/shell.json.bak.window-controls-20260930',
        '.config/omarchy/taskbar-session-order.json',
        '.config/omarchy/virtual-desktops.json',
        '.config/systemd/user/default.target.wants/omarchy-taskbar-attention.service',
        '.config/systemd/user/default.target.wants/omarchy-taskbar-launcher.service',
    ]
    for relative in relatives:
        source = HOME_ROOT / relative
        if source.exists() or source.is_symlink():
            entries.append((source, REPO / 'installed/home' / relative))
    for source in sorted((HOME_ROOT / '.cache').iterdir()):
        if source.name.startswith(('window-', 'taskbar-', 'hyprbars-', 'omarchy-files-mbt', 'omarchy-files-elevtest')):
            entries.append((source, REPO / 'evidence/home/.cache' / source.name))
    system_sources = [Path('/usr/bin/quickshell'), Path('/usr/lib/libQt6Quick.so.6')]
    qt = Path('/usr/lib/libQt6Quick.so.6')
    if qt.exists():
        system_sources.append(qt.resolve())
    for source in system_sources:
        if source.exists() or source.is_symlink():
            entries.append((source, REPO / 'installed/system' / str(source).lstrip('/')))
    for _, destination in entries:
        assert not destination.exists() and not destination.is_symlink(), f'Already captured: {destination}'
    capture_snapshot.main(entries=entries, provenance_directory=REPO / 'provenance/supplement-v1')
    print(json.dumps({'supplement': 'supplement-v1', 'additionalRoots': len(entries)}))

if __name__ == '__main__':
    main()
