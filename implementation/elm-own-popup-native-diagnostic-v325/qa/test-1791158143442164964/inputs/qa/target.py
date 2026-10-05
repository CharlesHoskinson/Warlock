"""Join owning GTK/raw-resource observation to exact authenticated native incarnation."""
from join import Refused
from stamp import counter

def join_target(bound,snapshot,facts,*,pid,binding):
 identity=bound['identity'];native=bound['native'];wire=bound['wire'];gtk=bound['gtk']
 if type(pid) is not int or native['pid']!=pid or gtk['pid']!=pid:raise Refused('exact native and toolkit PID')
 if identity['surfaceId']!=wire['wlSurfaceId'] or wire['configure']['serial']!=wire['ack']['serial'] or not wire['configure']['index']<wire['ack']['index']<wire['lastCommitIndex']:raise Refused('current resource configure ACK committed buffer')
 if wire['parentToplevel'] is not None or native['xwayland'] is not False:raise Refused('ordinary owner actual Wayland role')
 if snapshot['binding']!=binding or facts['binding']!=binding:raise Refused('same authenticated native peer')
 title=f"ELM-GTK4-{identity['role']}-{pid}"
 if native['title']!=title:raise Refused('actual unique title/native resource join')
 rows=[w for w in snapshot['windows'] if w['label']==title]
 if len(rows)!=1:raise Refused('unique actual native projection label')
 inc=rows[0]['incarnation'];counter(inc)
 windows=[w for w in facts['facts']['windows'] if w['incarnation']==inc]
 if len(windows)!=1:raise Refused('exact scene incarnation')
 fact=windows[0]
 if fact['application']!=rows[0]['application'] or fact['minimized']!=rows[0]['minimized'] or fact['geometry']!=[*native['at'],*native['size']] or fact['owner'] is not None:raise Refused('current owner state/geometry compatibility')
 return {'identity':identity,'nativeAddress':native['address'],'nativePID':pid,'binding':binding,'incarnation':inc,'wire':wire,'nativeFact':fact,'presentationProved':False}

def same(before,after):
 for k in ('identity','nativeAddress','nativePID','binding','incarnation'):
  if before[k]!=after[k]:raise Refused('actual native/toolkit lifetime changed')
 for k in ('wlSurfaceId','surfaceEpoch','xdgSurfaceId','toplevelId','parentToplevel'):
  if before['wire'][k]!=after['wire'][k]:raise Refused('actual Wayland root/resource epoch changed')
 return True
