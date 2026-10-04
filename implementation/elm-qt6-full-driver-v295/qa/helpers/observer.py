"""Strict native toolkit role query. Intent in GTK alone never proves modality."""
import re
from journal import Refused,integer
ADDRESS=re.compile(r'0x[0-9a-f]+')
FIELDS={'address','pid','parentAddress','xdgToplevel','dialogPresent','dialogModal','nativeModal','inputBlocked','acceptsInput','hidden','xwayland'}
def roles(value,*,compositor_pid):
 if type(value) is not dict or set(value)!={'schema','pid','windows'} or integer(value['schema'],1,1)!=1 or integer(value['pid'],2,2**31-1)!=integer(compositor_pid,2,2**31-1):raise Refused('owning native role schema/PID')
 if type(value['windows']) is not list or len(value['windows'])>256:raise Refused('native role inventory bound')
 seen=set()
 for row in value['windows']:
  if type(row) is not dict or set(row)!=FIELDS:raise Refused('exact native role fields')
  for key in ('address','parentAddress'):
   if type(row[key]) is not str or not ADDRESS.fullmatch(row[key]) or len(row[key])>18:raise Refused('native address syntax')
  if row['address']=='0x0' or row['address'] in seen:raise Refused('unique live native address')
  seen.add(row['address']);integer(row['pid'],2,2**31-1)
  for key in FIELDS-{'address','pid','parentAddress'}:
   if type(row[key]) is not bool:raise Refused('canonical native role boolean')
 return value['windows']
def selected(rows,*,address,pid,parent_address=None,modal=None,blocked=None):
 matches=[r for r in rows if r['address']==address and r['pid']==pid]
 if len(matches)!=1:raise Refused('exact current native role/address/PID')
 row=matches[0]
 if not row['xdgToplevel'] or row['xwayland'] or row['hidden']:raise Refused('visible owning Wayland root required')
 if parent_address is not None and row['parentAddress']!=parent_address:raise Refused('native transient parent mismatch')
 if modal is not None:
  if type(modal) is not bool or row['nativeModal']!=modal:raise Refused('effective native modality mismatch')
 if blocked is not None:
  if type(blocked) is not bool or row['inputBlocked']!=blocked or row['acceptsInput']==blocked:raise Refused('effective native blocker mismatch')
 return row
