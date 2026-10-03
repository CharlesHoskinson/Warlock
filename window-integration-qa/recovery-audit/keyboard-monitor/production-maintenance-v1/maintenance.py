"""Offline future maintenance implementation. No CLI/load side effects on import."""
from dataclasses import dataclass
import json,os,re

class Refused(RuntimeError):pass
@dataclass(frozen=True)
class Identity:
 signature:str
 pid:int
 start:int
 socket_dev:int
 socket_inode:int

def resolve(rows,explicit=None,environment=None):
 preferred=explicit or environment
 selected=[r for r in rows if r['instance']==preferred] if preferred else rows
 if len(selected)!=1:raise Refused('exact compositor unavailable or ambiguous')
 return selected[0]

def approved_manifest(row):
 if not all(row.get(k) is True for k in ('nativeAccepted','productionAccepted','privateProbeAbsent')):raise Refused('production acceptance prerequisites missing')
 if not re.fullmatch('[a-f0-9]{64}',row.get('sha256','')):raise Refused('invalid immutable artifact hash')
 if not re.fullmatch('[A-Za-z0-9_.-]+',row.get('packageID','')):raise Refused('invalid package identity')
 if not row.get('library','').startswith(os.path.expanduser('~/.local/lib/')):raise Refused('library outside user-local versioned store')
 return row

class Maintenance:
 """Transport/observations are injected for source tests; deployment wires exact IPC.

 observe_identity revalidates UID/PID/start/socket dev/inode before EVERY call.
 observe_artifact verifies approved SHA/path/maps inode and unique plugin identity.
 No D-Bus maintenance or application key-grab call exists here.
 """
 def __init__(self,identity,artifact,observe_identity,observe_artifact,transport):
  self.identity=identity;self.artifact=approved_manifest(artifact)
  self.observe_identity=observe_identity;self.observe_artifact=observe_artifact;self.transport=transport
 def guard(self):
  if self.observe_identity()!=self.identity:raise Refused('compositor identity changed')
  self.observe_artifact(self.artifact)
 def ipc(self,*args):
  self.guard()
  return self.transport(['hyprctl','-i',self.identity.signature,*args],{'HYPRLAND_INSTANCE_SIGNATURE':self.identity.signature})
 def native_identity(self):
  value=json.loads(self.ipc('repl','return hl.plugin.omarchy_a11y.identity()'))
  if value['instance']!=self.identity.signature or value['packageID']!=self.artifact['packageID']:raise Refused('loaded maintenance identity mismatch')
  return value
 def load(self):
  # observe_artifact must establish no existing same namespace/plugin before load.
  result=self.ipc('plugin','load',self.artifact['library'])
  if result.strip()!='ok':raise Refused('plugin load failed: '+result)
  return self.native_identity()
 def unload(self):
  self.native_identity()
  code='return hl.plugin.omarchy_a11y.prepare_unload('+json.dumps(self.identity.signature)+','+json.dumps(self.artifact['packageID'])+')'
  value=json.loads(self.ipc('repl',code))
  if value.get('instance')!=self.identity.signature or value.get('packageID')!=self.artifact['packageID'] or value.get('ready') is not True:raise Refused('normal unload refused; existing bridge preserved')
  result=self.ipc('plugin','unload',self.artifact['library'])
  if result.strip()!='ok':raise Refused('normal unload failed; bridge remains retired: '+result)
  return value
