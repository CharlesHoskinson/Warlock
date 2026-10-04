from pathlib import Path
import copy,hashlib,importlib.util,json,resource,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('observation',ROOT/'qa/parent_observation.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
value={'schema':1,'sequence':2,'revision':8,'parent':{'pid':20,'started':'30','uid':1000},'controller':{'pid':21,'started':'31'},'target':{'pid':22,'started':'32'},'viewId':3,'surfaceId':40,'surfaceExtent':[800,600],'corners':[[0,0],[800,0],[0,600],[800,600]],'viewportDestination':[800,600],'output':{'id':0,'name':'headless','origin':[0,0],'logicalExtent':[800,600],'modeExtent':[800,600],'scale':1},'pointer':{'global':[83,61],'focusedPid':22,'focusedStarted':'32','focusedViewId':3,'focusedSurfaceId':40}}
arguments={'sequence':2,'parent_pid':20,'parent_start':'30','uid':1000,'controller_pid':21,'controller_start':'31','target_pid':22,'target_start':'32','global_point':[83,61]}
checks=[]
def check(name,v,valid):
 try:m.proof(v,**arguments);passed=valid
 except ValueError:passed=not valid
 checks.append({'name':name,'passed':passed});assert passed,name
check('ActualTypedIdentityMapping',value,True)
def mutation(path,replacement):
 v=copy.deepcopy(value);node=v
 for key in path[:-1]:node=node[key]
 node[path[-1]]=replacement;return v
for label,path,replacement in [('wrongParent',['parent','pid'],23),('wrongController',['controller','started'],'33'),('wrongTarget',['target','pid'],21),('wrongUid',['parent','uid'],1001),('viewRetired',['viewId'],0),('surfaceRetired',['surfaceId'],0),('extentMismatch',['surfaceExtent'],[799,600]),('destinationMismatch',['viewportDestination'],[799,600]),('cornerOrigin',['corners',0],[1,0]),('outputOrigin',['output','origin'],[1,0]),('monitorScale2',['output','scale'],2),('parentModeMismatch',['output','modeExtent'],[1600,1200]),('focusForeign',['pointer','focusedPid'],21),('focusRetiredStart',['pointer','focusedStarted'],'99'),('focusOtherView',['pointer','focusedViewId'],4),('focusOtherSurface',['pointer','focusedSurfaceId'],41),('wrongGlobalPoint',['pointer','global'],[84,61]),('nonfinitePoint',['pointer','global'],[float('nan'),61]),('hugePositivePoint',['pointer','global'],json.loads(json.dumps([10**400,61]))),('hugeNegativePoint',['pointer','global'],json.loads(json.dumps([-10**400,61]))),('booleanPoint',['pointer','global'],[True,61]),('sequenceFloat',['sequence'],2.0),('extraField',['extra'],0),('startLeadingZero',['target','started'],'032'),('boolExtent',['surfaceExtent'],[True,600])]:check(label,mutation(path,replacement),False)
check('BufferDerivedDestination',mutation(['viewportDestination'],[-1,-1]),True)
check('HalfUnspecifiedDestination',mutation(['viewportDestination'],[-1,600]),False)
out=ROOT/'qa'/('observer-test-'+str(time.time_ns()));out.mkdir()
(out/'report.json').write_text(json.dumps({'passed':True,'checks':checks,'nativeObservation':False,'scope':'Typed consumer synthetic packet boundaries; no actual parent query','inputs':{str(ROOT/'qa/parent_observation.py'):hashlib.sha256((ROOT/'qa/parent_observation.py').read_bytes()).hexdigest(),str(Path(__file__)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}},indent=2)+'\n')
print(json.dumps({'passed':True,'checks':len(checks),'report':str(out/'report.json')}))
