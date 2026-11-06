#!/usr/bin/env python3
"""Preserve and normalize a review receipt; workflow admission stays in warlock.py."""
import argparse
import hashlib
import json
import os
import re
import secrets
import stat
import sys

MAX_BYTES = 1048576
DECISIONS = ('accepted', 'changes-required')


def _identity(value, label):
    if (not isinstance(value, str) or not value or len(value) > 512
            or value != value.strip() or any(ord(c) < 32 or ord(c) == 127 for c in value)):
        raise ValueError('Invalid ' + label)
    return value


def _sha(value, label):
    if not isinstance(value, str) or re.fullmatch('[0-9a-f]{64}', value) is None:
        raise ValueError('Invalid ' + label)
    return value


def _trusted_directory(fd, final):
    """Other UIDs cannot replace receipt names; same-UID actors remain trusted."""
    info = os.fstat(fd)
    if final:
        if info.st_uid != os.geteuid() or info.st_mode & 0o022:
            raise ValueError('Output parent must be owned by current UID and not group/other writable')
    elif (info.st_uid not in (0, os.geteuid())
          or (info.st_mode & 0o022 and not (info.st_uid == 0 and info.st_mode & stat.S_ISVTX))):
        raise ValueError('Unsafe output ancestor')


def _parent(path, trusted_output=False):
    """Open every directory without following symlinks, including parent aliases."""
    path = os.fspath(path)
    if not isinstance(path, str) or not path.startswith('/') or '\0' in path:
        raise ValueError('An absolute file path is required')
    parts = path.split('/')[1:]
    if not parts or any(part in ('', '.', '..') for part in parts):
        raise ValueError('Noncanonical file path')
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        if trusted_output:
            _trusted_directory(fd, final=len(parts) == 1)
        for index, part in enumerate(parts[:-1]):
            next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=fd)
            os.close(fd)
            fd = next_fd
            if trusted_output:
                _trusted_directory(fd, final=index == len(parts) - 2)
        return fd, parts[-1], path
    except BaseException:
        os.close(fd)
        raise


def _read(path):
    parent, name, path = _parent(path)
    try:
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC, dir_fd=parent)
        with os.fdopen(fd, 'rb') as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_BYTES:
                raise ValueError('Receipt must be a bounded regular file')
            raw = stream.read(MAX_BYTES + 1)
            after = os.fstat(stream.fileno())
            if (len(raw) > MAX_BYTES or len(raw) != before.st_size
                    or (before.st_size, before.st_mtime_ns, before.st_ctime_ns)
                    != (after.st_size, after.st_mtime_ns, after.st_ctime_ns)):
                raise ValueError('Receipt changed while reading')
        return raw, path
    finally:
        os.close(parent)


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON field: ' + key)
        result[key] = value
    return result


def _nonfinite(value):
    raise ValueError('Nonfinite JSON value: ' + value)


def _encode(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')


def _write_new(path, raw):
    """Publish complete bytes atomically; an existing file/link is never replaced."""
    parent, name, _ = _parent(path, trusted_output=True)
    temporary = '.review-' + secrets.token_hex(16)
    created = False
    try:
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                     0o600, dir_fd=parent)
        created = True
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, name, src_dir_fd=parent, dst_dir_fd=parent, follow_symlinks=False)
        os.fsync(parent)
    finally:
        try:
            if created:
                os.unlink(temporary, dir_fd=parent)
        finally:
            os.close(parent)


def canonicalize(*, input_path, expected_sha256, candidate_sha256, reviewer, owner, scope, output_path):
    """Validate explicit context and copy one decision into the core's field name."""
    _sha(expected_sha256, 'original receipt SHA256')
    _sha(candidate_sha256, 'candidate SHA256')
    _identity(reviewer, 'expected reviewer')
    _identity(owner, 'record owner')
    if reviewer.casefold() == owner.casefold():
        raise ValueError('Reviewer must differ from record owner')
    if scope not in ('cpu', 'native'):
        raise ValueError('Invalid expected scope')
    raw, source = _read(input_path)
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise ValueError('Original receipt hash differs')
    receipt = json.loads(raw.decode('utf-8'), object_pairs_hook=_object, parse_constant=_nonfinite)
    if not isinstance(receipt, dict) or type(receipt.get('schema')) is not int or receipt['schema'] != 1:
        raise ValueError('Expected schema 1 review object')
    if (receipt.get('candidateSha256') != candidate_sha256 or receipt.get('reviewer') != reviewer
            or receipt.get('scope') != scope):
        raise ValueError('Review candidate, reviewer or scope differs')
    fields = [key for key in ('disposition', 'verdict') if key in receipt]
    if not fields or any(receipt[key] not in DECISIONS for key in fields):
        raise ValueError('Missing or invalid review decision')
    if len(fields) == 2 and receipt[fields[0]] != receipt[fields[1]]:
        raise ValueError('Conflicting verdict and disposition')
    if 'receiptCanonicalization' in receipt:
        raise ValueError('Canonicalization provenance already exists')
    result = dict(receipt)
    result['disposition'] = receipt[fields[0]]
    result['receiptCanonicalization'] = {
        'schema': 1, 'original': {'path': source, 'sha256': expected_sha256},
        'inputDecisionFields': fields, 'operation': 'copy-existing-review-decision',
        'acceptanceAuthority': False,
    }
    _write_new(output_path, _encode(result))
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--candidate-sha256', required=True)
    parser.add_argument('--reviewer', required=True)
    parser.add_argument('--owner', required=True)
    parser.add_argument('--scope', choices=('cpu', 'native'), required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args(argv)
    try:
        result = canonicalize(input_path=args.input, expected_sha256=args.sha256,
                              candidate_sha256=args.candidate_sha256, reviewer=args.reviewer,
                              owner=args.owner, scope=args.scope, output_path=args.output)
        print(json.dumps({'path': args.output, 'sha256': hashlib.sha256(_encode(result)).hexdigest(),
                          'disposition': result['disposition'], 'acceptanceAuthority': False}))
        return 0
    except (OSError, ValueError) as error:
        print('Review receipt refused: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
