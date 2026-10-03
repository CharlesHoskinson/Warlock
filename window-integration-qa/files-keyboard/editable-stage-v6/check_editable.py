from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parent
baseline=json.loads((B.parent/'guard-stage/editable-probe-v5/report.json').read_text());actual=json.loads((B/'editable-probe/report.json').read_text())
checks=[]
def check(name,value):checks.append({'name':name,'passed':bool(value)})
check('actual native fixture completed normally',not actual.get('error') and actual['exitCode']==-15 and len(actual['cases'])==88)
base={(c['item'],c['context'],c['operation']):c for c in baseline['cases']}
for c in actual['cases']:
 key=(c['item'],c['context'],c['operation']);b=base[key]
 if c['context'] in ['hidden','disabled','modalBackground'] or (c['context']=='readOnly' and c['operation'] in ['delete','insert','replace','setValue']):
  check('/'.join(key)+' refuses mutation',not c['changed'] and c['before']==c['after'])
 else:check('/'.join(key)+' preserves native positive behavior',c['before']==b['before'] and c['after']==b['after'])
check('destroyed peer is defunct',not actual['destroyedPeer']['interfaceFound'] and not actual['destroyedPeer']['objectAlive'])
report={'scope':'Actual independent native editable/cursor/selection/Value calls on offscreen Qt TextInput/TextEdit; no reader/compositor claim','checks':checks,'result':'pass' if all(c['passed'] for c in checks) else 'fail','baselineSha256':hashlib.sha256((B.parent/'guard-stage/editable-probe-v5/report.json').read_bytes()).hexdigest(),'traceSha256':hashlib.sha256((B/'editable-probe/report.json').read_bytes()).hexdigest()}
(B/'editable-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'result':report['result'],'checks':len(checks),'failures':[c['name'] for c in checks if not c['passed']]}));assert report['result']=='pass'
