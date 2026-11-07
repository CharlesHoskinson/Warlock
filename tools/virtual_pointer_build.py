#!/usr/bin/env python3
"""Fixed ARM QA virtual-pointer generation/build; never connects to Wayland."""
import json
import os
from pathlib import Path
import re
import shlex
import stat
import xml.etree.ElementTree as ET

from arm64_toolchain import digest
from provider_callback_build import pin_image

BASE = 'implementation/warlock/qa/native-runtime-helpers/'
SOURCE_PINS = {'implementation/warlock/qa/native-runtime-helpers/virtual_pointer.c': '6486e89894eaabae30ef50dab4b591a4e98ad6656c10a15bb8ab8e8a8fcf5d95', 'implementation/warlock/qa/native-runtime-helpers/wlr-virtual-pointer-unstable-v1.xml': '3ff6d540be0bc5228195bf072bde42117ea17945a5c2061add5d3cf97d6bb524', 'implementation/warlock/qa/native-runtime-helpers/LICENSE.wlr-virtual-pointer.txt': 'de371ae38be7b1e9e4d339d13f85dfc448f279cbe3a75640e91bedd5bf7a9557', 'implementation/warlock/qa/native-runtime-helpers/virtual-pointer-protocol-provenance.json': '3d8a27c0cb4075a0288fb8f6ad5a51d61c957ecf7d9947f1f8591b9c2c1f2316'}
SYSTEM_SHA256 = '33b9ed73bd1d249225d228a35c8f40ae941f690bca8f3626fb2e6f5e267ac7b4'
LOADERS = {'/lib/ld-linux-aarch64.so.1', '/usr/lib/ld-linux-aarch64.so.1'}


def plain_file(root, name):
    file = root / name
    if file.resolve() != file or not file.is_file() or file.is_symlink():
        raise RuntimeError('Pointer source not a canonical regular file: ' + str(file))
    return file


def validate_sources(root):
    root = Path(root)
    expected_names = {BASE + name for name in ('virtual_pointer.c', 'wlr-virtual-pointer-unstable-v1.xml',
                                              'LICENSE.wlr-virtual-pointer.txt',
                                              'virtual-pointer-protocol-provenance.json')}
    if set(SOURCE_PINS) != expected_names:
        raise RuntimeError('Pointer fixed source bindings incomplete')
    for name, expected in SOURCE_PINS.items():
        if digest(plain_file(root, name)) != expected:
            raise RuntimeError('Pointer source drift: ' + name)
    document = ET.parse(root / (BASE + 'wlr-virtual-pointer-unstable-v1.xml')).getroot()
    interfaces = {row.attrib['name']: row.attrib.get('version') for row in document.findall('interface')}
    if (document.tag != 'protocol' or document.attrib.get('name') != 'wlr_virtual_pointer_unstable_v1'
            or interfaces != {'zwlr_virtual_pointer_v1': '2', 'zwlr_virtual_pointer_manager_v1': '2'}
            or document.find('copyright') is None):
        raise RuntimeError('Pointer protocol or copyright differs')


def command_plan(root, output):
    root, output = Path(root), Path(output)
    source = root / BASE
    generated = output / 'pointer-generated'
    xml = source / 'wlr-virtual-pointer-unstable-v1.xml'
    return [('pointer-header', ['/usr/bin/wayland-scanner', 'client-header', str(xml),
                               str(generated / 'virtual-pointer-client.h')]),
            ('pointer-code', ['/usr/bin/wayland-scanner', 'private-code', str(xml),
                             str(generated / 'virtual-pointer-client.c')]),
            ('pointer-object', ['/usr/bin/cc', '-O2', '-Wall', '-Wextra', '-I' + str(generated),
                                '-MD', '-MF', str(output / 'pointer.d'), '-c', str(source / 'virtual_pointer.c'),
                                '-o', str(output / 'pointer.o')]),
            ('pointer-protocol-object', ['/usr/bin/cc', '-O2', '-Wall', '-Wextra', '-I' + str(generated),
                                         '-MD', '-MF', str(output / 'protocol.d'), '-c',
                                         str(generated / 'virtual-pointer-client.c'), '-o', str(output / 'protocol.o')]),
            ('pointer-link', ['/usr/bin/cc', str(output / 'pointer.o'), str(output / 'protocol.o'),
                              '-o', str(output / 'dist/virtual-pointer'), '-lwayland-client', '-lm'])]


def dependency_names(text):
    if ':' not in text or len(text) > 1048576:
        raise RuntimeError('Invalid pointer dependency receipt')
    return shlex.split(text.replace('\\\n', ' ').split(':', 1)[1])


def parse_elf(text):
    if (len(text) > 1048576 or not re.search(r'Class:\s+ELF64\b', text)
            or not re.search(r'Data:.*little endian', text)
            or not re.search(r'Machine:\s+AArch64\b', text)):
        raise RuntimeError('Pointer closure has foreign or malformed ELF metadata')
    if re.search(r'\((?:RPATH|RUNPATH|AUDIT|DEPAUDIT|FILTER|AUXILIARY)\)', text):
        raise RuntimeError('Pointer closure loader redirection refused')
    needed = re.findall(r'\(NEEDED\).*?Shared library: \[([^\]]+)\]', text)
    if (len(needed) > 16 or len(set(needed)) != len(needed)
            or any(name != 'ld-linux-aarch64.so.1'
                   and re.fullmatch(r'lib[A-Za-z0-9_+.-]+\.so(?:\.[0-9]+)*', name) is None for name in needed)):
        raise RuntimeError('Pointer closure dependency name refused')
    interpreters = re.findall(r'Requesting program interpreter: ([^\]]+)\]', text)
    if len(interpreters) > 1 or any(value not in LOADERS for value in interpreters):
        raise RuntimeError('Pointer closure interpreter refused')
    return needed, interpreters[0] if interpreters else None


def system_pin(path, system):
    path = Path(path)
    aliases = []
    seen = set()
    while True:
        if str(path) in seen or len(seen) >= 12 or not str(path).startswith(('/usr/bin/', '/usr/lib/', '/usr/include/')):
            raise RuntimeError('Pointer system dependency path refused')
        seen.add(str(path))
        expected = system.get(str(path))
        if expected is None:
            raise RuntimeError('Pointer dependency absent from reviewed ARM inventory: ' + str(path))
        if path.is_symlink():
            link = os.readlink(path)
            if expected != {'link': link}:
                raise RuntimeError('Pointer system alias changed')
            aliases.append({'path': str(path), 'link': link})
            path = Path(os.path.normpath(str(path.parent / link))) if not Path(link).is_absolute() else Path(link)
            continue
        actual = {'mode': stat.S_IMODE(path.stat().st_mode), 'sha256': digest(path)}
        if not path.is_file() or actual != expected:
            raise RuntimeError('Pointer system dependency body changed')
        return path, {'path': str(path), **actual, 'aliases': aliases}


def run_profile(root, output, packet, run):
    root, output = Path(root), Path(output)
    validate_sources(root)
    inventory = Path(packet['systemInputs'])
    if digest(inventory) != SYSTEM_SHA256:
        raise RuntimeError('Pointer ARM system inventory changed')
    system = json.loads(inventory.read_text())['files']
    for tool in ('/usr/bin/wayland-scanner', '/usr/bin/cc', '/usr/bin/readelf'):
        system_pin(tool, system)
    generated = output / 'pointer-generated'
    generated.mkdir(mode=0o700)
    (output / 'dist').mkdir(mode=0o700)
    for label, argv in command_plan(root, output):
        run(label, argv, root, 120)
    generated_pins = {}
    for name in ('virtual-pointer-client.h', 'virtual-pointer-client.c'):
        file = plain_file(generated, name)
        size = file.stat().st_size
        if not 0 < size <= 1048576:
            raise RuntimeError('Pointer generated output bound exceeded')
        generated_pins[name] = {'path': str(file), 'sha256': digest(file), 'size': size}
    # The scanner outputs are first observed/pinned here, never fabricated in
    # the private proposal. They are rechecked after all static inspection.
    image = pin_image(output / 'dist/virtual-pointer', output / 'dist', 'virtual-pointer')
    dependencies = [name for receipt in ('pointer.d', 'protocol.d')
                    for name in dependency_names((output / receipt).read_text())]
    for name in dependencies:
        file = Path(name)
        if str(file) in {str(root / (BASE + 'virtual_pointer.c')),
                         str(generated / 'virtual-pointer-client.c'),
                         str(generated / 'virtual-pointer-client.h')}:
            continue
        system_pin(file, system)
    pending = [Path(image['path'])]
    inspected = {}
    while pending:
        file = pending.pop(0)
        if str(file) in inspected:
            continue
        if len(inspected) >= 32:
            raise RuntimeError('Pointer static library closure exceeds bound')
        label = 'pointer-static-' + str(len(inspected))
        metadata = run(label, ['/usr/bin/readelf', '-h', '-l', '-d', str(file)], root, 30)
        needed, interpreter = parse_elf(metadata)
        row = {'path': str(file), 'sha256': digest(file), 'needed': needed,
               'interpreter': interpreter, 'readelfLogLabel': label, 'resolved': []}
        for name in needed:
            resolved, pin = system_pin(Path('/usr/lib') / name, system)
            row['resolved'].append(pin)
            pending.append(resolved)
        if interpreter:
            loader = Path('/usr/lib/ld-linux-aarch64.so.1')
            resolved, pin = system_pin(loader, system)
            row['loader'] = pin
            pending.append(resolved)
        inspected[str(file)] = row
    if not {'libwayland-client.so.0', 'libc.so.6'}.issubset(set(inspected[image['path']]['needed'])):
        raise RuntimeError('Pointer lacks expected Wayland/C runtime linkage')
    for name, pin in generated_pins.items():
        if digest(generated / name) != pin['sha256']:
            raise RuntimeError('Pointer generated source changed during build')
    if pin_image(Path(image['path']), output / 'dist', 'virtual-pointer') != image:
        raise RuntimeError('Pointer image changed during static inspection')
    validate_sources(root)
    return {'scope': 'QA helper built and statically inspected only; no Wayland connection/input',
            'sourcePins': SOURCE_PINS, 'systemInventorySHA256': SYSTEM_SHA256,
            'generatedOutputs': generated_pins, 'image': image, 'staticClosure': inspected,
            'generatedOutputExpectation': 'Actual Root-generated hashes retained for independent review, not preclaimed',
            'inputCompletionProtocol': 'Existing source sync/ready sequence and real Wayland roundtrip; not exercised',
            'imageExecuted': False, 'waylandConnected': False, 'inputInjected': False,
            'loaderRuntimeObserved': False, 'nativeAcceptance': False, 'originalAcceptance': False}
