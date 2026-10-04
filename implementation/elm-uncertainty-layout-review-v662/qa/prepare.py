"""Protected CPU preparation. Actual compiled640 reducer and actual assets."""
import copy,hashlib,json,pathlib,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
ROOT=pathlib.Path(__file__).resolve().parents[1];GUI=ROOT.parent/'elm-recovery-delivery-integrated-gui-v640'
PARENT=GUI/'qa/tests-1791153820316433749';OUT=ROOT/'qa'/('prepare-'+str(time.time_ns()));OUT.mkdir()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
buildpath=pathlib.Path(json.loads((GUI/'qa/current-build.json').read_bytes())['report']);build=json.loads(buildpath.read_bytes());check('selected640_build_passed',build['passed'])
pins={str(buildpath):digest(buildpath),str(GUI/'qa/current-build.json'):digest(GUI/'qa/current-build.json')}
for name,h in build['inputs'].items():check('current_build_input_'+name,digest(GUI/name)==h);pins[str(GUI/name)]=h
for p in (PARENT/'inputs/src').glob('*.elm'):
 if p.name!='Probe.elm':check('compiled_probe_actual640_'+p.name,digest(p)==digest(GUI/'src'/p.name))
pins[str(PARENT/'worker.js')]=digest(PARENT/'worker.js');pins[str(GUI/'qa/probe.cjs')]=digest(GUI/'qa/probe.cjs')
assets=OUT/'assets';assets.mkdir()
for name in ['bar.html','bar.js','bar-adapter.js','popup.html','popup.js','popup-adapter.js','shell.css','context.js']:
 p=buildpath.parent/'inputs/assets'/name;shutil.copy2(p,assets/name);pins[str(p)]=digest(p)
events=json.loads((PARENT/'valid-events.json').read_bytes());prefix=copy.deepcopy(events[:5])
title='An exceptionally long window title with important document context — '+('Uncertainty remains visible '+ '∎ ')*5
check('title_within_actual_surface_bounds',len(title)<=256)
for event in prefix:
 if event.get('frame',{}).get('kind')=='action-projection':
  for row in event['frame']['scene']['windows']:row['label']=title
unknown=copy.deepcopy(events[5]);owner={'kind':'owner','frame':{'surfaceProtocol':2,'kind':'surface-owner','outputId':'1','providerId':'1'}}
variants={'ready':prefix,'pending':prefix+[{'kind':'act2'}],'unknown':prefix+[unknown],'unknown-menu':prefix+[owner,unknown,{'kind':'menu-open'}],'unknown-refresh':prefix+[unknown,{'kind':'refresh'}]}
cases=[];rows_by={}
for name,sequence in variants.items():
 ep=OUT/(name+'-events.json');rp=OUT/(name+'-rows.json');ep.write_text(json.dumps(sequence,indent=2)+'\n')
 p=subprocess.run(['node',str(GUI/'qa/probe.cjs'),str(PARENT/'worker.js'),str(ep),str(rp)],capture_output=True,text=True,timeout=6)
 (OUT/(name+'.log')).write_text(p.stdout+p.stderr);check('actual_compiled_reducer_'+name,p.returncode==0)
 rows=json.loads(rp.read_bytes());last=rows[-1];rows_by[name]=last
 cases.append({'name':name,'frame':last['frame'],'transaction':last['transaction'],'effectRequest':last['effectRequest'],'effectGeneration':last['effectGeneration'],'wires':last['wires']})
check('pending_actual_transaction',rows_by['pending']['transaction']['transaction']['status']=='Pending')
check('unknown_actual_transaction',rows_by['unknown']['transaction']['transaction']['status']=='Unknown')
check('unknown_actual_menu_rendered',rows_by['unknown-menu']['frame']['mode']=='menu')
check('refresh_actual_reducer_emits_reads_only',bool(rows_by['unknown-refresh']['wires']) and all(w['kind'] in ['projection-request','geometry-facts-request','reconciliation-ready'] for w in rows_by['unknown-refresh']['wires']))
check('refresh_keeps_unknown_effect_counters',all(rows_by['unknown-refresh'][n]==rows_by['unknown'][n] for n in ['effectRequest','effectGeneration','transaction']))
casepath=OUT/'cases.json';casepath.write_text(json.dumps(cases,indent=2)+'\n');pins[str(casepath)]=digest(casepath)
report={'passed':True,'scope':'Compiled640 root reducer with synthetic captured transport/title fixtures; actual640 Bar/Popup assets. Preparation only; no WebKit/native launch or AT compliance.','checks':checks,'sourcePins':pins,'assets':str(assets),'cases':str(casepath),'buildReport':str(buildpath),'nativeExecuted':False}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'qa/current-preparation.json').write_text(json.dumps({'report':str(OUT/'report.json'),'sha256':digest(OUT/'report.json')},indent=2)+'\n');print(OUT/'report.json')
