"""Draft private completed screencopy comparison, not physical cadence proof."""
from pathlib import Path
import hashlib,json,re
def require(value,message):
 if value is not True:raise ValueError(message)
def ppm(raw):
 require(type(raw)is bytes and len(raw)<=1600*1000*3+4096,'complete bounded current output bytes')
 # Fixed grim binary P6 output. Reject comments/unknown headers instead of
 # accepting malformed data or silently normalizing a different format.
 match=re.match(rb'P6\s+([1-9][0-9]*)\s+([1-9][0-9]*)\s+255\n',raw)
 require(match is not None,'exact RGB8 P6 header')
 width=int(match[1]);height=int(match[2]);require(width==1600 and height==1000,'actual configured unit-scale capture dimensions')
 data=raw[match.end():];require(len(data)==width*height*3,'exact complete RGB8 data, no stderr/trailing bytes')
 return width,height,data
def capture(controller,case,ordinal,output='WAYLAND-1'):
 controller.attest('before-private-output-capture');controller.session.guard()
 proc,row=controller.registry.launch(case,'shot',ordinal,output_name=output)
 proc.wait(timeout=2);path=Path(row['registered']['log'])
 raw=controller.raw('actual completed owned output capture',lambda:path.read_bytes().hex())
 data=bytes.fromhex(raw);frame=ppm(data)
 receipt=dict(kind='screencopy',output=output,rawSHA256=hashlib.sha256(data).hexdigest(),complete=True)
 controller.registry.terminal(proc,row,timeout=2,receipt=receipt)
 controller.attest('after-private-output-capture')
 return dict(receipt=receipt,path=str(path),frame=frame,scope='completed private compositor screencopy only; no hardware/cadence timestamp claim')
def roi(frame,rect):
 w,h,data=frame
 require(type(rect)is list and len(rect)==4 and all(type(v)is int for v in rect),'typed fixed interior pixel ROI')
 x,y,rw,rh=rect;require(rw>0 and rh>0 and 0<=x<x+rw<=w and 0<=y<y+rh<=h,'actual output-contained reference ROI')
 return b''.join(data[((y+i)*w+x)*3:((y+i)*w+x+rw)*3]for i in range(rh))
def protected_reference(owner,peer,overlap,rect):
 # Controller must separately bind same live owner/peer, unchanged actual boxes,
 # static interior widget content and actual source/complete frames. This pure
 # pixel comparison grants no lifetime/input/focus/native authority.
 a=roi(owner,rect);b=roi(peer,rect);c=roi(overlap,rect)
 require(a!=b,'discriminating actual owner/peer reference, no ambiguous pixels')
 require(c==a and c!=b,'actual protected pixels remain above peer in overlap')
 return dict(ownerSHA256=hashlib.sha256(a).hexdigest(),peerSHA256=hashlib.sha256(b).hexdigest(),overlapSHA256=hashlib.sha256(c).hexdigest(),rect=rect,presentationSubsetOnly=True)
