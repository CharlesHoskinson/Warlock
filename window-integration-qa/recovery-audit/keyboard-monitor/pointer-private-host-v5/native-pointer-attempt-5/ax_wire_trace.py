"""Read-only dbus-monitor correlation for actual private AX component calls."""
import re
from pathlib import Path
HEAD=re.compile(r'(?m)^(method call|method return|error|signal) ([^\n]*)\n')
def packets(text):
    found=list(HEAD.finditer(text));out=[]
    for i,m in enumerate(found):
        header=m.group(2);fields=dict(re.findall(r'(time|sender|destination|serial|reply_serial|path|interface|member)=([^ ;]+)',header))
        # dbus-monitor expresses destination as an arrow, not key=value.
        route=re.search(r' -> destination=([^ ;]+)',header)
        if route:fields['destination']=route.group(1)
        fields.update(kind=m.group(1),body=text[m.end():found[i+1].start() if i+1<len(found) else len(text)])
        out.append(fields)
    return out
def signed_query_evidence(path,*,after,reader_bus,app_bus,x,y,item_path):
    try:rows=packets(Path(path).read_text())
    except OSError:return []
    replies={(r.get('destination'),r.get('reply_serial')):r for r in rows if r['kind']=='method return'}
    matches=[]
    for row in rows:
        if row['kind']!='method call' or row.get('interface')!='org.a11y.atspi.Component' or row.get('member')!='GetAccessibleAtPoint':continue
        if row.get('sender')!=reader_bus or row.get('destination')!=app_bus or float(row.get('time','0'))<after:continue
        coords=[int(v) for v in re.findall(r'^\s*int32 (-?\d+)\s*$',row['body'],re.M)]
        # WINDOW is the official signed component query's coordinate convention.
        coord_type=re.findall(r'^\s*uint32 (\d+)\s*$',row['body'],re.M)
        if coords!=[x,y] or coord_type!=['1']:continue
        reply=replies.get((reader_bus,row.get('serial')))
        if reply is None or reply.get('sender')!=app_bus:continue
        paths=re.findall(r'object path "([^"]+)"',reply['body'])
        if item_path not in paths:continue
        matches.append(dict(call=row,reply=reply,signedCoordinates=coords,coordType='WINDOW',actualItemPath=item_path))
    return matches
