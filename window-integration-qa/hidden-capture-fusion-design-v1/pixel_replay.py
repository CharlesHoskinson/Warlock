"""Real ImageMagick comparison of original hidden pixel operations and fusion."""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from qa_launch import require_qa_scope

def stamp(path):return {'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'mode':stat.S_IMODE(path.stat().st_mode)}
def save(path,row):
    with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())

def main():
    scope=require_qa_scope();magick=Path('/usr/bin/magick');source=stamp(Path(__file__));producer=stamp(magick)
    folder=HERE/'pixel-fixtures';folder.mkdir(mode=0o700,exist_ok=False)
    commands=[];cases=[]
    def run(argv):
        start=time.monotonic_ns();p=subprocess.run([str(magick),*map(str,argv)],capture_output=True,timeout=5)
        commands.append({'argv':[str(magick),*map(str,argv)],'exitCode':p.returncode,'elapsedNs':time.monotonic_ns()-start,'stderr':p.stderr.decode(errors='replace')})
        if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace'))
        return p.stdout
    for width,height in ((460,300),(200,100)):
        for alpha in (0,.25,.5,1):
            for background in ('none','#27394f'):
                index=len(cases);root=folder/str(index);root.mkdir(mode=0o700)
                raw=root/'raw.png';frame=root/'frame.png';oldthumb=root/'old-thumb.png';oldwhole=root/'old-whole.png';newthumb=root/'new-thumb.png';newwhole=root/'new-whole.png'
                left,top,right,bottom=7,31,7,7
                run(['-size',f'{width}x{height}','xc:none','-fill',f'rgba(231,72,118,{alpha})','-draw',f'rectangle 0,0 {width-1},{height-1}','-fill',f'rgba(25,187,91,{alpha})','-draw',f'rectangle 11,13 {width//2},{height//2}',raw])
                run(['-size',f'{width+left+right}x{height+top+bottom}',f'xc:{background}','-fill','#bc882a','-draw',f'rectangle 0,0 {width+left+right-1},20',frame])
                resize=f'{width}x{height}!';geometry=f'+{left}+{top}'
                run([raw,'-thumbnail','300x180>',oldthumb])
                run([frame,'(',raw,'-resize',resize,')','-geometry',geometry,'-compose','SrcAtop','-composite',oldwhole])
                run(['-respect-parentheses','(',raw,'-thumbnail','300x180>','-write',newthumb,'+delete',')',frame,'(',raw,'-resize',resize,')','-geometry',geometry,'-compose','SrcAtop','-composite',newwhole])
                outputs=[]
                for role,old,new in (('raw-client-thumbnail',oldthumb,newthumb),('whole-composition',oldwhole,newwhole)):
                    oldspec=run([old,'-format','%w,%h,%z,%[channels]','info:']);newspec=run([new,'-format','%w,%h,%z,%[channels]','info:'])
                    oldpixels=run([old,'-depth','16','rgba:-']);newpixels=run([new,'-depth','16','rgba:-'])
                    if oldspec!=newspec or oldpixels!=newpixels:raise ValueError('actual pixel/geometry/channel equivalence failed')
                    outputs.append({'role':role,'geometryDepthChannels':oldspec.decode(),'rgba16SHA256':hashlib.sha256(oldpixels).hexdigest(),'old':{'path':str(old),**stamp(old)},'new':{'path':str(new),**stamp(new)}})
                cases.append({'index':index,'clientSize':[width,height],'alpha':alpha,'frameBackground':background,'outputs':outputs})
    if stamp(Path(__file__))!=source or stamp(magick)!=producer:raise ValueError('source/producer changed')
    report={'result':'pass','scope':scope,'cases':cases,'commands':commands,'source':source,'producer':{'path':str(magick),**producer},'nativeLaunch':False,'candidateApplied':False,'timingAcceptance':False,'limitations':['Synthetic PNG inputs; genuine native grim capture unchanged and not executed here','Does not establish B14 blocking callsite or production scene deadline success','PNG encoder metadata/hash may differ; decoded RGBA16, geometry, depth and channel layout compared exactly']}
    save(HERE/'pixel-replay.json',report);print(json.dumps({'result':'pass','cases':len(cases),'comparisons':2*len(cases),'report':str(HERE/'pixel-replay.json')}))

if __name__=='__main__':main()
