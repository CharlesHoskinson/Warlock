"""Private native pointer/GTK/actual Omarchy Orca compat acceptance matrix."""
import json,os,select,subprocess,time
from gi.repository import GLib

def run(c):
    here,env,reader_root=c['here'],c['env'],c['reader_root']
    check=lambda name,ok,**details:c['check'](c['report'],name,ok,**details)
    ctl=lambda *args:c['ctl'](env,*args)
    data=lambda *args:c['data'](env,*args)
    wait=c['wait'];manager=lambda method:c['manager'](env,method)
    def read_json(path):
        try:return json.loads(path.read_text())
        except (OSError,json.JSONDecodeError):return {}
    def events(path):
        try:return [json.loads(line) for line in path.read_text().splitlines() if line]
        except OSError:return []
    def pipe(args,label,launch_env=env):
        log=(here/(label+'.log')).open('w')
        process=subprocess.Popen(list(map(str,args)),env=launch_env,stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,stderr=log,text=True,start_new_session=True)
        c['processes'].append(process);return process
    def response(process,timeout=6):
        ready,_,_=select.select([process.stdout],[],[],timeout)
        assert ready,'fixture response timeout PID '+str(process.pid)
        line=process.stdout.readline();assert line,'fixture exited PID '+str(process.pid)
        return json.loads(line)
    def request(process,operation,**fields):
        process.stdin.write(json.dumps(dict(operation=operation,**fields))+'\n');process.stdin.flush()
        return response(process)
    def input_lines(process,lines):
        process.stdin.write(lines+'sync\n');process.stdin.flush()
        ready,_,_=select.select([process.stdout],[],[],8)
        assert ready and process.stdout.readline().strip()=='ready','native producer did not sync'
        time.sleep(.05)
    def orca(method,*args):
        output=subprocess.check_output(['gdbus','call','--session','--dest','org.gnome.Orca.Service',
            '--object-path','/org/gnome/Orca/Service/MouseReviewer','--method',
            'org.gnome.Orca.Module.'+method,*args],env=env,text=True,stderr=subprocess.PIPE,timeout=5)
        return GLib.Variant.parse(None,output.strip(),None,None).unpack()[0]
    def set_mouse(value):return orca('ExecuteRuntimeSetter','IsEnabled','<true>' if value else '<false>')
    def toggle():return orca('ExecuteCommand','Toggle','false')
    def client(tag):
        p=pipe(['python3',here/'native-fixture/pointer_client.py','org.omarchy.Pointer'+tag+'.KeyboardMonitor'],'pointer-client-'+tag)
        ready=response(p);check('independent protocol caller '+tag+' ready',ready.get('ready'),client=ready);return p
    a,b=client('A'),client('B')
    check('A owns actual monitor registration',request(a,'claim')['value'] in (1,4))
    check('B owns actual monitor registration',request(b,'claim')['value'] in (1,4))
    # A native held key while the actual public fresh device tries capability
    # negotiation must preserve its own registration and refuse the probe.
    ctl('plugin','load',c['lib'])
    with c['config'].open('a') as stream:stream.write('\nhl.config({ecosystem={enforce_permissions=false}})\n')
    ctl('reload');time.sleep(.15)
    keyboard=pipe([here/'native-fixture/native-input'],'pointer-keyboard')
    check('external registered caller explicitly requests full capture',request(b,'grab')['pass_'])
    wait(lambda:c['received'].exists(),'actual private Foot byte receiver')
    before=c['received'].read_bytes();input_lines(keyboard,'key 35 1\n')
    assert not json.loads(manager('State'))['quiescent'],'actual held capture absent'
    probe_env={**env,'PYTHONPATH':str(here)+':'+str(reader_root)+':'+str(reader_root/'prefix/usr/lib/python3.14/site-packages')}
    probe=pipe(['python3',here/'native-fixture/actual_capability_probe.py'],'actual-capability-probe',probe_env)
    ready=response(probe);check('actual fresh public factory uses official Manager device',ready.get('backend')=='AtspiDeviceA11yManager',device=ready)
    refused=request(probe,'capability')
    check('actual held capability probe refuses without dropping registration',not refused['pass_'] and 'refused' in refused.get('error','')
        and refused['before']==refused['after']==ready['ownUnique'] and refused['sameActualDevice'],result=refused)
    input_lines(keyboard,'key 35 0\n');check('held capability refusal keeps real Foot bytes suppressed',c['received'].read_bytes()==before)
    check('external capture removed only after real release',request(b,'ungrab')['pass_'])
    accepted=request(probe,'capability')
    check('same actual fresh device probes after real quiescence',accepted['pass_'] and accepted['value']&8
        and accepted['before']==accepted['after']==ready['ownUnique'] and accepted['sameActualDevice'],result=accepted)
    # No GObject pointer-moved observer or MouseReviewer exists in this probe.
    # The official GDBus callback alone must issue its real query and rearm.
    pointer=pipe([here/'native-fixture/native-pointer'],'actual-native-pointer')
    monitor=data('monitors')[0];width=monitor['width']/monitor['scale'];height=monitor['height']/monitor['scale']
    pending=json.loads(manager('State'))['pointerPending']
    check('actual successful capability bootstrap primes exactly one query',pending==1,pending=pending)
    input_lines(pointer,f'absolute 12.125 12.375 {width:.6f} {height:.6f}\n')
    first=request(probe,'pump-official-callback')
    check('first construction motion rearms via official callback before GObject observer',
        first['state']['pointerPending']==1 and first['sameActualDevice'] and not first['gobjectObserverInstalled'],result=first)
    input_lines(pointer,f'absolute 14.125 14.375 {width:.6f} {height:.6f}\n')
    second=request(probe,'pump-official-callback')
    check('second early motion retains official query signal chain',second['state']['pointerPending']==1,result=second)
    probe.stdin.write('{"operation":"exit"}\n');probe.stdin.flush();probe.wait(timeout=5)
    check('initial private bridge quiescent retirement',manager('PrepareUnload') is True);ctl('plugin','unload',c['lib'])
    # Actual reader predates the next service incarnation, preserving the
    # default disabled request and constructing its real Legacy device first.
    state_path=here/'pointer-reader-state.json';event_path=here/'pointer-reader-events.jsonl';speech=here/'pointer-utterances.jsonl'
    for p in (event_path,speech):p.write_text('');p.chmod(0o600)
    reader_env={**env,'PYTHONPATH':str(here)+':'+str(reader_root)+':'+str(reader_root/'prefix/usr/lib/python3.14/site-packages'),
        'LD_LIBRARY_PATH':str(reader_root/'prefix/usr/lib'),'GI_TYPELIB_PATH':str(reader_root/'prefix/usr/lib/girepository-1.0'),
        'XDG_DATA_DIRS':str(reader_root/'prefix/usr/share')+':/usr/local/share:/usr/share','GDK_BACKEND':'wayland',
        'ORCA_QA_LEGACY_GRAB_FIX':'1','ORCA_QA_NATIVE_WAYLAND_MODIFIERS':'1','ORCA_QA_UTTERANCES':str(speech),
        'POINTER_READER_EVENTS':str(event_path),'POINTER_READER_STATE':str(state_path)}
    reader_env.pop('DISPLAY',None)
    reader=c['launch'](['python3',here/'pointer_reader_entry.py','--speech-system','silent_factory','--debug-file',here/'pointer-reader.debug'],reader_env,'pointer-reader')
    legacy=wait(lambda:r if (r:=read_json(state_path)).get('backend')=='AtspiDeviceLegacy' and r.get('commands') else None,'real compat reader Legacy before bridge',20)
    check('real compat reader starts before Manager with pointer disabled',not legacy['mouseEnabled'] and legacy['currentItem'] is None,reader=legacy)
    ctl('plugin','load',c['lib'])
    official=wait(lambda:r if (r:=read_json(state_path)).get('backend')=='AtspiDeviceA11yManager' and r.get('epoch')==r.get('appliedEpoch') else None,'actual reader pointer Manager epoch',20)
    check('real compat reader reconstructs public device and capabilities',any(x.get('event')=='pointer-capability-probed' and x.get('capable') for x in events(event_path)),reader=official)
    saved_commands=official['commands']
    peers={};gtk_env={**env,'GDK_BACKEND':'wayland','GTK_A11Y':'atspi'}
    for tag,x in (('A',48),('B',520)):
        layout=here/('gtk-'+tag+'-layout.json')
        process=pipe(['python3',here/'native-fixture/gtk_peer.py',tag,layout],'actual-gtk-'+tag,gtk_env)
        window=wait(lambda:next((w for w in data('clients') if w['pid']==process.pid),None),'actual GTK peer '+tag)
        ctl('dispatch','hl.dsp.window.resize({x=360,y=240,window='+json.dumps('address:'+window['address'])+'})')
        ctl('dispatch','hl.dsp.window.move({x='+str(x)+',y=80,window='+json.dumps('address:'+window['address'])+'})')
        wait(lambda:read_json(layout).get('windows',[{}])[0].get('button'),'actual GTK allocation '+tag)
        peers[tag]=dict(process=process,layout=layout,window=window)
    def native_window(tag):return next(w for w in data('clients') if w['pid']==peers[tag]['process'].pid and 'second' not in w['title'])
    def ax():return json.loads(subprocess.check_output(['python3',here/'native-fixture/ax_observe.py'],env=env,text=True,stderr=subprocess.PIPE,timeout=8))
    def actual_frame(tag):
        row=next((r for r in ax() if r.get('pid')==peers[tag]['process'].pid),None)
        if row and len(row.get('children',[]))==1:return row['children'][0]
        return None
    frame_a=wait(lambda:actual_frame('A'),'actual GTK A AX frame');frame_b=wait(lambda:actual_frame('B'),'actual GTK B AX frame')
    check('real GTK AX singleton peers carry verified distinct identities',frame_a['app_bus']!=frame_b['app_bus'] and frame_a['object_path'].startswith('/') and frame_b['object_path'].startswith('/'),a=frame_a,b=frame_b)
    def move(x,y):input_lines(pointer,f'absolute {x:.6f} {y:.6f} {width:.6f} {height:.6f}\n')
    def target(tag):
        window=native_window(tag);bounds=read_json(peers[tag]['layout'])['windows'][0]['button']
        return (window['at'][0]+bounds['x']+bounds['width']/2+.125,
                window['at'][1]+bounds['y']+bounds['height']/2+.375)
    def query(p):return request(p,'query')
    def signals(p):return request(p,'signals')['value']
    def match(result,frame):
        if not result.get('pass_'):return False
        metadata=result['value'][0]
        return metadata.get('app-dbus-name')==frame['app_bus'] and metadata.get('toplevel-object-path')==frame['object_path']
    check('unauthorized QueryPointer denied',request(a,'release')['pass_'] and not query(a)['pass_'])
    x,y=target('A');move(x,y);check('unauthorized caller receives no pointer notification',signals(a)==[])
    check('A reacquires actual registration',request(a,'claim')['value'] in (1,4))
    ctl('dispatch','hl.dsp.focus({window='+json.dumps('address:'+native_window('B')['address'])+'})')
    focus=data('activewindow');result=query(a)
    check('hover mapping is independent of keyboard focus',focus['pid']==peers['B']['process'].pid and match(result,frame_a),query=result,focus=focus)
    window=native_window('A');rx,ry=result['value'][1:]
    check('fractional output query returns logical client relative doubles',monitor['scale']==1.25 and abs(rx-(x-window['at'][0]))<.02 and abs(ry-(y-window['at'][1]))<.02
          and abs(rx-round(rx))>.01 and abs(ry-round(ry))>.01,query=result,requested=[x,y],window=window,monitor=monitor)
    na,nb=len(signals(a)),len(signals(b));move(x+.125,y)
    wait(lambda:len(signals(a))==na+1,'fractional motion notification')
    check('same pixel native fractional motion sends directed one shot',len(signals(a))==na+1 and len(signals(b))==nb,a=signals(a),b=signals(b))
    move(x+.25,y);check('second motion without query sends no second notification',len(signals(a))==na+1)
    query(a);query(a);na=len(signals(a));move(x+.5,y)
    wait(lambda:len(signals(a))==na+1,'coalesced pointer query')
    check('repeated queries coalesce to exactly one later signal',len(signals(a))==na+1)
    query(a);na=len(signals(a));request(a,'release');request(a,'claim');move(x+.75,y)
    check('registration replacement discards stale pending signal',len(signals(a))==na)
    # Truthful unknown still arms; subsequent motion causes the client to query
    # again. The real non-AT-SPI Foot is not given fake accessibility metadata.
    foot=next(w for w in data('clients') if w['pid']==c['foot'].pid)
    ctl('dispatch','hl.dsp.window.resize({x=400,y=160,window='+json.dumps('address:'+foot['address'])+'})')
    ctl('dispatch','hl.dsp.window.move({x=48,y=380,window='+json.dumps('address:'+foot['address'])+'})')
    foot=next(w for w in data('clients') if w['pid']==c['foot'].pid)
    move(foot['at'][0]+100,foot['at'][1]+70);unknown=query(a)
    check('real unexported Foot returns truthful UnknownToplevel',not unknown['pass_'] and 'UnknownToplevel' in unknown.get('error',''),result=unknown)
    na=len(signals(a));move(x,y);wait(lambda:len(signals(a))==na+1,'authorized Unknown arms next motion')
    check('authorized Unknown arms exactly one later actual signal',len(signals(a))==na+1)
    request(peers['A']['process'],'second');wait(lambda:sum(w['pid']==peers['A']['process'].pid for w in data('clients'))==2,'same PID second GTK window')
    second=next(w for w in data('clients') if w['pid']==peers['A']['process'].pid and 'second' in w['title'])
    ctl('dispatch','hl.dsp.window.move({x=520,y=360,window='+json.dumps('address:'+second['address'])+'})')
    move(*target('A'));ambiguous=query(a)
    check('same PID real multiwindow refuses active sibling ambiguity',not ambiguous['pass_'] and 'UnknownToplevel' in ambiguous.get('error',''),result=ambiguous,actualAX=ax())
    request(peers['A']['process'],'close-second');wait(lambda:sum(w['pid']==peers['A']['process'].pid for w in data('clients'))==1,'remove actual second GTK window')
    frame_a=wait(lambda:actual_frame('A'),'single actual AX window after close')
    check('closed sibling restores actual singleton mapping',match(query(a),frame_a))
    window=native_window('A');ctl('dispatch','hl.dsp.window.move({x=96,y=120,window='+json.dumps('address:'+window['address'])+'})')
    x,y=target('A');move(x,y);result=query(a);window=native_window('A')
    check('moved client origin recomputes relative coordinates',match(result,frame_a) and abs(result['value'][1]-(x-window['at'][0]))<.02 and abs(result['value'][2]-(y-window['at'][1]))<.02,result=result,window=window)
    # The actual reader starts disabled, then presents the real hovered child
    # through the public official pointer-moved signal and unchanged navigation.
    check('actual reader pointer remains disabled before explicit enable',not read_json(state_path)['mouseEnabled'] and read_json(state_path)['currentItem'] is None)
    check('real public mouse enable succeeds',set_mouse(True) is True)
    start=time.monotonic();move(*target('B'));time.sleep(.08);move(*target('A'))
    found=wait(lambda:[e for e in events(event_path) if e.get('time',0)>=start and e.get('event')=='actual-public-current-item' and e.get('accessible',{}).get('name')=='Pointer target A'],'actual Orca current hovered GTK button',15)
    check('real official pointer-moved carries actual AX frame',any(e.get('event')=='actual-public-pointer-moved' and e.get('time',0)>=start and e.get('accessible',{}).get('app_bus')==frame_a['app_bus'] and e.get('accessible',{}).get('object_path')==frame_a['object_path'] for e in events(event_path)),events=events(event_path)[-20:])
    heard=wait(lambda:[e for e in events(speech) if e.get('time',0)>=start and 'pointer target a' in e.get('text','').lower()],'real Orca pointer navigation utterance',10)
    check('Omarchy Orca compat navigates to actual GTK child and speaks it',bool(found and heard),current=found,utterances=heard)
    start=time.monotonic();move(*target('B'))
    gtk_hit=wait(lambda:r if (r:=read_json(peers['B']['layout']).get('pointerEvent')) and r['time']>=start and r['actualPickedButton']=='Pointer target B' else None,'actual decorated GTK CSD child under pointer')
    csd_item=wait(lambda:[e for e in events(event_path) if e.get('time',0)>=start and e.get('event')=='actual-public-current-item' and e.get('accessible',{}).get('name')=='Pointer target B'],'actual Orca decorated GTK CSD child',15)
    check('actual CSD toolkit hit and Orca AX child agree independently',bool(gtk_hit and csd_item),toolkit=gtk_hit,reader=csd_item,layout=read_json(peers['B']['layout']))
    request(peers['A']['process'],'popover')
    popup=wait(lambda:read_json(peers['A']['layout']).get('popup'),'actual GTK popup native allocation')
    window=native_window('A');box=popup['button'];transform=popup['surfaceTransform']
    px=window['at'][0]+popup['position'][0]+box['x']+box['width']/2-transform[0]
    py=window['at'][1]+popup['position'][1]+box['y']+box['height']/2-transform[1]
    start=time.monotonic();move(px,py)
    popup_hit=wait(lambda:r if (r:=read_json(peers['A']['layout']).get('pointerEvent')) and r['time']>=start and r['actualPickedButton']=='Actual popup target A' else None,'actual GTK popup child under pointer')
    popup_query=query(a)
    popup_item=wait(lambda:[e for e in events(event_path) if e.get('time',0)>=start and e.get('event')=='actual-public-current-item' and e.get('accessible',{}).get('name')=='Actual popup target A'],'actual Orca popup AX child',15)
    check('actual popup origin maps to parent AX frame and real child',match(popup_query,frame_a) and bool(popup_hit and popup_item),query=popup_query,toolkit=popup_hit,reader=popup_item,popup=popup)
    check('outside-parent popup preserves negative logical client coordinate',popup_query['value'][2]<0,query=popup_query)
    request(peers['A']['process'],'close-popover')
    check('real public disable succeeds',set_mouse(False) is True);start=time.monotonic();move(*target('B'));time.sleep(.25)
    check('disabled reviewer exposes no current item or new item event',not read_json(state_path)['mouseEnabled'] and read_json(state_path)['currentItem'] is None and not any(e.get('event')=='actual-public-current-item' and e.get('time',0)>=start for e in events(event_path)))
    check('actual public toggle enables requested mouse review',toggle() is True and wait(lambda:read_json(state_path).get('mouseEnabled'),'toggle enabled'))
    check('actual public second toggle disables requested mouse review',toggle() is True and wait(lambda:read_json(state_path) if not read_json(state_path).get('mouseEnabled') else None,'toggle disabled'))
    check('enable request before actual service absence',set_mouse(True) is True)
    check('normal pointer service retirement is quiescent',manager('PrepareUnload') is True)
    retired=query(a);check('retirement rejects actual pointer queries',not retired['pass_'] and 'ServiceRetired' in retired.get('error',''))
    ctl('plugin','unload',c['lib']);wait(lambda:r if (r:=read_json(state_path)).get('backend')=='AtspiDeviceLegacy' else None,'actual pointer Legacy fallback')
    check('public disable during actual backend absence accepted',set_mouse(False) is True)
    ctl('plugin','load',c['lib']);returned=wait(lambda:r if (r:=read_json(state_path)).get('backend')=='AtspiDeviceA11yManager' and r.get('epoch')==r.get('appliedEpoch') else None,'pointer backend returns',20)
    check('actual outage disable survives backend return',not returned['mouseEnabled'] and returned['currentItem'] is None and returned['commands']==saved_commands,reader=returned)
    check('explicit enable before second quiescent restart',set_mouse(True) is True)
    check('second pointer retirement quiescent',manager('PrepareUnload') is True);ctl('plugin','unload',c['lib'])
    wait(lambda:r if (r:=read_json(state_path)).get('backend')=='AtspiDeviceLegacy' else None,'second Legacy fallback')
    ctl('plugin','load',c['lib']);returned=wait(lambda:r if (r:=read_json(state_path)).get('backend')=='AtspiDeviceA11yManager' and r.get('epoch')==r.get('appliedEpoch') and r.get('mouseEnabled') else None,'enabled pointer restart',20)
    check('actual enabled restart retains all command configuration',returned['commands']==saved_commands,reader=returned)
    start=time.monotonic();move(*target('B'));time.sleep(.08);move(*target('A'))
    resumed=wait(lambda:[e for e in events(event_path) if e.get('time',0)>=start and e.get('event')=='actual-public-current-item' and e.get('accessible',{}).get('name')=='Pointer target A'],'new actual device pointer navigation after restart',15)
    check('actual current item recovers on fresh official device after restart',bool(resumed),events=resumed)
    set_mouse(False)
    pointer.stdin.close();pointer.wait(timeout=5)
    keyboard.stdin.close();keyboard.wait(timeout=5)
    for tag in ('A','B'):request(peers[tag]['process'],'exit');peers[tag]['process'].wait(timeout=5)
    for p in (a,b):request(p,'exit');p.wait(timeout=5)
    c['pid_stop'](reader)
    check('final genuine quiescent private unload',manager('PrepareUnload') is True);ctl('plugin','unload',c['lib'])
    c['report']['pointerReaderIdentity']='Omarchy Orca compat'
    c['report']['mappingBoundary']='actual native Wayland + actual AX unique singleton; strict same-PID multiwindow Unknown; GTK4 undecorated/CSD/popup leaves; no physical hardware claim'
