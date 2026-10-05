"""Strict owner GTK callback stamp, never a controller grant."""
import json,re
from join import Refused,pairs,constant,integer,fields
NAMES={'hostPopupProtocol','kind','hostLifetime','pid','start','sequence','mapGeneration','view','generation','topology','publication','lease','popupSurface','rootSurface','binding','displaySyncComplete'}
def counter(v):
 if type(v) is not str or not re.fullmatch('[1-9][0-9]{0,19}',v) or int(v)>2**64-1:raise Refused('canonical positive native counter')
 return int(v)
def parse(raw,*,pid,start,binding,previous=0):
 if type(raw) is not bytes or len(raw)>65536:raise Refused('stamp byte bound')
 try:o=json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,parse_constant=constant)
 except (ValueError,UnicodeError,RecursionError) as e:raise Refused('strict stamp JSON') from e
 fields(o,NAMES);integer(pid,2,2**31-1);counter(str(start));integer(previous,0,2**64-1)
 if type(o['hostPopupProtocol']) is not int or o['hostPopupProtocol']!=1:raise Refused('stamp protocol')
 if type(o['hostLifetime']) is not str or not re.fullmatch('[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}',o['hostLifetime']):raise Refused('host lifetime UUID')
 for k in ('pid','start','sequence','mapGeneration','view','generation','topology','publication','lease'):counter(o[k])
 if int(o['pid'])!=pid or o['start']!=str(start) or int(o['sequence'])<=previous:raise Refused('exact owner PID/start/ordered callback')
 for b in (o['binding'],binding):
  fields(b,{'lifetime','session','frontend'})
  for v in b.values():counter(v)
 if o['binding']!=binding:raise Refused('exact authenticated host binding')
 integer(o['popupSurface'],1,2**32-1);integer(o['rootSurface'],1,2**32-1)
 if o['popupSurface']==o['rootSurface']:raise Refused('distinct real resources')
 if o['kind'] not in ('host-popup-mapped','host-popup-sync-complete') or type(o['displaySyncComplete']) is not bool or o['displaySyncComplete']!=(o['kind']=='host-popup-sync-complete'):raise Refused('actual lifecycle callback phase')
 return o

def retired(before,after):
 if before['kind']!='host-popup-mapped' or after['kind']!='host-popup-sync-complete':raise Refused('map then actual display sync')
 if any(before[k]!=after[k] for k in NAMES-{'kind','sequence','displaySyncComplete'}) or int(after['sequence'])<=int(before['sequence']):raise Refused('exact original map identity retirement')
 return True
