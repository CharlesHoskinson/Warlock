import hashlib, importlib.util, json, resource, sys, time
from pathlib import Path
from types import SimpleNamespace
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
r = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(r / 'initial'))
spec = importlib.util.spec_from_file_location('initial_pixels', r / 'initial/pixels.py')
pixels = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pixels)
out = r / 'qa' / ('witness-' + str(time.time_ns()))
out.mkdir()
image = bytes([255, 255, 0]) * (800 * 600)
# Identical marker bytes at the same point contain no target attribution.
samples = pixels.yellow_marker(image, [8, 8])
assert len(samples) == 9
bad = bytearray(image)
offset = (7 * 800 + 7) * 3
bad[offset:offset + 3] = bytes([0, 0, 0])
try:
    pixels.yellow_marker(bytes(bad), [8, 8])
    raise AssertionError('expected marker refusal')
except pixels.Refused as error:
    failure = {'exceptionType': type(error).__name__, 'args': list(error.args), 'dict': vars(error)}
    assert not hasattr(error, 'samples') and not vars(error)
host = SimpleNamespace(processes=[])
session = SimpleNamespace(env={}, guard=lambda: None, host=host)
calls = []
def fake_run(argv, stdout, stderr, env, timeout):
    calls.append(argv)
    if argv[0] == '/usr/bin/grim':
        Path(argv[-1]).write_bytes(b'synthetic PNG stand-in; decoder mocked')
    elif argv[1] == 'identify':
        stdout.write(b'800 600')
    else:
        Path(argv[-1].removeprefix('rgb:')).write_bytes(image)
    return SimpleNamespace(returncode=0)
original_run = pixels.subprocess.run
try:
    pixels.subprocess.run = fake_run
    actual, record = pixels.capture(session, out / 'capture', time.monotonic() + 6)
finally:
    pixels.subprocess.run = original_run
assert actual == image and len(calls) == 3 and not host.processes
assert not any('pid' in key.lower() or 'process' in key.lower() for key in record)
report = {'passed': True, 'nativeAcceptance': False, 'scope': 'Actual pre-fix pixels functions with synthetic RGB and subprocess stubs; no GUI or tool launch', 'findings': ['nine yellow samples lack target attribution', 'marker mismatch provides no sample evidence on exception', 'successful capture has no registered helpers or process identity'], 'markerSamples': samples, 'failure': failure, 'captureRecord': record, 'hostProcesses': [], 'sourceSHA256': hashlib.sha256((r / 'initial/pixels.py').read_bytes()).hexdigest()}
(out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(str(out / 'report.json'))
