"""Network namespace authority checked before browser exec; no imports spawn."""
import os,socket
from pathlib import Path

def routes(ipv4,ipv6):
 rows=ipv4.splitlines()[1:]
 for row in rows:
  fields=row.split()
  if fields and fields[0]!='lo':raise RuntimeError('External IPv4 route present')
 for row in ipv6.splitlines():
  fields=row.split()
  if fields and fields[-1]!='lo':raise RuntimeError('External IPv6 route present')
 return {'ipv4':ipv4,'ipv6':ipv6}

def network_authority(parent_namespace,expected_uid):
 current=os.readlink('/proc/self/ns/net')
 if os.getuid()!=expected_uid or os.geteuid()!=expected_uid:raise RuntimeError('Browser namespace must retain user UID')
 if current==parent_namespace:raise RuntimeError('Browser must have independent network namespace')
 result=routes(Path('/proc/net/route').read_text(),Path('/proc/net/ipv6_route').read_text())
 interfaces=sorted(name for _,name in socket.if_nameindex())
 if interfaces!=['lo']:raise RuntimeError('Browser net namespace has external interface')
 result.update(parentNetNamespace=parent_namespace,netNamespace=current,uid=os.getuid(),interfaces=interfaces)
 return result
