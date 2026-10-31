"""Development QA only: archive bounded, unattributed Elm/Haskell capture evidence.

This module never accepts a native scenario. The caller must retain the original
ToolObservation (including nonzero exit and stderr). Its archive parent must be a
trusted directory, with no hostile same-UID ancestor mutation during use.
"""
from __future__ import annotations

import base64
import binascii
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import struct
import zlib

MAX_STDOUT = 4 * 1024 * 1024
METADATA_RESERVE = 65536
MAX_PNG = 8 * 1024 * 1024


class FrameError(ValueError):
    """Evidence was refused; keep the raw observation for diagnosis."""


def _object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise FrameError("duplicate JSON key")
        value[key] = item
    return value


def _constant(_value):
    raise FrameError("nonfinite JSON number")


def _tree(value):
    pending = [(value, 0)]
    count = 0
    while pending:
        item, depth = pending.pop()
        count += 1
        if depth > 20 or count > 10000:
            raise FrameError("metadata structure exceeds bound")
        if isinstance(item, str):
            if any(0xD800 <= ord(c) <= 0xDFFF for c in item):
                raise FrameError("invalid Unicode scalar")
        elif isinstance(item, dict):
            pending.extend((part, depth + 1) for pair in item.items() for part in pair)
        elif isinstance(item, list):
            pending.extend((part, depth + 1) for part in item)
        elif isinstance(item, float):
            # Receipt schema has only integral facts. Refuse exponent overflow too.
            raise FrameError("floating point metadata refused")


def _png_container(png):
    """Check framing/CRCs, not image decompression, pixels or provenance."""
    if not png.startswith(b'\x89PNG\r\n\x1a\n'):
        raise FrameError("PNG signature")
    offset, chunks, seen_data = 8, 0, False
    while offset < len(png):
        if len(png) - offset < 12:
            raise FrameError("truncated PNG chunk")
        length = struct.unpack_from('>I', png, offset)[0]
        end = offset + 12 + length
        if end > len(png) or chunks >= 65536:
            raise FrameError("PNG chunk exceeds bound")
        kind = png[offset + 4:offset + 8]
        data = png[offset + 8:end - 4]
        crc = struct.unpack_from('>I', png, end - 4)[0]
        if zlib.crc32(kind + data) & 0xffffffff != crc:
            raise FrameError("PNG CRC mismatch")
        if chunks == 0:
            if kind != b'IHDR' or length != 13:
                raise FrameError("PNG first IHDR")
            width, height, depth, color, compression, filtering, interlace = struct.unpack('>IIBBBBB', data)
            if (width, height) != (800, 600):
                raise FrameError("PNG dimensions")
            depths = {0: (1, 2, 4, 8, 16), 2: (8, 16), 3: (1, 2, 4, 8), 4: (8, 16), 6: (8, 16)}
            if depth not in depths.get(color, ()) or compression or filtering or interlace not in (0, 1):
                raise FrameError("PNG IHDR fields")
        elif kind == b'IHDR':
            raise FrameError("duplicate PNG IHDR")
        if kind == b'IDAT':
            seen_data = True
        if kind == b'IEND':
            if length or end != len(png) or not seen_data:
                raise FrameError("PNG IEND or data framing")
            return {"containerCRCVerified": True, "width": 800, "height": 600,
                    "pixelsDecoded": False}
        offset, chunks = end, chunks + 1
    raise FrameError("PNG missing IEND")


def decode_frame(stdout: bytes):
    """Validate one complete producer frame; return receipt, bytes, limited facts."""
    if not isinstance(stdout, bytes) or len(stdout) > MAX_STDOUT - METADATA_RESERVE:
        raise FrameError("stdout frame exceeds budget")
    if not stdout.endswith(b'\n') or stdout.count(b'\n') != 1:
        raise FrameError("exactly one complete JSON line required")
    try:
        frame = json.loads(stdout.decode('utf-8'), object_pairs_hook=_object, parse_constant=_constant)
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise FrameError("invalid framed JSON") from exc
    _tree(frame)
    if not isinstance(frame, dict) or set(frame) != {'schema', 'receipt', 'pngBase64'}:
        raise FrameError("frame schema keys")
    if type(frame['schema']) is not int or frame['schema'] != 1:
        raise FrameError("frame schema version")
    receipt, encoded = frame['receipt'], frame['pngBase64']
    if not isinstance(receipt, dict) or not isinstance(encoded, str):
        raise FrameError("frame field types")
    if len(json.dumps(receipt, ensure_ascii=False).encode('utf-8')) > METADATA_RESERVE - 128:
        raise FrameError("receipt exceeds metadata budget")
    if receipt.get('result') != 'UNATTRIBUTED' or any(
        receipt.get(key) is not False for key in
        ('renderObserved', 'receiptFinalDeadlineChecked', 'toolIssuerBindingExternallyQualified')
    ):
        raise FrameError("unattributed evidence status changed")
    try:
        png = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise FrameError("invalid base64") from exc
    if len(png) > MAX_PNG or base64.b64encode(png).decode('ascii') != encoded:
        raise FrameError("noncanonical or oversized payload")
    image = receipt.get('image')
    facts = {"nativeAccepted": False, "renderObserved": False,
             "payloadSHA256Verified": False, "pixelsDecoded": False}
    if image is None:
        if png:
            raise FrameError("payload without image receipt")
        return receipt, png, facts
    if not isinstance(image, dict):
        raise FrameError("image receipt type")
    if type(image.get('bytes')) is not int or not 0 < image['bytes'] <= MAX_PNG:
        raise FrameError("image size type or bound")
    digest = image.get('sha256')
    if not isinstance(digest, str) or re.fullmatch('[0-9a-f]{64}', digest) is None:
        raise FrameError("image digest syntax")
    if len(png) != image['bytes'] or hashlib.sha256(png).hexdigest() != digest:
        raise FrameError("payload size or SHA256 mismatch")
    facts['payloadSHA256Verified'] = True
    try:
        facts.update(_png_container(png))
    except FrameError as exc:
        # Retain hash-matching malformed images for diagnosis, without claiming PNG validity.
        facts.update(containerCRCVerified=False, containerFailure=str(exc))
    return receipt, png, facts


@contextmanager
def _owned_fd(fd):
    """Attempt each close once, retaining operation and cleanup failures."""
    try:
        yield fd
    except BaseException as operation_error:
        try:
            os.close(fd)
        except BaseException as close_error:
            raise BaseExceptionGroup("archive operation and descriptor close failed",
                                     [operation_error, close_error]) from None
        raise
    else:
        os.close(fd)


def archive_frame(stdout: bytes, parent: Path, name: str):
    """Create a new private archive, never using producer-supplied file paths.

    On I/O failure, a partial archive may remain. Do not retry using that name.
    Invalid frames raise before any destination is created; caller retains stdout.
    """
    receipt, png, facts = decode_frame(stdout)
    if re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}', name) is None:
        raise FrameError("archive name")
    with _owned_fd(os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)) as parent_fd:
        info = os.fstat(parent_fd)
        if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
            raise FrameError("archive parent must be owned mode0700")
        os.mkdir(name, mode=0o700, dir_fd=parent_fd)
        with _owned_fd(os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                               dir_fd=parent_fd)) as child_fd:
            files = {'frame.stdout': stdout,
                     'receipt.json': (json.dumps(receipt, ensure_ascii=False, indent=2) + '\n').encode(),
                     'observation.json': (json.dumps(facts, indent=2) + '\n').encode()}
            if png:
                files['frame.png'] = png
            for filename, contents in files.items():
                with _owned_fd(os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                                       0o600, dir_fd=child_fd)) as fd:
                    remaining = memoryview(contents)
                    while remaining:
                        written = os.write(fd, remaining)
                        if written <= 0:
                            raise OSError("archive write made no progress")
                        remaining = remaining[written:]
                    os.fsync(fd)
            os.fsync(child_fd)
        os.fsync(parent_fd)
    return facts
