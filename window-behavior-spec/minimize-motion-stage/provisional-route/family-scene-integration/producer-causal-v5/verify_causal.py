"""Independent read-only diagnostic binding/math. No native/GL operations."""
import hashlib
import math
import os
from pathlib import Path
import re
import stat
import sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa/family-raster-oracle-v1')
from compare_scene import verify_scene
from raster_oracle import png_rgba,render,compare

COLORS=((100,50,25,255),(10,0,0,128),(0,12,24,64))
ORDERS=((1,),(0,1),(0,1,2))
FIELDS=('token','digest','stableId','pid','sequence','output','generation','progress','members','bufferWidth','bufferHeight')

def checked_rect(r):
    if not isinstance(r,dict) or set(r)!={'x','y','width','height'}:raise ValueError('complete exact rectangle required')
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in r.values()) or r['width']<=0 or r['height']<=0:raise ValueError('invalid rectangle')
    return r

def bind(record,fixture,full,swap,presented):
    if (record.get('event')!='ownedCausalReadback' or record.get('nativeAuthority') is not False
            or record.get('presentationProof') is not False or record.get('readError')!=0
            or record.get('encoding')!='premultiplied-RGBA8-top-left'):
        raise ValueError('diagnostic event/error/authority invalid')
    if (full.get('event')!='ownedFramebufferReadback' or full.get('readError')!=0
            or full.get('nativeAuthority') is not False or full.get('presentationProof') is not False
            or swap.get('event')!='swap' or swap.get('success') is not True):raise ValueError('matching complete own successful swap required')
    if re.fullmatch(r'[0-9a-f]{12}-[1-9][0-9]{0,14}',record.get('token','')) is None or re.fullmatch(r'[1-9][0-9]{0,19}',str(record.get('sequence',''))) is None:raise ValueError('whole token/sequence grammar required')
    if isinstance(record.get('progress'),bool) or not isinstance(record.get('progress'),(float,int)) or not math.isfinite(record['progress']) or not 0<=record['progress']<=1:raise ValueError('finite numeric held progress required')
    for field in FIELDS:
        if field not in record or any(r.get(field)!=record[field] for r in (full,swap,presented)):
            raise ValueError('exact full-frame binding mismatch: '+field)
    for m in record['members']:checked_rect(m['rectangle'])
    output,sources=verify_scene(fixture,presented)
    logical={k:output[k] for k in ('x','y','width','height')}
    if checked_rect(record.get('logicalOutput'))!=logical or any(record[k]!=output[k] for k in ('bufferWidth','bufferHeight')):raise ValueError('output logical/buffer extent differs')
    gl=full.get('glBuffer',{});egl=full.get('eglConfig',{})
    if any(gl.get(c)!=8 or egl.get(c)!=8 for c in ('red','green','blue','alpha')) or gl.get('samples')!=0 or egl.get('samples')!=0 or gl.get('framebuffer')!=0:raise ValueError('requires actual unmultisampled RGBA8 owned buffer')
    if record.get('nativeFormat') not in (0x1908,0x80e1) or record.get('nativeType')!=0x1401 or record['nativeFormat']!=gl.get('readFormat') or record['nativeType']!=gl.get('readType'):raise ValueError('actual queried supported native pair differs')
    if record.get('kind')=='member-prefix':
        n=record.get('prefixCount')
        if isinstance(n,bool) or not isinstance(n,int) or not 1<=n<=len(sources) or record.get('prefixMembers')!=record['members'][:n] or record.get('controls')!=[]:raise ValueError('exact actual ordered prefix required')
        expected=render(output,sources[:n],background=(0,0,0,0));tolerance=fixture['channelTolerance']
    elif record.get('kind')=='constant-control':
        controls=record.get('controls',[]);order=tuple(c.get('index') for c in controls)
        if order not in ORDERS or record.get('prefixCount')!=0 or record.get('prefixMembers')!=[] or controls!=[{'index':i,'premultipliedRGBA':list(COLORS[i])} for i in order]:raise ValueError('predeclared constant sample order/bytes required')
        members=[{'pixels':(1,1),'premultiplied':bytes(COLORS[i]),'rectangle':logical} for i in order]
        expected=render(output,members,background=(0,0,0,0));tolerance=0
    else:raise ValueError('unknown observation kind')
    return output,expected,tolerance

def read_image(directory,filename,raw_digest,extent):
    directory=Path(directory);ds=directory.lstat()
    if directory.resolve()!=directory.absolute() or not stat.S_ISDIR(ds.st_mode) or ds.st_uid!=os.getuid() or ds.st_mode&0o077:raise ValueError('exact private non-symlink directory required')
    if re.fullmatch(r'causal-[1-9][0-9]{0,19}-[1-9][0-9]{0,19}-[0-9]{1,3}-(rgba|native-rgba)\.png',filename or '') is None or re.fullmatch(r'[0-9a-f]{64}',raw_digest or '') is None:raise ValueError('diagnostic path/digest invalid')
    path=directory/filename;fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        s=os.fstat(fd)
        if not stat.S_ISREG(s.st_mode) or s.st_uid!=os.getuid() or s.st_mode&0o077 or s.st_size>256*1024*1024:raise ValueError('private regular bounded owned evidence required')
        parts=[]
        while part:=os.read(fd,1048576):parts.append(part)
        data=b''.join(parts);after=os.fstat(fd);named=path.lstat()
        fields=lambda a:(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)
        if fields(s)!=fields(after) or fields(s)!=fields(named):raise ValueError('evidence changed during read')
    finally:os.close(fd)
    class ImmutablePNG:
        def read_bytes(self):return data
    rgba=png_rgba(ImmutablePNG(),hashlib.sha256(data).hexdigest(),extent)
    if hashlib.sha256(rgba).hexdigest()!=raw_digest:raise ValueError('full raw evidence digest differs')
    return rgba

def compare_observation(record,fixture,full,swap,presented,directory):
    output,expected,tolerance=bind(record,fixture,full,swap,presented)
    w,h=output['bufferWidth'],output['bufferHeight'];extent=(w,h)
    stem=f"causal-{record['sequence']}-{record['generation']}-"
    a,b=record['rgbaFilename'],record['nativeRGBAFilename']
    if not a.startswith(stem) or a[:-9]+'-native-rgba.png'!=b:raise ValueError('evidence names differ from bound sequence/generation/pair')
    actual=read_image(directory,a,record['rgbaSHA256'],extent);native=read_image(directory,b,record['nativeRGBASHA256'],extent)
    if record.get('allReadFormatBytesEqual') is not (actual==native):raise ValueError('assigned equality differs from actual complete bytes')
    return {'nativeAuthority':False,'presentationProofForPrefix':False,'fullRGBACompared':True,
            'readFormatCompleteEquality':actual==native,'RGBA':compare(actual,expected,w,h,tolerance),
            'nativeRGBA':compare(native,expected,w,h,tolerance),'tolerance':tolerance}
