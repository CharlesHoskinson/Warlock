#!/usr/bin/env python3
"""Fixed QA Labwc/GLES2 foundation. No application, input, GTK or image during import."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import signal
import socket
import struct
import stat
import subprocess
import time

ROOT = Path('/home/hoskinson/Projects/Warlock')
PACKET = ROOT / '.warlock-contributor/evidence/nextloop-20261106/labwc-warn-ipc-foundation-20261108/packet.json'
BASE_PATH = ROOT / 'tools/run_arm_gl_foundation_renewed_20261107.py'
BASE_SHA = '1587fee27cc8521700cfbf46e759a53f6a987cd95eab67b81588b680b033761b'
QA_SHA = '6ef35104e4082249cfbabb747425210b1ca6fe988f675880a2afc059e13b5b23'
EXPIRES_UTC = '2026-11-08T04:23:00Z'
EXPIRES = 1794111780000000000
OPERATION_NS, CLEANUP_NS = 15_000_000_000, 2_000_000_000
CAP = 65536
REQUIRED = {'wl_compositor':6,'wl_shm':1,'wl_seat':9,'xdg_wm_base':6,'zwp_linux_dmabuf_v1':4}
NESTED_LUA = '-- QA-only fixed private instance; no startup commands, plugin or system session changes.\nhl.monitor({output="",mode="1280x800@60",position="0x0",scale=1})\nhl.config({\n    debug={disable_logs=true,enable_stdout_logs=false},\n    xwayland={enabled=false},\n    misc={disable_hyprland_logo=true,disable_splash_rendering=true,force_default_wallpaper=0},\n    general={gaps_in=0,gaps_out=0,border_size=0},\n    decoration={rounding=0},\n    animations={enabled=false},\n})\nhl.window_rule({name="ux003-owned-private-clients",match={class="^GTK Application$"},float=true,center=true,size={980,680}})\nhl.bind("ALT + F4",hl.dsp.window.close())\n'
NESTED_LUA_SHA = 'f5285bcba66500cadfd3283911456aeb381de7f711e8dab460eb0a4946ed14aa'
FONT = Path('/usr/share/fonts/liberation/LiberationSans-Regular.ttf')
FONT_SHA = 'ef452d55117c6b4b8b0a51f842c1ab16362518225f6c806b0e91f18ed0e331f5'
PRIVATE_LIB = ROOT / '.warlock-contributor/evidence/nextloop-20261106/labwc-build-inputs/prefix/usr/lib'
RC = '<?xml version="1.0"?><labwc_config><core><decoration>server</decoration></core></labwc_config>\n'

# A controlled-context classification, not immutable/generated-code attestation.
GENERATED_NAME = '/memfd:/.glXXXXXX (deleted)'
GENERATED_IMAGES = {
    'host': '361f74c4faf75225ee9b666a4bf799783487cdc086b35d27706e8c1e95698b79',
    'nested': 'd40e2edab24c2032a7a77b4d44c3d738e5003256d7d4199950dc7001fee9b6ba',
}
MAPS_CAP = 1048576
MAP_ENTRIES_CAP = 8192


OVERLAY_SOURCE_REL = '.warlock-contributor/evidence/nextloop-20261106/aquamarine-build-inputs/source'
OVERLAY_LOGGER_REL = OVERLAY_SOURCE_REL + '/src/backend/Logger.cpp'
OVERLAY_BACKEND_REL = OVERLAY_SOURCE_REL + '/src/backend/Backend.cpp'
OVERLAY_OLD_SHA = '15a7687942555ea5930e2962c3bc2687184f172d6ca89c613d1da4acda7d95ba'
OVERLAY_SHA = 'f48d2e4896cc79a4c7ddbfbcaf6a7c8f55a5277675ecd2362c063225cd7b2503'
OVERLAY_BACKEND_SHA = '3098ed4ad3eb665c81a130bccc8e9c8a5eb181d7447811b90c2f6ede0d1e0ae6'
OVERLAY_MANIFEST_SHA = '9e7347b8903b162c9042b5be6d3b6f52b3caac962fcb3d9b194c4d444ba9feb6'
OVERLAY_ACTIVE = ROOT / '.warlock-contributor/evidence/nextloop-20261106/aq-log-provider-build/Logger.cpp'
OVERLAY_BASE_REPORT = ROOT / '.warlock-contributor/arm64-cpu-1794081988078623474/report.json'
OVERLAY_BASE_REPORT_SHA = 'd572606cd81a4bb75fac1a8c6d0e6fdf90e0fadb6eafbdc4603e17440a9bbbf2'
OVERLAY_PROTOCOL_NAMES = {'.gitkeep','wayland.cpp','wayland.hpp','xdg-shell.cpp','xdg-shell.hpp','linux-dmabuf-v1.cpp','linux-dmabuf-v1.hpp'}


def overlay_provider_binding(nested, report, baseline):
    """Validate the new build kind explicitly; never relabel it as the old mode."""
    try:
        actual = report['aquamarineBuild']; image = actual['image']
        physical = report['sourceHashes']; effective = dict(physical)
        effective[OVERLAY_LOGGER_REL] = OVERLAY_SHA
        root = Path(image['path']).parent.parent
        expected_overlay = {
            'physicalTarget':str(ROOT/OVERLAY_LOGGER_REL),'physicalSha256':OVERLAY_OLD_SHA,
            'activeInput':str(OVERLAY_ACTIVE),'activeSha256':OVERLAY_SHA,
            'mechanism':'single RO bwrap file bind; physical target never written',
            'generatedProtocolDirectory':str(root/'protocols'),
            'namespaceProtocolTarget':str(ROOT/OVERLAY_SOURCE_REL/'protocols')}
        commands = report['commands']
        if (report['passed'] is not True or report['mode']!='--aquamarine-logger-overlay-build'
                or report['runtimeExecution'] is not False or report['nativeAcceptance'] is not False
                or physical != baseline['sourceHashes'] or len(physical)!=4255
                or physical.get(OVERLAY_LOGGER_REL)!=OVERLAY_OLD_SHA
                or physical.get(OVERLAY_BACKEND_REL)!=OVERLAY_BACKEND_SHA
                or report['effectiveCompiledSourceHashes']!=effective
                or report['overlay']!=expected_overlay
                or report['sourceInputs'].get(str(OVERLAY_ACTIVE))!=OVERLAY_SHA
                or actual['target']!='aquamarine' or actual['executed'] is not False
                or actual['runtimeMappingObserved'] is not False
                or actual['sourcePatchSha256']!=OVERLAY_BACKEND_SHA
                or actual['supplementalManifestSha256']!=OVERLAY_MANIFEST_SHA
                or actual['loggerOverlaySha256']!=OVERLAY_SHA
                or nested['compositor']!='/usr/bin/Hyprland'
                or nested['inputs'].get('/usr/bin/Hyprland')!=GENERATED_IMAGES['nested']
                or image['path']!=nested['backend'] or image['sha256']!=nested['inputs'].get(nested['backend'])
                or not re.fullmatch('[0-9a-f]{64}',image['sha256'])
                or root.parent!=ROOT/'.warlock-contributor'
                or not re.fullmatch('aq-log-provider-build-[0-9]+',root.name)
                or Path(image['path']).name!='libaquamarine.so.0.16.0'
                or Path(image['path']).parent!=root/'build'
                or str(root/'build')!=nested['libraryDir']
                or any(type(image[k]) is not int for k in ('size','device','inode','mode'))
                or not 4096<image['size']<134217728 or image['device']<0 or image['inode']<=0
                or image['mode']&0o6022
                or set(actual['generatedProtocols'])!=OVERLAY_PROTOCOL_NAMES
                or any(not re.fullmatch('[0-9a-f]{64}',v) for v in actual['generatedProtocols'].values())
                or not re.fullmatch('[0-9a-f]{64}',actual['compileCommandsSha256'])
                or actual['loggerCompileEntry']['file']!=str(ROOT/OVERLAY_LOGGER_REL)
                or actual['loggerCompileEntry']['directory']!=str(root/'build')
                or [x['name'] for x in commands]!=['builder-controls','source-contract-controls','configure','build','inspect']
                or any(type(x['exit']) is not int or x['exit']!=0 or x['timedOut'] is not False
                       or x['forcedCleanup'] is not False or x['groupAbsent'] is not True for x in commands)):
            raise ValueError('explicit WARN overlay provider/source/image binding differs')
        return image
    except (KeyError,TypeError,AttributeError) as problem:
        raise ValueError('complete actual WARN overlay build report required') from problem


def verify_private_provider(base, nested):
    report = regular_ref(base,nested['buildReport'])
    review = regular_ref(base,nested['sourceReview'])
    baseline = regular_ref(base,{'path':str(OVERLAY_BASE_REPORT),'sha256':OVERLAY_BASE_REPORT_SHA})
    pin = overlay_provider_binding(nested,report,baseline)
    if (review.get('disposition')!='accepted' or review.get('scope')!='arm-mandatory-wayland-warn-overlay-provider'
            or review.get('inputs')!=nested['inputs'] or review.get('buildReport')!=nested['buildReport']
            or review.get('loggerOverlaySha256')!=OVERLAY_SHA):
        raise ValueError('matching independent WARN overlay provider readiness missing')
    base.regular(ROOT/(OVERLAY_SOURCE_REL.removesuffix('/source')+'/inputs.json'),OVERLAY_MANIFEST_SHA)
    for name,pin_sha in report['sourceHashes'].items():
        relative=Path(name)
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('physical baseline path escaped repository')
        base.regular(ROOT/relative,pin_sha)
    for name,pin_sha in report['sourceInputs'].items():
        if not Path(name).is_absolute():raise ValueError('overlay build input must be absolute')
        base.regular(name,pin_sha)
    base.regular(OVERLAY_ACTIVE,OVERLAY_SHA)
    for name,pin_sha in nested['inputs'].items():base.regular(name,pin_sha)
    image=base.regular(pin['path'],pin['sha256'])
    if (image.st_dev,image.st_ino,image.st_size,stat.S_IMODE(image.st_mode))!=(pin['device'],pin['inode'],pin['size'],pin['mode']):
        raise ValueError('actual WARN provider image stat changed')
    root=Path(pin['path']).parent.parent
    actual=report['aquamarineBuild']
    if {p.name for p in (root/'protocols').iterdir()}!=OVERLAY_PROTOCOL_NAMES:
        raise ValueError('generated protocol output membership changed')
    for name,pin_sha in actual['generatedProtocols'].items():base.regular(root/'protocols'/name,pin_sha)
    compile_path=root/'build/compile_commands.json';base.regular(compile_path,actual['compileCommandsSha256'])
    entries=json.loads(compile_path.read_text(),object_pairs_hook=unique)
    if [x for x in entries if x.get('file')==str(ROOT/OVERLAY_LOGGER_REL)]!=[actual['loggerCompileEntry']]:
        raise ValueError('actual Logger compilation entry changed')
    inspect=report['commands'][-1]['stdout']
    if inspect['path']!=str(root/'inspect.stdout'):raise ValueError('static inspection path changed')
    base.regular(inspect['path'],inspect['sha256'])
    text=Path(inspect['path']).read_text()
    if ('Library soname: [libaquamarine.so.15]' not in text or '(RPATH)' in text or '(RUNPATH)' in text):
        raise ValueError('fixed static SONAME/search policy changed')
    base.private_soname(nested['libraryDir'],nested['backend'])
    return pin


def require_generated_role(role, image):
    if role not in GENERATED_IMAGES or image != GENERATED_IMAGES[role]:
        raise ValueError('generated RAM scope requires exact fixed host/nested image')


def parse_complete_maps(raw):
    if not isinstance(raw, bytes) or not raw or len(raw) > MAPS_CAP or not raw.endswith(b'\n'):
        raise ValueError('complete bounded kernel maps required')
    lines = raw.decode('utf-8', errors='surrogateescape').splitlines()
    if not lines or len(lines) > MAP_ENTRIES_CAP:
        raise ValueError('complete bounded kernel map entries required')
    result = []
    last_end = 0
    for line in lines:
        fields = line.split(maxsplit=5)
        if (len(fields) < 5 or not re.fullmatch(r'[0-9a-f]+-[0-9a-f]+', fields[0])
                or not re.fullmatch(r'[r-][w-][x-][ps]', fields[1])
                or not re.fullmatch(r'[0-9a-f]+', fields[2])
                or not re.fullmatch(r'[0-9a-f]+:[0-9a-f]+', fields[3])
                or not fields[4].isdigit()):
            raise ValueError('malformed complete kernel map')
        start, end = [int(x, 16) for x in fields[0].split('-')]
        if start < last_end or start >= end:
            raise ValueError('overlapping, duplicate or invalid kernel map range')
        last_end = end
        result.append(dict(address=fields[0], permissions=fields[1], offset=fields[2],
                           device=fields[3], inode=int(fields[4]), pathname=fields[5] if len(fields)==6 else None))
    return result


def classify_generated_snapshot(rows, links):
    candidates = [row for row in rows if row['pathname'] == GENERATED_NAME]
    if any((row['pathname'] or '').startswith('/memfd:') and row['pathname'] != GENERATED_NAME for row in rows):
        raise ValueError('other memfd object is outside generated RAM recipe')
    if not candidates:
        return None  # No exception used; ordinary strict file/device policy still applies.
    keys = {(tuple(int(x, 16) for x in row['device'].split(':')), row['inode']) for row in candidates}
    if len(keys) != 1:
        raise ValueError('generated object has multiple kernel backing identities')
    device, inode = next(iter(keys))
    if device != (0, 1) or type(inode) is not int or inode <= 0:
        raise ValueError('exact nonzero kernel memfd backing required')
    aliases = [row for row in rows if (tuple(int(x, 16) for x in row['device'].split(':')), row['inode']) == (device, inode)]
    if len(aliases) != 2 or aliases != candidates or {row['permissions'] for row in aliases} != {'rw-s', 'r-xs'}:
        raise ValueError('exact two shared writable/executable aliases required')
    sizes = []
    for row in aliases:
        start, end = [int(x, 16) for x in row['address'].split('-')]
        if end - start != 8192 or int(row['offset'], 16) != 0:
            raise ValueError('generated alias length/offset differs')
        metadata = links.get(row['address'], {})
        if metadata.get('link') != GENERATED_NAME:
            raise ValueError('matching kernel map_files link required')
        if 'backingStat' in metadata:
            backing = metadata['backingStat']
            if ((os.major(backing['device']), os.minor(backing['device'])) != device
                    or backing['inode'] != inode or backing['size'] != 8192):
                raise ValueError('available backing metadata differs from exact recipe')
            sizes.append(backing['size'])
    return dict(classification='observed-owned-NVIDIA-context-generated-runtime-object',
                kernelDevice=list(device), inode=inode, mappings=aliases, mappedBytesPerAlias=8192,
                mutableExecutableBacking=True, creatorAttested=False, contentSha256=None,
                backingSize=8192 if len(sizes)==2 else None, seals=None,
                metadata=links, attribution='controlled-context inference, not creator or code-safety proof')


def generated_key(value):
    if value is None:
        return None
    return (value['kernelDevice'], value['inode'], value['mappings'])


def require_generated_stability(before, after, first, second):
    if before != after or generated_key(first) != generated_key(second):
        raise ValueError('owned context/generated backing changed across snapshots')


def owned_context(base, proc, birth, image, clock):
    base.left(clock)
    base.check_process(proc, birth, image)
    root = Path('/proc', str(proc.pid))
    status = dict(line.split(':', 1) for line in (root/'status').read_text().splitlines() if ':' in line)
    uid = int(status['Uid'].split()[1])
    if uid != os.geteuid():
        raise ValueError('foreign generated-context owner')
    value = dict(pid=proc.pid, birth=base.process_birth(proc.pid), uid=uid, image=image,
                 namespaces={n:os.readlink(root/'ns'/n) for n in ('pid','mnt','user','net')},
                 cgroup=(root/'cgroup').read_text())
    if (value['birth'] != birth or value['cgroup'] != Path('/proc/self/cgroup').read_text()
            or value['namespaces'] != {n:os.readlink(Path('/proc/self/ns')/n) for n in ('pid','mnt','user','net')}):
        raise ValueError('generated context escaped original owned scope')
    base.check_process(proc, birth, image)
    base.left(clock)
    return value


def generated_snapshot(base, proc, clock, *, on_classifier_refusal=None):
    base.left(clock)
    root = Path('/proc', str(proc.pid))
    with (root/'maps').open('rb') as stream:
        raw = stream.read(MAPS_CAP+1)
    rows = parse_complete_maps(raw)
    links = {}
    candidates = [row for row in rows if row['pathname'] == GENERATED_NAME]
    if len(candidates)>2:
        raise ValueError('too many generated aliases')
    for row in candidates:
        base.left(clock)
        path = root/'map_files'/row['address']
        item = {'link':os.readlink(path)}  # Mandatory kernel link; no filename-only grant.
        try:
            info = path.stat()
            item['backingStat'] = dict(device=info.st_dev,inode=info.st_ino,size=info.st_size)
        except PermissionError as error:
            item['backingError'] = type(error).__name__+': '+str(error)
        links[row['address']] = item
    base.left(clock)
    try:
        generated = classify_generated_snapshot(rows, links)
    except Exception as error:
        if on_classifier_refusal is not None:
            try:
                on_classifier_refusal(raw, rows, links, error)
            except Exception:
                pass  # Diagnostic failure cannot replace the original mapping refusal.
        raise
    return rows, generated, hashlib.sha256(raw).hexdigest()


def strict_snapshot_files(base, rows, inventory, required, generated, clock):
    # Same ordinary file/device checks as frozen base.mapped. Only the already
    # classified exact two ranges are separate. Hash each distinct body per snapshot.
    import mmap
    seen = set()
    checked = {}
    exempt = generated['mappings'] if generated is not None else []
    for row in rows:
        base.left(clock)
        if row in exempt:
            continue
        path = row['pathname']
        if path is None or not path.startswith('/'):
            continue  # Preserve legacy anonymous/bracket-map policy; no new allowance.
        device = tuple(int(x,16) for x in row['device'].split(':'))
        if path in base.GRAPHICS['devices']:
            info = base.device_identity(path)
            if (info != base.GRAPHICS['devices'][path] or row['inode'] != info['inode']
                    or device != (os.major(info['device']),os.minor(info['device']))):
                raise ValueError('mapped graphics device identity differs')
            seen.add(path)
            continue
        if path.endswith(' (deleted)') or path not in inventory:
            raise ValueError('unqualified mapped file: '+path)
        if path not in checked:
            info = base.regular(path,inventory[path])
            with open(path,'rb') as stream:
                with mmap.mmap(stream.fileno(),min(4096,info.st_size),access=mmap.ACCESS_READ):
                    local = [line.split(maxsplit=5) for line in Path('/proc/self/maps').read_text().splitlines()]
                    if not any(len(x)==6 and x[5]==path
                               and tuple(int(y,16) for y in x[3].split(':'))==device
                               and int(x[4])==row['inode'] for x in local):
                        raise ValueError('mapped device/inode differs')
            checked[path] = (info, device)
        info, verified_map_device = checked[path]
        if row['inode']!=info.st_ino or device!=verified_map_device:
            raise ValueError('mapped regular-file identity differs')
        seen.add(path)
    if not set(required)<=seen:
        raise ValueError('required pinned provider not mapped')
    base.left(clock)
    return sorted(seen)


def generated_context_mapped(base, proc, birth, role, image, inventory, required, clock, packet):
    require_generated_role(role,image)
    verify_graphics(base,packet['graphics'],packet['hostInputs'])
    if role=='nested':
        verify_private_provider(base, packet['nested'])
    context_before = owned_context(base,proc,birth,image,clock)
    before, first, first_sha = generated_snapshot(base,proc,clock)
    seen = strict_snapshot_files(base,before,inventory,required,first,clock)
    middle = owned_context(base,proc,birth,image,clock)
    after, second, second_sha = generated_snapshot(base,proc,clock)
    seen_after = strict_snapshot_files(base,after,inventory,required,second,clock)
    if first is not None or second is not None:
        nvidia = {str(Path('/usr/lib/libEGL_nvidia.so.0').resolve()), '/usr/lib/libnvidia-eglcore.so.615.78.08'}
        if not nvidia <= set(seen) & set(seen_after):
            raise ValueError('generated object lacks the exact mapped NVIDIA context')
    context_after = owned_context(base,proc,birth,image,clock)
    require_generated_stability(context_before,middle,first,second)
    require_generated_stability(context_before,context_after,first,second)
    verify_graphics(base,packet['graphics'],packet['hostInputs'])
    base.left(clock)
    return dict(role=role,identity=context_before,completeBeforeSha256=first_sha,
                completeAfterSha256=second_sha,mapCountBefore=len(before),mapCountAfter=len(after),
                staticMappings=seen,staticMappingsAfter=seen_after,generatedObject=second,
                firstGeneratedObservation=first,ownedBeforeAndAfter=True,
                generatedContentsRead=False,creatorAttested=False,legacyAnonymousPolicyUnchanged=True)


def failure_census_context(base, proc, birth, image, clock):
    value = owned_context(base, proc, birth, image, clock)
    value = dict(value, executableLink=os.readlink(Path('/proc', str(proc.pid), 'exe')))
    base.check_process(proc, birth, image)
    base.left(clock)
    return value


def capture_failure_census(base, proc, birth, image, inventory, clock, sink):
    # Diagnostic data only. Neither these rows nor their completeness grant a mapping exception.
    sink.update(complete=False, qualification=False, snapshots=[], mapsByteCap=MAPS_CAP,
                mapsEntryCap=MAP_ENTRIES_CAP, snapshotLimit=2, originalDeadline=clock.get('deadline'))
    base.left(clock)
    expected = None
    for index in range(2):
        before = failure_census_context(base, proc, birth, image, clock)
        if expected is not None and before != expected:
            raise ValueError('failure census owned identity changed between snapshots')
        item = dict(index=index, identityBefore=before, complete=False)
        sink['snapshots'].append(item)
        base.left(clock)
        with Path('/proc', str(proc.pid), 'maps').open('rb') as stream:
            raw = stream.read(MAPS_CAP + 1)
        item.update(raw=raw[:MAPS_CAP].decode('utf-8', errors='surrogateescape'),
                    truncated=len(raw)>MAPS_CAP, bytesRead=len(raw))
        rows = parse_complete_maps(raw)
        item.update(rows=rows, sha256=hashlib.sha256(raw).hexdigest(),
                    unlistedAbsolutePaths=sorted({row['pathname'] for row in rows
                        if (row['pathname'] or '').startswith('/') and row['pathname'] not in inventory}))
        after = failure_census_context(base, proc, birth, image, clock)
        item['identityAfter'] = after
        if before != after:
            raise ValueError('failure census owned identity changed across snapshot')
        base.left(clock)
        item['complete'] = True
        expected = before
    base.left(clock)
    sink['mapsChangedBetweenSnapshots'] = sink['snapshots'][0]['sha256'] != sink['snapshots'][1]['sha256']
    sink['complete'] = True


def nested_mapped_with_failure_census(base, proc, birth, image, inventory, required, clock, packet, result):
    try:
        return generated_context_mapped(base, proc, birth, 'nested', image, inventory, required, clock, packet)
    except Exception:
        census = result.setdefault('nestedFailureMaps', {})
        try:
            capture_failure_census(base, proc, birth, image, inventory, clock, census)
        except Exception as problem:
            census['complete'] = False
            census['captureError'] = type(problem).__name__ + ': ' + str(problem)
        raise  # Preserve the original strict failure even when capture is incomplete or unavailable.


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def unique(pairs):
    d={}
    for k,v in pairs:
        if k in d:raise ValueError('duplicate JSON key')
        d[k]=v
    return d


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:raise ValueError('fixed helper missing')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def write_nested_config(output):
    path=output/'hyprland-ux003.lua'
    with path.open('xb') as stream:stream.write(NESTED_LUA.encode('utf-8'))
    if sha(path)!=NESTED_LUA_SHA:raise ValueError('literal current Lua config write differs')
    return path


def nested_argv(image,output):
    return [image,'--config',str(output/'hyprland-ux003.lua')]


def decode_config_errors(raw):
    if not isinstance(raw,bytes) or not raw or len(raw)>CAP:
        raise ValueError('bounded actual config-errors response required')
    value=json.loads(raw.decode('utf-8'),object_pairs_hook=unique)
    # Pinned acc1aa + hyprutils0.14.3 serializes no errors as one empty string.
    # Keep the raw wire in the receipt; normalize only these exact zero-error values.
    if not isinstance(value,list) or value not in ([], ['']):
        raise ValueError('actual current Lua configuration has errors or invalid reply')
    return []


def retain_config_reply(diagnostic, raw, eof=False):
    diagnostic.update(responseHex=bytes(raw[:CAP]).hex(), responseBytesObserved=len(raw),
                      responseTruncated=len(raw)>CAP, responseEOF=eof)


def read_config_errors(base,runtime,proc,born,image,clock,diagnostic=None):
    if diagnostic is None:diagnostic={}
    diagnostic.update(request='j/configerrors', pid=proc.pid, startTicks=born, image=image,
                      byteCap=CAP, originalDeadline=clock.get('deadline'), peerValidated=False,
                      socketStable=False, ownedAfterRead=False, decodeAccepted=False,
                      configSha256=NESTED_LUA_SHA)
    retain_config_reply(diagnostic,b'')
    # The only IPC command is a read-only query on this retained child's socket.
    # Source: Hyprland v0.57.1 ipc/s1 parses j/ as JSON and closes configerrors replies.
    while True:
        base.left(clock);base.check_process(proc,born,image);base.left(clock)
        sockets=list((runtime/'hypr').glob('*/.socket.sock'))
        if sockets:break
        time.sleep(min(0.01,base.left(clock)))
    if len(sockets)!=1:raise ValueError('ambiguous private nested config IPC socket')
    path=sockets[0]
    if path.resolve()!=path:raise ValueError('aliased nested config IPC socket')
    before=path.lstat()
    diagnostic.update(path=str(path),device=before.st_dev,inode=before.st_ino,uid=before.st_uid)
    if not stat.S_ISSOCK(before.st_mode) or before.st_uid!=os.getuid():
        raise ValueError('foreign nested config IPC socket')
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as peer:
        peer.settimeout(base.left(clock));peer.connect(str(path))
        pid,uid,_=struct.unpack('3i',peer.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
        diagnostic['peer']={'pid':pid,'uid':uid}
        if pid!=proc.pid or uid!=os.getuid():raise ValueError('nested config IPC peer differs')
        diagnostic['peerValidated']=True
        base.check_process(proc,born,image);peer.settimeout(base.left(clock))
        peer.sendall(b'j/configerrors')
        raw=bytearray()
        while True:
            peer.settimeout(base.left(clock));part=peer.recv(min(4096,CAP+1-len(raw)))
            if not part:
                retain_config_reply(diagnostic,raw,True)
                break
            raw.extend(part)
            retain_config_reply(diagnostic,raw)
            if len(raw)>CAP:raise ValueError('config IPC output exceeds bound')
    after=path.lstat()
    if (before.st_dev,before.st_ino,before.st_uid)!=(after.st_dev,after.st_ino,after.st_uid):
        raise ValueError('nested config IPC socket replaced')
    diagnostic['socketStable']=True
    base.check_process(proc,born,image);base.left(clock)
    diagnostic['ownedAfterRead']=True
    errors=decode_config_errors(bytes(raw))
    base.check_process(proc,born,image);base.left(clock)
    diagnostic['decodeAccepted']=True
    return {'path':str(path),'device':after.st_dev,'inode':after.st_ino,'pid':proc.pid,
            'startTicks':born,'request':'j/configerrors','responseHex':bytes(raw).hex(),'errors':errors,
            'configSha256':NESTED_LUA_SHA}


def host_argv(image,output):
    return [image,'--config-dir',str(output/'labwc-config'),'--config',str(output/'labwc-config/rc.xml')]


def apply_private_glib_environment(env):
    # GLib's built-in memory backend keeps settings in-process, without dconf backing storage.
    # Callers provide their already isolated environment; this function never inherits os.environ.
    return dict(env, GSETTINGS_BACKEND='memory')


def host_environment(runtime,output,library_dirs):
    # No host session endpoints, autostart search, PATH helpers or inherited renderer overrides.
    return {'PATH':'/nonexistent','LANG':'C.UTF-8','LC_ALL':'C.UTF-8',
            'HOME':str(output/'home'),'XDG_CONFIG_HOME':str(output/'config'),
            'XDG_CONFIG_DIRS':str(output/'empty-config'),'XDG_DATA_HOME':str(output/'data'),
            'XDG_DATA_DIRS':str(output/'empty-data'),'XDG_CACHE_HOME':str(output/'cache'),
            'XDG_RUNTIME_DIR':str(runtime),'DBUS_SESSION_BUS_ADDRESS':'unix:path='+str(runtime/'no-bus'),
            'LABWC_UPDATE_ACTIVATION_ENV':'false','WLR_BACKENDS':'headless',
            'WLR_HEADLESS_OUTPUTS':'1','WLR_RENDERER':'gles2',
            'WLR_RENDER_DRM_DEVICE':'/dev/dri/renderD128',
            '__EGL_VENDOR_LIBRARY_FILENAMES':'/usr/share/glvnd/egl_vendor.d/10_nvidia.json',
            'EGL_PLATFORM':'surfaceless','LD_LIBRARY_PATH':':'.join(library_dirs),
            'FONTCONFIG_FILE':str(output/'fonts.conf'),'FONTCONFIG_PATH':str(output/'empty-config'),
            'FONTCONFIG_USE_MMAP':'0'}


def font_config(output):
    return ('<?xml version="1.0"?><fontconfig><dir>'+str(output/'font')+
            '</dir><cachedir>'+str(output/'font-cache')+
            '</cachedir><config><rescan><int>0</int></rescan></config></fontconfig>\n')


def output_state(value,require_mode):
    if not isinstance(value,list) or len(value)!=1 or not isinstance(value[0],dict):
        raise ValueError('exact one actual headless output required')
    h=value[0]
    if (not isinstance(h.get('name'),str) or not re.fullmatch(r'HEADLESS-[1-9][0-9]{0,2}',h['name'])
            or h.get('enabled') is not True):
        raise ValueError('enabled headless output required')
    if require_mode:
        modes=h.get('modes')
        if (not isinstance(modes,list) or len(modes)>256
                or any(not isinstance(x,dict) for x in modes)):
            raise ValueError('bounded observed mode list required')
        current=[x for x in modes if x.get('current') is True]
        if len(current)!=1:raise ValueError('exact one observed current mode required')
        mode=current[0]
        if (type(mode.get('width')) is not int or type(mode.get('height')) is not int
                or (mode['width'],mode['height'])!=(1280,800)
                or type(h.get('scale')) not in (int,float) or h['scale']!=1
                or h.get('transform')!='normal' or h.get('position')!={'x':0,'y':0}
                or any(type(h['position'][k]) is not int for k in ('x','y'))):
            raise ValueError('actual 1280x800 scale1 normal origin0 readback required')
    return h


def output_apply(image,name):
    if not re.fullmatch(r'HEADLESS-[1-9][0-9]{0,2}',name):raise ValueError('foreign output selector')
    return [image,'--output',name,'--on','--custom-mode','1280x800@60Hz',
            '--scale','1','--transform','normal','--pos','0,0']


def packet_template():
    return dict(schema=1,kind='arm-private-labwc-gl-foundation-v1',armed=False,
                expiresUTC=EXPIRES_UTC,host=None,hostInputs={},sourceInputs={},readiness=None,nested=None,graphics=None)


def packet_shape(p):
    keys=set(packet_template())
    if (not isinstance(p,dict) or set(p)!=keys or p.get('schema')!=1 or p.get('armed') is not True
            or p.get('kind')!='arm-private-labwc-gl-foundation-v1' or p.get('expiresUTC')!=EXPIRES_UTC):
        raise ValueError('fixed independently reviewed packet not armed')
    host=p.get('host')
    if (not isinstance(host,dict) or set(host)!={'labwc','wlroots','outputTool','libraryDirs','buildReport','outputToolSource','wlrootsLookup'}
            or any(not isinstance(host.get(k),str) or not Path(host[k]).is_absolute() for k in ('labwc','wlroots','outputTool'))
            or not isinstance(host['libraryDirs'],list) or not 1<=len(host['libraryDirs'])<=4
            or any(not isinstance(x,str) or not Path(x).is_absolute() or ':' in x or Path(x).resolve()!=Path(x)
                   for x in host['libraryDirs'])
            or not p['hostInputs'] or not p['sourceInputs'] or p['nested'] is None):
        raise ValueError('closed Labwc tuple and nested provider required')
    if any(host[k] not in p['hostInputs'] for k in ('labwc','wlroots','outputTool')):
        raise ValueError('executable/provider/tool absent from host closure')
    if p['sourceInputs'].get(str(BASE_PATH))!=BASE_SHA:
        raise ValueError('exact unchanged reusable guard helper required')
    if set(p['nested'])!={'compositor','backend','inputs','libraryDir','buildReport','sourceReview'}:
        raise ValueError('fixed reviewed nested tuple required')


def regular_ref(base,ref):
    if set(ref)!={'path','sha256'}:raise ValueError('fixed hash reference required')
    base.regular(ref['path'],ref['sha256'])
    return json.loads(Path(ref['path']).read_text(),object_pairs_hook=unique)


def verify_graphics(base,graphics,inventory):
    # Preserve signed/current NVIDIA device/vendor tuple; Weston renderer is not a Labwc input.
    expected={k:v for k,v in base.GRAPHICS.items() if k!='renderer'}
    expected['files']={k:v for k,v in expected['files'].items() if k!=base.GRAPHICS['renderer']}
    if graphics!=expected or any(inventory.get(k)!=v for k,v in graphics['files'].items()):
        raise ValueError('explicit unchanged NVIDIA tuple required')
    for path,pin in graphics['devices'].items():
        if base.device_identity(path)!=pin:raise ValueError('graphics device drift')
    if sha(graphics['driver']['path'])!=graphics['driver']['sha256']:raise ValueError('driver binding drift')
    for path,target in graphics['aliases'].items():
        if str(Path(path).resolve(strict=True))!=target:raise ValueError('graphics alias drift')
    for path,pin in graphics['files'].items():base.regular(path,pin)


def validate_build_report(report):
    commands=report.get('commands')
    if (report.get('passed') is not True or not isinstance(commands,list)
            or [x.get('name') for x in commands]!=['configure','compile','inspect']
            or any(type(x.get('exitCode')) is not int or x['exitCode']!=0
                   or x.get('timedOut') is not False or x.get('forcedCleanup') is not False
                   or x.get('groupAbsent') is not True for x in commands)):
        raise ValueError('exact three normal completed builder commands required')


def require_caps(globals_):
    if any(type(globals_.get(k)) is not int or globals_[k]<v for k,v in REQUIRED.items()):
        raise ValueError('observed registry lacks mandatory6/9/6/DMA4')


def checked_spawn(base,clock,inventory,create):
    base.left(clock)
    for path,pin in inventory.items():base.regular(path,pin)
    base.left(clock)  # Hashing cannot extend original D; immediately before Popen.
    return create()


def record_host_observed(base,clock,result,last_check):
    last_check()  # Includes actual live process/image hash, not a caller fact.
    base.left(clock)
    result['hostObserved']=True


def verify_wlroots_lookup(base,host,inventory,build_sources):
    library=Path(host['wlroots'])
    try:resolved=library.resolve(strict=True)
    except OSError as error:raise ValueError('private wlroots body missing or broken alias') from error
    if resolved!=library or library.parent!=PRIVATE_LIB:
        raise ValueError('actual build-prefix private wlroots body required')
    if inventory.get(str(library)) is None or build_sources.get(str(library))!=inventory[str(library)]:
        raise ValueError('runtime private wlroots differs from actual build input')
    candidates=[Path(x)/'libwlroots-0.20.so' for x in host['libraryDirs']]
    if len(set(candidates))!=len(candidates) or not candidates or candidates[0].parent!=PRIVATE_LIB:
        raise ValueError('private build prefix must be first fixed loader directory')
    expected=host.get('wlrootsLookup')
    if not isinstance(expected,dict) or set(expected)!={str(x) for x in candidates}:
        raise ValueError('exact loader candidate membership required')
    found=[]
    for candidate in candidates:
        if candidate.exists() or candidate.is_symlink():
            try:target=candidate.resolve(strict=True)
            except OSError as error:raise ValueError('private loader alias broken') from error
            actual={'target':str(target),'link':os.readlink(candidate) if candidate.is_symlink() else None}
            if target!=library or expected[str(candidate)]!=actual:
                raise ValueError('private wlroots loader alias/body changed')
            base.regular(target,inventory[str(library)])
            found.append(candidate)
        elif expected[str(candidate)] is not None:
            raise ValueError('expected private loader entry missing')
    if len(found)!=1 or found[0]!=candidates[0]:
        raise ValueError('missing or additional wlroots loader candidate')


def verify_build(base,p):
    h=p['host'];report=regular_ref(base,h['buildReport'])
    # Report envelope is the fixed builder's protected success receipt, not an input Boolean grant.
    validate_build_report(report)
    build=report.get('labwcBuild',{})
    if build.get('target')!='labwc' or build.get('xwayland') is not False or build.get('executed') is not False:
        raise ValueError('Xwayland-disabled Labwc build binding absent')
    image=build.get('image',{})
    info=base.regular(h['labwc'],p['hostInputs'][h['labwc']])
    if image!={'path':h['labwc'],'sha256':p['hostInputs'][h['labwc']],
              'size':info.st_size,'device':info.st_dev,'inode':info.st_ino,'mode':stat.S_IMODE(info.st_mode)}:
        raise ValueError('actual built Labwc image identity changed')
    raw=Path(h['labwc']).read_bytes()[:20]
    if raw[:7]!=b'\x7fELF\x02\x01\x01' or raw[18:20]!=b'\xb7\x00':raise ValueError('built host not ELF64LE AArch64')
    inspection=Path(h['labwc']).parent.parent/'inspect.stdout'
    base.regular(inspection,build['dynamicInspectionSha256'])
    dynamic=inspection.read_text()
    if '(RPATH)' in dynamic:raise ValueError('DT_RPATH may bypass explicit private loader order')
    runpaths=re.findall(r'\(RUNPATH\).*\[([^]]*)\]',dynamic)
    if len(runpaths)>1 or any(not x or x not in h['libraryDirs'] for value in runpaths for x in value.split(':')):
        raise ValueError('unqualified runtime loader search path')
    source=regular_ref(base,h['outputToolSource'])
    if source.get('tool')!='wlr-randr' or source.get('version')!='0.5.0' or source.get('jsonCurrentModeReviewed') is not True:
        raise ValueError('primary output-manager JSON/control correspondence missing')
    if source.get('binary')!={'path':h['outputTool'],'sha256':p['hostInputs'][h['outputTool']]}:
        raise ValueError('output-manager source correspondence bound to another image')
    base.regular(source['mainSource']['path'],source['mainSource']['sha256'])
    regular_ref(base,source['signedPackageReceipt'])
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--sha256',required=True);args=parser.parse_args()
    # Import only the exact existing reviewed pure guards; never replace their globals/functions.
    if sha(BASE_PATH)!=BASE_SHA:raise ValueError('guard source drift')
    base=load('unchanged_gl_guards',BASE_PATH)
    base.regular(PACKET,args.sha256);p=json.loads(PACKET.read_text(),object_pairs_hook=unique);packet_shape(p)
    if p['sourceInputs'].get(str(Path(__file__).resolve()))!=sha(__file__):raise ValueError('collector source not included in actual packet')
    for path,pin in {**p['sourceInputs'],**p['hostInputs']}.items():base.regular(path,pin)
    if p['hostInputs'].get(str(FONT))!=FONT_SHA:raise ValueError('fixed font body absent from exact input closure')
    verify_graphics(base,p['graphics'],p['hostInputs']);build_report=verify_build(base,p)
    verify_wlroots_lookup(base,p['host'],p['hostInputs'],build_report['sourceHashes'])
    verify_private_provider(base, p['nested'])
    review=regular_ref(base,p['readiness'])
    if (review.get('disposition')!='accepted' or review.get('scope')!='arm-private-labwc-generated-runtime-foundation'
            or review.get('generatedRuntimeImages')!=GENERATED_IMAGES
            or review.get('generatedRuntimeMutableNotCreatorAttested') is not True
            or any(review.get(k)!=p[k] for k in ('host','hostInputs','sourceInputs','nested','graphics'))):
        raise ValueError('exact independent native readiness required')
    qa_path=ROOT/'window-integration-qa/qa_launch.py';base.regular(qa_path,QA_SHA)
    qa=load('labwc_protected_scope',qa_path);scope=qa.require_qa_scope()
    if time.time_ns()+OPERATION_NS+CLEANUP_NS>=EXPIRES:raise ValueError('insufficient original15+2 before cutoff')
    start=time.monotonic_ns();clock={'deadline':start+OPERATION_NS,'last':start,
                                    'boot':Path('/proc/sys/kernel/random/boot_id').read_text().strip()}
    os.umask(0o077);output=ROOT/'.warlock-contributor'/('labwc-gl-foundation-'+str(time.time_ns()));output.mkdir(mode=0o700)
    for name in ('home','config','cache','data','empty-config','empty-data','labwc-config','font','font-cache'):(output/name).mkdir(mode=0o700)
    base.regular(FONT,FONT_SHA);font_copy=output/'font/LiberationSans-Regular.ttf'
    shutil.copyfile(FONT,font_copy);base.regular(font_copy,FONT_SHA)
    (output/'fonts.conf').write_text(font_config(output))
    (output/'labwc-config/rc.xml').write_text(RC)
    nested_config=write_nested_config(output)
    runtime=qa.private_runtime();children=[];logs=[]
    qa.verify_runtime(runtime);runtime_stat=runtime.lstat()
    runtime_created={'path':str(runtime),'device':runtime_stat.st_dev,'inode':runtime_stat.st_ino,
                     'uid':runtime_stat.st_uid,'mode':stat.S_IMODE(runtime_stat.st_mode)}
    (output/'runtime-created.json').write_text(json.dumps(runtime_created,indent=2)+'\n')
    result=dict(schema=1,kind='labwc-gl-foundation-observation',scope=scope,packetSha256=args.sha256,
                clock=dict(clock),nestedConfig={'path':str(nested_config),'sha256':sha(nested_config)},hostObserved=False,nestedObserved=False,outputModeObserved=False,
                cleanup=False,forcedCleanup=False,originalAcceptance=False,nativeJourneyAccepted=False,processes=[],
                runtime={'creation':runtime_created,'removalAttempted':False,'removedByCollector':False})

    def left():return base.left(clock)

    def spawn(role,argv,env,inventory):
        left()
        if role=='host':verify_wlroots_lookup(base,p['host'],p['hostInputs'],build_report['sourceHashes'])
        out,err=output/(role+'.stdout'),output/(role+'.stderr');so,se=out.open('xb'),err.open('xb');logs.extend([so,se])
        child=checked_spawn(base,clock,inventory,lambda: subprocess.Popen(
            argv,env=env,stdin=subprocess.DEVNULL,stdout=so,stderr=se,
            close_fds=True,start_new_session=True,preexec_fn=base.bound_output))
        children.append((child,None,role));born=base.process_birth(child.pid);children[-1]=(child,born,role)
        result['processes'].append(dict(role=role,pid=child.pid,startTicks=born,argv=argv))
        return child,born

    def host_live():
        left();base.check_process(host,born,p['hostInputs'][h['labwc']])
        if any(os.fstat(x.fileno()).st_size>CAP for x in logs):raise ValueError('bounded output exceeded')

    def control(role,argv,env):
        child,cb=spawn(role,argv,env,p['hostInputs'])
        while child.poll() is None:
            host_live();time.sleep(min(0.01,left()))
        if child.wait(timeout=left())!=0:raise ValueError('output-manager command refused')
        host_live();raw=(output/(role+'.stdout')).read_bytes()
        if len(raw)>CAP:raise ValueError('output-manager JSON exceeds cap')
        return raw

    try:
        h=p['host'];env=host_environment(runtime,output,h['libraryDirs'])
        host,born=spawn('host',host_argv(h['labwc'],output),env,p['hostInputs'])
        sockets=[]
        while not sockets:
            host_live();sockets=[x for x in runtime.glob('wayland-*') if stat.S_ISSOCK(x.lstat().st_mode)]
            if not sockets:time.sleep(min(0.02,left()))
        if len(sockets)!=1:raise ValueError('ambiguous private Labwc socket')
        host_socket=sockets[0]
        registry=base.registry(host_socket,host,born,p['hostInputs'][h['labwc']],clock)
        require_caps(registry['globals'])
        cenv=dict(env,WAYLAND_DISPLAY=str(host_socket))
        initial=output_state(json.loads(control('output-before',[h['outputTool'],'--json'],cenv),object_pairs_hook=unique),False)
        control('output-apply',output_apply(h['outputTool'],initial['name']),cenv)
        final=output_state(json.loads(control('output-after',[h['outputTool'],'--json'],cenv),object_pairs_hook=unique),True)
        if final['name']!=initial['name']:raise ValueError('output identity/name changed')
        result['outputBefore']=initial;result['outputAfter']=final;result['outputModeObserved']=True
        result['host']=base.registry(host_socket,host,born,p['hostInputs'][h['labwc']],clock)
        if any(result['host'][k]!=registry[k] for k in ('path','device','inode','pid','startTicks')):
            raise ValueError('host socket/custody changed during output negotiation')
        result['hostGeneratedRuntime']=generated_context_mapped(base,host,born,'host',p['hostInputs'][h['labwc']],
            dict(p['hostInputs'],**{str(font_copy):FONT_SHA}),[h['labwc'],h['wlroots'],
            str(Path('/usr/lib/libEGL_nvidia.so.0').resolve()),'/usr/lib/libnvidia-eglcore.so.615.78.08'],clock,p)
        result['hostMappings']=result['hostGeneratedRuntime']['staticMappingsAfter']
        result['fontBinding']={'source':str(FONT),'sourceSha256':FONT_SHA,'copy':str(font_copy),
                               'copySha256':sha(font_copy),'configSha256':sha(output/'fonts.conf'),'cacheMmapDisabled':True}
        result['hostGraphicsFDs']=base.graphics_fds(host,born,p['hostInputs'][h['labwc']])
        verify_graphics(base,p['graphics'],p['hostInputs'])
        record_host_observed(base,clock,result,host_live)
        nested=p['nested'];verify_private_provider(base, nested)
        nenv=apply_private_glib_environment(base.graphics_environment(runtime,output));nenv['WAYLAND_DISPLAY']=str(host_socket);nenv['LD_LIBRARY_PATH']=nested['libraryDir']
        compositor,nb=spawn('nested',nested_argv(nested['compositor'],output),nenv,nested['inputs'])
        sockets=[]
        while not sockets:
            host_live();base.check_process(compositor,nb,nested['inputs'][nested['compositor']])
            sockets=[x for x in runtime.glob('wayland-*') if x!=host_socket and stat.S_ISSOCK(x.lstat().st_mode)]
            if not sockets:time.sleep(min(0.02,left()))
        if len(sockets)!=1:raise ValueError('ambiguous private nested socket')
        result['nested']=base.registry(sockets[0],compositor,nb,nested['inputs'][nested['compositor']],clock)
        require_caps(result['nested']['globals'])
        result['nestedGeneratedRuntime']=nested_mapped_with_failure_census(base,compositor,nb,nested['inputs'][nested['compositor']],
            nested['inputs'],[nested['compositor'],nested['backend']],clock,p,result)
        result['nestedMappings']=result['nestedGeneratedRuntime']['staticMappingsAfter']
        result['nestedGraphicsFDs']=base.graphics_fds(compositor,nb,nested['inputs'][nested['compositor']])
        result['nestedConfigErrors']=read_config_errors(base,runtime,compositor,nb,nested['inputs'][nested['compositor']],clock,
            result.setdefault('nestedConfigErrorsDiagnostic',{}))
        if sha(nested_config)!=NESTED_LUA_SHA:raise ValueError('nested Lua config changed during trial')
        host_live();verify_graphics(base,p['graphics'],p['hostInputs']);left();result['nestedObserved']=True
    except Exception as problem:
        result['error']=str(problem)
    finally:
        ceiling=clock['deadline']+CLEANUP_NS;clean=True
        for child,cb,role in reversed(children):
            forced=False;requested=None
            try:
                if child.poll() is None:
                    if cb is None or base.process_birth(child.pid)!=cb:raise ValueError('owned cleanup birth unknown')
                    requested='SIGTERM';os.killpg(child.pid,signal.SIGTERM)
                    budget=min(ceiling-1_000_000_000-time.monotonic_ns(),EXPIRES-time.time_ns())/1e9
                    try:
                        if budget<=0:raise subprocess.TimeoutExpired(child.args,0)
                        child.wait(timeout=budget)
                    except subprocess.TimeoutExpired:
                        forced=True;os.killpg(child.pid,signal.SIGKILL)
                        budget=min(ceiling-time.monotonic_ns(),EXPIRES-time.time_ns())/1e9
                        if budget<=0:raise TimeoutError('cleanup ceiling exhausted')
                        child.wait(timeout=budget)
                gone=False
                try:os.killpg(child.pid,0)
                except ProcessLookupError:gone=True
                clean=clean and child.returncode==0 and gone and not forced
                result['processes'].append(dict(role=role,exit=child.returncode,reaped=child.returncode is not None,
                                               requestedTermination=requested,groupAbsent=gone,forced=forced))
            except Exception as problem:
                clean=False;result.setdefault('cleanupErrors',[]).append(str(problem))
            result['forcedCleanup']=result['forcedCleanup'] or forced
        for stream in logs:stream.close()
        if clean:
            try:
                qa.verify_runtime(runtime);info=runtime.lstat()
                actual={'path':str(runtime),'device':info.st_dev,'inode':info.st_ino,
                        'uid':info.st_uid,'mode':stat.S_IMODE(info.st_mode)}
                if actual!=runtime_created:raise ValueError('runtime creation identity changed')
                result['runtime']['removalAttempted']=True
                shutil.rmtree(runtime);clean=not runtime.exists()
                result['runtime']['removedByCollector']=clean
            except Exception as problem:clean=False;result.setdefault('cleanupErrors',[]).append(str(problem))
        result['runtime']['pathPresentAfterCleanup']=runtime.exists()
        result['cleanup']=clean;result['passed']=result['hostObserved'] and result['outputModeObserved'] and result['nestedObserved'] and clean and 'error' not in result
        (output/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=result['passed'],report=str(output/'report.json'))))
    return 0 if result['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
