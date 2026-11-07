#!/usr/bin/env python3
"""Read-only fixed owner-route fixture binding check; never launches or admits QA."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys

RUNNER = 'tools/check_arm64_cpu.py'
TARGETS = (
    ('application-owner-peer-fixture', 'executable', 'fixture-application-owner-peer'),
    ('application-argv-fixture', 'executable', 'fixture-application-argv'),
    ('application-owner-route-controls', 'test-suite', 'test-application-owner-route'),
)
SHA = re.compile(r'[0-9a-f]{64}\Z')


class Refused(ValueError):
    pass


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise Refused('Duplicate JSON key')
        result[key] = value
    return result


def _read(root, relative, limit):
    """Read a bounded regular file through held nonsymlink directory descriptors."""
    path = Path(relative)
    if path.is_absolute() or not path.parts or any(p in ('.', '..') for p in path.parts):
        raise Refused('Expected repository-relative input')
    descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        for component in path.parts[:-1]:
            child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                            dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        leaf = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC,
                       dir_fd=descriptor)
        with os.fdopen(leaf, 'rb') as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
                raise Refused('Expected bounded regular input')
            data = stream.read(limit + 1)
            after = os.fstat(stream.fileno())
        fields = ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
        if len(data) > limit or any(getattr(before, f) != getattr(after, f) for f in fields):
            raise Refused('Input changed while reading')
        return data
    except OSError as error:
        raise Refused('Input missing, nonregular or symlinked: ' + relative) from error
    finally:
        os.close(descriptor)


def _form(node):
    if isinstance(node, ast.AST):
        return (type(node).__name__, tuple((key, _form(value))
                for key, value in ast.iter_fields(node) if key != 'ctx'))
    if isinstance(node, list):
        return tuple(_form(value) for value in node)
    return node


def _shape(node, expression):
    return _form(node) == _form(ast.parse(expression, mode='eval').body)


def _embedded_pins(source):
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError, UnicodeError) as error:
        raise Refused('Runner AST unavailable') from error
    parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    checks = [n for n in ast.walk(tree) if isinstance(n, ast.Compare)
              and _shape(n.left, "digest(directory_root / 'Main.hs')")
              and len(n.ops) == 1 and isinstance(n.ops[0], ast.NotEq)]
    if len(checks) != 1:
        raise Refused('Expected one fixed digest comparison')
    check = checks[0]
    if len(check.comparators) != 1 or not isinstance(check.comparators[0], ast.Subscript):
        raise Refused('Expected fixed literal map lookup')
    lookup = check.comparators[0]
    if not _shape(lookup.slice, 'name') or not isinstance(lookup.value, ast.Dict):
        raise Refused('Expected fixed literal map lookup')
    literal = lookup.value
    if any(not isinstance(k, ast.Constant) or type(k.value) is not str for k in literal.keys):
        raise Refused('Expected unique fixed fixture keys')
    keys = [k.value for k in literal.keys]
    names = {row[0] for row in TARGETS}
    if len(keys) != len(names) or len(set(keys)) != len(keys) or set(keys) != names:
        raise Refused('Expected unique fixed fixture keys')
    if any(not isinstance(v, ast.Constant) or type(v.value) is not str or not SHA.fullmatch(v.value)
           for v in literal.values):
        raise Refused('Expected literal SHA256 fixture values')
    ancestry = []
    node = check
    while node in parents:
        node = parents[node]
        ancestry.append(node)
    loops = [n for n in ancestry if isinstance(n, ast.For)
             and _shape(n.target, '(name, kind, directory)') and _shape(n.iter, 'application_targets')]
    branches = [n for n in ancestry if isinstance(n, ast.If) and _shape(n.test, 'args.application_owner_route')]
    if len(loops) != 1 or len(branches) != 1:
        raise Refused('Fixed owner-route branch or target loop is ambiguous')
    assignments = [n for n in ast.walk(branches[0]) if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'application_targets' for t in n.targets)]
    target_writes = [n for n in ast.walk(branches[0]) if isinstance(n, ast.Name)
                     and n.id == 'application_targets' and isinstance(n.ctx, ast.Store)]
    if len(assignments) != 1 or len(target_writes) != 1 or assignments[0] not in branches[0].body:
        raise Refused('Expected one literal target list')
    try:
        targets = ast.literal_eval(assignments[0].value)
    except (ValueError, TypeError, SyntaxError) as error:
        raise Refused('Expected one literal target list') from error
    if targets != TARGETS:
        raise Refused('Expected one literal target list')
    directories = [n for n in loops[0].body if isinstance(n, ast.Assign)
                   and len(n.targets) == 1 and _shape(n.targets[0], 'directory_root')]
    if len(directories) != 1 or not _shape(directories[0].value, "stage / 'runtime' / directory"):
        raise Refused('Fixed fixture directory binding differs')
    return dict(zip(keys, [v.value for v in literal.values]))


def inspect(root, review_relative, expected_sha256):
    """Return advisory consistency only; full QA closure and admission remain separate."""
    root = Path(root)
    if not isinstance(expected_sha256, str) or not SHA.fullmatch(expected_sha256):
        raise Refused('Review digest must be exact SHA256')
    review_bytes = _read(root, review_relative, 8 * 1024 * 1024)
    if _sha(review_bytes) != expected_sha256:
        raise Refused('Review digest differs')
    try:
        packet = json.loads(review_bytes, object_pairs_hook=_unique)
    except (ValueError, UnicodeError) as error:
        raise Refused('Review JSON invalid') from error
    if (not isinstance(packet, dict) or set(packet) != {'schema', 'runner', 'arguments', 'inputs'}
            or type(packet['schema']) is not int or packet['schema'] != 1
            or packet['runner'] != str(root / RUNNER)
            or packet['arguments'] != ['--application-owner-route']):
        raise Refused('Only fixed application-owner-route review is supported')
    inputs = packet['inputs']
    if not isinstance(inputs, dict) or not 4 <= len(inputs) <= 4096:
        raise Refused('Review input map invalid')
    source = _read(root, RUNNER, 2 * 1024 * 1024)
    if inputs.get(RUNNER) != _sha(source):
        raise Refused('Current runner differs from review')
    pins = _embedded_pins(source)
    bindings = []
    for name, _, directory in TARGETS:
        relative = 'implementation/warlock/haskell/runtime/' + directory + '/Main.hs'
        actual = _sha(_read(root, relative, 1024 * 1024))
        if inputs.get(relative) != actual:
            raise Refused('Current fixture differs from review: ' + name)
        if pins[name] != actual:
            raise Refused('Embedded fixture pin differs from packet/current bytes: ' + name)
        bindings.append({'name': name, 'path': relative, 'sha256': actual})
    # Detect a change during this observation. This is not a future execution lease.
    if _read(root, RUNNER, 2 * 1024 * 1024) != source or _read(root, review_relative, 8 * 1024 * 1024) != review_bytes:
        raise Refused('Runner or review changed during observation')
    for row in bindings:
        if _sha(_read(root, row['path'], 1024 * 1024)) != row['sha256']:
            raise Refused('Fixture changed during observation')
    return {'schema': 1, 'status': 'consistent-advisory-only', 'mode': '--application-owner-route',
            'reviewSHA256': expected_sha256, 'runnerSHA256': _sha(source),
            'fixtureBindings': bindings, 'sourceReady': False, 'nativeAuthority': False,
            'fullQaAndAllOtherGuardsStillRequired': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--review', type=Path, required=True)
    parser.add_argument('--sha256', required=True)
    args = parser.parse_args()
    try:
        root = args.root.absolute()
        relative = str(args.review.absolute().relative_to(root))
        result = inspect(root, relative, args.sha256)
    except (ValueError, OSError) as error:
        print(json.dumps({'schema': 1, 'status': 'refused', 'error': str(error),
                          'sourceReady': False, 'nativeAuthority': False}))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
