"""Bounded stdlib PNG decoder for actual cairo RGB/RGBA8 noninterlaced snapshots.
Validates chunk CRCs, exact inflate length, all five PNG row filters and genuine
decoded RGB color variation. No external image dependency and no OCR claim.
"""
import binascii
import pathlib
import struct
import zlib

class PNGError(ValueError): pass

def inspect_png(path):
    data=pathlib.Path(path).read_bytes()
    if len(data)>8*1024*1024 or data[:8]!=b'\x89PNG\r\n\x1a\n':raise PNGError('signature/size')
    offset=8;header=None;idat=[];ended=False;idat_closed=False
    while offset<len(data):
        if offset+12>len(data):raise PNGError('truncated chunk')
        size=struct.unpack('>I',data[offset:offset+4])[0];kind=data[offset+4:offset+8]
        if size>8*1024*1024 or offset+12+size>len(data):raise PNGError('chunk bound')
        body=data[offset+8:offset+8+size];crc=struct.unpack('>I',data[offset+8+size:offset+12+size])[0]
        if binascii.crc32(kind+body)&0xffffffff!=crc:raise PNGError('chunk CRC')
        if header is None and kind!=b'IHDR':raise PNGError('header first')
        if kind==b'IHDR':
            if header is not None or size!=13:raise PNGError('header shape')
            width,height,bits,color,compression,filtering,interlace=struct.unpack('>IIBBBBB',body)
            if not 0<width<=2048 or not 0<height<=2048 or width*height>1048576:raise PNGError('pixel bound')
            if bits!=8 or color not in [2,6] or (compression,filtering,interlace)!=(0,0,0):raise PNGError('unsupported snapshot format')
            header=(width,height,3 if color==2 else 4)
        elif kind==b'IDAT':
            if idat_closed:raise PNGError('noncontiguous IDAT')
            idat.append(body)
        elif kind==b'IEND':
            if size!=0 or not idat or offset+12!=len(data):raise PNGError('end shape/trailing bytes')
            ended=True;break
        else:
            if idat:idat_closed=True
            if kind[0]&32==0 and kind!=b'PLTE':raise PNGError('unknown critical chunk')
        offset+=size+12
    if not ended or header is None:raise PNGError('incomplete PNG')
    width,height,channels=header;stride=width*channels;expected=height*(stride+1)
    inflater=zlib.decompressobj()
    try:raw=inflater.decompress(b''.join(idat),expected+1)
    except zlib.error as e:raise PNGError('inflate') from e
    if len(raw)!=expected or not inflater.eof or inflater.unused_data or inflater.unconsumed_tail:raise PNGError('inflate length/trailing/bomb')
    previous=bytearray(stride);colors=set();offset=0
    def paeth(a,b,c):
        p=a+b-c;pa,pb,pc=abs(p-a),abs(p-b),abs(p-c)
        return a if pa<=pb and pa<=pc else b if pb<=pc else c
    for _ in range(height):
        mode=raw[offset];offset+=1
        if mode>4:raise PNGError('row filter')
        row=bytearray(raw[offset:offset+stride]);offset+=stride
        for i in range(stride):
            left=row[i-channels] if i>=channels else 0;up=previous[i];corner=previous[i-channels] if i>=channels else 0
            predictor=0 if mode==0 else left if mode==1 else up if mode==2 else (left+up)//2 if mode==3 else paeth(left,up,corner)
            row[i]=(row[i]+predictor)&255
        for i in range(0,stride,channels):colors.add(bytes(row[i:i+3]))
        previous=row
    return {'width':width,'height':height,'distinctColors':len(colors),'decodedPixels':width*height,'format':'RGB8' if channels==3 else 'RGBA8'}
