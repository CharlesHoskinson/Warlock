"""Desktop-entry catalog with private, atomic, inventory-validated caching.

No application commands are executed. Exec strings retain their original values;
launchers remain responsible for the existing argv construction.
"""
import configparser
import json
import os
from pathlib import Path
import stat
import tempfile

SCHEMA = 1
_FIELDS = {'id', 'name', 'icon', 'path', 'exec', 'wmclass', 'mime', 'terminal', 'actions'}


def _roots(data_home, data_dirs):
    home = Path(data_home if data_home is not None else os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share'))
    dirs = data_dirs if data_dirs is not None else os.environ.get('XDG_DATA_DIRS', '/usr/local/share:/usr/share').split(':')
    return [home.absolute()] + [Path(p).absolute() for p in dirs]


def _stamp(path, follow=True):
    s = path.stat() if follow else path.lstat()
    return [s.st_dev, s.st_ino, s.st_mode, s.st_size, s.st_mtime_ns, s.st_ctime_ns]


def _inventory(roots):
    """Enumerate all directories and desktop files; errors invalidate caching.

    Directory symlinks are not traversed, matching Path.glob('**/*.desktop').
    Desktop-file symlink targets are fingerprinted as well as the symlink.
    """
    inventory, groups = [], []
    for base in roots:
        directory = base / 'applications'
        files = []
        try:
            root_stamp = _stamp(directory)
        except FileNotFoundError:
            # A dangling root link becoming valid must invalidate the cache.
            link_stamp = _stamp(directory, False) if directory.is_symlink() else None
            inventory.append([str(directory), 'missing', link_stamp])
            groups.append((directory, files))
            continue
        inventory.append([str(directory), 'root', root_stamp])
        if not directory.is_dir():
            groups.append((directory, files))
            continue
        def visit(folder):
            inventory.append([str(folder), 'directory', _stamp(folder)])
            with os.scandir(folder) as iterator:
                children = sorted(iterator, key=lambda entry: entry.name)
            for child in children:
                path = Path(child.path)
                if child.is_dir(follow_symlinks=False):
                    visit(path)
                elif child.name.endswith('.desktop'):
                    # Include nonregular matches: parsing decides eligibility.
                    inventory.append([str(path), 'desktop', _stamp(path, False), _stamp(path)])
                    files.append(path)
                elif child.is_symlink():
                    inventory.append([str(path), 'symlink', _stamp(path, False)])
        visit(directory)
        groups.append((directory, sorted(files)))
    return inventory, groups


def _parse(groups):
    result, complete = {}, True
    for directory, files in groups:
        for path in files:
            key = str(path.relative_to(directory)).replace('/', '-')[:-8]
            if key in result:
                continue
            parser = configparser.ConfigParser(interpolation=None, strict=False)
            parser.optionxform = str
            try:
                if not path.is_file():
                    complete = False
                    continue
                # Explicit open detects unreadable files (ConfigParser.read hides IO errors).
                with path.open(encoding='utf-8') as source:
                    parser.read_file(source)
                section = parser['Desktop Entry']
                if section.get('Hidden', '').lower() == 'true':
                    result[key] = None
                    continue
                if section.get('Type') != 'Application' or not section.get('Exec'):
                    continue
                actions = []
                for action in section.get('Actions', '').split(';'):
                    name = 'Desktop Action ' + action
                    if action and name in parser and parser[name].get('Exec'):
                        actions.append({'id': action, 'name': parser[name].get('Name', action), 'exec': parser[name]['Exec']})
                result[key] = {'id': key, 'name': section.get('Name', key), 'icon': section.get('Icon', 'application-x-executable'), 'path': str(path), 'exec': section['Exec'], 'wmclass': section.get('StartupWMClass', ''), 'mime': section.get('MimeType', '').split(';'), 'terminal': section.get('Terminal', '').lower() == 'true', 'actions': actions}
            except (OSError, configparser.Error, KeyError, UnicodeError):
                complete = False
    return {k: v for k, v in result.items() if v}, complete


def _fallback(roots):
    # Match original catalog behavior even when a complete inventory is unavailable.
    return _parse([(root / 'applications', sorted((root / 'applications').glob('**/*.desktop'))) for root in roots])[0]


def _valid_catalog(value):
    if not isinstance(value, dict):
        return False
    for key, entry in value.items():
        if not isinstance(key, str) or not isinstance(entry, dict) or set(entry) != _FIELDS or entry['id'] != key:
            return False
        if any(not isinstance(entry[field], str) for field in ('id', 'name', 'icon', 'path', 'exec', 'wmclass')):
            return False
        if not isinstance(entry['terminal'], bool) or not isinstance(entry['mime'], list) or any(not isinstance(item, str) for item in entry['mime']):
            return False
        if not isinstance(entry['actions'], list):
            return False
        for action in entry['actions']:
            if not isinstance(action, dict) or set(action) != {'id', 'name', 'exec'} or any(not isinstance(v, str) for v in action.values()):
                return False
    return True


def _private_directory(directory):
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    info = directory.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise OSError('Cache directory must be private, owned, and nonsymlink')


def _read_cache(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077 or info.st_size > 32 * 1024 * 1024:
            raise OSError('Unsafe cache file')
        with os.fdopen(fd, 'r', encoding='utf-8') as source:
            fd = None
            return json.load(source)
    finally:
        if fd is not None:
            os.close(fd)


def _write_cache(directory, value):
    _private_directory(directory)
    fd, filename = tempfile.mkstemp(prefix='.catalog-', dir=directory)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as output:
            json.dump(value, output, ensure_ascii=False, separators=(',', ':'))
            output.flush()
            os.fsync(output.fileno())
        os.replace(filename, directory / 'catalog.json')
        directory_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        try:
            os.unlink(filename)
        except FileNotFoundError:
            pass


def load_catalog(data_home=None, data_dirs=None, cache_dir=None):
    """Return the original entries()-shaped catalog, without executing commands.

    Explicit roots/cache_dir support isolated fixtures. Inventory or cache errors
    cause a fresh parse; partial/malformed reads are never published to the cache.
    A catalog changed during parsing is returned fresh but is not cached.
    """
    roots = _roots(data_home, data_dirs)
    directory = Path(cache_dir) if cache_dir is not None else Path(os.environ.get('XDG_CACHE_HOME', Path.home() / '.cache')) / 'omarchy-windows-parity/taskbar-catalog'
    key = [str(root) for root in roots]
    try:
        before, groups = _inventory(roots)
    except OSError:
        return _fallback(roots)
    try:
        _private_directory(directory)
        cached = _read_cache(directory / 'catalog.json')
        if isinstance(cached, dict) and cached.get('schema') == SCHEMA and cached.get('roots') == key and cached.get('inventory') == before and _valid_catalog(cached.get('catalog')):
            # Revalidate the inventory after reading the cache, too.
            if _inventory(roots)[0] == before:
                return cached['catalog']
    except (OSError, ValueError, UnicodeError):
        pass
    catalog, complete = _parse(groups)
    if complete:
        try:
            after, _ = _inventory(roots)
            if before == after:
                _write_cache(directory, {'schema': SCHEMA, 'roots': key, 'inventory': after, 'catalog': catalog})
        except (OSError, ValueError):
            pass
    return catalog
