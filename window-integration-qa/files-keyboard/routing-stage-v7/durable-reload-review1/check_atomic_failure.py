#!/usr/bin/env python3
"""Actual sandbox rename failures, fake pidfd signals; no desktop/process mutation."""
from pathlib import Path
import json,tempfile,signal
from atomic_reload import replace_while_stopped,WriteFailure
checks=[]
with tempfile.TemporaryDirectory(prefix='files-atomic-gate-') as directory:
 b=Path(directory);rows=[]
 for n in range(3):
  live=b/f'live{n}';staged=b/f'staged{n}';rollback=b/f'rollback{n}'
  live.write_bytes(f'old{n}'.encode());staged.write_bytes(f'new{n}'.encode());rollback.write_bytes(live.read_bytes());rows.append({'path':str(n),'live':live,'staged':staged,'rollback':rollback})
 # Third write fails; rollback of the second also fails. The first must still
 # restore and CONT must still occur exactly once with the same handle.
 rows[2]['staged'].unlink();rows[1]['rollback'].unlink();signals=[]
 try:replace_while_stopped(987,rows,lambda handle,sig:signals.append((handle,sig)));raise AssertionError('failure not raised')
 except WriteFailure as error:
  checks=[{'name':'all replaced paths receive rollback attempts after one rollback fails','passed':rows[0]['live'].read_bytes()==b'old0' and rows[1]['live'].read_bytes()==b'new1'}, {'name':'rollback failure path retained explicitly','passed':error.replaced==['0','1'] and [r['path'] for r in error.rollback_errors]==['1']}, {'name':'STOP and CONT exactly once on exact handle after partial failure','passed':signals==[(987,signal.SIGSTOP),(987,signal.SIGCONT)]}, {'name':'unreplaced target unchanged','passed':rows[2]['live'].read_bytes()==b'old2'}]
 assert all(c['passed'] for c in checks)
print(json.dumps({'result':'pass','scope':'actual private filesystem rename failure; fake signals, no native deployment','checks':checks},indent=2))
