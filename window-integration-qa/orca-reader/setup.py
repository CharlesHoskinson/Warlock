#!/usr/bin/env python3
"""Extract signed official Arch packages locally; never calls pacman install or sudo."""
import hashlib
import json
import pathlib
import subprocess
import urllib.request

root = pathlib.Path(__file__).resolve().parent
packages = root / 'packages'
prefix = root / 'prefix'
packages.mkdir(exist_ok=True)
prefix.mkdir(exist_ok=True)
keys = root / 'archlinux-keys.gpg'
if not keys.exists():
    subprocess.run(['gpg', '--batch', '--dearmor', '--output', str(keys),
        '/usr/share/pacman/keyrings/archlinux.gpg'], check=True)
for package in json.loads((root / 'packages.json').read_text()):
    filename = package['url'].rsplit('/', 1)[1]
    target = packages / filename
    signature = pathlib.Path(str(target) + '.sig')
    if not target.exists():
        urllib.request.urlretrieve(package['url'], target)
    if not signature.exists():
        urllib.request.urlretrieve(package['url'] + '.sig', signature)
    assert hashlib.sha256(target.read_bytes()).hexdigest() == package['sha256'], filename
    subprocess.run(['gpgv', '--keyring', str(keys), str(signature), str(target)], check=True)
    subprocess.run(['bsdtar', '-xf', str(target), '-C', str(prefix)], check=True)
subprocess.run(['glib-compile-schemas', str(prefix / 'usr/share/glib-2.0/schemas')], check=True)
subprocess.run([str(root / 'run-orca'), '--help'], check=True)
