import hashlib,json,pathlib,sys,copy
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'qa'));from webgpu_claim import classify
checks=[]
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
base={'secureContext':True,'webgpu':{'exposed':True,'status':'executed','adapter':{'fallback':True},'value':42,'validation':None}}
r=classify(base);check('compute-known-result-distinct-from-hardware',r['capabilityRecordValid'] and r['computeResultQualified'] and not r['hardwareQualified'] and not r['wgslRenderQualified'])
for name,edit in [('wrong-result',lambda d:d['webgpu'].__setitem__('value',41)),('bool-result',lambda d:d['webgpu'].__setitem__('value',True)),('validation-error',lambda d:d['webgpu'].__setitem__('validation','error')),('missing-adapter',lambda d:d['webgpu'].pop('adapter')),('insecure-context',lambda d:d.__setitem__('secureContext',False)),('unexposed-execution',lambda d:d['webgpu'].__setitem__('exposed',False)),('unknown-status',lambda d:d['webgpu'].__setitem__('status','accepted'))]:
 d=copy.deepcopy(base);edit(d);r=classify(d);check('refuse-'+name,not r['capabilityRecordValid'] and not r['computeResultQualified'] and not r['hardwareQualified'])
for status in ['unavailable','no-adapter','failed']:
 d={'secureContext':True,'webgpu':{'exposed':status!='unavailable','status':status}};r=classify(d);check('explicit-'+status,r['capabilityRecordValid'] and not r['computeResultQualified'] and not r['hardwareQualified'])
check('malformed-record-refused',not classify({'secureContext':'true','webgpu':{}})['capabilityRecordValid'])
p=ROOT/'qa/claims-report.json';p.write_text(json.dumps({'passed':True,'checks':checks,'scope':'Synthetic CPU API/compute-claim classification only; no browser or GPU execution','sourceSHA256':hashlib.sha256((ROOT/'qa/webgpu_claim.py').read_bytes()).hexdigest()},indent=2)+'\n');print(json.dumps({'passed':True,'checks':len(checks)}))
