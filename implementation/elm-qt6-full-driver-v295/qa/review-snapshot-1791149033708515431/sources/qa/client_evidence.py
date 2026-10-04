import json,os,struct,subprocess,time
from pathlib import Path
records=[]
selected_colors={}

def events():
    global records
    raw = client_log.read_bytes()
    if len(raw) > 4 * 1024 * 1024:
        raise RuntimeError('Client evidence exceeded bound')
    parsed = []
    for line in raw.splitlines(keepends=True):
        if not line.endswith(b'\n'):
            break
        if not line.startswith(b'{'):
            continue  # Actual WAYLAND_DEBUG/stderr stays in the owned log.
        record = json.loads(line)
        if type(record.get('sequence')) is not int or record['sequence'] != len(parsed) + 1:
            raise RuntimeError('Client event sequence gap or duplicate')
        if record.get('event') == 'refused':
            raise RuntimeError('Actual client refused: ' + repr(record))
        parsed.append(record)
    if parsed[:len(records)] != records:
        raise RuntimeError('Client evidence changed after observation')
    records = parsed
    return parsed

def native_window():
    windows = [row for row in session.data('clients') if row.get('pid') == client.pid and row.get('title') == 'ELM-MAXIMIZE-PROBE']
    if len(windows) > 1:
        raise RuntimeError('Native fixture identity ambiguous')
    if not windows:
        return None
    row = windows[0]
    if 'address' in report.get('fixtureIdentity', {}) and row['address'] != report['fixtureIdentity']['address']:
        raise RuntimeError('Native fixture identity replaced')
    return row

def latest_buffer():
    return next((row for row in reversed(events()) if row['event'] == 'buffercommit'), None)

def request(command, deadline=None):
    if deadline is None:
        deadline = time.monotonic() + 6
    session.guard()
    assert client.poll() is None and host.original.same_process(client_identity)
    before = events()[-1]['sequence'] if events() else 0
    if time.monotonic() >= deadline:
        raise RuntimeError('Unchanged six-second observation deadline before request')
    client.stdin.write((command + '\n').encode())
    client.stdin.flush()
    packet = wait(lambda: next((row for row in events() if row['sequence'] > before and row['event'] == 'request' and row.get('command') == command), None), deadline=deadline)
    barrier = wait(lambda: next((row for row in events() if row['event'] == 'server-barrier' and row.get('requestSequence') == packet['sequence']), None), deadline=deadline)
    exact = [row for row in events() if row['event'] == 'server-barrier' and row.get('requestSequence') == packet['sequence']]
    check(command + ':exactRequestCorrelatedServerBarrier', len(exact) == 1 and
          barrier.get('command') == command and barrier.get('requestSerial') == packet['serial'] and
          barrier['sequence'] > packet['sequence'], request=packet, barrier=barrier)
    return packet

def settled(mode, after_sequence=None, suspended=False):
    row, buffer = native_window(), latest_buffer()
    if row is None or buffer is None:
        return None
    expected_maximized = mode == 1
    if row.get('fullscreen') != mode or row.get('fullscreenClient') != mode or row.get('xwayland') is not False:
        return None
    if buffer.get('maximized') is not expected_maximized or buffer.get('fullscreen') is not False or buffer.get('suspended') is not suspended:
        return None
    if after_sequence is not None and buffer['sequence'] <= after_sequence:
        return None
    if [buffer.get('bufferWidth'), buffer.get('bufferHeight')] != row['size']:
        return None
    return row, buffer

def validate_pixels(name, native, buffer, deadline=None):
    serial = buffer['ackedSerial']
    check(name + ':bufferUsesItsExactAckedConfigure', serial == buffer['serial'] and
          any(row['event'] == 'configure' and row['serial'] == serial and row['ackedSerial'] == serial and
              row['sequence'] < buffer['sequence'] and [row['width'], row['height']] == native['size']
              for row in events()), buffer=buffer)
    # Independent serial-color oracle, not the client's emitted argb alone.
    rgb = [0x28 ^ (serial & 63), 0x71 ^ ((serial >> 6) & 63), 0xc8 ^ ((serial >> 12) & 63)]
    argb = 'ff' + ''.join(f'{part:02x}' for part in rgb)
    check(name + ':serialColorHasNoCollision', buffer.get('argb') == argb and
          (argb not in selected_colors or selected_colors[argb] == serial), serial=serial, argb=argb)
    selected_colors[argb] = serial
    x, y = native['at']
    width, height = native['size']
    points = [(x + width // 2, y + height // 2), (x + 12, max(64, y + 12)), (x + width - 13, y + height - 13)]
    attempts = []

    def capture(deadline):
        path = OUTPUT / (name + '-pixels-' + str(len(attempts)) + '.png')
        session.guard()
        def unchanged():
            current = native_window()
            latest = latest_buffer()
            return current is not None and all(current.get(key) == native.get(key) for key in
                ('address', 'pid', 'at', 'size', 'fullscreen', 'fullscreenClient')) and latest == buffer
        if not unchanged():
            raise RuntimeError('Native window or selected exact buffer changed before pixel capture')
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError('Unchanged six-second observation deadline')
        result = subprocess.run(['/usr/bin/grim', str(path)], env=session.env, capture_output=True, timeout=min(5, remaining))
        if result.returncode:
            raise RuntimeError('Owned child grim failed: ' + result.stderr.decode(errors='replace'))
        png = path.read_bytes()
        if png[:8] != bytes.fromhex('89504e470d0a1a0a') or png[12:16] != b'IHDR' or struct.unpack('>II', png[16:24]) != (800, 600):
            raise RuntimeError('Screenshot is not the actual private 800x600 child output')
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError('Unchanged six-second observation deadline')
        decoded = subprocess.run(['/usr/bin/magick', str(path), '-depth', '8', 'rgb:-'], capture_output=True, timeout=min(5, remaining))
        if decoded.returncode or len(decoded.stdout) != 800 * 600 * 3:
            raise RuntimeError('Actual screenshot RGB decoding failed')
        samples = []
        for px, py in points:
            if type(px) is not int or type(py) is not int or not (0 <= px < 800 and 0 <= py < 600):
                raise RuntimeError('Pixel sample is outside exact output geometry')
            offset = (py * 800 + px) * 3
            samples.append(list(decoded.stdout[offset:offset + 3]))
        attempts.append({'path': str(path), 'sha256': host.digest(path), 'points': points, 'samples': samples})
        report.setdefault('pixelAttempts', []).append(attempts[-1])
        if not unchanged():
            raise RuntimeError('Native window or selected exact buffer changed during pixel capture')
        return attempts[-1] if all(sample == rgb for sample in samples) else None

    matched = wait(capture, timed=True, deadline=deadline)
    check(name + ':actualInteriorPixelsMatchSelectedConfigure', bool(matched), expectedRGB=rgb, capture=matched)
