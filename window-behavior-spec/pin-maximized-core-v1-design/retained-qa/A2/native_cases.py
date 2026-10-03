"""Root-owned real input controller. Importing this module has no side effects."""
from pathlib import Path
import hashlib, json, os, subprocess, time
from input_episode import episode
from case_authority import Case,token,public,matches,complete,integer_point,move_command,input_safe,cursor_owner,protected_order

QA=Path('/home/hoskinson/window-integration-qa')
PRODUCT=Path('/home/hoskinson/window-behavior-spec/pin-lifetime-v3')
FIXTURE=QA/'qt-modal-private-v9/build-v7/qt-window-modal-fixture'
POINTER=Path('/home/hoskinson/.local/share/hypr-window-controls/qa/virtual-pointer')
KEYBOARD=PRODUCT/'keyboard-chords/physical-keyboard'

def start(pid):return Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()[19]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

class NativeCases:
    def __init__(self,session,output):
        self.session=session;self.output=Path(output);self.output.mkdir(mode=0o700)
        self.report={'result':'pending','checks':[],'observations':[],'inputs':[],'setupCommands':[],
                     'nativeFeatureAccepted':False,'taskbarFrontendAccepted':False,'maxPinAccepted':False,
                     'mainGUIWrites':False,'physicalHardwareProved':False,'cleanup':{}}
        self.fixture=None;self.pointer=None;self.epoch=0;self.held=False;self.identity={};self.counter=0
    def persist(self):
        p=self.output/'cases.json';p.write_text(json.dumps(self.report,indent=2,allow_nan=False)+'\n');p.chmod(0o600)
    def observe(self,label,fn):
        if len(self.report['observations'])>=4096:raise RuntimeError('Bounded actual observation limit reached')
        row={'label':label,'sequence':len(self.report['observations'])+1,'startedNs':time.monotonic_ns()}
        self.report['observations'].append(row);self.persist()
        try:self.session.guard();row['value']=fn();row['completedNs']=time.monotonic_ns();self.persist();return row['value']
        except BaseException as e:row['error']=repr(e);self.persist();raise
    def wait(self,label,fn,seconds=5):
        deadline=time.monotonic()+seconds
        while time.monotonic()<deadline:
            value=self.observe(label,fn)
            if value:return value
            time.sleep(.04)
        raise RuntimeError('Bounded actual observation timed out: '+label)
    def check(self,name,value,**details):
        self.report['checks'].append({'name':name,'passed':value is True,**details});self.persist()
        if value is not True:raise AssertionError(name)
    def query(self,function):
        if function not in ('pin_stack_state','pin_bar_state','pin_events','window_families'):raise ValueError('Fixed readonly native query required')
        return json.loads(self.session.ctl('repl','print(hl.plugin.hyprbars.'+function+'())'))
    def native(self):return json.loads(self.session.ctl('repl','print(hl.plugin.qt_modal_probe.state())'))
    def seat(self):return json.loads(self.session.ctl('repl','print(hl.plugin.qt_modal_probe.keyboard_state())'))
    def state(self):return json.loads((self.output/'state.json').read_text())
    def own(self,name):
        if not self.fixture:return None
        if self.fixture.poll() is not None or start(self.fixture.pid)!=self.report['fixture']['start']:raise RuntimeError('Exact owned Qt lifetime changed')
        rows=[w for w in self.session.data('clients') if w['pid']==self.fixture.pid and w['title']=='Qt WindowModal QA '+name]
        if not rows:return None
        if len(rows)!=1:raise ValueError('Ambiguous actual Qt public identity')
        row=rows[0];key={k:row[k] for k in ('address','stableId','pid')}
        if name in self.identity and self.identity[name]!=key:raise RuntimeError('Unexpected native lifetime replacement')
        self.identity[name]=key;return row
    def capture(self,name):
        current=self.own(name)
        if not current:raise ValueError('Actual live captured public owner required')
        value={k:current[k] for k in ('address','stableId','pid')}
        query='print(hl.plugin.hyprbars.pin_capture({address='+json.dumps(value['address'])+',stableId='+json.dumps(value['stableId'])+',pid='+str(value['pid'])+'}))'
        captured=token(json.loads(self.session.ctl('repl',query)))
        if public(captured)!=value or captured['compositorPid']!=self.session.evidence['compositorPID'] or captured['compositorStart']!=self.session.evidence['compositorStart'] or captured['session']!=self.session.evidence['signature']:raise RuntimeError('Actual native capture differs from selected root/member')
        return captured
    def setup(self,label,command):
        self.session.guard();row={'label':label,'command':command,'featureAcceptance':False};self.report['setupCommands'].append(row);self.persist()
        try:row['rawACK']=self.session.ctl('dispatch',command);self.persist()
        except BaseException as e:row['error']=repr(e);self.persist();raise
        return row
    def focus(self,name,expected=None):
        row=self.own(name);self.setup('Explicit setup focus '+name,'hl.dsp.focus({window='+json.dumps('address:'+row['address'])+'})')
        target=self.own(expected or name)
        self.wait('Actual core and distinct Seat focus '+(expected or name),lambda:(self.native(),self.seat()) if matches(self.native().get('nativeFocus'),target) and matches(self.seat().get('keyboardOwner'),target) else None)
    def arrange(self,name,x,y,w,h):
        row=self.own(name);target=json.dumps('address:'+row['address'])
        if not row['floating']:self.setup('Fixture float '+name,'hl.dsp.window.float({action="set",window='+target+'})')
        self.setup('Fixture resize '+name,f'hl.dsp.window.resize({{x={w},y={h},window={target}}})')
        self.setup('Fixture move '+name,f'hl.dsp.window.move({{x={x},y={y},window={target}}})')
        self.wait('Actual configured geometry '+name,lambda:self.own(name) if self.own(name)['at']==[x,y] and self.own(name)['size']==[w,h] else None)
    def command(self,name):
        self.epoch+=1;p=self.output/'command.new';p.write_text(json.dumps({'epoch':self.epoch,'command':name}));p.replace(self.output/'command.json')
        self.report['setupCommands'].append({'fixtureCommand':name,'epoch':self.epoch,'featureAcceptance':False});self.persist()
        if name=='quit':
            self.fixture.wait(timeout=8)
            events=[json.loads(x) for x in (self.output/'events.jsonl').read_text().splitlines()]
            if self.fixture.returncode!=0 or not any(e.get('event')=='commandHandled' and e.get('command')==name and e.get('epoch')==self.epoch for e in events):raise RuntimeError('Actual same-epoch normal Qt quit required')
        else:self.wait('Actual fixture command '+name,lambda:self.state() if self.state()['commandEpoch']==self.epoch else None)
    def launch_legacy(self):
        env=dict(self.session.env,QT_QPA_PLATFORM='wayland',QT_QPA_PLATFORMTHEME='',QT_STYLE_OVERRIDE='Fusion',QT_NO_XDG_DESKTOP_PORTAL='1')
        env.pop('DISPLAY',None)
        self.fixture=self.session.host.launch('pin-legacy-qt',[str(FIXTURE),str(self.output)],env)
        self.report['fixture']={'pid':self.fixture.pid,'start':start(self.fixture.pid),'executable':str(FIXTURE),'sha256':sha(FIXTURE)}
        self.wait('Actual pre-plugin/pre-Service same-process windows',lambda:self.own('owner') and self.own('peer'))
        actual=self.wait('Actual old public Qt state',lambda:self.state() if (self.output/'state.json').exists() else None)
        self.report['actualLegacyQtState']=actual;self.persist()
        if actual.get('pid')!=self.fixture.pid or actual.get('qtVersion')!='6.11.2' or actual.get('platform')!='wayland' or any(self.own(name).get('xwayland') is not False for name in ('owner','peer')):raise RuntimeError('Actual exact Qt Wayland old-window fixture required')
        self.arrange('owner',140,180,620,420);self.arrange('peer',780,300,620,420);self.focus_without_probe('peer')
        owner=self.own('owner');self.setup('Explicit legacy fixture native pin seed','hl.dsp.window.pin({window='+json.dumps('address:'+owner['address'])+'})')
        self.wait('Actual pre-plugin legacy pinned state',lambda:self.own('owner') if self.own('owner')['pinned'] is True else None)
        self.report['legacyBeforeLoad']=self.session.data('clients');self.persist()
    def focus_without_probe(self,name):
        row=self.own(name);self.setup('Pre-plugin explicit fixture focus '+name,'hl.dsp.focus({window='+json.dumps('address:'+row['address'])+'})')
        self.wait('Actual pre-plugin focus '+name,lambda:self.session.data('activewindow') if matches(self.session.data('activewindow'),row) else None)
    def start_pointer(self):
        self.session.guard();log=(self.output/'pointer.log').open('x');self.pointer_log=log
        self.pointer=subprocess.Popen([str(POINTER),'1600','1000'],env=self.session.env,stdin=subprocess.PIPE,stdout=log,stderr=log,text=True,start_new_session=True)
        record={'pid':self.pointer.pid,'start':start(self.pointer.pid),'pgid':os.getpgid(self.pointer.pid),'name':'pin-pointer','command':[str(POINTER),'1600','1000'],'log':str(self.output/'pointer.log')}
        if record['pgid']!=self.pointer.pid:raise RuntimeError('Owned pointer process group required')
        self.session.host.processes.append((self.pointer,record));self.report['pointer']=record;self.persist()
    def move(self,point,captured):
        text=move_command(point,1600,1000);self.session.guard();input_safe(self.native())
        if not self.pointer or self.pointer.poll() is not None or start(self.pointer.pid)!=self.report['pointer']['start']:raise RuntimeError('Actual exact owned pointer process required')
        self.pointer.stdin.write(text);self.pointer.stdin.flush()
        def arrived():
            value=self.native()
            try:cursor_owner(value,point,captured);return value
            except ValueError:return None
        return self.wait('Exact actual cursor+hit before any press',arrived,3)
    def pin_point(self,captured):
        rows=self.query('pin_bar_state');matches_rows=[r for r in rows if r.get('captured')==captured]
        if len(matches_rows)!=1 or len(matches_rows[0]['pinHitBoxes'])!=1:raise RuntimeError('One actual reserved pin button box for captured owner required')
        return integer_point(matches_rows[0]['pinHitBoxes'][0],1600,1000),rows
    def scene(self):
        value={'clients':self.session.data('clients'),'native':self.native(),'seat':self.seat(),'stack':self.query('pin_stack_state')}
        protected_order(value['stack']);return value
    def input_events(self,route):
        if route not in ('titlebar','super-p','super-ctrl-t'):raise ValueError('fixed actual input probe route required')
        function='events' if route=='titlebar' else 'keyboard_events'
        return self.observe('Actual native delivery rows '+route,lambda:json.loads(self.session.ctl('repl','print(hl.plugin.qt_modal_probe.'+function+'())')))
    def toggle(self,name,route):
        captured=self.capture(name);before=self.scene();owner=next(r for r in before['clients'] if matches(r,captured));events=self.query('pin_events');case=Case(captured)
        row={'name':name,'route':route,'captured':captured,'before':before,'nativeEventsBefore':events,'automaticRetries':0};self.report['inputs'].append(row);self.persist()
        if route=='titlebar':
            point,boxes=self.pin_point(captured);row.update(point=point,pinBarWitness=boxes)
            row['beforePress']=self.move(point,captured);row['inputEventsBefore']=self.input_events(route);self.persist()
            self.pointer.stdin.write('button 272 1\n');self.pointer.stdin.flush();self.held=True
            # No native query can accept the case before the real release.
            self.pointer.stdin.write('button 272 0\n');self.pointer.stdin.flush();self.held=False
        elif route in ('super-p','super-ctrl-t'):
            seat=self.seat();state=self.query('pin_stack_state');input_safe(self.native())
            if not matches(seat.get('keyboardOwner'),captured) or not matches(seat.get('coreNativeFocus'),captured) or state.get('keyboardPresent') is not True or type(state.get('keyboardModifiers')) is not int or state['keyboardModifiers']!=0:raise RuntimeError('Exact captured actual Seat/core owner and zero modifier precondition required')
            row['keyboardBefore']=seat;row['modifierBefore']=state;row['inputEventsBefore']=self.input_events(route);self.persist()
            env=dict(self.session.env,WINDOW_QA_COMPOSITOR_PID=str(captured['compositorPid']),WINDOW_QA_COMPOSITOR_START=captured['compositorStart'])
            process=self.session.host.launch('pin-chord-'+str(len(self.report['inputs'])),[str(KEYBOARD),'--chord',route],env)
            pid=process.pid;identity=start(pid);process.wait(timeout=4)
            row['keyboardProcess']={'pid':pid,'start':identity,'argv':[str(KEYBOARD),'--chord',route],'exitCode':process.returncode,'executableSHA256':sha(KEYBOARD),'gone':not Path(f'/proc/{pid}').exists()};self.persist()
            if process.returncode!=0 or not row['keyboardProcess']['gone']:raise RuntimeError('Real private keyboard normal completion/all releases required')
        else:raise ValueError('Genuine admitted frontend input route required')
        def completed():
            row['inputEventsAfter']=self.input_events(route);self.persist()
            delivery=episode(row['inputEventsBefore'],row['inputEventsAfter'],route,captured,row.get('point'),allow_pending=True)
            if delivery is None:return None
            row['deliveryEvidence']=delivery;self.persist()
            case.press(delivery['observedPressAndRelease'],delivery['sameCapturedOwner'])
            case.release(delivery['observedPressAndRelease'])
            current=self.query('pin_events')
            if len(current)<=len(events):return None
            fresh=current[len(events):]
            if len(fresh)!=1:raise RuntimeError('One actual native toggle per input required')
            complete(fresh[0],captured,owner['pinned']);return fresh[0]
        row['receipt']=self.wait('Exact complete actual native pin receipt after release',completed);case.receipt=True
        after=self.scene();row['after']=after;self.persist()
        if route!='titlebar' and (type(after['stack'].get('keyboardModifiers')) is not int or after['stack']['keyboardModifiers']!=0):raise RuntimeError('Actual final zero keyboard modifiers required')
        current=self.capture(name)
        peers=lambda scene:{r['stableId']:{k:r.get(k) for k in ('address','stableId','pid','pinned','floating','at','size','workspace','monitor','fullscreen','fullscreenClient')}for r in scene['clients'] if not matches(r,captured)}
        if current!=captured or peers(before)!=peers(after):raise RuntimeError('Same lifetime and independent member state required')
        if before['native']['nativeFocus']!=after['native']['nativeFocus'] or before['seat']['keyboardOwner']!=after['seat']['keyboardOwner'] or before['seat']['keyboardSurfacePresent']!=after['seat']['keyboardSurfacePresent'] or before['seat']['keyboardResourcePresent']!=after['seat']['keyboardResourcePresent']:raise RuntimeError('No Pin-driven core/Seat focus change allowed')
        case.observed=True;self.check('Genuine '+route+' per-window Toggle pin '+name,case.accept(),inputIndex=len(self.report['inputs'])-1)
        return row
    def invariant_transition(self,label,action):
        before=self.scene();self.report.setdefault('lifecycleTransitions',[]).append({'label':label,'before':before});row=self.report['lifecycleTransitions'][-1];self.persist();action();after=self.wait('Actual protected band '+label,lambda:self.scene());row['after']=after;self.persist()
        before_bits={r['stableId']:r['pinned'] for r in before['clients']};after_bits={r['stableId']:r['pinned'] for r in after['clients']}
        self.check('Persistent band/member pin preservation after '+label,before_bits==after_bits,transitionIndex=len(self.report['lifecycleTransitions'])-1)
    def run(self):
        before=self.report['legacyBeforeLoad'];after=self.session.data('clients')
        projection=lambda rows:{r['stableId']:{k:r[k] for k in ('address','stableId','pid','pinned','floating','at','size','workspace','monitor','fullscreen','fullscreenClient')}for r in rows}
        self.check('Pre-plugin/pre-Service live window adoption preserves exact existing state',projection(before)==projection(after),before=before,after=after)
        self.start_pointer();self.focus('peer');self.toggle('owner','titlebar');self.toggle('owner','titlebar')
        self.focus('peer');self.toggle('peer','super-p');self.toggle('peer','super-ctrl-t')
        # Pin owner is protected while a genuinely unpinned peer receives a core raise/focus.
        self.invariant_transition('overlapping unpinned peer raise/focus',lambda:(self.arrange('peer',300,260,620,420),self.focus('peer')))
        self.command('open');self.wait('Actual new post-plugin child',lambda:self.own('child'));self.arrange('child',370,300,320,180)
        self.command('nested');self.wait('Actual post-plugin nested modal',lambda:self.own('nested'));self.arrange('nested',410,340,240,140)
        family=self.query('window_families');owner=self.own('owner');child=self.own('child');nested=self.own('nested')
        child_row=next(r for r in family if matches(r,child));nested_row=next(r for r in family if matches(r,nested))
        self.check('Actual new Qt modal and nested parent chain joins pinned owner band',child_row['modal'] is True and nested_row['modal'] is True and child_row['parent']==owner['address'] and nested_row['parent']==child['address'] and len(protected_order(self.query('pin_stack_state')))>=3,native=family)
        self.focus('peer');self.invariant_transition('pinned owner focus routes deepest actual modal',lambda:self.focus('owner','nested'))
        self.toggle('nested','super-p');self.toggle('nested','super-ctrl-t')
        captured=self.capture('child');self.command('closeNested');self.wait('Nested lifetime absent',lambda:self.own('nested') is None)
        self.command('closeChild');self.wait('Child lifetime absent',lambda:self.own('child') is None);self.identity.pop('child');self.identity.pop('nested')
        self.command('open');self.wait('Genuine new child native lifetime',lambda:self.own('child'));fresh=self.capture('child')
        self.check('Closed member capture cannot name fresh QObject/native lifetime',captured!=fresh,retired=captured,current=fresh,addressReuseActuallyObserved=captured['address']==fresh['address'])
        self.command('closeChild');self.wait('Fresh child lifetime absent',lambda:self.own('child') is None)
        self.focus('peer');self.toggle('owner','titlebar');self.toggle('owner','titlebar')
        old=self.capture('owner');before=self.scene();self.session.ctl('reload');self.wait('Actual config reload complete',lambda:not self.session.ctl('configerrors').strip())
        new=self.capture('owner');after=self.scene()
        self.check('Genuine private reload invalidates old token and preserves live pin bits',old!=new and old['epoch']!=new['epoch'] and {r['stableId']:r['pinned']for r in before['clients']}=={r['stableId']:r['pinned']for r in after['clients']},before=old,after=new)
        if len(self.report['checks'])!=14 or not all(r['passed']for r in self.report['checks']):raise RuntimeError('All14 exact native campaign A checks required')
        self.report['nativeFeatureAccepted']=True;self.report['result']='pass';self.persist()
    def close(self):
        errors=[]
        for label,process in [('pointer',self.pointer),('fixture',self.fixture)]:
            if not process:continue
            row={'pid':process.pid,'forced':False};self.report['cleanup'][label]=row;self.persist()
            try:
                if process.poll() is None:
                    if label=='pointer':
                        if self.held:self.pointer.stdin.write('button 272 0\n');self.pointer.stdin.flush();self.held=False
                        self.pointer.stdin.close();self.pointer.wait(timeout=5)
                    else:self.command('quit')
                row.update(exitCode=process.poll(),gone=not Path(f'/proc/{process.pid}').exists())
                if row['exitCode']!=0 or not row['gone']:raise RuntimeError('Normal exact owned client shutdown required')
            except BaseException as e:row['error']=repr(e);errors.append(repr(e))
            self.persist()
        if getattr(self,'pointer_log',None):self.pointer_log.close()
        self.report['normalCleanup']=not errors and bool(self.fixture) and self.session.data('clients')==[]
        if not self.report['normalCleanup']:self.report['result']='fail';self.report['cleanupErrors']=errors
        self.persist()
        if errors:raise RuntimeError('Private clients not normally closed: '+repr(errors))
