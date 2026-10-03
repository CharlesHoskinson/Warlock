"""Real private compositor/Orca startup, retirement, lock parity and restart.

Public monitor clients request policy; native producer packets and real Foot
bytes are the oracle. No synthetic reader events or backend substitution.
"""
import json, os, select, subprocess, threading, time

def run(c):
    here,env,reader_root=c['here'],c['env'],c['reader_root']
    check=lambda name,ok,**details:c['check'](c['report'],name,ok,**details)
    ctl=lambda *a:c['ctl'](env,*a)
    manager=lambda method:c['manager'](env,method)
    state=lambda:json.loads(manager('State'))
    wait=c['wait'];received=c['received']
    def read_json(p):
        try:return json.loads(p.read_text())
        except (FileNotFoundError,json.JSONDecodeError):return {}
    reader_state=here/'lifecycle-reader-state.json'
    reader_events=here/'lifecycle-reader-events.jsonl'
    speech_path=here/'lifecycle-utterances.jsonl'
    for p in (reader_events,speech_path):p.write_text('');p.chmod(0o600)
    reader_state.unlink(missing_ok=True)
    reader_env={**env,'PYTHONPATH':str(here)+':'+str(reader_root)+':'+str(reader_root/'prefix/usr/lib/python3.14/site-packages'),
        'LD_LIBRARY_PATH':str(reader_root/'prefix/usr/lib'),'GI_TYPELIB_PATH':str(reader_root/'prefix/usr/lib/girepository-1.0'),
        'XDG_DATA_DIRS':str(reader_root/'prefix/usr/share')+':/usr/local/share:/usr/share','GDK_BACKEND':'wayland',
        'ORCA_QA_LEGACY_GRAB_FIX':'1','ORCA_QA_NATIVE_WAYLAND_MODIFIERS':'1',
        'ORCA_QA_UTTERANCES':str(speech_path),'KEYBOARD_RECONNECT_EVENTS':str(reader_events),
        'KEYBOARD_RECONNECT_STATE':str(reader_state)}
    reader_env.pop('DISPLAY',None)
    reader=c['launch'](['python3',here/'reconnect_reader_entry.py','--speech-system','silent_factory',
                       '--debug-file',here/'lifecycle-reader.debug'],reader_env,'lifecycle-reader')
    legacy=wait(lambda:r if (r:=read_json(reader_state)).get('backend')=='AtspiDeviceLegacy' and r.get('watch') and r.get('commands') else None,
                'actual Orca active in Legacy before manager',20)
    check('actual official reader predates service in Legacy',True,reader=legacy)
    class Client:
        def __init__(self,tag):
            self.path=here/('lifecycle-'+tag+'-packets.jsonl')
            log=(here/('lifecycle-'+tag+'-client.log')).open('w')
            self.process=subprocess.Popen(['python3',str(here/'native-fixture/lifecycle_client.py'),tag,str(self.path),
                'org.omarchy.NativeLifecycle.KeyboardMonitor'],env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                stderr=log,text=True,start_new_session=True)
            c['processes'].append(self.process);self.serial=0
            self.ready=self.response();check('registration caller '+tag+' starts before bridge',self.ready.get('ready'),client=self.ready)
        def response(self):
            ready,_,_=select.select([self.process.stdout],[],[],5)
            assert ready,'public monitor caller response timeout'
            return json.loads(self.process.stdout.readline())
        def call(self,operation,**fields):
            self.serial+=1;self.process.stdin.write(json.dumps(dict(id=self.serial,operation=operation,**fields))+'\n');self.process.stdin.flush()
            return self.response()
    a,b=Client('A'),Client('B')
    churn=[];errors=[]
    def change_owners():
        try:
            for _ in range(25):
                for client,op in ((a,'release'),(b,'claim'),(b,'release'),(a,'claim')):
                    response=client.call(op);assert response['pass'];churn.append(dict(time=time.monotonic(),caller=client.ready['uniqueName'],operation=op))
                time.sleep(.005)
            assert a.call('release')['pass'];assert b.call('claim')['pass']
        except BaseException as error:errors.append(repr(error))
    worker=threading.Thread(target=change_owners);worker.start()
    started=time.monotonic();ctl('plugin','load',c['lib']);finished=time.monotonic()
    worker.join(timeout=10);assert not worker.is_alive() and not errors,errors
    c['report']['adoptionChurn']=dict(loadStart=started,loadEnd=finished,operations=churn)
    check('owner churn overlaps native adoption interval',any(started<=e['time']<=finished for e in churn),start=started,end=finished)
    official=wait(lambda:r if (r:=read_json(reader_state)).get('backend')=='AtspiDeviceA11yManager' and r.get('appliedEpoch')==r.get('epoch') else None,
                  'actual Orca reconnects to official Manager backend',20)
    check('actual Legacy reader transitions through public factory',True,reader=official)
    check('startup registration old owner denied',not a.call('watch')['pass'])
    check('startup current owner explicitly watches',b.call('watch')['pass'])
    # Production denied-device tests stay in the separate accepted policy trial.
    # This test uses startup plugin allow then a documented private enforcement
    # toggle before creating its native producer.
    with c['config'].open('a') as stream:stream.write('\nhl.config({ecosystem={enforce_permissions=false}})\n')
    ctl('reload');time.sleep(.2)
    producer=subprocess.Popen([str(here/'native-fixture/native-input')],env=env,stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,stderr=(here/'lifecycle-input.log').open('w'),text=True,start_new_session=True)
    c['processes'].append(producer)
    c['producer_ready'](producer,here/'lifecycle-input.log','lifecycle keyboard')
    def send(lines):
        producer.stdin.write(lines+'sync\n');producer.stdin.flush()
        ready,_,_=select.select([producer.stdout],[],[],8);assert ready,'native producer timeout'
        assert producer.stdout.readline().strip()=='ready';time.sleep(.15)
    def key(code):send(f'key {code} 1\nsleep 50\nkey {code} 0\nsleep 50\n')
    def chord():send('key 110 1\nsleep 80\nkey 35 1\nsleep 80\nkey 35 0\nsleep 80\nkey 110 0\nsleep 80\n')
    def heard_since(start,text):
        return [x for line in speech_path.read_text().splitlines() if (x:=json.loads(line))['time']>=start and text in x.get('text','').lower()]
    def packets_since(start):
        return [x for line in b.path.read_text().splitlines() if (x:=json.loads(line))['time']>=start]
    before=received.read_bytes();start=time.monotonic();chord()
    heard=wait(lambda:heard_since(start,'learn mode'),'actual startup global learn command',10)
    active=wait(lambda:r if (r:=read_json(reader_state)).get('learn') and r.get('full') else None,'learn explicit full grab')
    check('global command after startup adoption enters real learn mode',bool(heard),utterances=heard,reader=active)
    packets=packets_since(start)
    check('startup native command has exact directed down up packets',
          [(p['released'],p['keycode'],p['keysym']) for p in packets]==[(False,118,65379),(False,43,104),(True,43,104),(True,118,65379)],packets=packets)
    check('startup real command consumes terminal bytes',received.read_bytes()==before,before=before.hex(),after=received.read_bytes().hex())
    # Held key must prevent retirement without deleting the real learn full grab.
    send('key 35 1\n');held=state();check('held key PrepareUnload false',manager('PrepareUnload') is False,state=held)
    after_false=state();check('false retirement preserves explicit subscriptions',after_false['clients']==held['clients'] and not after_false['retiring'],state=after_false)
    send('key 35 0\n')
    for code,label in ((58,'Caps'),(69,'Num')):
        key(code);check('dirty '+label+' parity rejects unload',manager('PrepareUnload') is False,state=state())
    for code in (58,69):key(code)
    check('real Caps Num reconciliation restores unload quiescence',state()['unloadQuiescent'],state=state())
    before=received.read_bytes()
    check('quiescent real learn-mode service retirement succeeds',manager('PrepareUnload') is True)
    for op in ('watch','grab','grabs','unwatch','ungrab'):
        result=b.call(op,modifiers=[65509],strokes=[[104,0]]) if op=='grabs' else b.call(op)
        check('retired service rejects '+op,not result['pass'] and 'ServiceRetired' in result.get('error',''),result=result)
    check('retirement cannot recreate clients',state()['retiring'] and state()['clients']==0,state=state())
    saved_commands=active['commands']
    ctl('plugin','unload',c['lib'])
    wait(lambda:r if (r:=read_json(reader_state)).get('backend')=='AtspiDeviceLegacy' else None,'reader fallback during genuine service absence')
    ctl('plugin','load',c['lib'])
    restarted=wait(lambda:r if (r:=read_json(reader_state)).get('backend')=='AtspiDeviceA11yManager' and r.get('appliedEpoch')==r.get('epoch') and r.get('learn') and r.get('full') else None,'official restart restores requested learn full grab',20)
    check('actual service restart preserves requested learn full grab',True,reader=restarted)
    check('restart preserves active suspended command configuration',restarted['commands']==saved_commands,before=saved_commands,after=restarted['commands'])
    check('fixture watcher explicitly resubscribes after actual restart',b.call('watch')['pass'])
    start=time.monotonic();key(35)
    check('replayed full grab receives real key and consumes bytes',bool(wait(lambda:heard_since(start,'h'),'real learn key after restart')) and received.read_bytes()==before,
          before=before.hex(),after=received.read_bytes().hex())
    packets=packets_since(start)
    check('replayed full grab has exact native paired key packets',
          [(p['released'],p['keycode'],p['keysym']) for p in packets]==[(False,43,104),(True,43,104)],packets=packets)
    key(1);wait(lambda:not read_json(reader_state).get('learn'),'real learn exit after service restart')
    # Locks accepted normally before clean unload persist on this SAME virtual
    # device while the bridge is absent, and remain aligned on fresh load.
    for code in (58,69):key(code)
    devices=c['data'](env,'devices')['keyboards'];check('clean surviving device Caps Num enabled',any(k.get('capsLock') and k.get('numLock') for k in devices),devices=devices)
    check('clean surviving virtual device permits normal retirement',manager('PrepareUnload') is True)
    ctl('plugin','unload',c['lib']);before=received.read_bytes();key(30)
    check('surviving accepted Caps lock preserved without bridge',received.read_bytes()==before+b'A',before=before.hex(),after=received.read_bytes().hex())
    ctl('plugin','load',c['lib'])
    wait(lambda:r if (r:=read_json(reader_state)).get('backend')=='AtspiDeviceA11yManager' and r.get('appliedEpoch')==r.get('epoch') else None,'second official reconnect',20)
    devices=c['data'](env,'devices')['keyboards'];check('surviving accepted Caps Num preserved after reload',any(k.get('capsLock') and k.get('numLock') for k in devices),devices=devices)
    before=received.read_bytes();key(30);check('same surviving device Caps bytes remain uppercase after reload',received.read_bytes()==before+b'A')
    for code in (58,69):key(code)
    before=received.read_bytes();start=time.monotonic();chord()
    check('replayed selected command works after second restart',bool(wait(lambda:heard_since(start,'learn mode'),'second restart selected command')) and received.read_bytes()==before)
    key(1);wait(lambda:not read_json(reader_state).get('learn'),'final learn exit')
    producer.stdin.close();producer.wait(timeout=8)
    for p in (reader,a.process,b.process):c['pid_stop'](p)
    wait(lambda:state()['clients']==0,'all explicit clients removed')
    check('final private retirement quiescent',manager('PrepareUnload') is True)
    ctl('plugin','unload',c['lib'])
    c['report']['serviceRestartInputProved']=True
    c['report']['reconnectEvents']=[json.loads(line) for line in reader_events.read_text().splitlines()]
