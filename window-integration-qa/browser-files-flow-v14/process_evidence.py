"""Read-only owned process evidence. Importing does not read /proc or launch clients."""
from pathlib import Path
import base64,os,re,time
BINARY='/opt/brave-bin/brave'
def classify(raw):
 """Recognize exact argv switches or Chromium's one-string setproctitle form.

 The flattened form is diagnostic process-title tokens, never reconstructed argv.
 Its executable prefix must be exact; embedded switches in a value do not count.
 """
 if not isinstance(raw,bytes) or not raw or not raw.endswith(b'\0'):return {'role':None,'encoding':'unrecognized','reason':'Missing complete NUL-terminated cmdline'}
 parts=raw.rstrip(b'\0').split(b'\0')
 if len(parts)==1 and parts[0].startswith(BINARY.encode()+b' '):
  title=parts[0]
  if any(x in title for x in (b'\t',b'\r',b'\n',b'"',b"'")):
   return {'role':None,'encoding':'single-process-title','reason':'Ambiguous title characters'}
  tokens=title.split(b' ')
  # Chromium's title does not retain quoting. Only its leading role switch is
  # authoritative in this encoding; values later in the title are never scanned
  # to infer a renderer role. Preserve all tokens as evidence, not argv.
  encoding='single-process-title'
  if len(tokens)<2 or tokens[1]!=b'--type=renderer':return {'role':None,'encoding':encoding,'reason':'No leading exact renderer role'}
 elif len(parts)>1 and parts[0]==BINARY.encode():tokens=parts;encoding='nul-argv'
 else:return {'role':None,'encoding':'unrecognized','reason':'Exact executable argv/title prefix absent'}
 role_tokens=[t for t in tokens[1:] if t.startswith(b'--type=')]
 if role_tokens!=[b'--type=renderer']:return {'role':None,'encoding':encoding,'reason':'Missing, duplicate or conflicting role switch'}
 if any(t==b'--no-sandbox' or t.startswith(b'--no-sandbox=') for t in tokens[1:]):raise RuntimeError('Sandbox-disabled owned renderer refused')
 return {'role':'renderer','encoding':encoding,'roleTokens':[t.decode('ascii') for t in role_tokens]}
def snapshot(identity,same,proc=Path('/proc')):
 """Record every field and read failure before classification. Lifetime is checked twice."""
 pid=identity['pid'];p=proc/str(pid)
 record={'identity':dict(identity),'monotonicNs':time.monotonic_ns(),'lifetimeBefore':same(identity),'errors':{}}
 if not record['lifetimeBefore']:record['exitedDuringObservation']=True;return record
 def read(key,fn):
  try:record[key]=fn()
  except OSError as error:record['errors'][key]={'type':type(error).__name__,'errno':error.errno,'error':str(error)}
 read('rawCmdlineBase64',lambda:base64.b64encode((p/'cmdline').read_bytes()).decode('ascii'))
 read('status',lambda:(p/'status').read_text())
 read('stat',lambda:(p/'stat').read_text())
 read('exe',lambda:os.readlink(p/'exe'))
 for key,name in [('userNamespace','user'),('netNamespace','net'),('pidNamespace','pid'),('mountNamespace','mnt')]:read(key,lambda name=name:os.readlink(p/'ns'/name))
 record['lifetimeAfter']=same(identity)
 if 'rawCmdlineBase64' in record:
  raw=base64.b64decode(record['rawCmdlineBase64']);record['rawCmdlineBytes']=len(raw);record['nulSplit']=[x.decode('utf-8',errors='backslashreplace') for x in raw.split(b'\0')]
 if 'status' in record:record['statusFields']={k:v.strip() for k,v in (line.split(':',1) for line in record['status'].splitlines() if ':' in line)}
 record['exitedDuringObservation']=not record['lifetimeAfter'];return record
def renderer(record,uid,parent_netns):
 if record.get('exitedDuringObservation'):return None
 required=('rawCmdlineBase64','status','netNamespace','userNamespace')
 if any(k not in record for k in required):raise RuntimeError('Live owned process evidence unreadable:'+repr(record['identity']))
 classification=classify(base64.b64decode(record['rawCmdlineBase64']));record['classification']=classification
 if classification['role']!='renderer':return None
 fields=record['statusFields'];uids=fields.get('Uid','').split()
 if uids!=[str(uid)]*4:raise RuntimeError('Actual renderer real/effective/saved/filesystem UID mismatch')
 if fields.get('Seccomp')!='2' or fields.get('NoNewPrivs')!='1' or record['netNamespace']==parent_netns:raise RuntimeError('Actual renderer sandbox/network refusal')
 if not record.get('lifetimeBefore') or not record.get('lifetimeAfter'):raise RuntimeError('Renderer lifetime changed during evidence capture')
 return {'identity':record['identity'],'encoding':classification['encoding'],'rawCmdlineBase64':record['rawCmdlineBase64'],'nulSplit':record['nulSplit'],'seccomp':fields['Seccomp'],'noNewPrivileges':fields['NoNewPrivs'],'uids':uids,'userNamespace':record['userNamespace'],'netNamespace':record['netNamespace'],'readErrors':record['errors']}
