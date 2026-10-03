"""Actual monitor/Lua/reader maintenance oracles; no private Probe."""
import json,select,time

def run(c):
    control=c['control'];env=c['env'];check=c['check'];wait=c['wait'];received=c['received'];here=c['here'];ctl=c['ctl']
    state=lambda client=':0.0':control.capability_status(client)
    def jsonfile(p):
        try:return json.loads(p.read_text())
        except (OSError,ValueError):return {}
    disabled=c['reader']('disabled');disabled.wait(timeout=8)
    refusal=jsonfile(here/'disabled-reader-result.json')
    check('actual disabled bootstrap refuses before Orca imports',disabled.returncode==3 and refusal.get('refused') and not refusal.get('orcaImported'),result=refusal)
    check('disabled reader profile and speech inputs exact unchanged',c['profile_before']==c['profile_tree']())
    first=c['maintenance_action']('load');check('production native identity is exact current session',first['instance']==env['HYPRLAND_INSTANCE_SIGNATURE'] and len(first['incarnation'])==64,identity=first)
    check('actual Manager advertises public interfaces without Probe',c['introspection']())
    c['guard_negatives']()
    packet=here/'monitor-packets.jsonl'
    monitor=c['pipe'](['python3',here/'production_client.py','Production',packet])
    def response(p):
        ready,_,_=select.select([p.stdout],[],[],8);assert ready,'client reply timeout'
        line=p.stdout.readline();assert line,'client reply EOF';return json.loads(line)
    ready=response(monitor);unique=ready['uniqueName'];check('actual independent caller registered',ready['ready'],caller=ready)
    def request(op,**fields):
        monitor.stdin.write(json.dumps(dict(operation=op,**fields))+'\n');monitor.stdin.flush();return response(monitor)
    check('actual explicit Watch accepted',request('watch')['pass'])
    gate=wait(lambda:s if (s:=state(unique))['registered'] and s['callerPreReplay'] else None,'read-only production preReplay')
    check('Lua capability gate reports actual registered quiet preReplay',gate['quiescent'] and gate['managerOwner']==first['managerOwner'],status=gate)
    check('foreign unique client has no inferred registration',not state(':0.0')['registered'] and not state(':0.0')['callerPreReplay'])
    check('passive actual load retains disabled intent and exact profile',c['private_intent']() is False and c['profile_before']==c['profile_tree']())
    keyboard=c['keyboard']()
    def send(lines):
        keyboard.stdin.write(lines+'sync\n');keyboard.stdin.flush()
        ready,_,_=select.select([keyboard.stdout],[],[],8);assert ready and keyboard.stdout.readline().strip()=='ready';time.sleep(.15)
    key=lambda code:send(f'key {code} 1\nsleep 50\nkey {code} 0\nsleep 50\n')
    before=received.read_bytes();key(30);check('watch-only actual ordinary Foot bytes preserved',received.read_bytes()==before+b'a')
    key(88);check('watch-only actual compositor shortcut preserved',(c['runtime']/'shortcut-count').read_text()=='shortcut\n')
    check('explicit full grab accepted',request('grab')['pass']);check('replayed/full definition blocks preReplay',not state(unique)['callerPreReplay'])
    before=received.read_bytes();capture_start=time.monotonic();send('key 35 1\n')
    held=state(unique);check('actual captured held key blocks quiescence',not held['quiescent'])
    try:control.unload();raise AssertionError('held unload unexpectedly succeeded')
    except c['Refused']:pass
    check('false prepare preserves actual live instance and capture',control.native_identity()==first and not state(unique)['retiring'])
    send('key 35 0\n');check('natural captured release stays suppressed in real Foot',received.read_bytes()==before)
    packets=wait(lambda:es if len(es:=[json.loads(line) for line in packet.read_text().splitlines() if json.loads(line)['time']>=capture_start and json.loads(line)['keycode']==43])>=2 else None,'actual directed held capture and natural release')
    check('false prepare preserves exactly paired actual directed H packets',len(packets)==2 and [e['released'] for e in packets]==[False,True],packets=packets)
    for code,label in ((58,'Caps'),(69,'Num')):
        key(code);check('actual dirty '+label+' refuses normal unload',not state(unique)['unloadQuiescent'])
        try:control.unload();raise AssertionError('dirty unload unexpectedly succeeded')
        except c['Refused']:pass
    for code in (58,69):key(code)
    check('actual raw/accepted lock reconciliation permits normal unload',state(unique)['unloadQuiescent'])
    # Inspect retirement rejection before the path unload, using exact Lua.
    prepared=control.lua('prepare_unload',first['instance'],first['packageID'],first['incarnation'])
    check('actual exact-incarnation true retirement succeeds',prepared['ready'])
    for operation in ('watch','unwatch','grab','ungrab','grabs','query'):
        result=request(operation,modifiers=[65509],strokes=[[104,0]]) if operation=='grabs' else request(operation)
        check('retired actual service rejects '+operation,not result['pass'] and 'ServiceRetired' in result.get('error',''),result=result)
    cli_reload=c['maintenance_action']('reload');second=cli_reload['current']
    check('actual locked CLI reload returns exact previous incarnation',cli_reload['previous']=={**first,'ready':True})
    check('identical artifact same compositor reload creates fresh nonce',first['incarnation']!=second['incarnation'] and first['instance']==second['instance'] and first['packageID']==second['packageID'],before=first,after=second)
    check('surviving actual client explicitly resubscribes',request('watch')['pass'] and request('grab')['pass'])
    stale='return hl.plugin.omarchy_a11y.prepare_unload('+','.join(json.dumps(first[k]) for k in ('instance','packageID','incarnation'))+')'
    try:error=control.ipc('repl',stale)
    except c['Refused'] as actual_error:error=str(actual_error)
    check('actual stale nonce has specific native target/incarnation refusal','maintenance target/incarnation mismatch' in error,error=error)
    check('old nonce refusal preserves new capture policy',control.native_identity()==second and not state(unique)['retiring'] and not state(unique)['callerPreReplay'])
    before=received.read_bytes();key(35);check('new instance capture remains effective after stale prepare',received.read_bytes()==before)
    request('ungrab');monitor.stdin.close();monitor.wait(timeout=8);c['finish'](keyboard)
    control.unload()
    check('normal passive maintenance preserves false intent and exact profile',c['private_intent']() is False and c['profile_before']==c['profile_tree']())
    # Only the private bus's enabled intent and owned profile are changed.
    c['set_private_intent'](True);reader=c['reader']('enabled')
    reader_state=here/'enabled-reader-state.json';speech=here/'owned-utterances.jsonl'
    wait(lambda:jsonfile(reader_state).get('backend')=='AtspiDeviceLegacy','actual reader before service',25)
    identity=control.load()
    official=wait(lambda:r if (r:=jsonfile(reader_state)).get('backend')=='AtspiDeviceA11yManager' and r.get('commands') else None,'actual product bootstrap Manager backend',25)
    check('actual enabled owned reader uses production Manager',True,reader=official)
    packet=here/'reader-monitor-packets.jsonl'
    monitor=c['pipe'](['python3',here/'production_client.py','ProductionReader',packet])
    reader_monitor_ready=response(monitor)
    check('actual independent reader packet observer explicitly Watches',reader_monitor_ready['ready'] and request('watch')['pass'],caller=reader_monitor_ready)
    gtk,pointer,target,layout=c['pointer_target']()
    pointed=wait(lambda:r if ((r:=jsonfile(reader_state)).get('currentItem') or {}).get('name')=='Pointer target A' else None,'actual product PointerLocator public callback and AX child',15)
    check('actual product Lua capability chain yields real GTK child',pointed['mouseEnabled'] and pointed['currentItem']['app_bus'] and pointed['currentItem']['object_path'].startswith('/'),reader=pointed,actualTarget=target,layout=layout)
    keyboard=c['keyboard']()
    before=received.read_bytes();began=time.monotonic()
    send('key 110 1\nsleep 80\nkey 35 1\nsleep 80\nkey 35 0\nsleep 80\nkey 110 0\nsleep 80\n')
    heard=lambda:[r for line in speech.read_text().splitlines() if (r:=json.loads(line)).get('time',0)>=began and 'learn mode' in r.get('text','').lower()]
    wait(lambda:heard() and jsonfile(reader_state).get('learn'),'actual selected global command',12)
    check('actual product bootstrap global command consumes Foot bytes',received.read_bytes()==before,utterances=heard())
    commands=jsonfile(reader_state)['commands'];control.unload()
    wait(lambda:jsonfile(reader_state).get('backend')=='AtspiDeviceLegacy','actual service absence',20)
    fresh=control.load()
    recovered=wait(lambda:r if (r:=jsonfile(reader_state)).get('backend')=='AtspiDeviceA11yManager' and r.get('learn') else None,'actual public replay after normal production reload',25)
    check('actual learn command configuration survives production reload',recovered['commands']==commands and fresh['incarnation']!=identity['incarnation'],reader=recovered)
    check('private enabled intent preserved across actual maintenance',c['private_intent']() is True)
    check('actual mouse enabled request survives production reload',recovered['mouseEnabled'])
    check('actual independent observer explicitly resubscribes after production reload',request('watch')['pass'])
    before=received.read_bytes();spoken_start=time.monotonic();key(35)
    spoken=wait(lambda:es if (es:=[json.loads(line) for line in speech.read_text().splitlines() if json.loads(line).get('time',0)>=spoken_start and json.loads(line).get('text','').strip().lower()=='h']) else None,'actual restored learn H speech')
    check('actual restored learn full grab suppresses Foot and speaks H',received.read_bytes()==before,utterances=spoken)
    directed=wait(lambda:es if len(es:=[json.loads(line) for line in packet.read_text().splitlines() if json.loads(line)['time']>=spoken_start])>=2 else None,'actual independent restarted reader packets')
    check('actual reader reload delivers exact balanced H native packets',[(p['released'],p['keycode'],p['keysym']) for p in directed]==[(False,43,104),(True,43,104)],packets=directed)
    key(1);wait(lambda:not jsonfile(reader_state).get('learn'),'actual learn exit')
    c['finish'](keyboard);c['finish'](pointer);c['finish'](monitor);c['close_gtk'](gtk);c['stop_reader'](reader);control.unload();c['set_private_intent'](False)
    check('private enabled fixture intent restored false',c['private_intent']() is False)
