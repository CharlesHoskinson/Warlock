"""Read-only exact arithmetic/source audit of retained root Raster V6."""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import subprocess
import struct
import sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa/family-raster-oracle-v1')
from compare_scene import verify_scene
from raster_oracle import png_rgba,premultiply,render

def q(v):return F(str(v))
def nearest(x):return min(255,max(0,(x+F(1,2)).numerator//(x+F(1,2)).denominator))
def float32(x):return struct.unpack('f',struct.pack('f',x))[0]
def vertex_quantized_members(output,members):
    """Exact inverse viewport of the actual CPU GLfloat corner conversion.

    This models only Renderer.cpp's double-to-GLfloat vertex boundary. It
    does not assume rasterizer/texture-unit/interpolator arithmetic precision.
    """
    result=[]
    for m in members:
        r=m['rectangle'];ox,oy,ow,oh=(output[k] for k in ('x','y','width','height'))
        left=F.from_float(float32(2*(r['x']-ox)/ow-1))
        right=F.from_float(float32(2*(r['x']+r['width']-ox)/ow-1))
        top=F.from_float(float32(1-2*(r['y']-oy)/oh))
        bottom=F.from_float(float32(1-2*(r['y']+r['height']-oy)/oh))
        x=q(ox)+q(ow)*(left+1)/2;y=q(oy)+q(oh)*(1-top)/2
        result.append({**m,'rectangle':dict(x=x,y=y,width=q(ow)*(right-left)/2,height=q(oh)*(top-bottom)/2)})
    return result
def exact_pixel(output,members,x,y):
    lx=q(output['x'])+F(2*x+1,2)*q(output['width'])/output['bufferWidth']
    ly=q(output['y'])+F(2*y+1,2)*q(output['height'])/output['bufferHeight'];dst=[0]*4;steps=[]
    for m in members:
        r=m['rectangle'];rx,ry,rw,rh=(q(r[k]) for k in ('x','y','width','height'))
        if not (rx<=lx<rx+rw and ry<=ly<ry+rh):continue
        sw,sh=m['pixels'];sx=(lx-rx)/rw*sw-F(1,2);sy=(ly-ry)/rh*sh-F(1,2)
        ix,iy=sx.numerator//sx.denominator,sy.numerator//sy.denominator;fx,fy=sx-ix,sy-iy;sample=[F(0)]*4;taps=[]
        for dx,wx in ((0,1-fx),(1,fx)):
            for dy,wy in ((0,1-fy),(1,fy)):
                cx,cy=min(sw-1,max(0,ix+dx)),min(sh-1,max(0,iy+dy));base=(cy*sw+cx)*4;texel=list(m['premultiplied'][base:base+4]);weight=wx*wy;taps.append({'pixel':[cx,cy],'RGBA':texel,'weight':str(weight)})
                for c in range(4):sample[c]+=texel[c]*weight
        blended=[sample[c]+dst[c]*(1-sample[3]/255) for c in range(4)];new=[nearest(v) for v in blended]
        steps.append({'identity':[m['stableId'],m['pid']],'sampleCoordinates':[str(sx),str(sy)],'weights':[str(fx),str(fy)],'taps':taps,'sampleRGBA':[str(v) for v in sample],'previousRGBA':dst,'sourceOverRGBA':[str(v) for v in blended],'quantizedRGBA':new});dst=new
    return dst,steps

def main():
    evidence=Path('/home/hoskinson/window-integration-qa/family-raster-oracle-v6/attempt-private-1');destination=Path(__file__).parent;report={'nativeLaunch':False,'GPUOperation':False,'oracleChanged':False,'toleranceChanged':False,'sourceChecks':[],'pixelMath':[]}
    fixture=json.loads((evidence/'fixture-0-ORACLE-SECOND.json').read_text())
    for i,s in enumerate(fixture['members']):
        output=destination/f'cpu-upload-{i}.rgba';subprocess.run([str(destination/'decode-upload-cpu'),s['path'],s['digest'],*[str(v) for v in s['pixels']],str(output)],capture_output=True,check=True)
        expected=premultiply(png_rgba(Path(s['path']),s['digest'],tuple(s['pixels'])));actual=output.read_bytes()
        report['sourceChecks'].append({'source':s['path'],'PNG_SHA256':s['digest'],'pixels':s['pixels'],'actualFrozenUploadCPUBytesSHA256':hashlib.sha256(actual).hexdigest(),'independentPremultiplySHA256':hashlib.sha256(expected).hexdigest(),'byteCount':len(actual),'allBytesEqual':actual==expected})
        assert actual==expected
    cases=[('0-ORACLE-SECOND',[(48,107),(65,107),(65,108),(23,109),(23,110),(23,111),(23,112)]),('1-ORACLE-SECOND',[(73,166),(57,176)])]
    for stem,coords in cases:
        f=json.loads((evidence/f'fixture-{stem}.json').read_text());p=json.loads((evidence/f'presented-{stem}.json').read_text());output,members=verify_scene(f,p);members=[{**m,'stableId':s['stableId'],'pid':s['pid']} for m,s in zip(members,f['members'],strict=True)];ideal=render(output,members,background=(0,0,0,0));r=json.loads((evidence/f'readback-{stem}.json').read_text());path=evidence/'owned-readbacks'/r['filename'];actual=png_rgba(path,hashlib.sha256(path.read_bytes()).hexdigest(),(output['bufferWidth'],output['bufferHeight']))
        for x,y in coords:
            exact,steps=exact_pixel(output,members,x,y);base=(y*output['bufferWidth']+x)*4;double=list(ideal[base:base+4]);observed=list(actual[base:base+4])
            vertexMath,vertexSteps=exact_pixel(output,vertex_quantized_members(output,members),x,y)
            report['pixelMath'].append({'scene':stem,'pixel':[x,y],'exactRationalRGBA':exact,'existingDoubleOracleRGBA':double,'actualRawProducerRGBA':observed,'oracleMathEqual':exact==double,'steps':steps,'CPUFloat32VertexThenIdealRGBA':vertexMath,'vertexBoundarySteps':vertexSteps,'vertexModelOnly':True})
            assert exact==double
    source=destination.parent/'producer-readback-v4/Renderer.cpp';report['frozenRendererSHA256']=hashlib.sha256(source.read_bytes()).hexdigest();report['inference']='Exact frozen CPU upload bytes equal independent decoded/premultiplied bytes for all three complete textures. Exact rational sampling/source-over agrees with existing double oracle at all nine failing pixels. GPU filtering/vertex interpolation/fixed-function blend/unorm conversion/readback conversion remain potential boundaries; no unique GPU cause or repair established.'
    (destination/'retained-v6-arithmetic-source-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'sourceChecks':len(report['sourceChecks']),'failedPixelMathChecks':len(report['pixelMath']),'allEqual':True}))
if __name__=='__main__':main()
