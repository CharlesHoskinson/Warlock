#!/usr/bin/env python3
"""Private-network compiled Elm browser component check; root CPU runner only."""
import hashlib
import http.server
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import threading

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'window-integration-qa'))
from qa_launch import require_qa_scope

BROWSER = Path('/home/charl/.cache/ms-playwright/chromium-1248/chrome-linux64/chrome')
BROWSER_SHA256 = '377a9fc07b495c3b8d0ab8ec1fdfd153641759f9756fea34d8dfce4de82f5025'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    scope = require_qa_scope()
    output = Path(sys.argv[1]).resolve(strict=True)
    if output.parent != REPO / '.warlock-contributor' or not output.name.startswith('elm-cpu-'):
        raise RuntimeError('Expected root-owned compiled component output')
    parent_network = os.environ.get('WARLOCK_CPU_PARENT_NETNS')
    if not parent_network or os.readlink('/proc/self/ns/net') == parent_network:
        raise RuntimeError('Browser requires a network namespace distinct from its root runner')
    # bwrap exposes only the namespace loopback interface and hides host sockets.
    if [name for _, name in socket.if_nameindex()] != ['lo']:
        raise RuntimeError('Browser requires private loopback-only network namespace')
    if (Path('/run/user') / str(os.getuid()) / 'bus').exists() or os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY'):
        raise RuntimeError('Browser must not inherit host desktop access')
    if BROWSER.is_symlink() or sha(BROWSER) != BROWSER_SHA256:
        raise RuntimeError('Browser binary differs from reviewed local pin')
    root = REPO / 'implementation/warlock'
    serving = output / 'browser-site'
    assets = serving / 'assets'
    qa = serving / 'qa'
    assets.mkdir(parents=True)
    qa.mkdir()
    for name in ['Bar', 'Popup']:
        shutil.copy2(output / (name + '.js'), assets / (name.lower() + '.js'))
        (qa / ('feedback-context-' + name.lower() + '.html')).write_text(
            '<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="../assets/shell.css"></head>'
            '<body class="' + name.lower() + '"><div id="app"></div><script src="../assets/' + name.lower() + '.js"></script>'
            '<script>window.actions=[];window.testApp=Elm.' + name + '.init({node:document.getElementById("app")});'
            'testApp.ports.actions.subscribe(v=>actions.push(v));</script></body></html>')
    shutil.copy2(root / 'assets/shell.css', assets / 'shell.css')

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(serving), **kwargs)

        def log_message(self, *args):
            pass

    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    report = {'schema': 1, 'scope': 'isolated-network compiled Elm browser component', 'passed': False,
              'nativeAcceptance': False, 'releaseAccepted': False, 'protectedScope': scope,
              'browserSHA256': BROWSER_SHA256, 'networkNamespace': os.readlink('/proc/self/ns/net')}
    try:
        command = ['node', str(root / 'qa/feedback-context-browser.mjs'),
                   'http://127.0.0.1:' + str(server.server_port), str(output), str(BROWSER), str(output / 'feedback-context.json')]
        result = subprocess.run(command, capture_output=True, text=True, timeout=100)
        (output / 'browser-harness.stdout').write_text(result.stdout)
        (output / 'browser-harness.stderr').write_text(result.stderr)
        report['harnessExit'] = result.returncode
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        report['passed'] = sha(BROWSER) == BROWSER_SHA256
    except Exception as error:
        report['error'] = str(error)
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)
        (output / 'browser-protection.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report))
        shutil.rmtree(serving)
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
