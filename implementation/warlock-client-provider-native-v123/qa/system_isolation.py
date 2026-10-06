"""Explicit private refusing system-bus address; unsetting is not isolation."""
import os,stat
from pathlib import Path
from isolation import Refused,directory
NAME='denied-system-bus'
def refusing_address(runtime):
 runtime=directory(runtime);endpoint=runtime/NAME
 try:os.lstat(endpoint)
 except FileNotFoundError:pass
 else:raise Refused('Refusing system endpoint unexpectedly exists')
 return 'unix:path='+str(endpoint)
def supply(base,runtime):
 value=dict(base);value['DBUS_SYSTEM_BUS_ADDRESS']=refusing_address(runtime);return value
def validate(env,runtime):
 expected=refusing_address(runtime)
 if env.get('DBUS_SYSTEM_BUS_ADDRESS')!=expected:raise Refused('Missing/foreign/default system-bus override')
 return {'systemAddress':expected,'endpointAbsent':True,'defaultFallbackAllowed':False,'socketPeerPresent':False}
def validate_lineage(rows,runtime):
 if not rows:raise Refused('Empty observed process lineage')
 for row in rows:validate(row['environment'],runtime)
 return {'count':len(rows),'allObservedSystemOverridesExact':True,'completeLifetimeCoverage':False,'actualSocketPeerProved':False}
