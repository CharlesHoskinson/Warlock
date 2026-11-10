"""Fixed private Night/100% opener paint witness; never an acceptance oracle."""
import struct
import zlib
from ux003_input_geometry_720 import require_frame

EXTENT = (1280, 720)
WINDOW = (980, 680)
BACKGROUND = (24, 10, 104, 15)
LABEL = (22, 20, 118, 38)
CURSOR_EXCLUSION = (44, 20, 74, 38)
SELECTED = (53, 28, 31)       # SurfaceTheme.Night.surfaceSelected
TEXT_PRIMARY = (246, 239, 232)
MIN_INK = 100


def enabled_opener_pixels(background, label):
    return (len(background) == 400 and len(label) == 1188
            and all(pixel == SELECTED for pixel in background)
            and sum(pixel == TEXT_PRIMARY for pixel in label) >= MIN_INK)


def label_pixel_sampled(x, y):
    # Exclude the known opener arrow footprint at local48,28 entirely.
    return (LABEL[0] <= x < LABEL[2] and LABEL[1] <= y < LABEL[3]
            and not (CURSOR_EXCLUSION[0] <= x < CURSOR_EXCLUSION[2]
                     and CURSOR_EXCLUSION[1] <= y < CURSOR_EXCLUSION[3]))


def _paeth(a, b, c):
    estimate = a + b - c
    da, db, dc = abs(estimate - a), abs(estimate - b), abs(estimate - c)
    return a if da <= db and da <= dc else b if db <= dc else c


def opener_readiness(raw, window_at, window_size):
    if (type(window_at) not in (tuple, list) or len(window_at) != 2
            or any(type(v) is not int for v in window_at)
            or type(window_size) not in (tuple, list) or len(window_size) != 2
            or any(type(v) is not int for v in window_size) or tuple(window_size) != WINDOW):
        raise ValueError('fixed owned window geometry required')
    x0, y0 = window_at
    if x0 < 0 or y0 < 0 or x0 + WINDOW[0] > EXTENT[0] or y0 + WINDOW[1] > EXTENT[1]:
        raise ValueError('owned window outside fixed monitor')
    # Full existing CRC/chunk/framing/32MiB guard runs BEFORE inflation.
    require_frame(raw, EXTENT)
    width, height, depth, colour, compression, filtering, interlace = struct.unpack('>IIBBBBB', raw[16:29])
    if (width, height) != EXTENT or depth != 8 or colour not in (2, 6) or (compression, filtering, interlace) != (0, 0, 0):
        raise ValueError('fixed 8-bit RGB/RGBA noninterlaced capture required')
    channels = 3 if colour == 2 else 4
    stride = width * channels
    expected = (stride + 1) * height  # <= 3,687,120 fixed bytes
    compressed = bytearray()
    offset = 8
    while offset < len(raw):
        length = int.from_bytes(raw[offset:offset+4], 'big')
        if raw[offset+4:offset+8] == b'IDAT':
            compressed.extend(raw[offset+8:offset+8+length])
        offset += length + 12
    try:
        inflater = zlib.decompressobj()
        scan = inflater.decompress(compressed, expected + 1)
    except zlib.error as exc:
        raise ValueError('invalid bounded IDAT') from exc
    if len(scan) != expected or not inflater.eof or inflater.unused_data or inflater.unconsumed_tail:
        raise ValueError('PNG inflated length/stream differs')
    background, label = [], []
    previous = bytearray(stride)
    # Reconstruct only rows through the two fixed ROIs; full inflated length
    # was already checked. No OCR, image rewriting or external tool execution.
    for y in range(y0 + LABEL[3]):
        start = y * (stride + 1)
        kind = scan[start]
        row = bytearray(scan[start+1:start+1+stride])
        if kind not in (0, 1, 2, 3, 4):
            raise ValueError('unknown PNG row filter')
        if kind:
            for i in range(stride):
                a = row[i-channels] if i >= channels else 0
                b = previous[i]
                c = previous[i-channels] if i >= channels else 0
                predictor = a if kind == 1 else b if kind == 2 else (a+b)//2 if kind == 3 else _paeth(a,b,c)
                row[i] = (row[i] + predictor) & 255
        for bounds, pixels in ((BACKGROUND, background), (LABEL, label)):
            if y0 + bounds[1] <= y < y0 + bounds[3]:
                for x in range(x0 + bounds[0], x0 + bounds[2]):
                    if bounds == LABEL and not label_pixel_sampled(x-x0, y-y0):
                        continue
                    index = x * channels
                    pixel = tuple(row[index:index+3])
                    pixels.append(pixel if channels == 3 or row[index+3] == 255 else None)
        previous = row
    return {'ready': enabled_opener_pixels(background, label),
            'contract': 'fixed-Night-100-enabled-Applications-interior-v1',
            'backgroundMatches': sum(pixel == SELECTED for pixel in background),
            'backgroundExpected': 400, 'textPrimaryPixels': sum(pixel == TEXT_PRIMARY for pixel in label),
            'minimumTextPrimaryPixels': MIN_INK, 'cursorExclusionROI': list(CURSOR_EXCLUSION), 'windowAt': list(window_at),
            'backgroundROI': list(BACKGROUND), 'labelROI': list(LABEL),
            'interpretation': 'pre-input paint witness only; not eligible catalog, launch, or original acceptance'}
