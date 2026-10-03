#!/usr/bin/env python3
"""Assert required outcomes from recorded actual Qt traces, not source text."""
from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parent
r=json.loads((B/'retained-probe/report.json').read_text())
by={o['name']:o for o in r['observations']}
checks=[]
def check(name,value):checks.append({'name':name,'passed':bool(value)})
check('fixture completed normally',not r.get('error') and r['exitCode']==-15)
check('visible native action sanity',by['visible native press sanity']['callbackExecuted'])
for n in ['hidden window retained native press','hidden window raw retained QML activate']:
 check(n,by[n]['requiredRefusal'])
for n in ['prompt rejects retained background native and raw attached press','prompt Ctrl B routing','destroyed file delegate retained native peer','hidden file row native and raw attached callback authority']:
 check(n,by[n]['refused'])
o=by['prompt Ctrl L routing'];check('prompt Ctrl L stays inside prompt',o['after']=='Prompt.input' and o['promptStillVisible'] and not o['pathEditing'])
o=by['static media logical-path rebind through retained native peer'];check('old media native peer is retired',not o['after']['interfaceFound'] and not o['after']['objectAlive'])
o=by['new media logical peer remains actionable'];check('new media peer remains actionable',o['newPeer'] and o['selected']==['beta.svg'])
o=by['actual same PID focused file reload'];check('same PID file focus and path survive actual reload',o['samePid'] and o['requiredFocusPreserved'] and o['debugAfter']['current']==o['exportedFocus'])
o=by['actual hidden same PID reload preserves logical focus token without mapping'];check('hidden reload preserves identity without mapping',o['refusedMapping'] and o['identityPreserved'] and not o['backing'])
for n in ['deferred file restoration cannot override newer toolbar focus','deferred file restoration cannot override newer Tab input','deferred background restoration cannot override newer modal prompt']:
 check(n,by[n]['newerFocusPreserved'])
tree=json.loads((B/'native-qa/preflight-tree-fixed.json').read_text());check('focused compact tree is inside viewport',tree['treeFitsViewport'] and tree['sidebarScroll']>0 and tree['deepTreeFitsViewport'] and tree['deepLogicalPath'])
keys=json.loads((B/'offscreen-keys-report.json').read_text());check('actual Qt keyboard58',keys['result']=='pass' and len(keys['checks'])==58)
geometry=json.loads((B/'offscreen-report.json').read_text());check('actual geometry120',geometry['cases']==120 and not geometry['failures'])
parse=json.loads((B/'parse-check.json').read_text());check('QML parse26',len(parse)==26 and all(p['passed'] for p in parse))
report={'scope':'Copied Qt native interfaces, raw QML attached handlers and Qt keys on offscreen windows with isolated session D-Bus; no reader or physical compositor input claim','checks':checks,'result':'pass' if all(c['passed'] for c in checks) else 'fail','traceSha256':hashlib.sha256((B/'retained-probe/report.json').read_bytes()).hexdigest()}
(B/'evidence-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'result':report['result'],'checks':len(checks)}))
assert report['result']=='pass'
