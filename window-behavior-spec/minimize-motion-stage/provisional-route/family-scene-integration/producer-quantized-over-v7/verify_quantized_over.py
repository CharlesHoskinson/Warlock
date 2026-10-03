"""Independent configuration gate; actual full pixels remain a separate oracle."""
import ast
import hashlib
import re
from verify_sampling import verify as verify_sampling

POLICY='per-layer-explicit-over-nearest-rgba8-v1'

def shader_digests(header):
    over=re.search(r'fragment=R"GLSL\((.*?)\)GLSL";',header,re.S)
    copy=re.search(r'copyFragment=("[^"\n]*");',header)
    if not over or not copy:raise ValueError('frozen complete over/copy source absent')
    return (hashlib.sha256(over[1].encode()).hexdigest(),
            hashlib.sha256(ast.literal_eval(copy[1]).encode()).hexdigest())

def positive(value):return type(value) is int and 0<value<=0x7fffffff

def copy_state(record,framebuffer,texture,extent,program,attachment=0):
    if not isinstance(record,dict):raise ValueError('actual copy state missing')
    expected={'program':program,'framebuffer':framebuffer,'texture':texture,'unit':1,'extentUniform':extent,
        'minFilter':9728,'magFilter':9728,'wrapS':33071,'wrapT':33071,'blend':False,'inspectionError':0,
        'attachedTexture':attachment,'attachmentType':5890 if framebuffer else 0}
    if (not positive(record.get('program')) or any(record.get(k)!=v or type(record.get(k)) is not type(v) for k,v in expected.items())):
        raise ValueError('actual copy sampler/target/program/extent/disabled-blend differs')

def verify(events,readback,source_material,expected_shader_digests):
    over_digest,copy_digest=expected_shader_digests
    shaders=[e for e in events if e.get('event')=='quantizedOverExperiment']
    if len(shaders)!=1 or not positive(shaders[0].get('overProgram')) or not positive(shaders[0].get('copyProgram')) or shaders[0]['overProgram']==shaders[0]['copyProgram']:
        raise ValueError('positive distinct compiled program roles required')
    over_program,copy_program=shaders[0]['overProgram'],shaders[0]['copyProgram']
    expected={'overProgram':over_program,'copyProgram':copy_program,'event':'quantizedOverExperiment','policy':POLICY,'fragmentSHA256':over_digest,
        'copyFragmentSHA256':copy_digest,'rasterDiagnostic':True,'nativeAuthority':False,'pixelProof':False}
    if shaders!=[expected]:raise ValueError('actual exact compiled experiment configuration absent')
    paths=[e for e in events if e.get('event')=='rasterPathSelected']
    if paths!=[{'event':'rasterPathSelected','path':'shader-per-layer-quantized-over','sampler':'four-nearest-centers-highp-bilinear','rasterDiagnostic':True,'nativeAuthority':False,'pixelProof':False}]:raise ValueError('explicit selected diagnostic path differs')
    sampling=verify_sampling(events,source_material,over_digest)
    matching=[e for e in events if e.get('event')=='quantizedOverFrameConfigured' and e.get('sequence')==readback['sequence']]
    if len(matching)!=1:raise ValueError('one exact immutable sequence configuration required')
    frame=matching[0]
    if (frame.get('policy')!=POLICY or frame.get('nativeAuthority') is not False or frame.get('pixelProof') is not False
            or any(frame.get(k)!=readback[k] for k in ('token','sequence','output','generation','bufferWidth','bufferHeight','members'))):
        raise ValueError('immutable frame/output/source/extent binding differs')
    extent=[frame['bufferWidth'],frame['bufferHeight']]
    if any(not positive(v) for v in extent) or type(frame['generation']) is not int or frame['generation']<=0:
        raise ValueError('exact current generation and buffer extent required')
    sampler={e['textureId']:e for e in events if e.get('event')=='samplingConfigured'}
    passes=frame.get('passes')
    if not isinstance(passes,list) or not passes:raise ValueError('complete ordered source-over passes missing')
    groups=[];group=[]
    for p in passes:
        if not isinstance(p,dict) or not positive(p.get('prefixCount')):raise ValueError('bounded integer prefix index required')
        if p['prefixCount']==1 and group:groups.append(group);group=[]
        if p['prefixCount']!=len(group)+1:raise ValueError('prefix source order has a gap/repetition')
        group.append(p)
    groups.append(group)
    family=groups[-1]
    if len(family)!=len(source_material):raise ValueError('complete immutable family vector required')
    if len(groups)>1:
        if [[p.get('controlIndex') for p in g] for g in groups[:-1]]!=[[1],[0,1],[0,1,2]]:
            raise ValueError('exact control pass vectors required')
    pair=None
    for group in groups:
        previous=None
        for p in group:
            read,write=p.get('readTexture'),p.get('writeTexture');fbo=p.get('writeFramebuffer')
            if any(not positive(v) for v in (read,write,fbo,p.get('sourceTexture'),p.get('shaderProgram'))) or len({read,write,p['sourceTexture']})!=3 or type(p.get('shaderProgram')) is not int or p['shaderProgram']!=over_program:
                raise ValueError('separate exact bounded source/prefix attachment IDs required')
            current={read,write}
            if pair is None:pair=current
            if current!=pair or previous is not None and read!=previous:
                raise ValueError('previous prefix attachment or output ownership changed')
            previous=write
            wanted={'readTextureBinding':read,'sourceTextureBinding':p['sourceTexture'],'attachedTexture':write,
                'attachmentType':5890,'blend':False,'bits':[8,8,8,8],'samples':0,'minFilter':9728,'magFilter':9728,
                'wrapS':33071,'wrapT':33071,'sourceUnit':0,'prefixUnit':1,'extentUniform':extent,'inspectionError':0}
            if any(p.get(k)!=v or type(p.get(k)) is not type(v) for k,v in wanted.items()):raise ValueError('actual prefix state differs')
            copy_state(p.get('prefixCopy'),fbo,read,extent,copy_program,write)
            upload=sampler.get(p['sourceTexture'])
            if not upload or type(p.get('controlIndex')) is not int or any(p.get(k)!=upload.get(k) for k in ('sourceDigest','pixels','controlIndex')):
                raise ValueError('actual queried source texture differs from immutable upload')
    for p,source,member in zip(family,source_material,frame['members'],strict=True):
        if (p['controlIndex']!=-1 or p['sourceDigest']!=source['digest'] or p['pixels']!=source['pixels']
                or member['digest']!=source['digest']):raise ValueError('ordered family source/digest/extent mismatch')
    copy_state(frame.get('finalCopy'),0,family[-1]['writeTexture'],extent,copy_program)
    return {'policy':POLICY,'sequence':frame['sequence'],'output':frame['output'],'generation':frame['generation'],
        'familyPassCount':len(family),'controlPassCount':sum(len(g) for g in groups[:-1]),
        'actualConfigurationGate':True,'sampling':sampling,'pixelProof':False,'nativeAuthority':False}
