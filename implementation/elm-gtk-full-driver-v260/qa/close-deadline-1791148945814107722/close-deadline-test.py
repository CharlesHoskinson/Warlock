"""Actual complete Driver.run rejects a close which finishes after original6s."""
import hashlib,importlib.util,json,os,pathlib,resource,sys,time
from types import SimpleNamespace
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'qa'));assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('close-deadline-'+str(time.time_ns()));OUT.mkdir()
old=ROOT/'qa/review-snapshot-1791148790643019677/sources/qa/driver.py'
def exercise(path,tag):
 spec=importlib.util.spec_from_file_location('actual_driver_'+tag,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);clock=SimpleNamespace(now=0);module.time=SimpleNamespace(monotonic=lambda:clock.now)
 model=module.Driver.__new__(module.Driver);model.directory=OUT/tag;model.directory.mkdir();model.report={'passed':False,'phases':[],'openGates':[]};model.endpoint=SimpleNamespace();model.session=SimpleNamespace(host=SimpleNamespace(processes=[(None,{'name':'hyprland','pid':os.getpid()})]));model.parent_factory=lambda end:SimpleNamespace(close=lambda deadline:setattr(clock,'now',clock.now+7),abort=lambda:None)
 for phase in module.PHASES:setattr(model,phase,lambda:None)
 refused=False
 try:model.run()
 except module.Refused:refused=True
 return {'refused':refused,'report':model.report,'sourceSHA256':hashlib.sha256(path.read_bytes()).hexdigest()}
report={'passed':False,'nativeAcceptance':False,'checks':[]}
try:
 unsafe=exercise(old,'preserved-unsafe');report['unsafeWitness']=unsafe;assert not unsafe['refused'] and unsafe['report']['passed'] and len(unsafe['report']['phases'])==8;report['checks'].append({'name':'actual-preserved-source-accepts-7s-close-under6s','characterizationPassed':True,'nativeAcceptance':False})
 current=exercise(ROOT/'qa/driver.py','current');report['current']=current
 if current['sourceSHA256']==unsafe['sourceSHA256']:report['scope']='pre-fix unsafe actualrun characterization';report['passed']=True;report['correctionAccepted']=False
 else:
  assert current['refused'] and not current['report']['passed'] and len(current['report']['phases'])==1 and current['report']['phases'][0]['passed'] is False;report['checks'].append({'name':'actual-current-source-refuses-overrun-before-marking-phase-passed','passed':True});report.update(passed=True,correctionAccepted=True)
except BaseException as error:report['error']=repr(error)
(OUT/'close-deadline-test.py').write_bytes(pathlib.Path(__file__).read_bytes());(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(OUT/'report.json'),'passed':report['passed'],'correctionAccepted':report.get('correctionAccepted'),'error':report.get('error')}));raise SystemExit(0 if report['passed'] else 1)
