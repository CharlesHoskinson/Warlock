"""Read-only actual GDBus headers and callback chronology; no protocol calls."""
import json,os,time
from pathlib import Path
class WireTrace:
 def __init__(self,path):
  path=Path(path)
  if path.parent.stat().st_uid!=os.getuid() or path.parent.stat().st_mode&0o777!=0o700:
   raise RuntimeError('wire trace requires an owned0700 private attempt')
  self.fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_APPEND,0o600)
  self.arrivals=[]
 def record(self,event,**fields):
  row=dict(event=event,monotonic=time.monotonic(),wall=time.time(),**fields)
  os.write(self.fd,(json.dumps(row,default=str,separators=(',',':'))+'\n').encode());return row
 def filter(self,connection,message,incoming,user_data):
  body=message.get_body()
  header=dict(incoming=bool(incoming),messageType=int(message.get_message_type()),
      serial=message.get_serial(),replySerial=message.get_reply_serial(),
      sender=message.get_sender(),destination=message.get_destination(),
      interface=message.get_interface(),member=message.get_member(),
      body=body.unpack() if body else None)
  row=self.record('actual-wire-message',**header)
  if incoming and header['interface']=='org.freedesktop.a11y.PointerLocator' and header['member']=='PointerPositionChanged':
   self.arrivals.append(row)
  return message
 def close(self):os.close(self.fd)
