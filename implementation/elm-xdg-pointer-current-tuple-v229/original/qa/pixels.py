"""Actual private output capture. Measurement records are not acceptance authority."""
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import time

ORACLE='implementation/elm-xdg-presented-landmark-oracle-v210'

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def oracle_inputs(repo):
    base=repo/ORACLE
    manifest=base/'component-manifest.json'
    pin=Path(__file__).resolve().parents[1]/'oracle-pin.json'
    expected=json.loads(pin.read_text())
    if digest(manifest)!=expected['manifestSHA256']:raise RuntimeError('Oracle held pin mismatch')
    packet=json.loads(manifest.read_text())
    files={str(pin):digest(pin),str(manifest):digest(manifest)}
    for name,row in packet['files'].items():
        path=base/name
        value=row if type(row) is str else row['sha256']
        if digest(path)!=value:raise RuntimeError('Oracle inventory mismatch: '+name)
        files[str(path)]=value
    if files.get(str(base/'oracle.py'))!=expected['oracleSHA256']:raise RuntimeError('Oracle source mismatch')
    return files

def held_oracle(repo):
    oracle_inputs(repo)
    path=repo/ORACLE/'oracle.py';spec=importlib.util.spec_from_file_location('held_landmark_oracle',path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result

def diagnostic_samples(rgb,width,height,args):
    """Capture all neighborhoods, even when the authoritative oracle refuses."""
    x,y,w,h=args['geometry'];rx,ry,_,_=args['real'];mx,my=args['monitor_origin'];s=args['monitor_scale'];serial=args['serial']
    local=[(x+4,y+4),(x+w-4,y+4),(x+4,y+h-4),(x+w-4,y+h-4),(x+w//2,y+h//2)]
    expected=[(255,48,48),(48,255,48),(48,48,255),(255,255,48),(0x28^(serial&63),0x71^((serial>>6)&63),0xc8^((serial>>12)&63))]
    samples=[]
    for (lx,ly),color in zip(local,expected):
        px,py=math.floor((rx+lx-x-mx)*s),math.floor((ry+ly-y-my)*s)
        measured=[]
        for dy in (-1,0,1):
            for dx in (-1,0,1):
                sx,sy=px+dx,py+dy
                offset=(sy*width+sx)*3
                measured.append({'pixel':[sx,sy],'rgb':list(rgb[offset:offset+3]) if 0<=sx<width and 0<=sy<height else None})
        samples.append({'surfaceLocal':[lx,ly],'screenshotPixel':[px,py],'expectedRGB':list(color),'measured':measured})
    return samples

def capture(session,host,output,name,events,identity,fact,buffer,raw,monitor,deadline,oracle):
    directory=output/(name+'-pixels-'+str(buffer['sequence']));directory.mkdir(mode=0o700)
    result={'passed':False,'directory':str(directory),'owner':identity,'incarnation':fact['incarnation'],'address':raw['address'],
            'bufferSequence':buffer['sequence'],'output':monitor,'native':raw,'buffer':buffer,'captureMethod':'one actual grim output capture; no capture retry'}
    def persist():
        result['artifacts']={p.name:digest(p) for p in directory.iterdir() if p.is_file() and p.name!='measurement.json'}
        (directory/'measurement.json').write_text(json.dumps(result,indent=2)+'\n')
    def command(argv,label):
        session.guard()
        remaining=deadline-time.monotonic()
        if remaining<=0:raise RuntimeError('Original six-second screenshot deadline')
        log=directory/(label+'.stderr');stream=os.fdopen(os.open(log,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb');session.host.logs.append(stream)
        process=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=stream,env=session.env,cwd=session.host.runtime,start_new_session=True)
        row=host.original.process(process.pid);row.update(name='pixel-'+label,command=argv,log=str(log));session.host.processes.append((process,row))
        try:stdout,_=process.communicate(timeout=remaining)
        except subprocess.TimeoutExpired:
            process.terminate()
            raise RuntimeError('Original six-second screenshot subprocess deadline')
        if process.returncode!=0:raise RuntimeError('Screenshot tool refused: '+label)
        if len(stdout)>256:raise RuntimeError('Screenshot metadata extent')
        if time.monotonic()>=deadline:raise RuntimeError('Original six-second screenshot completion deadline')
        session.guard();return stdout
    try:
        if not host.original.same_process(identity):raise RuntimeError('Capture owner retired')
        commits=[e for e in events if e.get('event')=='buffercommit']
        history=[e['ackedSerial'] for e in commits]
        selected=[e for e in events if e.get('event')=='configure' and e.get('serial')==buffer['ackedSerial']]
        if len(selected)!=1:raise RuntimeError('Selected configure serial reuse/wrap ambiguous')
        args={'monitor_origin':[monitor['x'],monitor['y']],'monitor_scale':monitor['scale'],
              'real':fact['visualGeometry'],'geometry':buffer['geometry'],'serial':buffer['ackedSerial'],
              'observed_serials':history,'diagnostic_nonzero':any(buffer['geometry'][:2])}
        # JSON parser commonly yields integer scales as 1.0; bind actual exact integer before invoking strict oracle.
        if type(args['monitor_scale']) not in (int,float) or args['monitor_scale'] not in (1,2):raise RuntimeError('Actual output scale unsupported')
        args['monitor_scale']=int(args['monitor_scale'])
        result['oracleArguments']=args;result['configureEvent']=selected[0];persist()
        png=directory/'capture.png';command(['/usr/bin/grim','-o',monitor['name'],str(png)],'grim')
        if not png.is_file() or png.stat().st_size>16*1024*1024:raise RuntimeError('PNG byte bound')
        dimensions=command(['/usr/bin/magick',str(png),'-format','%w %h','info:'],'dimensions').decode('ascii').split()
        if len(dimensions)!=2 or any(not v.isdigit() for v in dimensions):raise RuntimeError('PNG dimension grammar')
        width,height=map(int,dimensions)
        if [width,height]!=[monitor['width'],monitor['height']] or width*height*3>128*1024*1024:raise RuntimeError('Actual output capture dimensions')
        rgbfile=directory/'capture.rgb';command(['/usr/bin/magick',str(png),'-depth','8','rgb:'+str(rgbfile)],'decode')
        if rgbfile.stat().st_size!=width*height*3:raise RuntimeError('Decoded RGB extent')
        rgb=rgbfile.read_bytes();result['dimensions']=[width,height]
        result['samples']=diagnostic_samples(rgb,width,height,args);persist()
        result['oracleResult']=oracle.inspect(rgb,width,height,**args)
        if not host.original.same_process(identity):raise RuntimeError('Capture owner replaced')
        if time.monotonic()>=deadline:raise RuntimeError('Original six-second oracle deadline')
        result['passed']=True
    except Exception as error:result['error']=repr(error)
    finally:persist()
    return result
