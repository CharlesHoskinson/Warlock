"""Static source-bound native staging manifest. Never execute a staged product image."""
import hashlib
import json
import os
from pathlib import Path
import re
import stat

TARGETS = (
    ('warlock-ui-backend', 'warlock-runtime:exe:warlock-ui-backend'),
    ('warlock-ui-owner', 'warlock-runtime:exe:warlock-ui-owner'),
    ('application-argv-fixture', 'warlock-runtime:exe:application-argv-fixture'),
)
HELPERS = (
    '/usr/lib/webkitgtk-6.0/WebKitNetworkProcess',
    '/usr/lib/webkitgtk-6.0/WebKitWebProcess',
    '/usr/lib/webkitgtk-6.0/injected-bundle/libwebkitgtkinjectedbundle.so',
    '/usr/bin/bwrap',
    '/usr/bin/xdg-dbus-proxy',
)
READELF = '/usr/bin/readelf'
# Exact current system image bytes only; this is not a general RUNPATH waiver.
APPROVED_RUNPATHS = {
    ('/usr/lib/libsqlite3.so.3.54.1', '3009375a8361a58b6f7e75cd66ab706d218aeff37d30c26501170f29154ef6e2'): ('/usr/lib',),
    ('/usr/lib/libjpeg.so.8.3.2', '2d500d82dd923ed8c91ab6029aa7b733f7bcda7e46160f7e53fd19e16dbbefab'): ('/usr/lib',),
    ('/usr/lib/libtinysparql-3.0.so.0.1200.0', '4794555fcee7375ad8c75e7bb31c9afff001b227190cd1c6d62d02cdbb6571d7'): ('/usr/lib/tinysparql-3.0',),
}
PRIVATE_RUNPATH = '/usr/lib/tinysparql-3.0'
PRIVATE_ENTRIES = ('libtracker-http-soup3.so', 'libtracker-parser-libicu.so')


def elf_header(data):
    if (len(data) < 64 or data[:7] != b'\x7fELF\x02\x01\x01'
            or int.from_bytes(data[18:20], 'little') != 183
            or int.from_bytes(data[16:18], 'little') not in (2, 3)):
        raise ValueError('Expected ELF64 little-endian AArch64 executable/shared image')
    return {'class': 'ELF64', 'byteOrder': 'little', 'machine': 'AArch64',
            'type': int.from_bytes(data[16:18], 'little')}


def approved_runpath(text, image_path=None, image_sha256=None):
    if re.search(r'\(RPATH\)', text):
        raise ValueError('RPATH remains unsupported')
    markers = re.findall(r'\(RUNPATH\)', text)
    rows = re.findall(r'\(RUNPATH\)[^\n]*\[([^\]]*)\]', text)
    if not markers:
        return ()
    if len(markers) != 1 or len(rows) != 1:
        raise ValueError('RUNPATH is malformed or ambiguous')
    expected = APPROVED_RUNPATHS.get((str(image_path), image_sha256))
    actual = tuple(rows[0].split(':'))
    if expected is None or actual != expected:
        raise ValueError('RUNPATH image/hash/value lacks the exact reviewed recipe')
    return actual


def library_recipe(name, runpaths):
    if re.fullmatch(r'[A-Za-z0-9_+.-]+', name) is None or name in ('.', '..'):
        raise ValueError('NEEDED must be a fixed basename')
    if runpaths not in ((), ('/usr/lib',), (PRIVATE_RUNPATH,)):
        raise ValueError('No reviewed RUNPATH resolution recipe')
    # The only private RUNPATH has NO reviewed private DT_NEEDED candidate.
    # A newly present file or symlink must fail, even if its basename looks safe.
    absent = [PRIVATE_RUNPATH + '/' + name] if runpaths == (PRIVATE_RUNPATH,) else []
    return '/usr/lib/' + name, absent


def readelf_dependencies(text, image_path=None, image_sha256=None):
    approved_runpath(text, image_path, image_sha256)
    needed = re.findall(r'\(NEEDED\)[^\n]*\[([^\]]+)\]', text)
    if len(needed) != len(set(needed)) or any(re.fullmatch(r'[A-Za-z0-9_+.-]+', name) is None
            or name in ('.', '..') for name in needed):
        raise ValueError('Ambiguous or non-basename ELF NEEDED')
    interpreters = re.findall(r'\[Requesting program interpreter:\s*([^\]]+)\]', text)
    if len(interpreters) > 1 or (interpreters and interpreters[0] not in ('/lib/ld-linux-aarch64.so.1', '/usr/lib/ld-linux-aarch64.so.1')):
        raise ValueError('Unsupported or ambiguous AArch64 interpreter')
    return needed, interpreters[0] if interpreters else None


def pin(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError('Expected non-symlink physical image: ' + str(path))
    with path.open('rb') as stream:
        before = os.fstat(stream.fileno())
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        after = os.fstat(stream.fileno())
    fields = ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
    if any(getattr(before, name) != getattr(after, name) for name in fields):
        raise ValueError('Image changed during pinning')
    return {'path': str(path), 'device': str(before.st_dev), 'inode': str(before.st_ino),
            'size': str(before.st_size), 'sha256': digest, 'mode': stat.S_IMODE(before.st_mode)}


def system_image(logical, system):
    path = Path('/usr/lib/ld-linux-aarch64.so.1') if logical == '/lib/ld-linux-aarch64.so.1' else Path(logical)
    aliases = []
    for _ in range(16):
        if not (str(path).startswith('/usr/lib/') or str(path).startswith('/usr/bin/')):
            raise ValueError('System dependency escaped fixed system roots')
        expected = system.get(str(path))
        if not isinstance(expected, dict):
            raise ValueError('System dependency not in reviewed ARM inventory: ' + str(path))
        if path.is_symlink():
            link = os.readlink(path)
            if expected != {'link': link}:
                raise ValueError('System loader/library alias differs')
            aliases.append({'path': str(path), 'link': link})
            path = Path(os.path.normpath(link if os.path.isabs(link) else str(path.parent / link)))
            continue
        observed = pin(path)
        if expected != {'mode': observed['mode'], 'sha256': observed['sha256']}:
            raise ValueError('System dependency bytes/mode differ')
        return observed, aliases
    raise ValueError('System dependency alias chain too long')



def private_directory_snapshot(system):
    path = Path(PRIVATE_RUNPATH)
    if path.is_symlink() or not path.is_dir():
        raise ValueError('Private RUNPATH directory is not physical')
    before = path.stat()
    names = tuple(sorted(p.name for p in path.iterdir()))
    if names != PRIVATE_ENTRIES:
        raise ValueError('Private RUNPATH directory entries differ from reviewed recipe')
    entries = {}
    for name in names:
        image, aliases = system_image(str(path / name), system)
        entries[name] = {'image': image, 'aliases': aliases}
    after = path.stat()
    fields = ('st_dev', 'st_ino', 'st_mtime_ns', 'st_ctime_ns')
    if any(getattr(before, field) != getattr(after, field) for field in fields):
        raise ValueError('Private RUNPATH directory changed')
    return {'path': PRIVATE_RUNPATH, 'device': str(after.st_dev), 'inode': str(after.st_ino),
            'mtimeNs': after.st_mtime_ns, 'ctimeNs': after.st_ctime_ns, 'entries': entries}


def stage_image_names(provider_probe=False):
    if type(provider_probe) is not bool:
        raise ValueError('Provider probe role must be fixed boolean')
    return {name for name, _ in TARGETS} | ({'webkit-provider-probe'} if provider_probe else set())


def collect(output, packet, binaries, documents, run, provider_probe=False):
    """Root protected builder calls only fixed readelf argv, never ELF targets."""
    if set(binaries) != stage_image_names(provider_probe) or set(documents) != {'controller', 'bar', 'popup'}:
        raise ValueError('Native stage requires exact three images and three Http documents')
    system_path = Path(packet['systemInputs'])
    expected_system = packet['files'][str(system_path)]
    if hashlib.sha256(system_path.read_bytes()).hexdigest() != expected_system:
        raise ValueError('Reviewed system inventory differs')
    system = json.loads(system_path.read_text())['files']
    readelf_pin, _ = system_image(READELF, system)
    queue = [(item['path'], 'authored-product') for item in binaries.values()]
    queue += [(name, 'fixed-system-helper') for name in HELPERS]
    nodes, aliases, edges = {}, {}, []
    before = {}
    private_snapshot = None
    required_absences = set()
    while queue:
        logical, role = queue.pop(0)
        if role == 'authored-product':
            actual = pin(logical)
            links = []
            original = next(v for v in binaries.values() if v['path'] == logical)
            if any(actual[key] != original[key] for key in ('path', 'device', 'inode', 'size', 'sha256')):
                raise ValueError('Compiled product image differs before static inspection')
        else:
            actual, links = system_image(logical, system)
        aliases[logical] = {'physical': actual['path'], 'links': links}
        physical = actual['path']
        if physical in nodes:
            continue
        if len(nodes) >= 512:
            raise ValueError('Static native ELF dependency bound exceeded')
        with Path(physical).open('rb') as stream:
            header = elf_header(stream.read(64))
        text = run('native-static-readelf-' + str(len(nodes)),
                   [READELF, '--file-header', '--program-headers', '--dynamic', '--wide', physical], timeout=30)
        needed, interpreter = readelf_dependencies(text, physical, actual['sha256'])
        runpaths = approved_runpath(text, physical, actual['sha256'])
        if runpaths == (PRIVATE_RUNPATH,) and private_snapshot is None:
            private_snapshot = private_directory_snapshot(system)
        before[physical] = actual
        nodes[physical] = {'role': role, 'image': actual, 'elf': header,
                           'needed': needed, 'interpreter': interpreter, 'approvedRunpath': list(runpaths)}
        for name in needed:
            selected, absent = library_recipe(name, runpaths)
            for candidate in absent:
                if Path(candidate).exists() or Path(candidate).is_symlink():
                    raise ValueError('Private RUNPATH candidate absence violated: ' + candidate)
                required_absences.add(candidate)
            edges.append({'from': physical, 'needed': name, 'selectedByRecipe': selected,
                          'requiredAbsentCandidates': absent})
            queue.append((selected, 'static-system-dependency'))
        if interpreter:
            edges.append({'from': physical, 'interpreter': interpreter})
            queue.append((interpreter, 'declared-loader'))
    if private_snapshot is not None and private_directory_snapshot(system) != private_snapshot:
        raise ValueError('Private RUNPATH directory inventory changed')
    if any(Path(name).exists() or Path(name).is_symlink() for name in required_absences):
        raise ValueError('Private RUNPATH candidate appeared during static inspection')
    for path, original in before.items():
        if pin(path) != original:
            raise ValueError('Inspected native dependency changed')
    if pin(READELF) != readelf_pin:
        raise ValueError('Readelf tool changed')
    for role, document in documents.items():
        actual = pin(document['path'])
        if any(actual[key] != document[key] for key in ('path', 'device', 'inode', 'size', 'sha256')):
            raise ValueError('Compiled Http document changed: ' + role)
    result = {'schema': 1, 'kind': 'aarch64-static-native-build-staging-manifest',
              'executables': binaries, 'httpDocuments': documents, 'heldSelfEngine': binaries['warlock-ui-owner'],
              'systemInventory': {'path': str(system_path), 'sha256': expected_system},
              'staticReadelfTool': readelf_pin, 'nodes': nodes, 'aliases': aliases, 'edges': edges,
              'fixedHelpers': list(HELPERS),
              'approvedRunpathRecipes': [{'path': name, 'sha256': digest, 'runpath': list(paths)}
                                         for (name, digest), paths in sorted(APPROVED_RUNPATHS.items())],
              'privateRunpathSnapshot': private_snapshot,
              'requiredAbsentCandidates': sorted(required_absences),
              'nativeExecution': False, 'providerQualified': False,
              'actualLoaderResolutionObserved': False, 'dynamicModulesComplete': False,
              'cleanupQualified': False, 'inputQualified': False, 'nativeAcceptance': False,
              'originalAcceptance': False, 'releaseAccepted': False,
              'scope': 'Static inspected DT_NEEDED and fixed helper closure using reviewed /usr/lib recipe only. '
                       'No target/native/runtime API invoked. dlopen/plugins/runtime routing and provider2.54.2 '
                       'remain separate qualification; no installed-version allowlist change.'}
    destination = Path(output) / 'native-build-stage-manifest.json'
    with destination.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    return {'path': str(destination), 'sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
            'nativeAcceptance': False, 'originalAcceptance': False, 'releaseAccepted': False}
