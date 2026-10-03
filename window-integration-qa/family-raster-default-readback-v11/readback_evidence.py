"""Bind owned pre-swap pixels to actual own presentation; no native authority."""
import hashlib
import re
import stat
from pathlib import Path

from raster_oracle import png_rgba


def verify_readback(row, frame, directory):
    if row.get('event') != 'ownedFramebufferReadback':
        raise ValueError('requires owned framebuffer observation')
    for key in ('token', 'digest', 'stableId', 'pid', 'sequence', 'output',
                'generation', 'progress', 'members', 'bufferWidth', 'bufferHeight'):
        if key not in row or row[key] != frame.get(key):
            raise ValueError('readback/presentation binding differs: ' + key)
    if frame.get('event') != 'presented' or frame.get('accepted') is not True:
        raise ValueError('readback requires accepted matching own presentation')
    if row.get('nativeAuthority') is not False or row.get('presentationProof') is not False:
        raise ValueError('readback cannot grant authority or presentation proof')
    if row.get('encoding') != 'premultiplied-RGBA8-top-left' or row.get('readError') != 0:
        raise ValueError('readback encoding/error differs')
    extent = (row['bufferWidth'], row['bufferHeight'])
    if any(type(x) is not int or x <= 0 for x in extent) or extent[0]*extent[1]*4 > 256*1024*1024:
        raise ValueError('readback extent exceeds contract')
    if row.get('eglSurface') != dict(zip(('width', 'height'), extent)):
        raise ValueError('actual EGL surface extent differs')
    for category, keys in (
        ('eglConfig', ('red', 'green', 'blue', 'alpha', 'buffer', 'samples',
                       'sampleBuffers', 'configId', 'colorBufferType', 'nativeVisualId')),
        ('glBuffer', ('red', 'green', 'blue', 'alpha', 'readFormat', 'readType',
                      'sampleBuffers', 'samples', 'framebuffer')),
    ):
        observed = row.get(category, {})
        if any(type(observed.get(key)) is not int or observed[key] < 0 for key in keys):
            raise ValueError('missing actual buffer inspection: ' + category)
    filename = row.get('filename', '')
    if not re.fullmatch(r'owned-[0-9]+-[0-9]+\.png', filename):
        raise ValueError('invalid readback evidence filename')
    if filename != f"owned-{frame['sequence']}-{frame['generation']}.png":
        raise ValueError('readback evidence filename binding differs')
    directory = Path(directory)
    info = directory.lstat()
    import os
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
        raise ValueError('readback evidence directory must be owned private nonsymlink')
    path = directory / filename
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o600:
        raise ValueError('readback evidence must be owned private regular nonsymlink file')
    image_digest = hashlib.sha256(path.read_bytes()).hexdigest()
    pixels = png_rgba(path, image_digest, extent)
    if hashlib.sha256(pixels).hexdigest() != row.get('rawSHA256'):
        raise ValueError('raw readback bytes differ from submitted observation')
    return pixels, image_digest


def record_pixels(checks, name, comparison, **details):
    """Retain failed pixel gates while collecting independent planned samples."""
    checks.append({'name': name, 'passed': bool(comparison['passed']),
                   'comparison': comparison, **details})


def all_pixels_accepted(checks, expected_count=8):
    pixel_checks = [row for row in checks if 'comparison' in row]
    return len(pixel_checks) == expected_count and all(row['passed'] for row in pixel_checks)
