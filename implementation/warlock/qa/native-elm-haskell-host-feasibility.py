"""QA-only entry intended for implementation/warlock/qa/native-elm-haskell-host-feasibility.py."""
import hashlib
from pathlib import Path
import sys

sys.dont_write_bytecode = True
PACKET = Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/elm-haskell-redesign-20261030/astra-host-native-v3')
PINS = {
    'runner.py': '8d37d7da30374b7acafca84e8011c8fa21d648e76c9ada8ebc8d13c5f5351b03',
    'host_derivative.py': '849ce4e19cd8bd42782a885460f72269a2982f86b56db0655d05759f278bf8dc',
}
held = {}
for name, expected in PINS.items():
    raw = (PACKET / name).read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise RuntimeError('Frozen host feasibility source changed: ' + name)
    held[name] = raw
sys.argv[0] = str(PACKET / 'runner.py')
exec(compile(held['runner.py'], str(PACKET / 'runner.py'), 'exec'),
     {'__name__': '__main__', '__file__': str(PACKET / 'runner.py')})
