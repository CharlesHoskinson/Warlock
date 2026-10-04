#!/usr/bin/python3
"""Private CPU/QML probe backend. Root owns launching its QML consumer."""
import json
import os
from pathlib import Path
import sys

root = Path(os.environ['TASKBAR_FAKE_STATE_DIR'])
marker = root / 'started'
first = not marker.exists()
marker.write_text('started')
epoch = 'first' if first else 'second'

def emit(sequence, override=None):
    print(json.dumps({'protocolVersion':1,'epoch':override or epoch,'sequence':sequence,
        'groups':[],'snapGroups':[],'monitors':[],'settings':{},'focusedAddress':'',
        'reducedMotion':False}), flush=True)

emit(1)
if first:
    emit(1) # stale sequence
    emit(2, 'foreign') # unexpected epoch while same tracked process
    sys.exit(3)
for line in sys.stdin:
    if line == 'refresh\n':
        emit(2)
        (root / 'refresh-received').write_text('refresh')
