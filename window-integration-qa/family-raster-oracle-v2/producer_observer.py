"""Actual producer observer for reviewed private sessions; no compositor launcher."""
import json,subprocess,threading,time
from raster_oracle import encode_png

def wait(fn, label, timeout=15):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        value = fn()
        if value:
            return value
        time.sleep(0.03)
    raise AssertionError(label)


class Observer:
    def __init__(self, command, env, output):
        self.rows, self.lock = [], threading.Lock()
        self.error_log = (output / 'producer.stderr').open('w')
        self.process = subprocess.Popen(command, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=self.error_log, text=True, bufsize=1, start_new_session=True)
        self.log = (output / 'producer-events.jsonl').open('w')
        self.thread = threading.Thread(target=self.read, daemon=True)
        self.thread.start()

    def read(self):
        for line in self.process.stdout:
            self.log.write(line)
            self.log.flush()
            row = json.loads(line)
            with self.lock:
                self.rows.append(row)

    def send(self, **row):
        self.process.stdin.write(json.dumps(row, allow_nan=False) + '\n')
        self.process.stdin.flush()

    def find(self, predicate, label):
        def observed():
            with self.lock:
                fatal = next((r for r in self.rows if r.get('event') in ('fatal', 'rejected')), None)
                if fatal:
                    raise AssertionError(f'{label}: {fatal}')
                found = next((r for r in reversed(self.rows) if predicate(r)), None)
            if found:
                return found
            if self.process.poll() is not None:
                raise AssertionError(f'{label}: producer exited {self.process.returncode}')
            return None
        return wait(observed, label)

    def close(self):
        if self.process.poll() is None:
            self.send(command='stop')
            self.process.wait(timeout=5)
        self.thread.join(timeout=2)
        self.process.stdin.close()
        self.process.stdout.close()
        self.log.close()
        self.error_log.close()
        return self.process.returncode


def generated_source(path, width, height, member):
    # Deliberately asymmetric, non-square stripes and three distinct member
    # palettes expose flips, wrong order, dropped child and shifted boundaries.
    colors = ((224, 24, 48), (16, 216, 64), (32, 72, 224))
    rgba = bytearray()
    for y in range(height):
        for x in range(width):
            rgb = colors[member]
            if y < 8:
                rgb = (240, 192 - member * 32, 16 + member * 32)
            elif x < 4 or y >= height - 4 or x >= width - 4:
                rgb = (16, 16, 16)
            elif (x // 8 + y // 8) % 3 == 0:
                rgb = (rgb[0] // 2, rgb[1] // 2, rgb[2] // 2)
            alpha = 255 if member == 0 else (48, 128, 192, 255)[(x // 8 + y // 8) % 4]
            if member == 2 and (x < 4 or y < 4): alpha = 0
            rgba.extend((*rgb, alpha))
    path.write_bytes(encode_png(width, height, bytes(rgba)))
    path.chmod(0o600)

