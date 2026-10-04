import hashlib,json,resource,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('test-'+str(time.time_ns()));OUT.mkdir()
source=ROOT/'candidate/src/config/shared/monitor/MonitorRuleManager.cpp';template=ROOT/'qa/template.cpp'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def body(text,marker):
 start=text.index(marker);a=text.index('{',start);b=a+1;depth=1
 while depth:depth+=(text[b]=='{')-(text[b]=='}');b+=1
 return text[start:b],text[a+1:b-1]
r={'passed':False,'nativeAcceptance':False,'scope':'Actual reload scheduling/render/consume fragments with typed event-loop singleton mocks; monitor body excluded','inputs':{str(p):sha(p) for p in [source,template,Path(__file__)]},'commands':[]}
def run(name,cmd,expected=0):
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=60);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);r['commands'].append({'command':cmd,'exitCode':p.returncode,'expected':expected});assert p.returncode==expected,p.stderr or p.stdout;return p.stdout
try:
 text=source.read_text();schedule=body(text,'void CMonitorRuleManager::scheduleReload()')[0]
 render=body(text,'m_listeners.preChecksRender =')[1]
 consume=body(text,'void CMonitorRuleManager::ensureMonitorStatus()')[1].split('std::vector<PHLMONITOR>',1)[0]
 assert text.count('m_reloadScheduled = false;')==1 and 'm_reloadScheduled = false;' in consume
 cpp=template.read_text().replace('// PRODUCTION_SCHEDULE',schedule).replace('// PRODUCTION_RENDER',render).replace('// PRODUCTION_CONSUME',consume)
 (OUT/'test.cpp').write_text(cpp)
 flags=['c++','-std=c++23','-O2','-Wall','-Wextra','-Werror']
 run('compile',[*flags,str(OUT/'test.cpp'),'-o',str(OUT/'test')]);r['checks']=int(run('test',[str(OUT/'test')]).split('checks: ')[1])
 before='++applications;';assert cpp.count(before)==1
 (OUT/'unsafe.cpp').write_text(cpp.replace(before,'++applications;').replace('if(duringApply) { auto fn=std::move(duringApply);duringApply={};fn(); }','if(duringApply) { auto fn=std::move(duringApply);duringApply={};fn(); }\n        m_reloadScheduled=false;'))
 run('mutation-compile',[*flags,str(OUT/'unsafe.cpp'),'-o',str(OUT/'unsafe')]);run('mutation-rejected',[str(OUT/'unsafe')],expected=1)
 r.update(passed=True,lateClearMutationRejected=True)
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
