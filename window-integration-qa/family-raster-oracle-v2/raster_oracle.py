"""Independent CPU reference for held, diagnostic EGL scene screenshots."""
from __future__ import annotations

import hashlib
import math
from pathlib import Path
import struct
import subprocess
import zlib


def png_rgba(path: Path, expected_digest: str, expected_size: tuple[int, int]) -> bytes:
    material = path.read_bytes()
    if hashlib.sha256(material).hexdigest() != expected_digest:
        raise ValueError("source digest differs from frozen fixture")
    if len(material) < 24 or material[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("source is not PNG")
    width, height = struct.unpack(">II", material[16:24])
    if (width, height) != expected_size or not (0 < width <= 8192 and 0 < height <= 8192):
        raise ValueError("source pixel extent differs from frozen fixture")
    # Read immutable bytes on stdin, avoiding a pathname decode race.
    raw = subprocess.run(
        ["magick", "png:-", "-depth", "8", "rgba:-"], input=material,
        capture_output=True, check=True, timeout=15,
    ).stdout
    if len(raw) != width * height * 4:
        raise ValueError("decoded RGBA extent differs")
    return raw


def encode_png(width: int, height: int, rgba: bytes) -> bytes:
    """Write deterministic fixture material without color/gamma metadata."""
    if len(rgba) != width * height * 4 or width <= 0 or height <= 0:
        raise ValueError("invalid fixture extent")
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    rows = b"".join(b"\x00" + rgba[y * width * 4:(y + 1) * width * 4] for y in range(height))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))


def premultiply(rgba: bytes) -> bytes:
    out = bytearray(rgba)
    for i in range(0, len(out), 4):
        a = out[i + 3]
        for c in range(3):
            out[i + c] = (out[i + c] * a + 127) // 255
    return bytes(out)


def bilinear(source: bytes, width: int, height: int, u: float, v: float) -> tuple[float, ...]:
    sx, sy = u * width - 0.5, v * height - 0.5
    ix, iy = math.floor(sx), math.floor(sy)
    fx, fy = sx - ix, sy - iy
    result = [0.0] * 4
    for dx, wx in ((0, 1 - fx), (1, fx)):
        for dy, wy in ((0, 1 - fy), (1, fy)):
            x, y = min(width - 1, max(0, ix + dx)), min(height - 1, max(0, iy + dy))
            base = (y * width + x) * 4
            for c in range(4):
                result[c] += source[base + c] * wx * wy
    return tuple(result)


def render(output: dict, members: list[dict], background=(0, 0, 0, 255)) -> bytes:
    """Return top-left RGBA8 raster in untransformed surface-buffer coordinates.

    Source identity validation belongs to the caller's immutable fixture manifest.
    The supplied rectangle must come from an actual presented scene, not a newly
    queried native window or inferred animation progress.
    """
    bw, bh = output["bufferWidth"], output["bufferHeight"]
    lw, lh = float(output["width"]), float(output["height"])
    ox, oy = float(output["x"]), float(output["y"])
    if not all(math.isfinite(v) for v in (lw, lh, ox, oy)) or lw <= 0 or lh <= 0:
        raise ValueError("invalid logical output")
    if not (isinstance(bw, int) and isinstance(bh, int) and 0 < bw <= 8192 and 0 < bh <= 8192):
        raise ValueError("invalid buffer extent")
    if any(not 0 <= c <= 255 for c in background) or len(background) != 4:
        raise ValueError("invalid background")
    # A transparent reference layer is quantized after every draw, just as an
    # RGBA8 framebuffer; the desktop background is composited only at the end.
    dst = bytearray(bw * bh * 4)
    for m in members:
        sw, sh = m["pixels"]
        source = m["premultiplied"]
        if len(source) != sw * sh * 4:
            raise ValueError("source extent differs")
        r = m["rectangle"]
        rx, ry, rw, rh = (float(r[k]) for k in ("x", "y", "width", "height"))
        if not all(math.isfinite(v) for v in (rx, ry, rw, rh)) or rw <= 0 or rh <= 0:
            raise ValueError("invalid member rectangle")
        for py in range(bh):
            ly = oy + (py + 0.5) * lh / bh
            if not ry <= ly < ry + rh:
                continue
            v = (ly - ry) / rh
            for px in range(bw):
                lx = ox + (px + 0.5) * lw / bw
                if not rx <= lx < rx + rw:
                    continue
                sample = bilinear(source, sw, sh, (lx - rx) / rw, v)
                base = (py * bw + px) * 4
                remaining = 1.0 - sample[3] / 255.0
                for c in range(4):
                    dst[base + c] = min(255, max(0, math.floor(sample[c] + dst[base + c] * remaining + 0.5)))
    for base in range(0, len(dst), 4):
        remaining = 1.0 - dst[base + 3] / 255.0
        for c in range(4):
            dst[base + c] = min(255, max(0, math.floor(dst[base + c] + background[c] * remaining + 0.5)))
    return bytes(dst)


def compare(actual: bytes, expected: bytes, width: int, height: int, tolerance: int = 0) -> dict:
    if tolerance not in (0, 1):
        raise ValueError("only predeclared exact or one-channel quantization bound allowed")
    if len(actual) != width * height * 4 or len(actual) != len(expected):
        raise ValueError("full screenshot extent differs")
    bad_pixels, bad_channels, max_error = 0, 0, 0
    first = []
    for pixel in range(width * height):
        errors = [abs(actual[pixel * 4 + c] - expected[pixel * 4 + c]) for c in range(4)]
        max_error = max(max_error, *errors)
        failures = sum(e > tolerance for e in errors)
        if failures:
            bad_pixels += 1
            bad_channels += failures
            if len(first) < 16:
                first.append({"x": pixel % width, "y": pixel // width, "errors": errors})
    return {"passed": bad_pixels == 0, "pixelsCompared": width * height,
            "channelsCompared": width * height * 4, "tolerance": tolerance,
            "badPixels": bad_pixels, "badChannels": bad_channels,
            "maxChannelError": max_error, "firstFailures": first,
            "actualSHA256": hashlib.sha256(actual).hexdigest(),
            "expectedSHA256": hashlib.sha256(expected).hexdigest()}
