"""Stage fixed, hash-verified official Elm packages into a disposable QA cache."""
import hashlib
import json
import os
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'tools/elm-http-dependencies.json'


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def regular(path):
    if path.is_symlink() or not path.is_file():
        raise RuntimeError('Expected regular Elm dependency: ' + str(path))


def inventory(directory):
    if directory.is_symlink() or not directory.is_dir() or directory.resolve() != directory:
        raise RuntimeError('Expected nonsymlink Elm dependency directory: ' + str(directory))
    result = {}
    for path in sorted(directory.rglob('*')):
        if path.is_symlink():
            raise RuntimeError('Unexpected Elm dependency symlink: ' + str(path))
        if path.is_file():
            result[str(path.relative_to(directory))] = digest(path)
    return result


def verify():
    regular(MANIFEST)
    packet = json.loads(MANIFEST.read_text())
    if packet['schema'] != 1 or [(p['package'], p['version']) for p in packet['packages']] != [
            ('elm/http', '2.0.0'), ('elm/bytes', '1.0.8'), ('elm/file', '1.0.5')]:
        raise RuntimeError('Unexpected Elm dependency selection')
    cache = Path(packet['cacheDirectory'])
    if cache != Path('/home/charl/.cache/warlock-elm-http') or cache.resolve() != cache or cache.stat().st_uid != os.getuid():
        raise RuntimeError('Unexpected private Elm dependency cache')
    for package in packet['packages']:
        archive = Path(package['publisherArchive']['file'])
        source = cache / 'packages' / package['package'] / package['version']
        if archive.parent != cache or str(source) != package['cachePath']:
            raise RuntimeError('Elm dependency escaped its cache')
        regular(archive)
        if digest(archive) != package['publisherArchive']['sha256'] or inventory(source) != package['files']:
            raise RuntimeError('Pinned official Elm dependency differs: ' + package['package'])
    return packet


def stage(home):
    packet = verify()
    for package in packet['packages']:
        source = Path(package['cachePath'])
        target = Path(home) / '0.19.2/packages' / package['package'] / package['version']
        if target.exists() or target.is_symlink():
            raise RuntimeError('Disposable Elm dependency already exists: ' + str(target))
        shutil.copytree(source, target)
        if inventory(target) != package['files']:
            raise RuntimeError('Staged Elm dependency differs')
    verify()
    return {'manifestSHA256': digest(MANIFEST), 'packages': [
        {'name': p['package'], 'version': p['version'], 'archiveSHA256': p['publisherArchive']['sha256'],
         'sourceFiles': p['files']} for p in packet['packages']]}
