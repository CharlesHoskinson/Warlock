"""Reconstruct complete reviewed V10 originals from explicit diagnostic-only hunks."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent
OLD=B.parent/'toolkit-held-matrix-v10'
def reconstructed(name,data=None):
 rows=json.loads((B/'source-delta-v11.json').read_text());row=rows[name]
 old=(OLD/name).read_bytes()
 if hashlib.sha256(old).hexdigest()!=row['oldSHA256']:raise RuntimeError('Immutable original source changed')
 source=old.decode();lines=source.splitlines(keepends=True);expected=[];cursor=0
 for hunk in row['hunks']:
  first,last=hunk['oldRange']
  if first<cursor or ''.join(lines[first:last])!=hunk['old']:raise RuntimeError('Exact diagnostic source hunk differs')
  expected.append(''.join(lines[cursor:first]));expected.append(hunk['new']);cursor=last
 expected.append(''.join(lines[cursor:]));expected=''.join(expected).encode()
 actual=(B/name).read_bytes() if data is None else data
 if name=='helper_observer.py':
  fresh=b'    except (FileNotFoundError, ProcessLookupError) as error:\n        if error.errno not in (errno.ENOENT, errno.ESRCH):raise\n        return False\n'
  before_except=b'    except FileNotFoundError:\n        return False\n'
  if actual.count(b'import errno\n')!=1 or actual.count(fresh)!=1:raise RuntimeError('Exact selected process disappearance refinement differs')
  actual=actual.replace(b'import errno\n',b'',1).replace(fresh,before_except,1)
 if actual!=expected:raise RuntimeError('Source differs beyond exact diagnostic-only hunks: '+name)
 return old

def reconstructed_runner(data=None):
 actual=(B/'run_native.py').read_bytes() if data is None else data
 additions=[b'\nimport private_output_host,output_readiness',b'    host_api=private_output_host.adapt(host_api)\n',b"            report['exactOutputReadiness']=output_readiness.collect(session,output/'host/output-readiness-evidence.json')\n"]
 for addition in additions:
  if actual.count(addition)!=1:raise RuntimeError('Exact bounded output insertion differs')
  actual=actual.replace(addition,b'',1)
 if actual!=(B.parent/'toolkit-held-matrix-v12/run_native.py').read_bytes():raise RuntimeError('Runner differs beyond exact output adapter and collector')
 return actual
