import importlib.util,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
s=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('landmark',s/'oracle.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
checks=[]
def check(name,condition):assert condition,name;checks.append(name)
def image(scale,serial):
    width,height=240*scale,180*scale;pixels=bytearray(width*height*3)
    colors=[(255,48,48),(48,255,48),(48,48,255),(255,255,48),m.center_rgb(serial)]
    for (x,y),color in zip([(24,24),(116,24),(24,96),(116,96),(70,60)],colors):
        for yy in range((y-2)*scale,(y+3)*scale):
            for xx in range((x-2)*scale,(x+3)*scale):
                off=(yy*width+xx)*3;pixels[off:off+3]=bytes(color)
    return bytes(pixels),width,height
for scale in (1,2):
    rgb,w,h=image(scale,87)
    def invoke(**kw):
        args=dict(rgb=rgb,width=w,height=h,monitor_origin=[100,200],monitor_scale=scale,real=[120,220,100,80],geometry=[0,0,100,80],serial=87,observed_serials=[86,87]);args.update(kw);return m.inspect(**args)
    check('actual monitor scale '+str(scale),len(invoke()['samples'])==5)
    check('diagnostic origin transform '+str(scale),invoke(geometry=[16,24,100,80],diagnostic_nonzero=True)['nonzeroCapabilityAccepted'] is False)
    for name,kw in [('stale serial',{'serial':86}),('color alias',{'observed_serials':[87,87+2**18]}),('absent history',{'observed_serials':[]}),('double scale',{'monitor_scale':3-scale}),('wrong output origin',{'monitor_origin':[0,0]}),('wrong native extent',{'real':[120,220,101,80]}),('unsupported nonzero',{'geometry':[16,24,100,80]}),('short RGB',{'rgb':rgb[:-1]}),('clipped',{'real':[100,200,100,80]}),('nonfinite',{'real':[float('nan'),220,100,80]})]:
        try:invoke(**kw)
        except m.Refused:checks.append(name+' '+str(scale))
        else:raise AssertionError(name)
out=s/'qa'/('test-'+str(time.time_ns()));out.mkdir();report={'passed':True,'checks':checks,'scope':'Synthetic screenshot unsafe-transform/serial controls only; no native capture or presentation acceptance','nativeAcceptance':False};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'checks':len(checks)}))
