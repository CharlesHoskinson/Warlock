#!/usr/bin/env python3
"""Fixed QA-only private ARM foundation observation. No launch during import."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import resource
import shutil
import signal
import socket
import stat
import struct
import subprocess
import sys
import time

ROOT = Path('/home/hoskinson/Projects/Warlock')
PACKET = ROOT / '.warlock-contributor/evidence/nextloop-20261106/arm-gl-foundation/packet.json'
QA_SHA = '6ef35104e4082249cfbabb747425210b1ca6fe988f675880a2afc059e13b5b23'
EXPIRES = 1794082980000000000
CAP = 65536
COMPOSITOR_SHA = 'd40e2edab24c2032a7a77b4d44c3d738e5003256d7d4199950dc7001fee9b6ba'
AQ_BASE = '.warlock-contributor/evidence/nextloop-20261106/aquamarine-build-inputs'
AQ_SOURCE = AQ_BASE + '/source/src/backend/Backend.cpp'
AQ_SOURCE_SHA = '3098ed4ad3eb665c81a130bccc8e9c8a5eb181d7447811b90c2f6ede0d1e0ae6'
AQ_MANIFEST_SHA = '9e7347b8903b162c9042b5be6d3b6f52b3caac962fcb3d9b194c4d444ba9feb6'
PACKAGE = Path('/home/hoskinson/.local/state/warlock-team/20261105/nextloop-20261106/arm-private-weston-intake/package-root/usr')
HOST = {'weston': str(PACKAGE / 'bin/weston'), 'headless': str(PACKAGE / 'lib/libweston-15/headless-backend.so'),
        'kiosk': str(PACKAGE / 'lib/weston/kiosk-shell.so'),
        'gl': str(PACKAGE / 'lib/libweston-15/gl-renderer.so'),
        'libraryDirs': [str(PACKAGE / 'lib'), str(PACKAGE / 'lib/weston')]}
REQUIRED = {'wl_compositor': 6, 'wl_shm': 1, 'wl_seat': 9, 'xdg_wm_base': 6, 'zwp_linux_dmabuf_v1': 4}
HYPR_CONFIG = '''monitor = ,1280x800@60,0x0,1
xwayland { enabled = false }
misc {
 disable_hyprland_logo = true
 disable_splash_rendering = true
 force_default_wallpaper = 0
}
animations { enabled = false }
general { gaps_in = 0
 gaps_out = 0
 border_size = 0
}
'''
WESTON_CONFIG = '[core]\nidle-time=0\nxwayland=false\n[shell]\nlocking=false\n'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def unique(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError('duplicate JSON field')
        out[key] = value
    return out


def regular(path, expected):
    path = Path(path)
    if not path.is_absolute() or path.resolve() != path:
        raise ValueError('canonical regular path required')
    before = path.stat()
    if not stat.S_ISREG(before.st_mode) or before.st_mode & 0o022:
        raise ValueError('writable/irregular qualified input')
    if sha(path) != expected:
        raise ValueError('input changed: ' + str(path))
    after = path.stat()
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
        raise ValueError('input changed during hash')
    return before


def packet_shape(p):
    keys = {'schema', 'kind', 'armed', 'expiresUTC', 'host', 'hostInputs', 'sourceInputs', 'readiness', 'nested', 'graphics'}
    if (not isinstance(p, dict) or set(p) != keys or p.get('schema') != 1 or p.get('armed') is not True
            or p['kind'] != 'arm-private-gl-foundation-v1' or p['expiresUTC'] != '2026-11-07T20:23:00Z'
            or set(p['host']) != {'weston', 'headless', 'kiosk', 'gl', 'libraryDirs'}
            or p['host'] != HOST or not p['hostInputs'] or not p['sourceInputs']):
        raise ValueError('unarmed or expanded foundation packet')
    graphics_shape(p['graphics'], p['hostInputs'])
    if p['nested'] is not None and set(p['nested']) != {'compositor', 'backend', 'inputs', 'libraryDir', 'buildReport', 'sourceReview'}:
        raise ValueError('only exact reviewed nested tuple allowed')


def remaining(clock, now, boot):
    if boot != clock['boot'] or now < clock['last']:
        raise ValueError('clock regressed or rebooted')
    clock['last'] = now
    if now >= clock['deadline']:
        raise TimeoutError('original foundation deadline exhausted')
    return clock['deadline'] - now


def left(clock):
    if time.time_ns() >= EXPIRES:
        raise TimeoutError('human authorization expired')
    return remaining(clock, time.monotonic_ns(), Path('/proc/sys/kernel/random/boot_id').read_text().strip()) / 1e9


def cleanup_ceiling(deadline):
    return deadline + 2_000_000_000


def clean_environment(runtime, output):
    return {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8',
            'HOME': str(output / 'home'), 'XDG_CONFIG_HOME': str(output / 'config'),
            'XDG_CACHE_HOME': str(output / 'cache'), 'XDG_DATA_HOME': str(output / 'data'),
            'XDG_RUNTIME_DIR': str(runtime), 'DBUS_SESSION_BUS_ADDRESS': 'unix:path=' + str(runtime / 'no-bus'),
            'HYPRLAND_NO_SD_VARS': '1', 'HYPRLAND_NO_SD_TARGET': '1', 'HYPRLAND_NO_RT': '1',
            'HYPRLAND_NO_WATCHDOG': '1'}


def host_argv(weston, output):
    return [weston, '--backend=headless', '--renderer=gl', '--fake-seat', '--width=1280', '--height=800',
            '--socket=host-wayland', '--shell=kiosk-shell.so', '--idle-time=0',
            '--config=' + str(output / 'weston.ini'), '--log=' + str(output / 'weston.log')]



# Frozen passive identity. This is an explicit NVIDIA trial, not a vendor fallback.
GRAPHICS = {'vendorJson': '/usr/share/glvnd/egl_vendor.d/10_nvidia.json', 'renderer': '/home/hoskinson/.local/state/warlock-team/20261105/nextloop-20261106/arm-private-weston-intake/package-root/usr/lib/libweston-15/gl-renderer.so', 'files': {'/usr/share/glvnd/egl_vendor.d/10_nvidia.json': '9e6f14afaa7523370ad96e6675d3357441ee3985e60405cb3e0ced30b2ddaf76', '/usr/lib/libEGL.so.1.1.0': 'd2b76272182bccaf0b36d1e89e64998f1b5c7ab175e6dfe7b9910804c84970a0', '/usr/lib/libGLESv2.so.2.1.0': '983e6c9e65341ff407020c71d25796bbac6144b112b7139c1704fe1d3f0c52b5', '/usr/lib/libGLdispatch.so.0.0.0': '4341cba6efd6f63fd079d444daa753691cb900b96e405a227e7cff1e90312d99', '/usr/lib/libEGL_nvidia.so.615.78.08': '412168fcc28f41fc609b946652a6db94a886ed47940c866425fd66ab4a985537', '/usr/lib/libGLESv2_nvidia.so.615.78.08': 'd6f154416240416c6acb93c6d743db5be40be0a1e4675335d4a19cddcac8536e', '/usr/lib/libnvidia-eglcore.so.615.78.08': 'db6f1f12087e74a87eecc28a24f19cb846680f4bf421595a7e1ab8b067927d2c', '/usr/lib/libnvidia-glsi.so.615.78.08': '6bd3e02ed14ef624adf6a83a7d7f7c178d291407547bbec6de27a83cb42c003c', '/home/hoskinson/.local/state/warlock-team/20261105/nextloop-20261106/arm-private-weston-intake/package-root/usr/lib/libweston-15/gl-renderer.so': 'bf45c4c9d3cedcac33300c6c960d18102c3d28ab887f825e58905c5ab0f92ec4'}, 'aliases': {'/usr/lib/libEGL.so.1': '/usr/lib/libEGL.so.1.1.0', '/usr/lib/libGLESv2.so.2': '/usr/lib/libGLESv2.so.2.1.0', '/usr/lib/libGLdispatch.so.0': '/usr/lib/libGLdispatch.so.0.0.0', '/usr/lib/libEGL_nvidia.so.0': '/usr/lib/libEGL_nvidia.so.615.78.08', '/usr/lib/libGLESv2_nvidia.so.2': '/usr/lib/libGLESv2_nvidia.so.615.78.08'}, 'devices': {'/dev/dri/renderD128': {'device': 9, 'inode': 203, 'rdev': 57984, 'mode': 8630, 'uid': 0, 'gid': 987}, '/dev/nvidia0': {'device': 9, 'inode': 1046, 'rdev': 49920, 'mode': 8630, 'uid': 0, 'gid': 0}, '/dev/nvidiactl': {'device': 9, 'inode': 1044, 'rdev': 50175, 'mode': 8630, 'uid': 0, 'gid': 0}, '/dev/nvidia-modeset': {'device': 9, 'inode': 1086, 'rdev': 50174, 'mode': 8630, 'uid': 0, 'gid': 0}, '/dev/nvidia-uvm': {'device': 9, 'inode': 630, 'rdev': 130304, 'mode': 8630, 'uid': 0, 'gid': 0}, '/dev/nvidia-uvm-tools': {'device': 9, 'inode': 632, 'rdev': 130305, 'mode': 8630, 'uid': 0, 'gid': 0}}, 'driver': {'path': '/sys/devices/pci000f:00/000f:00:00.0/000f:01:00.0/uevent', 'sha256': 'd8d970b6bae38f99f6f3a3cf41432fe3a18e753381fb09c203e6c669b2458de7'}}


def device_identity(path):
    value = Path(path).lstat()  # metadata only: never open a GPU device here
    if not stat.S_ISCHR(value.st_mode):
        raise ValueError('graphics device is not a direct character node')
    return {'device': value.st_dev, 'inode': value.st_ino, 'rdev': value.st_rdev,
            'mode': value.st_mode, 'uid': value.st_uid, 'gid': value.st_gid}


def graphics_shape(graphics, inventory):
    if graphics != GRAPHICS:
        raise ValueError('only frozen explicit NVIDIA GL tuple allowed')
    if any(inventory.get(path) != digest for path, digest in GRAPHICS['files'].items()):
        raise ValueError('GL renderer/vendor/driver missing from host closure')


def verify_graphics(graphics, inventory):
    graphics_shape(graphics, inventory)
    for path, expected in graphics['devices'].items():
        if device_identity(path) != expected:
            raise ValueError('graphics device identity drift')
    if sha(graphics['driver']['path']) != graphics['driver']['sha256']:
        raise ValueError('render-node kernel binding changed')
    for alias, target in graphics['aliases'].items():
        if str(Path(alias).resolve(strict=True)) != target:
            raise ValueError('graphics SONAME alias changed')
    for path, digest in graphics['files'].items():
        regular(path, digest)


def graphics_environment(runtime, output):
    env = clean_environment(runtime, output)
    env['__EGL_VENDOR_LIBRARY_FILENAMES'] = GRAPHICS['vendorJson']
    env['EGL_PLATFORM'] = 'surfaceless'
    # Do not inherit software/DRI/vendor overrides or external display endpoints.
    return env


def graphics_fds(proc, birth, image):
    check_process(proc, birth, image)
    result = {}
    for fd in Path('/proc/' + str(proc.pid) + '/fd').iterdir():
        try:
            target = os.readlink(fd)
            if target.startswith('/dev/dri/') or target.startswith('/dev/nvidia'):
                if target not in GRAPHICS['devices']:
                    raise ValueError('unqualified graphics device opened')
                value = fd.stat()
                if value.st_rdev != GRAPHICS['devices'][target]['rdev']:
                    raise ValueError('graphics fd device mismatch')
                result[target] = GRAPHICS['devices'][target]
        except FileNotFoundError:
            continue  # transient descriptor closure is not positive evidence
    check_process(proc, birth, image)
    return result


def missing_protocols(globals_):
    return [name + '>=' + str(version) for name, version in REQUIRED.items() if globals_.get(name, 0) < version]


def parse_registry(data):
    """Only registry globals and display/callback bookkeeping; no bind or input."""
    globals_ = {}
    offset = 0
    done = False
    while offset < len(data):
        if len(data) - offset < 8:
            raise ValueError('partial Wayland header')
        object_id, packed = struct.unpack_from('<II', data, offset)
        size, opcode = packed >> 16, packed & 65535
        if size < 8 or size % 4 or offset + size > len(data):
            raise ValueError('invalid Wayland message length')
        body = data[offset + 8:offset + size]
        if object_id == 2 and opcode == 0:
            if len(body) < 16:
                raise ValueError('short registry global')
            _, length = struct.unpack_from('<II', body)
            padded = (length + 3) & ~3
            if length < 2 or length > 256 or len(body) != 12 + padded or body[8 + length - 1] != 0:
                raise ValueError('invalid registry string')
            name = body[8:8 + length - 1].decode('ascii')
            version = struct.unpack_from('<I', body, 8 + padded)[0]
            if not re.fullmatch('[A-Za-z0-9_]+', name) or name in globals_:
                raise ValueError('ambiguous registry protocol')
            globals_[name] = version
        elif object_id == 3 and opcode == 0 and len(body) == 4:
            if done:
                raise ValueError('duplicate sync completion')
            done = True
        elif object_id == 1 and opcode == 1 and len(body) == 4:
            pass  # display.delete_id; no request or authority follows it
        else:
            raise ValueError('display error or unexpected registry message')
        offset += size
    return globals_, done


def process_birth(pid):
    fields = Path('/proc', str(pid), 'stat').read_text().rsplit(')', 1)[1].split()
    return fields[19]


def check_process(proc, birth, expected):
    if proc.poll() is not None or process_birth(proc.pid) != birth:
        raise ValueError('owned process exited or changed')
    if sha(Path('/proc', str(proc.pid), 'exe').resolve()) != expected:
        raise ValueError('owned executable changed')


def mapped(proc, inventory, required):
    seen = set()
    for line in Path('/proc', str(proc.pid), 'maps').read_text().splitlines():
        fields = line.split(maxsplit=5)
        if len(fields) != 6 or not fields[5].startswith('/'):
            continue
        path = fields[5]
        if path in GRAPHICS['devices']:
            info = device_identity(path)
            expected = GRAPHICS['devices'][path]
            device = tuple(int(value, 16) for value in fields[3].split(':'))
            if (info != expected or int(fields[4]) != info['inode']
                    or device != (os.major(info['device']), os.minor(info['device']))):
                raise ValueError('mapped graphics device identity differs')
            seen.add(path)
            continue  # never read/hash/mmap a character device
        if path.endswith(' (deleted)') or path not in inventory:
            raise ValueError('unqualified mapped file: ' + path)
        info = regular(path, inventory[path])
        if int(fields[4]) != info.st_ino:
            raise ValueError('mapped inode differs')
        # Cross-check device using a local read-only mapping, like historical guard.
        import mmap
        with open(path, 'rb') as stream:
            with mmap.mmap(stream.fileno(), min(4096, info.st_size), access=mmap.ACCESS_READ):
                matches = [x.split(maxsplit=5) for x in Path('/proc/self/maps').read_text().splitlines()]
                if not any(len(x) == 6 and x[5] == path and x[3:5] == fields[3:5] for x in matches):
                    raise ValueError('mapped device/inode differs')
        seen.add(path)
    if not set(required) <= seen:
        raise ValueError('required private provider not mapped')
    return sorted(seen)


def registry(path, proc, birth, image, clock):
    before = path.lstat()
    if not stat.S_ISSOCK(before.st_mode) or before.st_uid != os.getuid():
        raise ValueError('owned private Wayland socket required')
    check_process(proc, birth, image)
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.settimeout(left(clock))
        client.connect(str(path))
        pid, uid, _ = struct.unpack('3i', client.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
        if pid != proc.pid or uid != os.getuid():
            raise ValueError('foreign Wayland peer')
        # wl_display.get_registry(new_id2), then sync(new_id3).
        client.sendall(struct.pack('<IIIIII', 1, (12 << 16) | 1, 2, 1, 12 << 16, 3))
        data = bytearray()
        while True:
            client.settimeout(left(clock))
            block = client.recv(min(4096, CAP + 1 - len(data)))
            if not block or len(data) + len(block) > CAP:
                raise ValueError('registry EOF/output cap')
            data.extend(block)
            # Wait for complete framed messages; malformed complete frames fail.
            cursor = 0
            while cursor + 8 <= len(data):
                packed = struct.unpack_from('<I', data, cursor + 4)[0]
                size = packed >> 16
                if size < 8 or size % 4:
                    raise ValueError('malformed Wayland frame')
                if cursor + size > len(data):
                    break
                cursor += size
            if cursor == len(data):
                globals_, done = parse_registry(data)
                if done:
                    break
    after = path.lstat()
    if (before.st_dev, before.st_ino, before.st_uid) != (after.st_dev, after.st_ino, after.st_uid):
        raise ValueError('Wayland socket replaced')
    check_process(proc, birth, image)
    return {'path': str(path), 'device': before.st_dev, 'inode': before.st_ino, 'pid': proc.pid,
            'startTicks': birth, 'globals': globals_}


def private_soname(directory, backend):
    """Installed pinned Hyprland needs .15; reject fallback BEFORE any spawn."""
    directory, backend = Path(directory), Path(backend)
    info = directory.lstat()
    if (directory.resolve() != directory or not stat.S_ISDIR(info.st_mode)
            or info.st_uid != os.getuid() or info.st_mode & 0o022
            or backend.parent != directory or backend.name != 'libaquamarine.so.0.16.0'
            or backend.is_symlink() or not backend.is_file()):
        raise ValueError('unsafe private provider directory/body')
    aliases = {'libaquamarine.so.15', 'libaquamarine.so', 'libaquamarine.so.0'}
    required = directory / 'libaquamarine.so.15'
    if not required.is_symlink() or os.readlink(required) != backend.name:
        raise ValueError('exact required private SONAME15 alias absent or foreign')
    for item in directory.glob('libaquamarine.so*'):
        if item == backend:
            continue
        if (item.name not in aliases or not item.is_symlink()
                or os.readlink(item) != backend.name or item.resolve() != backend):
            raise ValueError('unqualified private Aquamarine search candidate')
    return required


def provider_build_binding(nested, report):
    try:
        actual = report['aquamarineBuild']
        image = actual['image']
        if (report['passed'] is not True or report['mode'] != '--aquamarine-build'
                or actual['target'] != 'aquamarine' or actual['executed'] is not False
                or actual['sourcePatchSha256'] != AQ_SOURCE_SHA
                or actual['supplementalManifestSha256'] != AQ_MANIFEST_SHA
                or report['sourceHashes'].get(AQ_SOURCE) != AQ_SOURCE_SHA
                or nested['compositor'] != '/usr/bin/Hyprland'
                or nested['inputs'].get('/usr/bin/Hyprland') != COMPOSITOR_SHA
                or image['path'] != nested['backend'] or image['sha256'] != nested['inputs'].get(nested['backend'])
                or not re.fullmatch('[0-9a-f]{64}', image['sha256'])
                or Path(image['path']).name != 'libaquamarine.so.0.16.0'
                or str(Path(image['path']).parent) != nested['libraryDir']
                or any(type(image[k]) is not int for k in ('size', 'device', 'inode', 'mode'))
                or not 4096 < image['size'] < 134217728 or image['device'] < 0 or image['inode'] <= 0
                or image['mode'] & 0o6022):
            raise ValueError('actual provider build/image/source binding differs')
        return image
    except (KeyError, TypeError) as problem:
        raise ValueError('actual aquamarineBuild report schema required') from problem


def verify_private_provider(nested):
    for key in ('buildReport', 'sourceReview'):
        regular(nested[key]['path'], nested[key]['sha256'])
    report = json.loads(Path(nested['buildReport']['path']).read_text(), object_pairs_hook=unique)
    review = json.loads(Path(nested['sourceReview']['path']).read_text(), object_pairs_hook=unique)
    pin = provider_build_binding(nested, report)
    if (review.get('disposition') != 'accepted' or review.get('scope') != 'arm-mandatory-wayland-provider'
            or review.get('inputs') != nested['inputs']):
        raise ValueError('matching independent provider readiness missing')
    regular(ROOT / (AQ_BASE + '/inputs.json'), AQ_MANIFEST_SHA)
    for name, expected in report['sourceHashes'].items():
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('provider build source path escaped repository')
        regular(ROOT / relative, expected)
    for path, expected in nested['inputs'].items():
        regular(path, expected)
    image = regular(pin['path'], pin['sha256'])
    if (image.st_dev, image.st_ino, image.st_size, stat.S_IMODE(image.st_mode)) != (pin['device'], pin['inode'], pin['size'], pin['mode']):
        raise ValueError('actual provider build image stat changed')
    private_soname(nested['libraryDir'], nested['backend'])
    return pin


def bound_output():
    resource.setrlimit(resource.RLIMIT_FSIZE, (CAP, CAP))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sha256', required=True)
    args = parser.parse_args()
    regular(PACKET, args.sha256)
    p = json.loads(PACKET.read_text(), object_pairs_hook=unique)
    packet_shape(p)
    verify_graphics(p['graphics'], p['hostInputs'])  # before ANY Popen
    for path, expected in {**p['sourceInputs'], **p['hostInputs']}.items():
        regular(path, expected)
    review_path = Path(p['readiness']['path'])
    regular(review_path, p['readiness']['sha256'])
    review = json.loads(review_path.read_text(), object_pairs_hook=unique)
    if (review.get('disposition') != 'accepted' or review.get('scope') != 'arm-private-gl-foundation'
            or review.get('hostInputs') != p['hostInputs'] or review.get('host') != p['host']
            or review.get('sourceInputs') != p['sourceInputs'] or review.get('nested') != p['nested']
            or review.get('graphics') != p['graphics']):
        raise ValueError('matching independent foundation readiness absent')
    # This preflight is before ANY Popen, including the host. Missing .15
    # cannot execute the system provider and then fail only after mapping.
    if p['nested'] is not None:
        verify_private_provider(p['nested'])
    qa_path = ROOT / 'window-integration-qa/qa_launch.py'
    regular(qa_path, QA_SHA)
    spec = importlib.util.spec_from_file_location('foundation_qa', qa_path)
    if spec is None or spec.loader is None:
        raise ValueError('protected launch contract missing')
    qa = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(qa)
    scope = qa.require_qa_scope()
    if time.time_ns() + 17_000_000_000 >= EXPIRES:
        raise ValueError('insufficient authorization for original15+cleanup2')
    start = time.monotonic_ns()
    clock = {'deadline': start + 15_000_000_000, 'last': start,
             'boot': Path('/proc/sys/kernel/random/boot_id').read_text().strip()}
    os.umask(0o077)
    output = ROOT / '.warlock-contributor' / ('arm-gl-foundation-' + str(time.time_ns()))
    output.mkdir(mode=0o700)
    for name in ('home', 'config', 'cache', 'data'):
        (output / name).mkdir(mode=0o700)
    (output / 'weston.ini').write_text(WESTON_CONFIG)
    (output / 'hyprland.conf').write_text(HYPR_CONFIG)
    runtime = qa.private_runtime()
    env = graphics_environment(runtime, output)
    host = p['host']
    env['LD_LIBRARY_PATH'] = ':'.join(host['libraryDirs'])
    env['WESTON_MODULE_MAP'] = 'headless-backend.so=' + host['headless'] + ';kiosk-shell.so=' + host['kiosk'] + ';gl-renderer.so=' + host['gl']
    result = {'schema': 1, 'kind': 'arm-private-gl-foundation-observation', 'scope': scope,
              'packetSha256': args.sha256, 'clock': dict(clock), 'hostObserved': False,
              'nestedObserved': False, 'cleanup': False, 'forcedCleanup': False,
              'nativeJourneyAccepted': False, 'originalAcceptance': False, 'processes': []}
    children = []
    logs = []

    def spawn(role, argv, environment, inventory):
        left(clock)
        for path, expected in inventory.items():
            regular(path, expected)
        out, err = output / (role + '.stdout'), output / (role + '.stderr')
        stdout, stderr = out.open('xb'), err.open('xb')
        logs.extend([stdout, stderr])
        proc = subprocess.Popen(argv, env=environment, stdin=subprocess.DEVNULL,
                                stdout=stdout, stderr=stderr, close_fds=True, start_new_session=True, preexec_fn=bound_output)
        # Register custody before any observation that can fail. Popen retains
        # this unreaped child's identity even if /proc disappears immediately.
        children.append((proc, None, role))
        born = process_birth(proc.pid)
        children[-1] = (proc, born, role)
        result['processes'].append({'role': role, 'pid': proc.pid, 'startTicks': born, 'argv': argv,
                                    'stdout': str(out), 'stderr': str(err)})
        return proc, born

    def wait_socket(path, proc, born, image):
        while not path.exists():
            check_process(proc, born, image)
            for stream in logs:
                if os.fstat(stream.fileno()).st_size > CAP:
                    raise ValueError('bounded output exceeded')
            if (output / 'weston.log').exists() and (output / 'weston.log').stat().st_size > CAP:
                raise ValueError('Weston log cap exceeded')
            time.sleep(min(0.02, left(clock)))
        return registry(path, proc, born, image, clock)

    try:
        verify_graphics(p['graphics'], p['hostInputs'])
        weston, host_birth = spawn('host', host_argv(host['weston'], output), env, p['hostInputs'])
        observation = wait_socket(runtime / 'host-wayland', weston, host_birth, p['hostInputs'][host['weston']])
        result['host'] = observation
        result['hostMappings'] = mapped(weston, p['hostInputs'], [host['weston'], host['headless'], host['kiosk'], host['gl'],
            str(Path('/usr/lib/libEGL_nvidia.so.0').resolve()), '/usr/lib/libnvidia-eglcore.so.615.78.08'])
        verify_graphics(p['graphics'], p['hostInputs'])
        result['hostGraphicsFDs'] = graphics_fds(weston, host_birth, p['hostInputs'][host['weston']])
        result['hostObserved'] = True
        result['missingNestedProtocols'] = missing_protocols(observation['globals'])
        if result['missingNestedProtocols']:
            raise ValueError('explicit GL host lacks required AQ protocols; no nested launch or alternate renderer')
        nested = p['nested']
        if nested is None:
            raise ValueError('independently built mandatory-Wayland provider missing')
        verify_private_provider(nested)  # recheck exact same pins/SONAME immediately before spawn
        nenv = graphics_environment(runtime, output)
        nenv['WAYLAND_DISPLAY'] = str(runtime / 'host-wayland')
        nenv['LD_LIBRARY_PATH'] = nested['libraryDir']
        verify_graphics(p['graphics'], p['hostInputs'])
        compositor, born = spawn('nested', [nested['compositor'], '--config', str(output / 'hyprland.conf')], nenv, nested['inputs'])
        sockets = []
        while not sockets:
            check_process(compositor, born, nested['inputs'][nested['compositor']])
            sockets = [path for path in runtime.glob('wayland-*') if stat.S_ISSOCK(path.lstat().st_mode)]
            if not sockets:
                time.sleep(min(0.02, left(clock)))
        if len(sockets) != 1:
            raise ValueError('ambiguous private nested display')
        result['nested'] = registry(sockets[0], compositor, born, nested['inputs'][nested['compositor']], clock)
        result['nestedMappings'] = mapped(compositor, nested['inputs'], [nested['compositor'], nested['backend']])
        result['nestedGraphicsFDs'] = graphics_fds(compositor, born, nested['inputs'][nested['compositor']])
        verify_graphics(p['graphics'], p['hostInputs'])
        result['nestedObserved'] = True
        # Foundation ends here. No input, application, arbitrary callback or handoff.
    except Exception as problem:
        result['error'] = str(problem)
    finally:
        ceiling = cleanup_ceiling(clock['deadline'])
        all_clean = True
        for proc, born, role in reversed(children):
            forced = False
            try:
                if proc.poll() is None:
                    if born is not None and process_birth(proc.pid) != born:
                        raise ValueError('owned cleanup birth mismatch')
                    os.killpg(proc.pid, signal.SIGTERM)
                    budget = min(ceiling - 1_000_000_000 - time.monotonic_ns(), EXPIRES - time.time_ns()) / 1e9
                    try:
                        if budget <= 0:
                            raise subprocess.TimeoutExpired(proc.args, 0)
                        proc.wait(timeout=budget)
                    except subprocess.TimeoutExpired:
                        forced = True
                        os.killpg(proc.pid, signal.SIGKILL)
                        budget = min(ceiling - time.monotonic_ns(), EXPIRES - time.time_ns()) / 1e9
                        if budget <= 0:
                            raise TimeoutError('kill reap exceeds cleanup ceiling')
                        proc.wait(timeout=budget)
                group_gone = False
                try:
                    os.killpg(proc.pid, 0)
                except ProcessLookupError:
                    group_gone = True
                clean = proc.returncode == 0 and group_gone and not forced
                all_clean = all_clean and clean
                result['processes'].append({'role': role, 'exit': proc.returncode, 'reaped': proc.returncode is not None,
                                            'requestedTermination': 'SIGTERM', 'groupAbsent': group_gone, 'forced': forced})
            except Exception as problem:
                all_clean = False
                result.setdefault('cleanupErrors', []).append(str(problem))
            result['forcedCleanup'] = result['forcedCleanup'] or forced
        for stream in logs:
            stream.close()
        if all_clean:
            try:
                qa.verify_runtime(runtime)
                shutil.rmtree(runtime)
                all_clean = not runtime.exists()
            except Exception as problem:
                all_clean = False
                result.setdefault('cleanupErrors', []).append(str(problem))
        result['cleanup'] = all_clean
        result['passed'] = result['hostObserved'] and result['nestedObserved'] and all_clean
        with (output / 'report.json').open('x') as stream:
            json.dump(result, stream, indent=2)
            stream.write('\n')
    print(json.dumps({'passed': result['passed'], 'hostObserved': result['hostObserved'],
                      'nestedObserved': result['nestedObserved'], 'cleanup': result['cleanup'],
                      'report': str(output / 'report.json')}))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
