"""Run the actual extracted Orca in this fixture's private home and buses.

Only speech output and an observation getter are adapted; no reader semantics
are replaced and no real sound/braille acceptance follows from the transcript.
"""
import os
from pathlib import Path
import shutil
import sys

runtime = Path(os.environ['XDG_RUNTIME_DIR']).resolve()
assert Path(os.environ['HOME']).resolve().is_relative_to(runtime)
for key in ['XDG_DATA_HOME', 'XDG_CONFIG_HOME', 'XDG_CACHE_HOME']:
    assert Path(os.environ[key]).resolve().is_relative_to(runtime)
assert os.environ['DBUS_SESSION_BUS_ADDRESS'] == 'unix:path=' + str(runtime / 'bus')
assert os.environ['AT_SPI_BUS_ADDRESS'] == 'unix:path=' + str(runtime / 'a11y-bus')
assert not Path(os.environ['DBUS_SYSTEM_BUS_ADDRESS'].removeprefix('unix:path=')).exists()
held = Path('/home/hoskinson/window-integration-qa/orca-reader')
prefix = held / 'prefix/usr'
adapter = runtime / 'orca-adapter'
adapter.mkdir(mode=0o700)
shutil.copyfile(held / 'silent_factory.py', adapter / 'silent_factory.py')
custom = Path(os.environ['XDG_DATA_HOME']) / 'orca'
custom.mkdir(mode=0o700, parents=True, exist_ok=True)
shutil.copyfile(held / 'data/orca/orca-customizations.py', custom / 'orca-customizations.py')
os.environ.update(PYTHONPATH=str(adapter) + ':' + str(prefix / 'lib/python3.14/site-packages'),
                  LD_LIBRARY_PATH=str(prefix / 'lib'),
                  GI_TYPELIB_PATH=str(prefix / 'lib/girepository-1.0'),
                  XDG_DATA_DIRS=str(prefix / 'share') + ':/usr/local/share:/usr/share',
                  GSETTINGS_BACKEND='memory')
os.environ.pop('ORCA_QA_LEGACY_GRAB_FIX', None)
os.execv('/usr/bin/python3', ['/usr/bin/python3', '-B', str(prefix / 'bin/orca'), '--speech-system', 'silent_factory', *sys.argv[1:]])
