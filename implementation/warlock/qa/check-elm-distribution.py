"""Protected offline npm distribution correspondence, not license approval.

Raw primary responses were captured with Scrapling. Archives are parsed only as
data; neither installer scripts nor compiler binaries are executed here.
"""
import base64
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import stat
import sys
import tarfile

REPO = Path(__file__).resolve().parents[3]
INSTALLED = REPO/'implementation/warlock-preview-provider-v143/qa/toolchain/npm-package'
PACKET = Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/elm-distribution-terra1-v1')
LOCK_SHA = 'a2a339e6df901717a4fd0a4d88e1430e22d35bbe1641d339d5e4c477c93f22f0'
BINARY_SHA = 'c4db5a7ef59fc582a1df29c16383520015e9cefb0802e6eb49955e49211d7948'
PINS = {
    'elm.tgz': 'a3aea90afb69d755eb889253a3361cc03a4f924990323c27ea527c70da68d518',
    'elm.json': '6b82a9030dc678326c68484f65e8892f414370edd23f82b753f0484aee0d1fd9',
    'linux-x64.tgz': 'ea998aa56c892bf174c055059dde6c55f6fa42239569bc13b4cfa4b36745a0fd',
    'linux-x64.json': '3802386554ca42a2807265fbae5ea415c6b91772308cbeefb8f9f678ce2c55c4',
    'responses.json': 'b7f736d16d2b7bccdfbcbf6c0c19562a191ad00f9230eaf43c4976945bfa3409',
    'inventory.json': '47b4920cd1e7e8495237c44b333190ea1cac91f58950ff0f2ff4b3e42b89921f',
}
PACKAGES = (
    ('elm', 'node_modules/elm', 'elm', 'https://registry.npmjs.org/elm/0.19.2-0'),
    ('linux-x64', 'node_modules/@elm_binaries/linux_x64', '@elm_binaries/linux_x64',
     'https://registry.npmjs.org/@elm_binaries%2Flinux_x64/0.19.2-0'),
)


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'Duplicate JSON key: '+key)
        result[key] = value
    return result


def decode(body):
    return json.loads(body, object_pairs_hook=unique)


def read_regular(path, maximum=60_000_000):
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), 'rb') as stream:
        before = os.fstat(stream.fileno())
        need(stat.S_ISREG(before.st_mode) and before.st_size <= maximum, 'Nonregular/oversized input: '+str(path))
        body = stream.read(maximum+1)
        after = os.fstat(stream.fileno())
    identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    need(len(body) <= maximum and identity(before) == identity(after) == identity(path.lstat()), 'Input changed during read: '+str(path))
    return body, before


def sri_matches(body, expected):
    try:
        algorithm, encoded = expected.split('-', 1)
        return algorithm == 'sha512' and base64.b64decode(encoded, validate=True) == hashlib.sha512(body).digest()
    except (ValueError, TypeError, AttributeError):
        return False


def archive_files(body, expected_sri):
    need(len(body) <= 20_000_000 and sri_matches(body, expected_sri), 'Archive integrity/size mismatch')
    # Bound expanded bytes before tarfile processes even extended/PAX headers.
    with gzip.GzipFile(fileobj=io.BytesIO(body)) as zipped:
        raw = zipped.read(66_000_001)
    need(len(raw) <= 66_000_000, 'Expanded archive bound')
    files, seen = {}, set()
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:') as archive:
        for member in archive:
            name = member.name
            need(len(seen) < 1000 and name not in seen, 'Duplicate/member-count bound')
            need(name.startswith('package/') and '\\' not in name and '\x00' not in name
                 and str(PurePosixPath(name)) == name
                 and all(p not in ('', '.', '..') for p in name.split('/')), 'Unsafe archive path')
            seen.add(name)
            need(member.type in (tarfile.REGTYPE, tarfile.AREGTYPE) and member.sparse is None
                 and not any(k.startswith('GNU.sparse') or k == 'SCHILY.realsize' for k in member.pax_headers)
                 and not member.linkname and 0 <= member.size <= 60_000_000,
                 'Unsupported archive member type/size')
            data = archive.extractfile(member).read()
            need(len(data) == member.size, 'Truncated archive member')
            files[name.removeprefix('package/')] = data
    need(bool(files), 'Empty archive')
    return files


def response_matches(row, key, kind, url, filename, body):
    need(row.get('package') == key and row.get('kind') == kind and row.get('file') == filename,
         'Response identity differs')
    need(row.get('requestedURL') == row.get('responseURL') == url and row.get('status') == 200,
         'Response URL/status differs')
    need(row.get('size') == len(body) and row.get('sha256') == sha(body), 'Response body differs')
    headers = row.get('headers')
    need(isinstance(headers, dict), 'Response headers differ')
    length = headers.get('content-length')
    need(isinstance(length, str) and length.isascii() and length.isdecimal()
         and int(length) == len(body), 'Response Content-Length differs')
    need(row.get('redirectPolicy') == 'disabled' and row.get('requestAcceptEncoding') == 'identity'
         and headers.get('content-encoding', 'identity').lower() in ('', 'identity'),
         'Response encoding/redirect scope differs')


def installed_files(root):
    files, identities = {}, {}
    for _, key, _, _ in PACKAGES:
        base = root/key
        need(base.is_dir() and not base.is_symlink(), 'Installed package root differs')
        for path in sorted(base.rglob('*')):
            mode = path.lstat().st_mode
            if stat.S_ISDIR(mode):
                continue
            need(stat.S_ISREG(mode), 'Installed link/special input: '+str(path))
            body, info = read_regular(path)
            rel = str(path.relative_to(root))
            files[rel] = sha(body)
            identities[rel] = dict(sha256=sha(body), size=len(body), mode=oct(stat.S_IMODE(info.st_mode)),
                                   device=info.st_dev, inode=info.st_ino, nlink=info.st_nlink)
    return files, identities


def validate_installed(files, archives):
    expected = {}
    for name, key, _, _ in PACKAGES:
        expected.update({key+'/'+path: sha(body) for path, body in archives[name].items()})
    binary = sha(archives['linux-x64']['elm'])
    need(binary == BINARY_SHA, 'Compiler differs from held toolchain')
    need(sha(archives['elm']['bin/elm']) != binary, 'Installer wrapper unexpectedly equals ELF')
    # This is the one documented content placement in the pinned binary.js.
    need(sha(archives['elm']['binary.js']) == '43e17364dd32cf7a3a8613cdd38e909604f9037b8bb43d54071ab0bf9b637e62'
         and archives['elm']['install.js'] == b"require('./binary.js')();\n", 'Install recipe differs')
    metadata = decode(archives['elm']['package.json'])
    need(metadata['bin']['elm'] == 'bin/elm' and metadata['optionalDependencies']['@elm_binaries/linux_x64'] == '0.19.2-0',
         'Installer target differs')
    expected['node_modules/elm/bin/elm'] = binary
    need(files == expected, 'Installed package file inventory/bytes differ')
    return expected


def verify(held, lock_body, root=INSTALLED):
    need(sha(lock_body) == LOCK_SHA, 'Held package lock differs')
    lock = decode(lock_body)
    responses = decode(held['responses.json'])
    need(responses.get('lockPath') == str(INSTALLED/'package-lock.json') and responses.get('lockSHA256') == LOCK_SHA,
         'Response lock provenance differs')
    rows = responses.get('responses', [])
    need(len(rows) == 4, 'Unexpected response count')
    archives, records = {}, []
    for name, key, regname, metadata_url in PACKAGES:
        entry = lock['packages'][key]
        need(entry['version'] == '0.19.2-0', 'Selected version differs')
        for kind, filename, url in [('metadata', name+'.json', metadata_url), ('archive', name+'.tgz', entry['resolved'])]:
            matches = [row for row in rows if row.get('kind') == kind and row.get('package') == key]
            need(len(matches) == 1, 'Ambiguous response record')
            response_matches(matches[0], key, kind, url, filename, held[filename])
        meta = decode(held[name+'.json'])
        need(meta['name'] == regname and meta['version'] == entry['version']
             and meta['dist']['integrity'] == entry['integrity'] and meta['dist']['tarball'] == entry['resolved'],
             'Registry metadata differs from lock')
        members = archive_files(held[name+'.tgz'], entry['integrity'])
        package = decode(members['package.json'])
        need(package['name'] == regname and package['version'] == entry['version'], 'Archived package identity differs')
        archives[name] = members
        records.append(dict(name=regname, version=entry['version'], url=entry['resolved'],
                            archiveSHA256=sha(held[name+'.tgz']), integrity=entry['integrity'],
                            metadataSHA256=sha(held[name+'.json']), declaredLicense=package.get('license'),
                            files={path: dict(sha256=sha(data), size=len(data)) for path, data in members.items()}))
    files, identities = installed_files(root)
    validate_installed(files, archives)
    a, b = (identities[p] for p in ['node_modules/elm/bin/elm', 'node_modules/@elm_binaries/linux_x64/elm'])
    return dict(passed=True, archives=records, installed=identities,
                sameCurrentInode=(a['device'], a['inode']) == (b['device'], b['inode']),
                placement='Installed ELF matches the binary archive and documented installer content placement; this does not prove historical installer execution or hardlinking.',
                responseLimits='Response headers have explicit cookie redaction; current fetch script was edited after capture and is not an attested executed-source identity.',
                upstreamSourceBuildCorrespondenceEstablished=False, redistributionApproved=False,
                nativeAcceptance=False, releaseAccepted=False)


def frozen_inputs():
    held = {}
    for name, expected in PINS.items():
        body, _ = read_regular(PACKET/name, 20_000_000)
        need(sha(body) == expected, 'Frozen response input differs: '+name)
        held[name] = body
    lock, _ = read_regular(INSTALLED/'package-lock.json')
    return held, lock


def main():
    need(not sys.argv[1:], 'No arguments supported; exact held scope only')
    sys.path.insert(0, str(REPO/'window-integration-qa'))
    from qa_launch import require_qa_scope
    scope = require_qa_scope()
    held, lock = frozen_inputs()
    result = verify(held, lock)
    result['scope'] = scope
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
