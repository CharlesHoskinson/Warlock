"""Formal-contract cases against real private bridge, packets, locks and Foot bytes."""
import json,os,select,subprocess,time
from pathlib import Path

def run(ctx):
    here,env,report=ctx['here'],ctx['env'],ctx['report']
    check,manager,ctl,data=ctx['check'],ctx['manager'],ctx['ctl'],ctx['data']
    received,packet_path,config=ctx['received'],ctx['packet_path'],ctx['config']
    baseline_config=config.read_text();owned=[];streams=[]
    def pipe(args,label):
        errors=(here/(label+'.log')).open('w');streams.append(errors)
        p=subprocess.Popen(list(map(str,args)),env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=errors,text=True,start_new_session=True)
        ctx['processes'].append(p);owned.append(p);return p
    def reply(p):
        ready,_,_=select.select([p.stdout],[],[],8)
        assert ready,'private fixture response timeout'
        line=p.stdout.readline();assert line,'private fixture exited: '+str(p.poll())
        return line.strip()
    keyboard=None
    def native(*lines):
        keyboard.stdin.write('\n'.join(lines)+'\nsync\n');keyboard.stdin.flush()
        assert reply(keyboard)=='ready';time.sleep(.12)
    def client(tag):
        p=pipe(['python3',here/'native-fixture/policy_client.py',tag,here/('policy-'+tag+'-packets.jsonl')],'policy-client-'+tag)
        assert json.loads(reply(p))['ready'];return p
    a=None
    def request(p,operation,**values):
        p.stdin.write(json.dumps(dict(operation=operation,**values))+'\n');p.stdin.flush()
        result=json.loads(reply(p));assert result['pass'],result
        time.sleep(.03)
    def grabs(modifiers=(),strokes=()):request(a,'grabs',modifiers=list(modifiers),strokes=list(strokes))
    def taps(code,count=1):
        for _ in range(count):native(f'key {code} 1','sleep 60',f'key {code} 0','sleep 60')
    def packets(start):return [x for line in packet_path.read_text().splitlines() if line and (x:=json.loads(line))['time']>=start]
    def begin():return received.read_bytes(),time.monotonic()
    def finish(name,before,start,expected=b'',predicate=lambda events:True,**extra):
        events=packets(start);after=received.read_bytes()
        check(report,name,after==before+expected and predicate(events),before=before.hex(),after=after.hex(),packets=events,**extra)
    def state():return json.loads(manager(env,'State'))
    def device_rows():return [d for d in data(env,'devices')['keyboards'] if d['name'].startswith('hl-virtual-keyboard-native-input')]
    def locks():
        rows=device_rows();assert rows,'exact private native producer missing'
        return [(d['capsLock'],d['numLock']) for d in rows]
    def reset():
        # Recreate a fully released device instead of guessing the producer's
        # raw/accepted lock parity from a literal mask reset.
        grabs();request(a,'ungrab');native('drop','create','mods 0 0 0 0');time.sleep(.1)
    def reload(extra='',enforce=False):
        snapshot=baseline_config+'hl.config({ecosystem={enforce_permissions='+('true' if enforce else 'false')+'}})\n'+extra
        index=len(report.setdefault('privatePolicyReloads',[]))+1
        saved=here/('private-policy-config-'+str(index)+'.lua');saved.write_text(snapshot);saved.chmod(0o600)
        config.write_text(snapshot);ctl(env,'reload');time.sleep(.4)
        option=data(env,'getoption','ecosystem:enforce_permissions')
        report['privatePolicyReloads'].append(dict(snapshot=str(saved),expectedEnforcement=enforce,actualOption=option))
        assert option['bool'] is enforce,'private permission control-plane option did not change'
        assert not ctl(env,'configerrors'),'private policy reload error'
        assert 'keyboard-monitor-private' in ctl(env,'plugin','list'),'private policy reload unloaded reviewed plugin'
    try:
        reload()
        keyboard=pipe([here/'native-fixture/native-input'],'policy-input')
        ctx['producer_ready'](keyboard,here/'policy-input.log','policy keyboard')
        a=client('A')
        native('auto')
        check(report,'native producer matches predeclared startup deny',len(device_rows())==1 and device_rows()[0]['name']==ctx['deny_name'],declared=ctx['deny_name'],devices=device_rows())
        reset()
        request(a,'watch')
        before,start=begin();native('key 42 1','sleep 60','key 35 1','sleep 60','key 35 0','sleep 60','key 42 0')
        finish('native watch Shift/H pre-event masks and ordinary bytes',before,start,b'H',lambda es:[(e['keysym'],e['mask'],e['released']) for e in es]==[(65505,0,False),(72,1,False),(72,1,True),(65505,1,True)])
        before,start=begin();taps(58);taps(35)
        finish('native watch Caps toggle and packet lock state',before,start,b'H',lambda es:len(es)==4 and es[0]['mask']==0 and es[1]['mask']&2 and es[2]['keysym']==72,caps=locks())
        check(report,'native watched Caps accepted lock',all(caps for caps,num in locks()))
        reset();before,start=begin();taps(69);taps(35)
        finish('native watch Num toggle leaves ordinary letter',before,start,b'h',lambda es:len(es)==4 and es[0]['mask']==0 and es[1]['mask']&16)
        check(report,'native watched Num accepted lock',all(num for caps,num in locks()))
        reset();grabs(strokes=[(104,0)])
        before,start=begin();taps(35);taps(30)
        finish('native selected h balanced capture and a passthrough',before,start,b'a',lambda es:[e['keycode'] for e in es]==[43,43,38,38])
        before,start=begin();native('key 35 1');grabs();native('key 35 0');taps(35)
        finish('native grab definition change preserves captured release',before,start,b'h',lambda es:[e['released'] for e in es]==[False,True,False,True])
        request(a,'grab');before,start=begin();taps(58);taps(69);taps(35)
        finish('native full grab suppresses typing and locking keys',before,start,b'',lambda es:len(es)==6)
        check(report,'native full grab keeps accepted Caps Num unchanged',locks()==[(False,False)],locks=locks())
        reset();grabs(modifiers=[65509]);before,start=begin();native('key 58 1','key 35 1','key 35 0','key 58 0')
        finish('native custom Caps chord keeps lowercase symbol without toggle',before,start,b'',lambda es:[e['keysym'] for e in es]==[65509,104,104,65509])
        check(report,'native custom Caps accepted lock stays off',locks()==[(False,False)],locks=locks())
        reset();grabs(modifiers=[65379]);before,start=begin();native('key 110 1','key 35 1','key 35 0','key 110 0')
        finish('native custom Insert chord paired capture',before,start,b'',lambda es:[e['keycode'] for e in es]==[118,43,43,118])
        reset();grabs(modifiers=[65509]);before,start=begin();taps(58,2)
        finish('native consecutive custom Caps double tap preserves normal toggle',before,start,b'',lambda es:len(es)==4)
        check(report,'native second Caps tap toggles accepted lock',locks()==[(True,False)],locks=locks())
        reset();grabs(modifiers=[65509]);before,start=begin();taps(58);taps(35);taps(58)
        finish('native intervening ordinary h disarms Caps double tap',before,start,b'h',lambda es:len(es)==6)
        check(report,'native nonconsecutive Caps stays suppressed',locks()==[(False,False)],locks=locks())
        reset();grabs(strokes=[(104,0)]);before,start=begin();native('key 35 1','key 35 1','key 35 1','key 35 0')
        finish('native capture repeats share one release route',before,start,b'',lambda es:[e['released'] for e in es]==[False,False,False,True])
        check(report,'native repeat ledger quiescent after one release',state()['quiescent'])
        before,start=begin();native('key 35 1');ctx['pid_stop'](a);time.sleep(.2);native('key 35 0');taps(35)
        finish('native client disconnect retains captured release and future passthrough',before,start,b'h',lambda es:[e['released'] for e in es]==[False,True,False,True])
        a=client('A');reset();grabs(strokes=[(104,0)]);before,start=begin();native('key 35 1','device 1','create','key 35 1','device 0','drop')
        check(report,'native device retire preserves other captured device',not state()['quiescent'],state=state())
        native('device 1','key 35 0')
        finish('native independent device removal leaves no user bytes',before,start,b'')
        check(report,'native retired and released device routes quiescent',state()['quiescent'])
        native('device 1','drop','device 0','create');reset();grabs(strokes=[(104,0)])
        before,start=begin();native('key 35 1','map us variant:dvorak','auto','key 35 0');grabs();taps(35)
        finish('native keymap replacement retains release sym and new-map fresh key',before,start,b'd',lambda es:[e['keysym'] for e in es]==[104,104,100,100])
        native('map us -','mods 0 0 0 0');reset();grabs(modifiers=[65509]);before,start=begin();native('key 58 1','map us ctrl:nocaps','auto','key 58 0');grabs();taps(35)
        finish('native locking keymap modifier-only rebuild retains release identity',before,start,b'h',lambda es:[e['keysym'] for e in es]==[65509,65509,104,104])
        check(report,'native locking keymap replacement has no lock residue',locks()==[(False,False)],locks=locks())
        native('map us -','mods 0 0 0 0');reset();grabs(strokes=[(104,0)]);before,start=begin();native('key 35 1')
        name=device_rows()[0]['name']
        check(report,'native permission target still matches startup deny',name==ctx['deny_name'],declared=ctx['deny_name'],actual=name)
        reload('hl.device({name='+json.dumps(name)+',enabled=true})\n',enforce=True)
        revoke_start=time.monotonic();native('key 35 1','key 35 0','key 30 1','key 30 0')
        finish('native actual permission deny drains captured release silently',before,start,b'',lambda es:len(es)==1 and not packets(revoke_start),device=name)
        check(report,'native actual permission deny ledger quiescent',state()['quiescent'])
        reload('hl.device({name='+json.dumps(name)+',enabled=true})\n');grabs();before,start=begin();taps(30);finish('native permission allow restores ordinary bytes',before,start,b'a')
        reset();grabs(strokes=[(104,0)]);before,start=begin();native('key 35 1');reload('hl.device({name='+json.dumps(name)+',enabled=false})\n')
        revoke_start=time.monotonic();native('key 35 0');finish('native enabled-device revoke drains silent captured release',before,start,b'',lambda es:len(es)==1 and not packets(revoke_start))
        reload();reset();before,start=begin();taps(30);finish('native enabled-device restore passes ordinary bytes',before,start,b'a')
        reset();grabs(strokes=[(104,0)]);before,start=begin();native('key 35 1','ime on');ignored_start=time.monotonic();native('key 35 1','key 35 0','key 30 1','key 30 0')
        finish('native real same-client IME-ignore transition drains capture silently',before,start,b'a',lambda es:len(es)==1 and not packets(ignored_start))
        native('ime off');grabs();before,start=begin();taps(30);finish('native IME exit restores monitored ordinary input',before,start,b'a',lambda es:len(es)==2)
        reset();grabs(modifiers=[65509]);before,start=begin();native('raw 58 1','raw 35 1','auto','raw 35 0','raw 58 0','auto')
        finish('native explicit virtual batching preserves capture and accepted locks',before,start,b'',lambda es:[e['keysym'] for e in es]==[65509,104,104,65509])
        check(report,'native batched captured Caps does not toggle accepted lock',locks()==[(False,False)],locks=locks())
        reset();grabs(strokes=[(104,0)]);before,start=begin();native('key 35 1')
        check(report,'native PrepareUnload refuses captured held key',manager(env,'PrepareUnload') is False)
        native('key 35 0');finish('native refused unload keeps balanced release and active subscription',before,start,b'',lambda es:[e['released'] for e in es]==[False,True])
        check(report,'native all policy routes quiescent at end',state()['quiescent'])
        report['widerPolicyInputProved']=True
    finally:
        # Paired natural releases on EOF precede client cleanup and final unload.
        if keyboard is not None and keyboard.poll() is None:
            keyboard.stdin.close()
            try:keyboard.wait(timeout=5)
            except subprocess.TimeoutExpired:ctx['pid_stop'](keyboard)
        for p in owned:
            if p is not keyboard:ctx['pid_stop'](p)
        for stream in streams:stream.close()
        config.write_text(baseline_config)
