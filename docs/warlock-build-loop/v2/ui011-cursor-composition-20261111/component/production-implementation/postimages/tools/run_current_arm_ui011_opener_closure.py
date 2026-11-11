#!/usr/bin/env python3
"""Fixed connected standard-v3 observer qualification. No import-time effects.

Uses actual private nested-stack/window custody; never grants original acceptance.
"""
from __future__ import annotations
import argparse,copy,ctypes,hashlib,importlib.util,json,os,re,select,shutil,signal,socket,stat,struct,subprocess,sys,time
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
sys.dont_write_bytecode=True
attempt_auth=boot_correspondence=owned_fonts=keyboard_fixture=geometry=None
ROOT=Path('/home/hoskinson/Projects/Warlock')
SELF=ROOT/'tools/run_current_arm_ui011_opener_closure.py'
PACKET=ROOT/'.warlock-contributor/evidence/nextloop-20261106/ui011-original-opener-closure-v2/packet.json'
RECORD='.warlock-contributor/ui011-observed-opener-closure-root-20261110.json'
IDENTITY='92c1b16592f13f61b89310cd071b2a48554bf6caf7effa4d395ca78ccb9096ad'
LOG_LIMIT=4*1024*1024
JOURNEY_NS=28_000_000_000
CLEANUP_NS=2_000_000_000
_STACK_KEY=object()
GENERATED_HELPER='tools/run_labwc_gl_foundation_ipc_20261108.py'
GENERATED_IMAGES={'host':'361f74c4faf75225ee9b666a4bf799783487cdc086b35d27706e8c1e95698b79','nested':'d40e2edab24c2032a7a77b4d44c3d738e5003256d7d4199950dc7001fee9b6ba'}
ASSETS={'controls','owner','recorder','controller','bar','popup','hyprctl','keyboardSeat','wtype','grim','compositor','nestedConfig','opener'}
REVIEWS={'sourceAndImages','providerAndABI','nestedInput'}
SYSTEM_ASSETS={'hyprctl':'/usr/bin/hyprctl','wtype':'/usr/bin/wtype','grim':'/usr/bin/grim','compositor':'/usr/bin/Hyprland'}
CLOSE_ARGV=['-M','alt','-k','F4','-m','alt']
DEADLINE_ENV='WARLOCK_FOREIGN_ENDPOINT_DEADLINE_NS'
PHASE_LIBC={'path':'/usr/lib/libc.so.6','sha256':'6ab264fb4e8df9942b0fb75b48fcd5c30b2f081d8dfaa6c25d7be1d3fce5b2ab'}
CONTRACT_SHA='6490c0202f7377f9a768cce6a6e558b01bd32dae92eb40dc04ddd2f021dbecf5'
HELPERS={'plugins/warlock-contributor/scripts/warlock.py': '6835bb428154d23d7e89e85b17c971c2db30c293a2a8ee1f5b3ddf9ef721ff78', 'window-integration-qa/qa_launch.py': '6ef35104e4082249cfbabb747425210b1ca6fe988f675880a2afc059e13b5b23', 'tools/omarchy_ui_mvp.py': '3ec7be274604e485b52b3c15c07ac57f3d7b24384dc1465ed109e47d063239cc', 'tools/run_labwc_gl_foundation_window_rule_20261108.py': '1930bc749aed250b1fed2e4ab884e8c4e1c94b4c1036eea118075b5fec2270ad', 'tools/run_labwc_gl_foundation_ipc_20261108.py': 'f313c21d4e47adf8b3d37a3abd9ac9b5901b397901260cf71970e4abf47a1f69', 'tools/run_arm_gl_foundation_renewed_20261107.py': '1587fee27cc8521700cfbf46e759a53f6a987cd95eab67b81588b680b033761b', 'tools/run_arm_gl_foundation_renewed_20261108_0623.py': '769f48e13990909a88b588e3e145775b5ee16571a81817fac17eede1252bcdd2', 'tools/ux023_current_boot_correspondence.py': 'e4cee72fcf5c6bf3a0b41a869edd7dbb5ed629c27d72cf88123e8e905c10eba0', 'tools/ux003_owned_fonts.py': 'b9d7956e8a934ba5f4db4523114e732b673927ece04afb0c0525fd9501a6bbf3', 'tools/ux023_notifications_keyboard_fixture.py': '47ef863f8e0e0486f1ba12e5d8f537d35987f3bdc64f66a3a342a9ed0083b6a3', 'tools/ux003_input_geometry_720.py': 'e879f98eb419cc53e7a371f06384ae0e776b66d7d46847bca3a2e6039df174b0', 'tools/ui011_foreign_toplevel_attempt_authorization.py': 'fa005ec6e4cdb4acb27ffff54d5a55690c6a32b4190a066b6064da5cebd6130c', 'tools/ui011_opener_journey.py': '4b8b7caeab6cafcf1d9192e01c7ab9e043de1ba27eefdccf85973b909db7fc13', 'tools/ui011_owned_at_provider.py': 'd9d02854b6213eaca3109f522d3b8497b3d9eff8f1192c2ba27b13e94b1c6b11'}

def validate_generated_foundation_basis(foundation, report):
    sources=foundation.get('sourceInputs',{})
    for relative in (GENERATED_HELPER,'tools/run_arm_gl_foundation_renewed_20261107.py'):
        if sources.get(str(ROOT/relative))!=HELPERS[relative]:
            raise ValueError('qualified foundation uses a different helper/guard policy')
    if (foundation.get('hostInputs',{}).get(foundation.get('host',{}).get('labwc'))!=GENERATED_IMAGES['host']
            or foundation.get('nested',{}).get('inputs',{}).get(foundation.get('nested',{}).get('compositor'))!=GENERATED_IMAGES['nested']):
        raise ValueError('qualified foundation image tuple differs')
    for role,image in GENERATED_IMAGES.items():
        observed=report.get(role+'GeneratedRuntime',{})
        if (observed.get('role')!=role or observed.get('identity',{}).get('image')!=image
                or observed.get('creatorAttested') is not False):
            raise ValueError('qualified foundation role/context evidence differs')
        generated=observed.get('generatedObject')
        if generated is not None and (generated.get('mutableExecutableBacking') is not True
                                      or generated.get('creatorAttested') is not False):
            raise ValueError('generated RAM must remain mutable and not creator-attested')

def digest(body):
    return hashlib.sha256(body).hexdigest()

def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON field')
        result[key] = value
    return result

def regular(path, cap=LOG_LIMIT):
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts or path.resolve() != path:
        raise ValueError('noncanonical or symlink path')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    with os.fdopen(fd, 'rb') as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size > cap:
            raise ValueError('bounded regular file required')
        body = stream.read(cap + 1)
        after = os.fstat(stream.fileno())
    fields = ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
    if len(body) > cap or any(getattr(before, x) != getattr(after, x) for x in fields):
        raise ValueError('file changed or exceeded cap')
    return body

def pinned(ref, cap=LOG_LIMIT):
    if not isinstance(ref, dict) or set(ref) != {'path', 'sha256'}:
        raise ValueError('exact file reference required')
    body = regular(ref['path'], cap)
    if digest(body) != ref['sha256']:
        raise ValueError('file hash changed: ' + ref['path'])
    return body

def product_environment(source):
    runtime = source.get('XDG_RUNTIME_DIR', '')
    display = source.get('WAYLAND_DISPLAY', '')
    socket_name = Path(display).name
    if (not runtime.startswith('/') or runtime.startswith('//') or str(Path(runtime)) != runtime
            or str(Path(display)) != display or str(Path(display).parent) != runtime
            or '..' in Path(runtime).parts or '..' in Path(display).parts
            or not re.fullmatch(r'wayland-[A-Za-z0-9_-]+',socket_name) or len(socket_name)>64):
        raise ValueError('canonical issued private nested socket required')
    return {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8',
            'GDK_BACKEND': 'wayland', 'XDG_RUNTIME_DIR': runtime,
            'WAYLAND_DISPLAY': socket_name,
            'DBUS_SESSION_BUS_ADDRESS': 'unix:path=' + runtime + '/bus'}

def remaining(clock, now, boot):
    if boot != clock['boot'] or now < clock['last']:
        raise ValueError('clock/boot changed')
    clock['last'] = now
    left = clock['deadline'] - now
    if left <= 0:
        raise TimeoutError('same original deadline exhausted')
    return left

def left(clock):
    if time.time_ns() >= attempt_auth.clock_authorization_deadline_ns(clock):
        raise TimeoutError('human authorization expired')
    return remaining(clock, time.monotonic_ns(), Path('/proc/sys/kernel/random/boot_id').read_text().strip())

def input_group_absent(pid):
    try:
        os.killpg(pid,0)
    except ProcessLookupError:
        return True
    return False

class _HeldKeyboard:
    """One actual parent-owned keyboard, advertised before any GTK client starts."""
    def __init__(self, proc, image_sha, clock, stderr_path):
        if not isinstance(proc, subprocess.Popen):
            raise ValueError('actual retained keyboard Popen required')
        self.proc=proc;self.image_sha=image_sha;self.clock=clock
        self.stderr_path=stderr_path;self.start_ticks=birth(proc.pid)[0]
        self.used=set();self.bootstrap=None;self.final=None;self.closing=False
        self.attest()

    def attest(self):
        left(self.clock)
        if self.closing or self.proc.poll() is not None:
            raise ValueError('held keyboard no longer live')
        if birth(self.proc.pid)[0]!=self.start_ticks or os.getpgid(self.proc.pid)!=self.proc.pid:
            raise ValueError('held keyboard process custody changed')
        if digest(regular(Path('/proc',str(self.proc.pid),'exe').resolve(),256*1024*1024))!=self.image_sha:
            raise ValueError('held keyboard image changed')
        if regular(self.stderr_path,LOG_LIMIT):
            raise ValueError('held keyboard diagnostics nonempty')
        left(self.clock)

    def read_ack(self, expected):
        raw=b''
        while len(raw)<len(expected):
            self.attest()
            readable,_,_=select.select([self.proc.stdout.fileno()],[],[],left(self.clock)/1_000_000_000)
            if not readable:
                raise TimeoutError('keyboard ACK absent under same original deadline')
            chunk=os.read(self.proc.stdout.fileno(),64)
            if not chunk:
                raise ValueError('keyboard EOF before exact live ACK')
            raw+=chunk
            if len(raw)>len(expected) or not expected.startswith(raw):
                raise ValueError('stale or extra held keyboard ACK bytes')
        self.attest()
        return raw

    def exchange(self, payload, expected):
        self.attest()
        # Any pre-existing bytes/EOF are unsolicited, never a later transaction ACK.
        if select.select([self.proc.stdout.fileno()],[],[],0)[0]:
            raise ValueError('unsolicited held keyboard output before transaction')
        if self.proc.stdin.write(payload)!=len(payload):
            raise ValueError('partial keyboard write; no replay')
        self.proc.stdin.flush()
        actual=self.read_ack(expected)
        self.attest()
        return {'pid':self.proc.pid,'startTicks':self.start_ticks,'exit':None,'alive':True,
                'inputHex':payload.hex(),'ackHex':actual.hex(),
                'monotonicNs':time.monotonic_ns(),'originalDeadlineNs':self.clock['deadline'],
                'meaning':keyboard_fixture.BOOTSTRAP_MEANING}

    def start(self):
        if 'bootstrap' in self.used:
            raise ValueError('keyboard bootstrap already attempted')
        self.used.add('bootstrap')
        self.bootstrap=self.exchange(b'sync 0\n',b'ready 0\n')
        keyboard_fixture.require_bootstrap_reply(bytes.fromhex(self.bootstrap['ackHex']))
        return self.bootstrap


    def finish(self):
        if self.final is not None:
            return self.final
        self.attest();self.closing=True
        # EOF retires the SAME device only after GUI close, never between keyboard steps.
        tail,_=self.proc.communicate(b'',timeout=left(self.clock)/1_000_000_000)
        if self.proc.returncode!=0 or tail or regular(self.stderr_path,LOG_LIMIT):
            raise ValueError('held keyboard normal retirement/empty output absent')
        if not input_group_absent(self.proc.pid):
            raise ValueError('held keyboard process group retained after reap')
        left(self.clock)
        self.final={'pid':self.proc.pid,'startTicks':self.start_ticks,'exit':self.proc.returncode,
                    'normal':True,'groupAbsent':True,'stdoutTailHex':tail.hex(),'monotonicNs':time.monotonic_ns()}
        return self.final

def derive_live_font_stack(packet, historical, reuse):
    proof=json.loads(pinned(reuse['fontIsolation'],32*1024*1024),object_pairs_hook=unique)
    live_inputs=owned_fonts.live_inputs(historical['nested']['inputs'])
    if (proof.get('schema')!=1 or proof.get('disposition')!='accepted'
            or proof.get('scope')!='ux003-owned-nested-font-isolation'
            or proof.get('historicalFoundationPacket')!=packet['foundationPacket']
            or proof.get('historicalNestedInputs')!=historical['nested']['inputs']
            or proof.get('liveNestedInputs')!=live_inputs
            or proof.get('fontFiles')!=owned_fonts.FONT_PINS
            or proof.get('globalCachePinsRemoved')!=owned_fonts.GLOBAL_CACHE_PINS):
        raise ValueError('exact independent nested-font isolation correspondence required')
    live=copy.deepcopy(historical)
    live['nested']['inputs']=live_inputs
    live['nested']['sourceReview']=proof['liveProviderReadiness']
    return live

def birth(pid):
    fields = Path('/proc', str(pid), 'stat').read_text().rsplit(')', 1)[1].split()
    return fields[19], int(fields[1])

def attest_process_image(pid, expected_birth, expected_sha):
    """Follow only this fixed procfs magic link; retain ordinary file no-follow policy."""
    if type(pid)is not int or pid<=0 or not isinstance(expected_birth,str) or not expected_birth.isdecimal():
        raise ValueError('exact process PID and birth required')
    if not isinstance(expected_sha,str) or re.fullmatch('[0-9a-f]{64}',expected_sha)is None:
        raise ValueError('exact process image digest required')
    def live_birth():
        try:fields=Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()
        except FileNotFoundError as exc:raise ValueError('process image process exited') from exc
        if len(fields)<20 or fields[19]!=expected_birth:raise ValueError('process image birth changed')
        if fields[0] in ('Z','X','x'):raise ValueError('process image process is dead or zombie')
    live_birth()
    path=Path('/proc',str(pid),'exe')
    # EngineCustody uses this same kernel executable-link contract. Do not
    # interpret its readlink text as an ordinary pathname or apply NOFOLLOW.
    fd=os.open(path,os.O_RDONLY|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        before=os.fstat(fd);named_before=os.stat(path)
        fields=('st_dev','st_ino','st_mode','st_size','st_mtime_ns','st_ctime_ns')
        stamp=lambda value:tuple(getattr(value,k)for k in fields)
        if not stat.S_ISREG(before.st_mode) or not 0<before.st_size<=256*1024*1024 or stamp(before)!=stamp(named_before):
            raise ValueError('bounded held process image identity required')
        hashed=hashlib.sha256();total=0
        while total<=before.st_size:
            chunk=os.read(fd,min(1024*1024,before.st_size+1-total))
            if not chunk:break
            total+=len(chunk);hashed.update(chunk)
        after=os.fstat(fd);named_after=os.stat(path)
        if total!=before.st_size or stamp(before)!=stamp(after) or stamp(before)!=stamp(named_after):
            raise ValueError('process image changed during bounded read')
        live_birth()
        if hashed.hexdigest()!=expected_sha:raise ValueError('process image digest differs')
    finally:os.close(fd)


def descendant(pid, ancestor, ancestor_birth):
    for _ in range(12):
        current, parent = birth(pid)
        if pid == ancestor:
            return current == ancestor_birth
        if parent <= 1 or parent == pid:
            return False
        pid = parent
    return False

def write_json(path, value):
    with path.open('x', encoding='utf-8') as stream:
        os.chmod(path, 0o600)
        json.dump(value, stream, indent=2)
        stream.write('\n')

def staging_clock(staged,boot):
    origin=int(staged['generatedMonotonicNs']);deadline=int(staged['deadlineMonotonicNs'])
    if origin<=0 or deadline-origin!=JOURNEY_NS:raise ValueError('exact original28s staging deadline required')
    return dict(origin=origin,deadline=deadline,last=origin,boot=boot)

def global_snapshot():
    cgroup=Path('/proc/self/cgroup').read_text()
    same={}
    for path in Path('/proc').glob('[0-9]*/cgroup'):
        try:
            if path.read_text()==cgroup:
                pid=int(path.parent.name);same[str(pid)]=birth(pid)[0]
        except (OSError,ValueError,IndexError):pass
    return dict(namespaces={n:os.readlink('/proc/self/ns/'+n) for n in ('mnt','pid','user','net','uts','ipc','cgroup')},
                environment=dict(os.environ),cgroup=cgroup,scopeProcesses=same)

def global_restored(before,after):
    # No changing a global desktop/session object, user config or environment.
    # The sole protected scope must contain no newly live orphan at retirement.
    return (before['namespaces']==after['namespaces'] and before['environment']==after['environment']
            and before['cgroup']==after['cgroup']
            and all(before['scopeProcesses'].get(pid)==born for pid,born in after['scopeProcesses'].items()))

def require_live_stack(stack,deadline):
    if not isinstance(stack,_OwnedStack) or stack.key is not _STACK_KEY or stack.deadline!=deadline or stack.closed:
        raise ValueError('actual same-parent live stack custody required; retired reports are not leases')
    stack.current()
    return stack

class _OwnedStack:
    """Private QA custody: actual retained Popen objects, never minted from a report."""
    def __init__(self,foundation,qa,collector,base,clock,output,nested_config,current_boot,provider_source_correspondence,cursor_correspondence=None):
        self.key=_STACK_KEY;self.p=foundation;self.qa=qa;self.c=collector;self.base=base;self.clock=clock
        self.nested_config=nested_config;self.current_boot=current_boot;self.provider_source_correspondence=provider_source_correspondence;self.cursor_correspondence=cursor_correspondence
        self.output=output;self.deadline=clock['deadline'];self.closed=False;self.children=[];self.logs=[]
        self.host=None;self.nested=None;self.runtime=None;self.facts={};self.instance=None;self.env=None
        self.font_layout=None;self.nested_inventory=None

    def spawn(self,role,argv,environment,inventory):
        left(self.clock)
        stdout=(self.output/(role+'.stdout')).open('xb');stderr=(self.output/(role+'.stderr')).open('xb')
        self.logs.extend([stdout,stderr])
        proc=self.c.checked_spawn(self.base,self.clock,inventory,lambda:subprocess.Popen(
            argv,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,env=environment,
            close_fds=True,start_new_session=True,preexec_fn=self.base.bound_output))
        self.children.append((proc,None,role));born=self.base.process_birth(proc.pid);self.children[-1]=(proc,born,role)
        return proc,born

    def host_live(self):
        left(self.clock)
        if self.host is None:raise ValueError('host not issued')
        self.base.check_process(self.host,self.host_birth,self.p['hostInputs'][self.p['host']['labwc']])
        if any(os.fstat(x.fileno()).st_size>self.c.CAP for x in self.logs):raise ValueError('bounded stack log exceeded')
        left(self.clock)

    def output_command(self,role,argv,env):
        proc,_=self.spawn(role,argv,env,self.p['hostInputs'])
        while proc.poll() is None:self.host_live();time.sleep(min(0.01,left(self.clock)/1e9))
        if proc.wait(timeout=left(self.clock)/1e9)!=0:raise ValueError('owned output management refused')
        self.host_live()
        raw=regular(self.output/(role+'.stdout'),self.c.CAP)
        if regular(self.output/(role+'.stderr'),self.c.CAP):raise ValueError('output management diagnostics')
        return raw

    def ipc_peer(self,path):
        import socket,struct
        info=path.lstat()
        if not stat.S_ISSOCK(info.st_mode) or info.st_uid!=os.getuid():raise ValueError('foreign nested IPC socket')
        with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as peer:
            peer.settimeout(left(self.clock)/1e9);peer.connect(str(path))
            pid,uid,_=struct.unpack('3i',peer.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
            if pid!=self.nested.pid or uid!=os.getuid():raise ValueError('nested IPC peer differs')
        after=path.lstat()
        if (info.st_dev,info.st_ino)!=(after.st_dev,after.st_ino):raise ValueError('IPC socket replaced')

    def map_generated_role(self,role):
        # Only these retained fixed-image Popen owners use the scoped RAM recipe.
        if role=='host':
            h=self.p['host'];image=self.p['hostInputs'][h['labwc']]
            inventory=dict(self.p['hostInputs'],**{str(self.output/'font/LiberationSans-Regular.ttf'):self.c.FONT_SHA})
            return boot_correspondence.generated_context_mapped(self.current_boot,self.c,self.base,self.host,self.host_birth,'host',image,inventory,
                [h['labwc'],h['wlroots'],str(Path('/usr/lib/libEGL_nvidia.so.0').resolve()),'/usr/lib/libnvidia-eglcore.so.615.78.08'],self.clock,self.p,self.provider_source_correspondence)
        if role=='nested':
            n=self.p['nested'];image=n['inputs'][n['compositor']]
            return boot_correspondence.generated_context_mapped(self.current_boot,self.c,self.base,self.nested,self.nested_birth,'nested',image,self.nested_inventory,
                [n['compositor'],n['backend']],self.clock,self.p,self.provider_source_correspondence,self.cursor_correspondence)
        raise ValueError('generated mapping classification is only for fixed owned host/nested roles')

    def start(self):
        p=self.p;c=self.c;base=self.base;h=p['host'];clock=self.clock;output=self.output
        self.runtime=self.qa.private_runtime();runtime=self.runtime
        for n in ('home','config','cache','data','empty-config','empty-data','labwc-config','font','font-cache'):(output/n).mkdir(mode=0o700)
        base.regular(c.FONT,c.FONT_SHA);font=output/'font/LiberationSans-Regular.ttf';shutil.copyfile(c.FONT,font);base.regular(font,c.FONT_SHA)
        (output/'fonts.conf').write_text(c.font_config(output));(output/'labwc-config/rc.xml').write_text(c.RC)
        if digest(self.nested_config)!=c.NESTED_LUA_SHA:raise ValueError('exact reviewed Lua content required')
        self.config_path=c.write_nested_config(output)
        if self.config_path.read_bytes()!=self.nested_config:raise ValueError('actual written Lua differs')
        boot_correspondence.verify_graphics(self.current_boot,base,p['graphics'],p['hostInputs']);build=boot_correspondence.verify_build(self.current_boot,c,base,p)
        c.verify_wlroots_lookup(base,h,p['hostInputs'],build['sourceHashes'])
        env=c.host_environment(runtime,output,h['libraryDirs'])
        self.host,self.host_birth=self.spawn('host',c.host_argv(h['labwc'],output),env,p['hostInputs'])
        sockets=[]
        while not sockets:
            self.host_live();sockets=[x for x in runtime.glob('wayland-*') if stat.S_ISSOCK(x.lstat().st_mode)]
            if not sockets:time.sleep(min(0.02,left(clock)/1e9))
        if len(sockets)!=1:raise ValueError('ambiguous owned host socket')
        self.host_socket=sockets[0]
        observed=base.registry(self.host_socket,self.host,self.host_birth,p['hostInputs'][h['labwc']],clock);c.require_caps(observed['globals'])
        cenv=dict(env,WAYLAND_DISPLAY=str(self.host_socket))
        initial=c.output_state(json.loads(self.output_command('output-before',[h['outputTool'],'--json'],cenv),object_pairs_hook=unique),False)
        self.output_command('output-apply',c.output_apply(h['outputTool'],initial['name']),cenv)
        final=c.output_state(json.loads(self.output_command('output-after',[h['outputTool'],'--json'],cenv),object_pairs_hook=unique),True)
        if initial['name']!=final['name']:raise ValueError('owned host output changed')
        self.facts['hostOutput']=final
        self.facts['hostGeneratedRuntime']=self.map_generated_role('host')
        self.facts['hostMappings']=self.facts['hostGeneratedRuntime']['staticMappingsAfter']
        self.facts['hostGraphicsFDs']=boot_correspondence.graphics_fds(self.current_boot,base,p['graphics'],self.host,self.host_birth,p['hostInputs'][h['labwc']])
        boot_correspondence.verify_graphics(self.current_boot,base,p['graphics'],p['hostInputs']);self.host_live();left(clock)
        nested=p['nested'];boot_correspondence.verify_private_provider(self.current_boot,c,base,nested,self.provider_source_correspondence,self.cursor_correspondence)
        self.font_layout=owned_fonts.prepare(output,lambda:left(clock))
        self.nested_inventory=dict(boot_correspondence.cursor_inputs(self.current_boot,nested,self.cursor_correspondence),**owned_fonts.mapping_inputs(self.font_layout))
        nenv=owned_fonts.environment(c.apply_private_glib_environment(base.graphics_environment(runtime,output)),self.font_layout);nenv['WAYLAND_DISPLAY']=str(self.host_socket);nenv['LD_LIBRARY_PATH']=nested['libraryDir']
        self.nested,self.nested_birth=self.spawn('nested',c.nested_argv(nested['compositor'],output),nenv,self.nested_inventory)
        sockets=[]
        while not sockets:
            self.host_live();base.check_process(self.nested,self.nested_birth,nested['inputs'][nested['compositor']])
            sockets=[x for x in runtime.glob('wayland-*') if x!=self.host_socket and stat.S_ISSOCK(x.lstat().st_mode)]
            if not sockets:time.sleep(min(0.02,left(clock)/1e9))
        if len(sockets)!=1:raise ValueError('ambiguous owned nested display')
        self.nested_socket=sockets[0]
        self.facts['nestedOwnedFonts']={'configuration':{'path':self.font_layout['config'],'sha256':self.font_layout['configSha256']},'copies':dict(self.font_layout['copies']),'requestedEnvironment':{k:nenv[k] for k in ('FONTCONFIG_FILE','FONTCONFIG_PATH','FONTCONFIG_USE_MMAP')}}
        registry=base.registry(self.nested_socket,self.nested,self.nested_birth,nested['inputs'][nested['compositor']],clock);c.require_caps(registry['globals'])
        self.facts['nestedRegistry']=registry
        self.facts['nestedGeneratedRuntime']=self.map_generated_role('nested')
        self.facts['nestedMappings']=self.facts['nestedGeneratedRuntime']['staticMappingsAfter']
        self.facts['nestedGraphicsFDs']=boot_correspondence.graphics_fds(self.current_boot,base,p['graphics'],self.nested,self.nested_birth,nested['inputs'][nested['compositor']])
        ipc=[]
        while not ipc:
            self.host_live();base.check_process(self.nested,self.nested_birth,nested['inputs'][nested['compositor']])
            ipc=list((runtime/'hypr').glob('*/.socket.sock'))
            if not ipc:time.sleep(min(0.02,left(clock)/1e9))
        if len(ipc)!=1:raise ValueError('ambiguous private nested IPC')
        self.ipc=ipc[0];self.ipc_peer(self.ipc);signature=self.ipc.parent.name
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,100}',signature):raise ValueError('invalid actual nested signature')
        self.instance=dict(pid=self.nested.pid,startTicks=self.nested_birth,signature=signature,config=str(self.config_path))
        self.env=product_environment(dict(XDG_RUNTIME_DIR=str(runtime),WAYLAND_DISPLAY=str(self.nested_socket)))
        self.env['HYPRLAND_INSTANCE_SIGNATURE']=signature
        self.env.update(FONTCONFIG_FILE=str(output/'fonts.conf'),FONTCONFIG_PATH=str(output/'empty-config'),FONTCONFIG_USE_MMAP='0')
        self.current();return self

    def current(self):
        if self.closed or self.host is None or self.nested is None or self.env is None:raise ValueError('live stack not active')
        left(self.clock);self.host_live();n=self.p['nested']
        self.base.check_process(self.nested,self.nested_birth,n['inputs'][n['compositor']]);self.ipc_peer(self.ipc)
        if self.config_path.read_bytes()!=self.nested_config:raise ValueError('owned nested config drift')
        boot_correspondence.verify_graphics(self.current_boot,self.base,self.p['graphics'],self.p['hostInputs']);left(self.clock)

    def retire(self):
        if self.closed:return {'normal':False,'reason':'duplicate retirement refused'}
        self.closed=True;rows=[];normal=True;ceiling=self.deadline+CLEANUP_NS
        for proc,born,role in reversed(self.children):
            forced=False
            try:
                if proc.poll() is None:
                    if born is None or self.base.process_birth(proc.pid)!=born:raise ValueError('owned retirement birth unknown')
                    os.killpg(proc.pid,signal.SIGTERM)
                    available=min(ceiling-1_000_000_000-time.monotonic_ns(),attempt_auth.clock_authorization_deadline_ns(self.clock)-time.time_ns())/1e9
                    try:
                        if available<=0:raise subprocess.TimeoutExpired(proc.args,0)
                        proc.wait(timeout=available)
                    except subprocess.TimeoutExpired:
                        forced=True;os.killpg(proc.pid,signal.SIGKILL)
                        available=min(ceiling-time.monotonic_ns(),attempt_auth.clock_authorization_deadline_ns(self.clock)-time.time_ns())/1e9
                        if available<=0:raise TimeoutError('shared original cleanup ceiling')
                        proc.wait(timeout=available)
                gone=False
                try:os.killpg(proc.pid,0)
                except ProcessLookupError:gone=True
                ok=proc.returncode==0 and gone and not forced;normal=normal and ok
                rows.append(dict(role=role,pid=proc.pid,startTicks=born,exit=proc.returncode,reaped=proc.returncode is not None,groupAbsent=gone,forced=forced,normal=ok))
            except Exception as exc:
                normal=False;rows.append(dict(role=role,error=str(exc),normal=False,forced=forced))
        for f in self.logs:f.close()
        if normal and self.runtime is not None:
            try:self.qa.verify_runtime(self.runtime);shutil.rmtree(self.runtime);normal=not self.runtime.exists()
            except Exception as exc:normal=False;rows.append(dict(runtimeError=str(exc)))
        return dict(normal=normal,processes=rows,originalDeadlineNs=self.deadline,cleanupCeilingNs=ceiling)

def phase_renameat2():
    # Existing inventory-pinned libc; synchronous closed rename only, no callback.
    pinned(PHASE_LIBC,4*1024*1024)
    library=ctypes.CDLL(PHASE_LIBC['path'],use_errno=True)
    rename=library.renameat2
    rename.argtypes=(ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint)
    rename.restype=ctypes.c_int
    return library,rename

def phase_publish_request(rename,dirfd,sequence):
    if type(dirfd)is not int or dirfd<0 or type(sequence)is not int or not 1<=sequence<=keyboard_fixture.PHASE_LIMIT:
        raise ValueError('fixed held-directory phase rename required')
    temporary=('.qa-phase-request-%02d.tmp'%sequence).encode('ascii')
    final=('qa-phase-request-%02d'%sequence).encode('ascii')
    if rename(dirfd,temporary,dirfd,final,1)!=0:
        code=ctypes.get_errno()
        raise OSError(code,os.strerror(code))

def close_ready_matches(pair,binding,runtime_binding):
    """Read-only derivative gate: exact current closed view, no Notifications journey."""
    try:
        keyboard_fixture.validate_phase_pair(pair,binding)
        bar,popup=(pair[role]['snapshot'] for role in ('bar','popup'))
        if bar['root'] is None or popup['root'] is None:return False
        if bar['root']['mode'] is not None or popup['root']['mode']!='closed':return False
        if popup['documentFocused'] is not False or popup['controls']!=[]:return False
        if any(snap['query'] is not None or snap['retained'] is not None or snap['root']['loading']!='false' for snap in (bar,popup)):return False
        if bar['root']['pub']!=popup['root']['pub'] or bar['root']['lease']!='0' or popup['root']['lease']!='0' or binding['expectedLease']!=0:return False
        counters={key:runtime_binding[key] for key in ('lifetime','session','frontend')}
        if any(not isinstance(value,str) or re.fullmatch('[1-9][0-9]{0,19}',value) is None or int(value)>18446744073709551615 for value in counters.values()):return False
        host=json.dumps(counters,separators=(',',':'))
        prefix='applications:'+host+':'
        rows=[row for row in bar['controls'] if row['control']=='bar:applications']
        if len(rows)!=1:return False
        matched=re.fullmatch(re.escape(prefix)+r'([1-9][0-9]{0,19}):control:opener',rows[0]['id'])
        if matched is None or int(matched.group(1))>18446744073709551615:return False
        presentation=matched.group(1)
        # Desktop.key uses model.presentation; Surface publication is independent.
        # Corroborate that exact presentation against the current owning document,
        # never against publication or a suffix-only match. Freshness/custody comes
        # from validate_phase_pair. No independent numeric relation is claimed.
        witnesses={'bar:applications':'control:opener','bar:overview':'control:overview-opener',
          'bar:switcher':'control:switcher-opener','bar:notifications':'notifications:opener',
          'bar:files':'files:opener','bar:system':'system:opener','bar:settings':'settings:opener'}
        for identity,suffix in witnesses.items():
            current=[row for row in bar['controls'] if row['control']==identity]
            if (len(current)!=1 or current[0]['tag']!='BUTTON'
                    or current[0]['id']!=prefix+presentation+':'+suffix
                    or current[0]['focusOnly']!='false'):return False
        return rows[0]['disabled'] is False and rows[0]['ariaDisabled']=='false'
    except (KeyError,TypeError,ValueError,OverflowError):return False


MENU_STEPS = [
    {'name':'current-group','argv':['-k','Tab']},
    {'name':'open-menu','argv':['-M','shift','-k','F10','-m','shift']},
    {'name':'tab-forward','argv':['-k','Tab']},
    {'name':'tab-wrap','argv':['-k','Tab']},
    {'name':'tab-reverse-wrap','argv':['-M','shift','-k','Tab','-m','shift']},
    {'name':'dismiss','argv':['-k','Escape']},
    {'name':'reopen','argv':['-M','shift','-k','F10','-m','shift']},
    {'name':'dismiss-again','argv':['-k','Escape']},
    {'name':'close-owned-gui','argv':['-M','alt','-k','F4','-m','alt']},
]


UI011_TRANSACTIONS=[{'name':'tab-opener-1','argv':['-k','Tab']},{'name':'tab-opener-2','argv':['-k','Tab']},{'name':'open-opener-menu','argv':['-M','shift','-k','F10','-m','shift']},{'name':'close-shell','argv':CLOSE_ARGV}]
def menu_journey_mode(packet):
    require(packet.get('journey')=='ui011-focus-scope-opener-closure'and observed_producer_mode(packet),'fixed UI011 actual observation journey required')
    return True

def menu_journey_witness(step,pair,binding,runtime_binding,window,origin):
    """Scheduling only. Pixels and source-bound live lifecycle remain separate evidence."""
    try:
        names=[row['name'] for row in MENU_STEPS]
        if step not in names:return None
        index=names.index(step)
        if (index==0 and origin is not None) or (index>0 and (not isinstance(origin,dict) or origin['stepIndex']!=index-1)):return None
        keyboard_fixture.validate_phase_pair(pair,binding)
        bar,popup=(pair[role]['snapshot'] for role in ('bar','popup'))
        if any(snap['root'] is None or snap['retained'] is not None or snap['query'] is not None or snap['root']['loading']!='false' for snap in (bar,popup)):return None
        lease=(0,0,1,1,1,1,1,2,2)[index]
        if binding['expectedLease']!=lease or any(int(snap['root']['lease'])!=lease for snap in (bar,popup)):return None
        if bar['root']['mode'] is not None or bar['root']['pub']!=popup['root']['pub']:return None
        publication=int(bar['root']['pub'])
        if origin is not None and index in (2,6,7,8) and publication<=origin['publication']:return None
        counters={key:runtime_binding[key] for key in ('lifetime','session','frontend')}
        for value in counters.values():keyboard_fixture._phase_decimal(value,1)
        host=json.dumps(counters,separators=(',',':'))
        app_id=window.get('class')
        if not isinstance(app_id,str) or not app_id or len(app_id)>256:return None
        group_key='observed:application:'+app_id
        identity='bar:group:'+group_key
        controls=bar['controls']
        if len({row['control']for row in controls})!=len(controls):return None
        groups=[row for row in controls if row['control'].startswith('bar:group:')]
        if len(groups)!=1 or groups[0]['control']!=identity:return None
        group=groups[0]
        def eligible(row):
            return row['tag']=='BUTTON' and row['disabled'] is False and row['ariaDisabled']=='false' and row['focusOnly']=='false'
        if not eligible(group):return None
        matched=re.fullmatch(re.escape('group:observed:'+host+':')+r'([1-9][0-9]{0,19}):([1-9][0-9]{0,19}):'+re.escape(group_key),group['id'])
        if matched is None:return None
        owner,revision=matched.groups();keyboard_fixture._phase_decimal(owner,1);keyboard_fixture._phase_decimal(revision,1)
        if owner!=counters['frontend']:return None
        opener=[row for row in controls if row['control']=='bar:applications']
        if len(opener)!=1:return None
        presentation_match=re.fullmatch(re.escape('applications:'+host+':')+r'([1-9][0-9]{0,19}):control:opener',opener[0]['id'])
        if presentation_match is None:return None
        presentation=presentation_match.group(1);keyboard_fixture._phase_decimal(presentation,1)
        if origin is not None:
            if origin['identity']!=identity or origin['owner']!=owner or origin['presentation']!=presentation:return None
            expected_revision=origin['revision']+(1 if index in (6,8) else 0)
            if int(revision)!=expected_revision:return None
        def focused(snap,row):
            return snap['documentFocused'] is True and snap['active']=={key:row[key] for key in ('tag','id','control')}
        opened=index in (2,3,4,5,7)
        menu_id=None if origin is None else origin['menuId']
        if opened:
            if popup['root']['mode']!='menu' or bar['documentFocused'] is not False:return None
            rows=popup['controls'];ready=[row for row in rows if eligible(row)]
            if [row['control'] for row in ready]!=['control:menu-close','control:observation-refresh']:return None
            if len({row['control']for row in rows})!=len(rows):return None
            if any(row['focusOnly']!='false' for row in rows):return None
            if any(row not in ready and (row['disabled'] is not True or row['ariaDisabled']!='true') for row in rows):return None
            close_match=re.fullmatch(r'menu:([1-9][0-9]{0,9}):close',ready[0]['id'])
            if close_match is None:return None
            current_menu=int(close_match.group(1))
            if current_menu>2147483647 or ready[1]['id']!='menu:'+str(current_menu)+':refresh':return None
            if index==2:menu_id=current_menu
            elif current_menu!=menu_id+(1 if index==7 else 0):return None
            menu_id=current_menu
            if not focused(popup,ready[1 if index in (3,5) else 0]):return None
        else:
            if popup['root']['mode']!='closed' or popup['controls']!=[] or popup['documentFocused'] is not False:return None
            if index==0:
                ready=[row for row in controls if eligible(row)]
                if not ready or ready[0]!=group:return None
                if any(eligible(row) and (row['control'].startswith('bar:pin:') or row['control'] in ('bar:recovery-refresh','bar:workspace-refresh','bar:reconnect','bar:refresh-windows','bar:pins-summary')) for row in controls):return None
                if bar['documentFocused'] is not True or bar['active']!={'tag':'BODY','id':'','control':None}:return None
            elif not focused(bar,group):return None
        return {'stepIndex':index,'identity':identity,'owner':owner,'presentation':presentation,
                'revision':int(revision),'publication':publication,'menuId':menu_id,
                'groupDomId':group['id'],'phaseSchedulingOnly':True}
    except (KeyError,TypeError,ValueError,OverflowError):return None


class _ObserverCloseSnapshots:
    """Finite scheduling evidence from the exact live owner's held backing root."""
    def __init__(self,backend,backend_birth,window,window_birth,assets,clock,current,same_window,held,receipt,runtime_binding,journey=False):
        if not isinstance(backend,subprocess.Popen)or backend.poll()is not None:
            raise ValueError('retained live backend Popen required for phase discovery')
        self.backend=backend;self.backend_birth=backend_birth;self.window=window
        self.window_birth=window_birth;self.assets=assets;self.clock=clock
        self.current=current;self.same_window=same_window;self.held=held;self.receipt=receipt
        self.root_fd=None;self.role_fds={};self.role_pins={};self.sequence=0;self.ready=None
        self.runtime_binding=runtime_binding
        self.journey=journey;self.journey_origin=None;self.journey_step=0
        self.minimum_publication={'bar':1,'popup':1}
        self.application_lease=0  # SurfaceController.initial; opening notifications increments, DND updates and dismissal do not.
        try:
            self.current();self.same_window();self.held.attest()
            self.phase_library,self.rename_request=phase_renameat2()
            candidates=[];cursor=window['pid'];reached=False
            for _ in range(12):
                left(clock);start,parent=birth(cursor)
                if cursor==window['pid']and start!=window_birth:raise ValueError('phase GUI birth differs')
                if cursor==backend.pid and start!=backend_birth:raise ValueError('phase backend birth differs')
                image=Path('/proc',str(cursor),'exe').resolve()
                owner_image=digest(regular(image,256*1024*1024))==assets['owner']['sha256']
                if owner_image:
                    table=Path('/proc',str(cursor),'fd');entries=list(table.iterdir())
                    if len(entries)>256:raise ValueError('owner descriptor table exceeds phase bound')
                    for entry in entries:
                        if not entry.name.isdecimal():continue
                        try:path=os.readlink(entry)
                        except FileNotFoundError:continue
                        if re.fullmatch('/tmp/warlock-ui-backing-[0-9a-f]{64}',path)is None:continue
                        source=os.stat(entry);named=os.lstat(path)
                        self._private_dir(source);self._private_dir(named)
                        if self._pin(source)!=self._pin(named):raise ValueError('held phase root differs from named root')
                        candidates.append((cursor,start,entry.name,path,self._pin(source)))
                if cursor==backend.pid:reached=True;break
                if parent<=1 or parent==cursor:break
                cursor=parent
            if not reached:raise ValueError('phase discovery escaped retained backend ancestry')
            identities={(x[3],x[4])for x in candidates}
            if len(identities)!=1:raise ValueError('exactly one live owned held backing root required')
            self.parent_pid,self.parent_birth,self.parent_fd,self.path,self.root_pin=candidates[0]
            self.root_fd=os.open(self.path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
            if self._pin(os.fstat(self.root_fd))!=self.root_pin:raise ValueError('phase root changed during open')
            for role in ('bar','popup'):
                fd=os.open(role,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=self.root_fd)
                self.role_fds[role]=fd;status=os.fstat(fd);self._private_dir(status)
                if status.st_dev!=self.root_pin[0]:raise ValueError('phase role device differs')
                self.role_pins[role]=self._pin(status)
            status=regular(Path('/proc',str(window['pid']),'status'),1024*1024).decode('ascii')
            namespace_rows=[line.split(':',1)[1].split()for line in status.splitlines()if line.startswith('NSpid:')]
            if len(namespace_rows)!=1 or len(namespace_rows[0])<2:raise ValueError('held GUI PID namespace identity unavailable')
            self.owner_pid=namespace_rows[0][-1]
            if not self.owner_pid.isdecimal()or int(self.owner_pid)<1:raise ValueError('invalid held namespace PID')
            receipt['phaseChannel']={'status':'live-descriptor-bound','path':self.path,
                'parentPid':self.parent_pid,'parentStartTicks':self.parent_birth,'parentFd':self.parent_fd,
                'root':self._root_binding(),'ownerNamespacePid':self.owner_pid,'originalDeadlineNs':clock['deadline'],
                'acceptanceAuthority':False}
            receipt['phaseObservations']=[];self.attest()
        except BaseException:
            self.close();raise
    @staticmethod
    def _pin(status):return (status.st_dev,status.st_ino,status.st_uid)
    @staticmethod
    def _private_dir(status):
        if not stat.S_ISDIR(status.st_mode)or stat.S_IMODE(status.st_mode)!=0o700 or status.st_uid!=os.getuid():
            raise ValueError('private nonsymlink phase directory required')
    def _root_binding(self):return dict(zip(('device','inode','owner'),map(str,self.root_pin)))
    def attest(self):
        self.current();self.held.attest();self.same_window()
        if (self.backend.poll()is not None or birth(self.backend.pid)[0]!=self.backend_birth
                or birth(self.window['pid'])[0]!=self.window_birth
                or not descendant(self.window['pid'],self.backend.pid,self.backend_birth)
                or birth(self.parent_pid)[0]!=self.parent_birth
                or not descendant(self.window['pid'],self.parent_pid,self.parent_birth)):
            raise ValueError('phase process ancestry or birth changed')
        if digest(regular(Path('/proc',str(self.parent_pid),'exe').resolve(),256*1024*1024))!=self.assets['owner']['sha256']:
            raise ValueError('phase parent owner image changed')
        source=Path('/proc',str(self.parent_pid),'fd',self.parent_fd)
        if os.readlink(source)!=self.path:raise ValueError('held backing descriptor changed')
        for status in (os.stat(source),os.lstat(self.path),os.fstat(self.root_fd)):
            self._private_dir(status)
            if self._pin(status)!=self.root_pin:raise ValueError('phase root identity changed')
        for role,fd in self.role_fds.items():
            for status in (os.fstat(fd),os.stat(role,dir_fd=self.root_fd,follow_symlinks=False)):
                self._private_dir(status)
                if self._pin(status)!=self.role_pins[role]:raise ValueError('phase role identity changed')
        status=regular(Path('/proc',str(self.window['pid']),'status'),1024*1024).decode('ascii')
        rows=[line.split(':',1)[1].split()for line in status.splitlines()if line.startswith('NSpid:')]
        if len(rows)!=1 or not rows[0]or rows[0][-1]!=self.owner_pid:raise ValueError('phase owner namespace PID changed')
        left(self.clock)
    @staticmethod
    def _file_stamp(status):
        return tuple(getattr(status,k)for k in ('st_dev','st_ino','st_uid','st_gid','st_mode','st_nlink','st_size','st_mtime_ns','st_ctime_ns'))
    def _response(self,role,sequence):
        name='qa-phase-response-%02d.json'%sequence
        try:fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=self.role_fds[role])
        except FileNotFoundError:return None
        try:
            before=os.fstat(fd)
            if before.st_nlink==2:return None  # Link publication is not final until temporary-name unlink.
            if (not stat.S_ISREG(before.st_mode)or stat.S_IMODE(before.st_mode)!=0o600
                    or before.st_uid!=os.getuid()or before.st_dev!=self.root_pin[0]
                    or before.st_nlink!=1 or not 1<=before.st_size<=9216):
                raise ValueError('bounded immutable phase response required')
            raw=os.read(fd,9217);after=os.fstat(fd)
            named=os.stat(name,dir_fd=self.role_fds[role],follow_symlinks=False)
            if len(raw)!=before.st_size or self._file_stamp(before)!=self._file_stamp(after) or self._pin(named)!=self._pin(before)or named.st_nlink!=1:
                raise ValueError('phase response changed during bounded read')
            value=json.loads(raw.decode('utf-8'),object_pairs_hook=unique,
                parse_constant=lambda value:(_ for _ in ()).throw(ValueError('nonfinite phase JSON')))
            return value,{'role':role,'file':name,'sha256':digest(raw),'device':str(before.st_dev),'inode':str(before.st_ino)}
        finally:os.close(fd)
    def await_phase(self,step):
        expected=MENU_STEPS[self.journey_step]['name'] if self.journey and self.journey_step<len(MENU_STEPS) else ('close-gui' if not self.journey else None)
        if step!=expected or self.ready is not None:raise ValueError('invalid or unconsumed phase request')
        while self.sequence<keyboard_fixture.PHASE_LIMIT:
            self.attest();self.sequence+=1;sequence=self.sequence;nonce=os.getrandom(32,os.GRND_NONBLOCK).hex()
            if len(nonce)!=64:raise ValueError('complete nonblocking phase nonce required')
            issued=time.monotonic_ns();requests={}
            for role,dirfd in self.role_fds.items():
                left(self.clock);name='qa-phase-request-%02d'%sequence
                temporary='.qa-phase-request-%02d.tmp'%sequence
                fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=dirfd)
                try:
                    raw=(nonce+'\n').encode('ascii')
                    if os.write(fd,raw)!=65:raise ValueError('incomplete immutable phase request')
                    status=os.fstat(fd)
                    if (not stat.S_ISREG(status.st_mode)or status.st_nlink!=1 or stat.S_IMODE(status.st_mode)!=0o600
                            or status.st_uid!=os.getuid()or status.st_dev!=self.root_pin[0]or status.st_size!=65):
                        raise ValueError('phase request file identity differs')
                    requests[role]={'device':str(status.st_dev),'inode':str(status.st_ino)}
                finally:os.close(fd)
                left(self.clock)
                phase_publish_request(self.rename_request,dirfd,sequence)
                named=os.stat(name,dir_fd=dirfd,follow_symlinks=False)
                if (self._pin(named)!=self._pin(status)or named.st_size!=65 or named.st_mode!=status.st_mode or named.st_nlink!=1):
                    raise ValueError('published phase request identity differs')
                left(self.clock)
            pair={};files=[]
            while len(pair)!=2:
                self.current();self.held.attest()
                if self.backend.poll()is not None:raise ValueError('backend exited while phase snapshot pending')
                for role in ('bar','popup'):
                    if role in pair:continue
                    found=self._response(role,sequence)
                    if found is not None:pair[role]=found[0];files.append(found[1])
                left(self.clock)
            self.attest();binding={'seq':sequence,'nonce':nonce,'root':self._root_binding(),
                'requests':requests,'ownerPid':self.owner_pid,'issuedNs':issued,
                'deadlineNs':self.clock['deadline'],'nowNs':time.monotonic_ns(),
                'minimumPublication':dict(self.minimum_publication),
                'expectedLease':((0,0,1,1,1,1,1,2,2)[self.journey_step] if self.journey else self.application_lease+(1 if step in ('traverse-dnd','dismiss-again')else 0))}
            keyboard_fixture.validate_phase_pair(pair,binding)
            observed=menu_journey_witness(step,pair,binding,self.runtime_binding,self.window,self.journey_origin) if self.journey else None
            matched=(observed is not None) if self.journey else close_ready_matches(pair,binding,self.runtime_binding)
            self.receipt['phaseObservations'].append({'beforeStep':step,'binding':binding,'responses':pair,
                'files':files,'phaseComplete':matched,'originalAcceptance':False})
            if matched:
                self.minimum_publication={role:int(pair[role]['snapshot']['root']['pub'])for role in ('bar','popup')}
                self.application_lease=binding['expectedLease']
                if self.journey:self.journey_origin=observed
                self.ready=step;return
        raise ValueError('finite phase snapshot budget exhausted before '+step)
    def consume(self,step):
        if self.ready!=step:raise ValueError('fresh phase completion required before next key')
        self.ready=None;self.attest();left(self.clock)
        if self.journey:self.journey_step+=1
    def close(self):
        errors=[]
        for fd in list(self.role_fds.values())+([self.root_fd]if self.root_fd is not None else []):
            try:os.close(fd)
            except OSError as exc:errors.append(str(exc))
        self.role_fds={};self.root_fd=None
        return {'status':'closed'if not errors else'unknown','errors':errors,'cleanupAuthority':False}

def require(value,message):
    if not value:raise ValueError(message)


def load_helper(relative,name):
    path=ROOT/relative;expected=HELPERS[relative]
    require(digest(regular(path))==expected,'reviewed helper changed: '+relative)
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module)
    require(digest(regular(path))==expected,'helper changed during import')
    return module


def json_ref(reference,cap=32*1024*1024):
    return json.loads(pinned(reference,cap),object_pairs_hook=unique)


def canonical(value):
    return digest(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())


def observed_producer_mode(packet):
    if 'producerMode' not in packet:return False
    require(packet['producerMode']=='observed-window-read','only explicit read-only observed producer mode')
    return True


def observed_producer_config(original,endpoint,binding,clock):
    # Metadata adapter only. Actual SO_PEERCRED/ancestry/executable validation is
    # performed by EndpointLease.capture and again by the production owner.
    require(isinstance(original,dict) and original.get('binding')==binding
        and original.get('deadlineMonotonicNs')==str(clock['deadline'])
        and original.get('applicationAttachment') is True
        and 'compositorObservation' not in original,'exact original producer binding/deadline/attachment required')
    require(isinstance(endpoint,dict) and set(endpoint)=={'bootId','ancestors','name','socket','processes','executable','generation'}
        and endpoint['generation']==binding['frontend'],'selected endpoint must match actual full binding')
    result=copy.deepcopy(original)
    # Production derives generation from binding.frontend; no caller counter.
    result['compositorObservation']={name:copy.deepcopy(value) for name,value in endpoint.items() if name!='generation'}
    require(len((json.dumps(result,indent=2)+'\n').encode())<=65536,'producer configuration bound')
    return result


def require_current_documents(packet,report,current_sources):
    require(report.get('passed') is True and report.get('nativeAcceptance') is False,
            'actual successful source-bound document build required')
    if report.get('currentDocumentProvenance')=='installed-current-source':
        require(report.get('candidateOnly') is False and report.get('liveSourcesAdopted') is True
            and report.get('qualificationVariant') is None,'installed-source provenance cannot relabel private candidate')
        prefix='implementation/warlock/src/'
        compiled={name[len(prefix):]:pin for name,pin in report.get('sources',{}).items() if name.startswith(prefix)}
        require(compiled==current_sources,'actual installed-source compilation map differs')
    else:
        require(report.get('qualificationVariant')=='candidate' and report.get('candidateOnly') is True
            and report.get('candidateElmSources')==current_sources,'actual private candidate document compilation map differs')
    require(report.get('currentDocumentSourceHashes')==current_sources,
            'all current Elm sources must match actual compiled documents')
    documents=report.get('currentHttpDocuments',{})
    require(set(documents)=={'controller','bar','popup'},'exact current HttpMain/HttpBar/HttpPopup documents required')
    for role in ('controller','bar','popup'):
        selected=documents[role];origin=packet['assetSources'][role]
        require(origin['report']==packet['documentBuildReport'] and origin['selector']==['currentHttpDocuments',role],
            'document selector must refer to actual current compilation')
        require(packet['assets'][role]=={'path':selected['path'],'sha256':selected['sha256']}
            and origin['mode']==selected['mode'],'current document asset differs')


def parse_packet(value):
    fields={'schema','kind','armed','recordPath','recordIdentitySha256','selectionGeneration','authorization',
      'sourceHashes','guardHashes','assets','assetSources','buildReport','foundationPacket','foundationReport',
      'reuse','reviews','input','binding','contract','processInventory','abi','keyboardBuildReport','documentBuildReport','documentFixtureOnly','openerBuildReport','atTransportReport','atProviderPins'}
    if isinstance(value,dict) and 'producerMode' in value:fields.add('producerMode')
    if isinstance(value,dict) and 'journey' in value:fields.add('journey')
    require(isinstance(value,dict) and set(value)==fields,'exact fixed packet fields required')
    observed=observed_producer_mode(value);journey=menu_journey_mode(value)
    require(type(value['schema']) is int and value['schema']==1 and value['kind']=='ui011-original-opener-closure' and value['armed'] is True,'unarmed or wrong fixed packet')
    require(value['recordPath']==RECORD and value['recordIdentitySha256']==IDENTITY and type(value['selectionGeneration']) is int and value['selectionGeneration']>0,'current participant required')
    require(isinstance(value['sourceHashes'],dict) and set(HELPERS)<=set(value['sourceHashes']) and str(SELF.relative_to(ROOT)) in value['sourceHashes'],'complete helper/source membership required')
    require(all(value['sourceHashes'].get(name)==pin for name,pin in HELPERS.items()),'static helper pin differs from packet')
    require(set(value['assets'])==ASSETS and set(value['assetSources'])==ASSETS-{'nestedConfig'},'exact fixed assets required')
    require(set(value['reviews'])==REVIEWS,'three existing scoped readiness roles required')
    require(value['documentFixtureOnly'] is (not observed),'historical and current-document modes must remain distinct')
    require(isinstance(value['processInventory'],dict) and 1<=len(value['processInventory'])<=20000,'bounded reviewed process mapping inventory required')
    fixed_input={'monitorSize':[1280,720],'windowSize':[980,680],'closeArgv':CLOSE_ARGV,'pointer':False,'frameLimit':16}
    if journey:fixed_input.update(transactions=UI011_TRANSACTIONS,maximumKeyboardTransactions=4,openerDefaultSize=[320,180])
    require(value['input']==fixed_input,'fixed geometry/close/input bounds required')
    bound=value['binding'];require(isinstance(bound,dict) and set(bound)=={'lifetime','session','frontend'},'fixed binding required')
    require(all(isinstance(v,str) and re.fullmatch('[1-9][0-9]{0,19}',v) and int(v)<=2**64-1 for v in bound.values()),'positive UInt64 binding required')
    return value


def selected_image(packet,role,current):
    origin=packet['assetSources'][role]
    require(isinstance(origin,dict) and set(origin)=={'report','selector','mode'},'exact image source selector required')
    value=json_ref(origin['report'])
    require(isinstance(origin['selector'],list) and 1<=len(origin['selector'])<=6,'bounded image source selector required')
    for part in origin['selector']:
        require(isinstance(part,str) and isinstance(value,dict) and part in value,'image source selector differs');value=value[part]
    asset=packet['assets'][role]
    if role in SYSTEM_ASSETS:
        require(asset['path']==SYSTEM_ASSETS[role] and isinstance(value,dict) and value.get('sha256')==asset['sha256'] and value.get('mode')==origin['mode'],'exact selected system inventory asset required')
        observed=boot_correspondence.regular_identity(asset['path'])
        require(observed['sha256']==asset['sha256'] and observed['mode']==origin['mode'] and origin['mode']&0o111 and not origin['mode']&0o6022,'system executable mode/body drift')
        return value
    require(value.get('path')==asset['path'] and value.get('sha256')==asset['sha256'],'selected image differs from source report')
    if asset['path'] in current.check()['regularArtifacts']:
        observed=current.regular(value,origin['report'])
    else:
        observed=boot_correspondence.regular_identity(asset['path'])
        require(all(int(value[k])==observed[k] for k in ('device','inode','size')),'fresh image physical identity differs')
        require(observed['sha256']==asset['sha256'],'fresh image bytes differ')
    require(type(origin['mode']) is int and observed['mode']==origin['mode'] and not origin['mode']&0o022,'source image mode differs')
    if role not in {'controller','bar','popup'}:require(origin['mode']&0o111 and not origin['mode']&0o6000,'nonexecutable/set-id asset')
    return value


def canonical_prerequisite(reference):
    """Same file/hash represented for core's repository-relative reference API."""
    require(isinstance(reference,dict) and set(reference)=={'path','sha256'},'exact readiness reference required')
    path=Path(reference['path'])
    require(path.is_absolute() and '..' not in path.parts and path.resolve()==path,'canonical absolute readiness reference required')
    try:relative=path.relative_to(ROOT)
    except ValueError as exc:raise ValueError('readiness reference outside repository') from exc
    require(relative.parts and isinstance(reference['sha256'],str) and re.fullmatch('[0-9a-f]{64}',reference['sha256']),'exact readiness hash required')
    return {'path':str(relative),'sha256':reference['sha256']}


def preflight(expected):
    require(re.fullmatch('[0-9a-f]{64}',expected) is not None,'packet SHA required')
    require(digest(regular(PACKET))==expected,'fixed packet hash differs')
    packet=parse_packet(json.loads(regular(PACKET),object_pairs_hook=unique))
    for name,pin in {**packet['sourceHashes'],**packet['guardHashes'],**HELPERS}.items():
        require(isinstance(name,str) and not Path(name).is_absolute() and '..' not in Path(name).parts,'source escaped repository')
        require(isinstance(pin,str) and re.fullmatch('[0-9a-f]{64}',pin) and digest(regular(ROOT/name,64*1024*1024))==pin,'source/guard drift: '+name)
    require(packet['contract']['sha256']==CONTRACT_SHA,'fixed Main wire contract differs');json_ref(packet['contract'])
    for ref in packet['assets'].values():pinned(ref,256*1024*1024)
    global attempt_auth,boot_correspondence,owned_fonts,keyboard_fixture,geometry
    attempt_auth=load_helper('tools/ui011_foreign_toplevel_attempt_authorization.py','connected_authorization')
    boot_correspondence=load_helper('tools/ux023_current_boot_correspondence.py','connected_boot')
    owned_fonts=load_helper('tools/ux003_owned_fonts.py','connected_fonts')
    keyboard_fixture=load_helper('tools/ux023_notifications_keyboard_fixture.py','connected_keyboard')
    geometry=load_helper('tools/ux003_input_geometry_720.py','connected_geometry')
    core=load_helper('plugins/warlock-contributor/scripts/warlock.py','connected_core')
    record=json.loads(regular(ROOT/RECORD,32*1024*1024),object_pairs_hook=unique);record['_recordPath']=RECORD
    reqs,state=core.context(ROOT);core.current_selection(record,state,packet['selectionGeneration'])
    history=core.delivery_state(ROOT,record,reqs);candidate=history['candidate']
    core.validate_delivery_candidate(ROOT,record,candidate,current=True)
    expected_argv=['/usr/bin/python3','-B',str(ROOT/'window-integration-qa/qa_run.py'),'--','/usr/bin/python3','-B',str(SELF),'--sha256',expected]
    require(candidate['scope']=='native' and candidate['argv']==expected_argv and candidate['manifest']['profiles'].get(str(PACKET.relative_to(ROOT)))==expected,'not current canonical fixed native candidate')
    require(all(packet['sourceHashes'].get(n)==v for n,v in candidate['manifest']['sources'].items()),'owned product source map differs')
    require(packet['guardHashes']==core.effective_delivery_guards(record),'original guards differ')
    for role,reference in packet['reviews'].items():
        review=json_ref(reference)
        require(review.get('schema')==1 and review.get('disposition')=='accepted' and review.get('scope')=='ui011-original-opener-closure' and review.get('role')==role,'scoped readiness missing')
        require(all(review.get(key)==packet[key] for key in ('recordPath','recordIdentitySha256','selectionGeneration','sourceHashes','guardHashes','assets','assetSources','input','binding','foundationPacket','foundationReport','reuse','buildReport','documentBuildReport','keyboardBuildReport','abi','contract','processInventory','documentFixtureOnly','authorization','openerBuildReport','atTransportReport','atProviderPins')) and review.get('componentOnly') is True,'readiness does not bind actual component tuple')
        require(review.get('producerMode')==packet.get('producerMode'),'readiness must bind explicit producer mode')
        require(review.get('journey')==packet.get('journey'),'readiness must bind original journey mode')
        require(canonical_prerequisite(reference) in candidate['nativePrerequisites'],'readiness not canonical prerequisite')
    authority=attempt_auth.resolve_authorization(packet['authorization'],record,IDENTITY,packet['selectionGeneration'],core)
    current=boot_correspondence.CurrentBoot(packet['reuse']['currentBootCorrespondence'],pinned)
    build=json_ref(packet['buildReport']);require(build.get('passed') is True,'fresh two-target build not qualified')
    require(all(packet['sourceHashes'].get(n)==v for n,v in build['sourceHashes'].items()),'compiled source closure differs')
    for role,name in [('owner','warlock-ui-owner'),('controls','ui-webkit-controls')]:
        image=build['compiledImages'][name];require(packet['assets'][role]=={'path':image['path'],'sha256':image['sha256']},'fresh compiled image differs')
        require(packet['assetSources'][role]['report']==packet['buildReport'] and packet['assetSources'][role]['selector']==['compiledImages',name],'fresh image selector differs')
    opener_build=json_ref(packet['openerBuildReport'])
    require(all(packet['sourceHashes'].get(n)==v for n,v in opener_build['sourceHashes'].items()),'current opener compiled source closure differs')
    require(opener_build.get('openerAdmission',{}).get('passed')is True and opener_build['openerAdmission'].get('contractCount')==22 and opener_build['openerAdmission'].get('seedCount')==32,'actual opener admission22/32 required')
    image=opener_build['compiledImages']['ui011-opener-fixture'];require(packet['assets']['opener']=={'path':image['path'],'sha256':image['sha256']}and packet['assetSources']['opener']['report']==packet['openerBuildReport']and packet['assetSources']['opener']['selector']==['compiledImages','ui011-opener-fixture'],'actual fresh opener build source required')
    transport=json_ref(packet['atTransportReport'])
    transport_result=transport.get('atTransport',{})
    require(transport.get('passed')is True and transport_result.get('classification')=='component-pass'and transport_result.get('caseCount')==18 and transport_result.get('seedCount')==32 and len(transport_result.get('checks',[]))==18 and all(v.get('passed')is True for v in transport_result['checks'])and [v.get('seed')for v in transport_result.get('seeded',[])]==list(range(32))and all(v.get('passed')is True for v in transport_result['seeded']),'actual selected AT product transport18/32 qualification required before original journey')
    require(all(packet['sourceHashes'].get(n)==v for n,v in transport['sourceHashes'].items()),'current AT transport source closure differs')
    require(isinstance(packet['atProviderPins'],dict)and set(packet['atProviderPins'])=={'/usr/bin/dbus-daemon','/usr/lib/at-spi2-registryd','/usr/lib/webkitgtk-6.0/WebKitWebProcess','/usr/bin/xdg-dbus-proxy'},'exact source-bound four AT provider images required')
    for path,pin in packet['atProviderPins'].items():require(packet['processInventory'].get(path)==pin and digest(regular(path,256*1024*1024))==pin,'AT provider/mapping source pin differs')
    for role in packet['assetSources']:selected_image(packet,role,current)
    keyboard_build=json_ref(packet['keyboardBuildReport']);require(keyboard_build.get('passed') is True,'keyboard source build not qualified')
    require(packet['assetSources']['keyboardSeat']['report']==packet['keyboardBuildReport'],'keyboard image source report differs')
    keyboard_fixture.keyboard_build_binding(packet,current.keyboard_view(packet,keyboard_build))
    documents=json_ref(packet['documentBuildReport']);require(documents.get('passed') is True,'document fixture build not qualified')
    if observed_producer_mode(packet):
        source_root=ROOT/'implementation/warlock/src'
        current_sources={str(path.relative_to(source_root)):digest(regular(path)) for path in source_root.rglob('*.elm')}
        require_current_documents(packet,documents,current_sources)
        require(json_ref(packet['assetSources']['recorder']['report']).get('passed') is True,'retained recorder build qualification required')
    else:
        require(all(packet['assetSources'][role]['report']==packet['documentBuildReport'] for role in ('controller','bar','popup','recorder')),'document fixture source reports differ')
    abi=json_ref(packet['abi']);pinned(abi['library'],64*1024*1024)
    for path,pin in abi['headers'].items():require(digest(regular(path))==pin,'compiled ABI header drift')
    require(packet['processInventory'].get(abi['library']['path'])==abi['library']['sha256'],'selected libwayland mapping absent')
    for path,pin in packet['processInventory'].items():
        require(Path(path).is_absolute() and isinstance(pin,str) and re.fullmatch('[0-9a-f]{64}',pin),'mapping inventory malformed')
        require(digest(regular(path,256*1024*1024))==pin,'mapping inventory drift')
    collector=load_helper('tools/run_labwc_gl_foundation_window_rule_20261108.py','connected_collector')
    old_base=load_helper('tools/run_arm_gl_foundation_renewed_20261108_0623.py','connected_primitives')
    base=attempt_auth.effect_base(old_base,authority)
    historical=json_ref(packet['foundationPacket']);collector.packet_shape(historical)
    report=json_ref(packet['foundationReport'])
    require(report.get('packetSha256')==packet['foundationPacket']['sha256'] and report.get('forcedCleanup') is False and all(report.get(k) is True for k in ('passed','hostObserved','nestedObserved','outputModeObserved','cleanup')),'qualified owned stack basis missing')
    validate_generated_foundation_basis(historical,report)
    foundation=boot_correspondence.derive_schema(packet,historical,derive_live_font_stack(packet,historical,packet['reuse']),packet['reuse'],pinned)
    require(foundation['nested']['compositor']==packet['assets']['compositor']['path'],'different selected nested compositor')
    cursor_reference=packet['reuse'].get('currentCursorCorrespondence')
    live_nested=boot_correspondence.cursor_inputs(current,foundation['nested'],cursor_reference)
    for inventory in (foundation['hostInputs'],live_nested):
        for path,pin in inventory.items():base.regular(path,pin)
    boot_correspondence.verify_graphics(current,base,foundation['graphics'],foundation['hostInputs'])
    boot_correspondence.verify_build(current,collector,base,foundation)
    boot_correspondence.verify_private_provider(current,collector,base,foundation['nested'],packet['reuse']['providerSourceCorrespondence'],cursor_reference)
    require(digest(pinned(packet['assets']['nestedConfig']))==collector.NESTED_LUA_SHA,'fixed nested config differs')
    qa=load_helper('window-integration-qa/qa_launch.py','connected_scope')
    stage=load_helper('tools/omarchy_ui_mvp.py','connected_stage')
    return dict(packet=packet,core=core,authority=authority,current=current,collector=collector,base=base,foundation=foundation,qa=qa,stage=stage,abi=abi)


class EndpointLease:
    """Capture only actual held components and retained nested Popen, never report PIDs."""
    def __init__(self,stack,clock):self.stack=stack;self.clock=clock;self.fds=[]
    def directory_chain(self,path):
        path=Path(path);require(path.resolve()==path,'canonical endpoint directory required')
        fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);self.fds.append(fd)
        def row(path,s):return dict(path=str(path),device=str(s.st_dev),inode=str(s.st_ino),uid=str(s.st_uid),mode=str(stat.S_IMODE(s.st_mode)))
        rows=[row(Path('/'),os.fstat(fd))];current=Path('/')
        for part in path.parts[1:]:
            left(self.clock);fd=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=fd);self.fds.append(fd)
            current=current/part;s=os.fstat(fd);require(stat.S_ISDIR(s.st_mode) and not s.st_mode&0o022,'unsafe endpoint ancestor')
            require((s.st_dev,s.st_ino)==(current.lstat().st_dev,current.lstat().st_ino),'endpoint ancestor replaced');rows.append(row(current,s))
        return rows
    def capture(self,binding):
        stack=self.stack;stack.current();socket_path=stack.nested_socket
        ancestors=self.directory_chain(socket_path.parent);a=socket_path.lstat();require(stat.S_ISSOCK(a.st_mode),'selected nested socket absent')
        with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as client:
            client.settimeout(left(self.clock)/1e9);client.connect(str(socket_path))
            peer=struct.unpack('3i',client.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
        require(peer==(stack.nested.pid,os.getuid(),os.getgid()),'actual nested socket peer differs')
        processes=[]
        for pid in (stack.nested.pid,os.getpid()):
            left(self.clock);ticks,parent=birth(pid);s=Path('/proc',str(pid)).stat()
            processes.append(dict(pid=str(pid),birth=ticks,parent=str(parent),uid=str(s.st_uid),gid=str(s.st_gid)))
        require(processes[0]['birth']==stack.nested_birth and processes[0]['parent']==processes[1]['pid'],'retained nested ancestry differs')
        executable=Path('/proc',str(stack.nested.pid),'exe').resolve(strict=True)
        expected=stack.p['nested']['compositor'];require(str(executable)==expected,'retained nested executable pathname differs')
        directories=self.directory_chain(executable.parent);s=executable.lstat();require(stat.S_ISREG(s.st_mode) and s.st_size<=64*1024*1024,'selected executable exceeds fixed bound')
        pins=[dict(path=row['path'],device=row['device'],inode=row['inode'],kind='directory') for row in directories[1:]]
        pins.append(dict(path=str(executable),device=str(s.st_dev),inode=str(s.st_ino),kind='regular'))
        after=socket_path.lstat();require((a.st_dev,a.st_ino)==(after.st_dev,after.st_ino),'selected socket replaced')
        require(digest(regular(executable,64*1024*1024))==stack.p['nested']['inputs'][expected],'selected executable bytes differ')
        stack.current()
        return dict(bootId=self.clock['boot'],ancestors=ancestors,name=socket_path.name,
          socket=dict(device=str(a.st_dev),inode=str(a.st_ino),uid=str(a.st_uid),mode=str(stat.S_IMODE(a.st_mode))),processes=processes,
          executable=dict(root={k:directories[0][k] for k in ('device','inode')},pins=pins,path=str(executable.relative_to('/')),size=str(s.st_size),sha256=stack.p['nested']['inputs'][expected]),generation=binding['frontend'])
    def close(self):
        failures=[];retained=[]
        for fd in reversed(self.fds):
            try:os.close(fd)
            except OSError as exc:failures.append(type(exc).__name__);retained.append(fd)
        self.fds=list(reversed(retained));return {'closed':not failures,'errors':failures}


def phase_response(value,phase,sequence,nonce,binding):
    fields={'schema','nonce','sequence','phase','binding','configChecks','nativeAcceptance','readsPerformed','rows'}
    require(isinstance(value,dict) and set(value)==fields and type(value['schema']) is int and value['schema']==1 and value['phase']==phase and type(value['sequence']) is int and value['sequence']==sequence,'fixed phase response differs')
    require(value['nonce']==nonce and value['binding']==binding and type(value['configChecks']) is int and value['configChecks']==15 and value['nativeAcceptance'] is False,'phase scope/config correspondence differs')
    require(type(value['readsPerformed']) is int and 1<=value['readsPerformed']<=(1 if phase=='READ_INITIAL' else 16) and isinstance(value['rows'],list) and len(value['rows'])<=256,'bounded actual snapshot required')
    for row in value['rows']:
        require(set(row)=={'handleOrdinal','identityScope','title','appId','states','outputOrdinals','parentOrdinal'},'row fields differ')
        require(row['identityScope']=='same-owner-QA-label-not-protocol-wire-id','wire identity misrepresented')
        require(isinstance(row['handleOrdinal'],str) and re.fullmatch('[1-9][0-9]{0,19}',row['handleOrdinal']),'actual opaque handle label missing')
        require(all(isinstance(row[k],str) and len(row[k].encode('utf-8'))<=1024 for k in ('title','appId')),'bounded actual title/appId required')
        require(isinstance(row['states'],list) and len(set(row['states']))==len(row['states']) and set(row['states'])<={'maximized','minimized','activated','fullscreen'},'actual state set differs')
        require(isinstance(row['outputOrdinals'],list) and len(row['outputOrdinals'])<=64 and len(set(row['outputOrdinals']))==len(row['outputOrdinals']) and all(isinstance(v,str) and re.fullmatch('[1-9][0-9]{0,19}',v) for v in row['outputOrdinals']),'actual output labels malformed')
        require(row['parentOrdinal'] is None,'singleton must not infer foreign parent')
    return value


def match_mapped(value,window):
    require(len(value['rows'])==1,'committed real window singleton absent')
    row=value['rows'][0]
    require(row['title']==window.get('title') and row['appId']==window.get('class'),'callback metadata differs from independently owned actual IPC window')
    return row


def terminal_response(value,nonce,binding):
    fields={'schema','nonce','sequence','phase','binding','configChecks','nativeAcceptance','completedPhases','actionPassed','status','passed','error'}
    require(isinstance(value,dict) and set(value)==fields and type(value['schema']) is int and value['schema']==1 and value['phase']=='RETIRE' and type(value['sequence']) is int and value['sequence']==4,'fixed terminal differs')
    require(value['nonce']==nonce and value['binding']==binding and value['configChecks']==15 and value['nativeAcceptance'] is False,'terminal source/config differs')
    require(value['status'] in ('Retired','RetainedUnknown'),'unknown retirement enum')
    require(value['completedPhases']==4 and value['actionPassed'] is True and value['status']=='Retired' and value['passed'] is True and value['error'] is None,'actual observer retirement unconfirmed')
    return value


class ObserverPipe:
    def __init__(self,proc,clock,nonce,binding,wire):
        self.proc=proc;self.clock=clock;self.nonce=nonce;self.binding=binding;self.sequence=0;self.buffer=b'';self.wire=wire;self.last_response=None
    def command(self,phase):
        expected=('READ_INITIAL','READ_WINDOW','READ_CLOSED','RETIRE')
        require(self.sequence<4 and phase==expected[self.sequence],'observer command order/replay refused')
        left(self.clock);require(self.proc.poll() is None,'observer exited before command')
        require(not self.buffer and not select.select([self.proc.stdout.fileno()],[],[],0)[0],'unsolicited observer bytes or EOF')
        self.sequence+=1;raw=(phase+'\n').encode();require(os.write(self.proc.stdin.fileno(),raw)==len(raw),'partial observer command, no replay')
        if phase=='RETIRE':self.proc.stdin.close();self.proc.stdin=None
        while b'\n' not in self.buffer:
            left(self.clock)
            readable,_,_=select.select([self.proc.stdout.fileno()],[],[],left(self.clock)/1e9)
            require(bool(readable),'observer response deadline exhausted')
            chunk=os.read(self.proc.stdout.fileno(),min(4096,262145-len(self.buffer)))
            require(bool(chunk),'observer EOF before fixed response');self.buffer+=chunk
            require(len(self.buffer)<=262144,'observer response cap exceeded')
        line,self.buffer=self.buffer.split(b'\n',1);require(not self.buffer,'extra observer response bytes')
        self.wire.write(line+b'\n');self.wire.flush()
        value=json.loads(line,object_pairs_hook=unique);self.last_response=value
        return terminal_response(value,self.nonce,self.binding) if phase=='RETIRE' else phase_response(value,phase,self.sequence,self.nonce,self.binding)
def wait_normal(proc,clock):
    proc.wait(timeout=left(clock)/1e9)
    require(proc.returncode==0 and input_group_absent(proc.pid),'actual normal child exit/group absence required')


def producer_observation(raw,clock,window,window_birth,namespace,owner_sha):
    value=json.loads(raw,object_pairs_hook=unique)
    require(value.get('schema')==1 and value.get('kind')=='ux003-backend-observation','actual public Backend observer receipt missing')
    require(value.get('backend',{}).get('passed') is True and value.get('backend',{}).get('cleanup') is True,'actual Backend result/retirement failed')
    require(value.get('application') is None and value.get('publishedLaunch') is None,'unexpected application launch')
    observed=(value.get('owner') or {}).get('engineObservation') or {};engine=observed.get('engine') or {}
    require(observed.get('deadlineMonotonicNs')==str(clock['deadline']) and engine.get('pid')==str(window['pid']) and engine.get('startTicks')==window_birth,'actual engine/run binding differs')
    require((engine.get('startupImage') or {}).get('sha256')==owner_sha and ((engine.get('lastLiveImage') or {}).get('image') or {}).get('sha256')==owner_sha,'engine startup/live image differs')
    require(engine.get('namespace')==namespace['engine'] and engine.get('parentNamespace')==namespace['parent'],'actual engine namespace differs')
    backing=(observed.get('backing') or {}).get('path')
    require(isinstance(backing,str) and re.fullmatch(r'/tmp/warlock-ui-backing-[0-9a-f]{64}',backing) and not Path(backing).exists() and not Path(backing).is_symlink(),'actual backing absence unproved')
    require(not Path('/proc',str(window['pid'])).exists(),'actual engine PID still present')
    return value



def deleted_map_family(rows):
    """Recognize only the observed diagnostic shape. This never qualifies a mapping."""
    deleted=[row for row in rows if isinstance(row.get('pathname'),str) and row['pathname'].endswith(' (deleted)')]
    if not deleted:
        return None
    if len(deleted)!=2:
        raise ValueError('diagnostic needs exactly two deleted rows')
    identities=set()
    addresses=set()
    for row in deleted:
        if (set(row)!={'address','permissions','offset','device','inode','pathname'}
                or re.fullmatch(r'/dev/shm/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12} \(deleted\)',row['pathname']) is None
                or row['permissions']!='r--p' or row['offset']!='00000000'
                or type(row['inode']) is not int or row['inode']<=0
                or re.fullmatch(r'[0-9a-f]+:[0-9a-f]+',row['device']) is None
                or re.fullmatch(r'[0-9a-f]+-[0-9a-f]+',row['address']) is None):
            raise ValueError('deleted row is outside the bounded diagnostic shape')
        start,end=(int(value,16)for value in row['address'].split('-'))
        if end-start!=12288 or start%4096 or end%4096 or row['address'] in addresses:
            raise ValueError('diagnostic range differs from observed two 12KiB maps')
        addresses.add(row['address'])
        identities.add((row['device'],row['inode'],row['pathname']))
    if len(identities)!=1:
        raise ValueError('diagnostic rows do not share one backing identity')
    device,inode,pathname=next(iter(identities))
    return dict(device=device,inode=inode,pathname=pathname,rows=deleted)


def feedback_wire_string(payload,offset=0):
    require(len(payload)>=offset+4,'truncated Wayland string')
    size=struct.unpack_from('<I',payload,offset)[0];end=offset+4+size;padded=offset+4+((size+3)&~3)
    require(1<=size<=256 and padded<=len(payload) and payload[end-1:end]==b'\0'
            and b'\0'not in payload[offset+4:end-1],'invalid bounded Wayland string')
    return payload[offset+4:end-1].decode('ascii'),padded


def feedback_wire_array(payload):
    require(len(payload)>=4,'truncated feedback array')
    size=struct.unpack_from('<I',payload)[0]
    require(size<=4096 and 4+((size+3)&~3)==len(payload),'feedback array bounds')
    return payload[4:4+size]


class OwnedFeedbackWire:
    """One v4 default-feedback object. No surface, buffer, seat or input request."""
    def __init__(self):
        self.buffer=bytearray();self.pending=[];self.owned=[];self.globals={};self.done=set();self.deleted=set()
        self.phase=3;self.table=None;self.main=None;self.tranche=None;self.tranches=[];self.feedback_done=False
        self.bytes=0;self.receives=0;self.event_count=0;self.observed={}
    def close(self):
        errors=[]
        for fd in dict.fromkeys(self.owned):
            try:os.close(fd)
            except OSError as error:errors.append(type(error).__name__)
        self.owned=[];self.pending=[]
        require(not errors,'received feedback descriptor close failed')
    def feed(self,data,ancillary,flags):
        import array
        ancillary_valid=True
        for level,kind,body in ancillary:
            if level!=socket.SOL_SOCKET or kind!=socket.SCM_RIGHTS:
                ancillary_valid=False;continue
            values=array.array('i');whole=len(body)-len(body)%values.itemsize
            values.frombytes(body[:whole]);self.owned.extend(values);self.pending.extend(values)
            if whole!=len(body):ancillary_valid=False
        require(ancillary_valid and not flags&(socket.MSG_CTRUNC|socket.MSG_TRUNC),'invalid/truncated ancillary data')
        require(len(self.owned)<=1 and len(set(self.owned))==len(self.owned),'extra/duplicate received descriptor')
        self.receives+=1;self.bytes+=len(data)
        require(data and self.receives<=64 and self.bytes<=65536,'feedback wire EOF/bound')
        self.buffer.extend(data)
        while len(self.buffer)>=8:
            target,packed=struct.unpack_from('<II',self.buffer);size=packed>>16;opcode=packed&65535
            require(8<=size<=4096 and size%4==0,'invalid feedback wire frame size')
            if len(self.buffer)<size:break
            payload=bytes(self.buffer[8:size])
            if target==6 and opcode==1 and not self.pending:
                require(self.table is None,'duplicate format table before ancillary')
                break
            del self.buffer[:size];self.event_count+=1
            require(self.event_count<=512,'feedback event bound')
            if target==1:
                require(opcode==1 and len(payload)==4,'display error/unexpected display event')
                retired=struct.unpack('<I',payload)[0]
                require(retired in self.done and retired not in self.deleted,'unexpected delete_id');self.deleted.add(retired)
            elif target==2:
                require(opcode==0 and len(payload)>=12,'registry removal/unexpected event')
                name=struct.unpack_from('<I',payload)[0];interface,end=feedback_wire_string(payload,4)
                require(end+4==len(payload) and name>0 and name not in self.globals and len(self.globals)<256,'registry global duplicate/bound')
                version=struct.unpack_from('<I',payload,end)[0];require(version>0,'registry version zero')
                self.globals[name]=(interface,version)
            elif target in (3,5,7):
                require(target==self.phase and opcode==0 and len(payload)==4 and target not in self.done,'unexpected sync callback')
                self.done.add(target)
            elif target==6:
                require(self.phase==7 and not self.feedback_done,'feedback outside current one-shot request')
                if opcode==1:
                    self.observed={'object':target,'opcode':opcode,'payloadBytes':len(payload),
                        'size':struct.unpack('<I',payload)[0] if len(payload)==4 else None,'receivedFdCount':len(self.pending)}
                    require(len(payload)==4 and self.table is None and len(self.pending)==1,'format-table shape/duplicate/descriptor count')
                    length=struct.unpack('<I',payload)[0]
                    require(8192<length<=12288 and length%16==0,'format table outside observed bounded record family')
                    self.table=(self.pending.pop(0),length)
                elif opcode==2:
                    raw=feedback_wire_array(payload)
                    require(len(raw)==8 and self.main is None and not self.tranches and self.tranche is None,'main device shape/order')
                    self.main=raw.hex()
                elif opcode==4:
                    raw=feedback_wire_array(payload)
                    require(len(raw)==8 and self.main is not None and self.table is not None and self.tranche is None and len(self.tranches)<16,'tranche target shape/order/bound')
                    self.tranche={'device':raw.hex(),'flags':None,'indices':[]}
                elif opcode==6:
                    require(len(payload)==4 and self.tranche is not None and self.tranche['flags'] is None,'tranche flags shape/order')
                    flags_=struct.unpack('<I',payload)[0];require(flags_&~1==0,'unknown v4 tranche flags');self.tranche['flags']=flags_
                elif opcode==5:
                    raw=feedback_wire_array(payload)
                    require(self.tranche is not None and self.tranche['flags'] is not None and len(raw)>0 and len(raw)%2==0,'tranche indices shape/order')
                    indices=list(struct.unpack('<'+'H'*(len(raw)//2),raw))
                    require(all(i<self.table[1]//16 for i in indices) and len(self.tranche['indices'])+len(indices)<=768,'tranche index outside table/bound')
                    self.tranche['indices'].extend(indices)
                elif opcode==3:
                    require(not payload and self.tranche is not None and self.tranche['flags'] is not None and self.tranche['indices'],'incomplete tranche')
                    self.tranches.append(self.tranche);self.tranche=None
                elif opcode==0:
                    require(not payload and self.table is not None and self.main is not None and self.tranches and self.tranche is None,'incomplete feedback done')
                    self.feedback_done=True
                else:raise ValueError('unexpected feedback event')
            else:raise ValueError('unexpected Wayland object')
    def receive_until_sync(self,client,clock):
        while self.phase not in self.done or self.buffer:
            client.settimeout(left(clock)/1e9)
            data,ancillary,flags,_=client.recvmsg(4096,socket.CMSG_SPACE(16),socket.MSG_CMSG_CLOEXEC)
            self.feed(data,ancillary,flags)
        require(not self.pending,'unassigned ancillary descriptor at sync')
    def request(self,client,clock):
        def send(body):client.settimeout(left(clock)/1e9);client.sendall(body)
        send(struct.pack('<IIIIII',1,(12<<16)|1,2,1,12<<16,3));self.receive_until_sync(client,clock)
        managers=[(name,version)for name,(interface,version)in self.globals.items()if interface=='zwp_linux_dmabuf_v1']
        require(len(managers)==1 and managers[0][1]>=4,'one current dmabuf version4 required')
        self.phase=5;label=b'zwp_linux_dmabuf_v1\0'
        payload=struct.pack('<II',managers[0][0],len(label))+label+b'\0'*((-len(label))%4)+struct.pack('<II',4,4)
        send(struct.pack('<II',2,((8+len(payload))<<16))+payload+struct.pack('<III',1,12<<16,5));self.receive_until_sync(client,clock)
        self.phase=7;send(struct.pack('<IIIIII',4,(12<<16)|2,6,1,12<<16,7));self.receive_until_sync(client,clock)
        require(self.feedback_done and self.table is not None and len(self.owned)==1,'one complete actual feedback table required')
        return self.table


def feedback_fd_observation(fd):
    import fcntl
    s=os.fstat(fd)
    return {'identity':{name:getattr(s,name)for name in ('st_dev','st_ino','st_size','st_mode','st_uid','st_nlink','st_mtime_ns','st_ctime_ns')},
        'link':os.readlink(Path('/proc/self/fd')/str(fd)),
        'accessMode':fcntl.fcntl(fd,fcntl.F_GETFL)&os.O_ACCMODE,'closeOnExec':bool(fcntl.fcntl(fd,fcntl.F_GETFD)&fcntl.FD_CLOEXEC)}


def validate_owned_feedback_fd(fd,length,family):
    observed=feedback_fd_observation(fd);s=observed['identity'];device=tuple(int(x,16)for x in family['device'].split(':'))
    require(stat.S_ISREG(s['st_mode']) and s['st_uid']==os.getuid() and s['st_nlink']==0
            and (os.major(s['st_dev']),os.minor(s['st_dev']))==device and s['st_ino']==family['inode']
            and s['st_size']==length and 8192<length<=12288 and length%16==0,'received table does not back exact opener mappings')
    # Pinned Hyprland retains allocateSHMFilePair's second (read-only) descriptor.
    require(observed['accessMode']==os.O_RDONLY and observed['closeOnExec'],'received table FD is not read-only/cloexec')
    require(observed['link']==family['pathname'],'received format table link differs')
    data=os.pread(fd,length+1,0)
    require(len(data)==length and len(data)%16==0,'incomplete format table body')
    # The protocol allows duplicate pairs and leaves the four padding bytes unused.
    records=[(fmt,modifier)for fmt,modifier in struct.iter_unpack('<I4xQ',data)]
    require(len(records)==length//16,'format table record count')
    require(observed==feedback_fd_observation(fd),'format table changed while reading')
    return observed,data


def owned_feedback_mappings(context,lease,endpoint,proc,born,image,rows,inventory,required,clock,output):
    stack=lease.stack;family=deleted_map_family(rows)
    require(family is not None,'expected exact opener feedback family absent')
    def attest(client=None):
        left(clock);stack.current();context['base'].check_process(proc,born,image)
        require(endpoint['bootId']==clock['boot'],'endpoint boot changed')
        held={(os.fstat(fd).st_dev,os.fstat(fd).st_ino)for fd in lease.fds}
        for row in endpoint['ancestors']:
            s=Path(row['path']).lstat()
            require(stat.S_ISDIR(s.st_mode) and (s.st_dev,s.st_ino)in held and
                    (str(s.st_dev),str(s.st_ino),str(s.st_uid),str(stat.S_IMODE(s.st_mode)))==tuple(row[k]for k in ('device','inode','uid','mode')),'held endpoint ancestor changed')
        s=stack.nested_socket.lstat();p=endpoint['socket']
        require(stack.nested_socket.name==endpoint['name'] and stat.S_ISSOCK(s.st_mode)
                and (str(s.st_dev),str(s.st_ino),str(s.st_uid),str(stat.S_IMODE(s.st_mode)))==tuple(p[k]for k in ('device','inode','uid','mode')),'selected endpoint changed')
        owner=endpoint['processes'][0]
        require(str(stack.nested.pid)==owner['pid'] and stack.nested_birth==owner['birth']
                and birth(stack.nested.pid)==(owner['birth'],int(owner['parent'])),'selected compositor lifecycle changed')
        for pin in endpoint['executable']['pins']:
            s=Path(pin['path']).lstat()
            require((str(s.st_dev),str(s.st_ino))==(pin['device'],pin['inode'])
                    and (stat.S_ISDIR(s.st_mode) if pin['kind']=='directory' else stat.S_ISREG(s.st_mode)), 'selected executable pin changed')
        if client is not None:
            require(struct.unpack('3i',client.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))==tuple(int(owner[k])for k in ('pid','uid','gid')),'feedback peer differs from held endpoint')
        left(clock)
    attest();wire=OwnedFeedbackWire()
    evidence={'schema':1,'kind':'owned-wayland-dmabuf-format-table-mapping','peer':endpoint['processes'][0],
        'endpoint':endpoint,'mappings':family['rows'],'inputIssued':False,'nativeAcceptance':False,
        'creatorAttested':False,'mappingQualified':False}
    try:
        with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)as client:
            client.settimeout(left(clock)/1e9);client.connect(str(stack.nested_socket));attest(client)
            fd,length=wire.request(client,clock);attest(client)
            evidence['receivedDescriptor']=feedback_fd_observation(fd);evidence['size']=length
            observed,data=validate_owned_feedback_fd(fd,length,family)
            evidence.update(sha256=digest(data),recordCount=length//16,mainDevice=wire.main,tranches=wire.tranches)
            attest(client)
            repeated,generated,_=context['collector'].generated_snapshot(context['base'],proc,clock)
            require(generated is None and deleted_map_family(repeated)==family,'opener feedback ranges changed')
            require(validate_owned_feedback_fd(fd,length,family)==(observed,data),'format table changed across map snapshot')
            attest(client);evidence['repeatedMappings']=deleted_map_family(repeated)['rows']
            # Existing exact-row seam only. Ordinary mappings and required images stay checked.
            mapped=boot_correspondence.strict_snapshot_files(context['current'],context['base'],context['foundation']['graphics'],repeated,inventory,required,evidence,clock)
            attest(client);require(validate_owned_feedback_fd(fd,length,family)==(observed,data),'format table changed during ordinary map verification')
            evidence.update(mappingQualified=True,protocolSourceAttested=True)
            return mapped,evidence
    except Exception as error:
        evidence['error']=str(error)[:512]
        raise
    finally:
        evidence.update(event=wire.observed,wireReceives=wire.receives,wireBytes=wire.bytes)
        if wire.owned and 'receivedDescriptor'not in evidence:
            try:evidence['receivedDescriptor']=feedback_fd_observation(wire.owned[0])
            except OSError as error:evidence['descriptorObservationError']=type(error).__name__
        try:wire.close()
        except Exception as error:
            evidence.update(mappingQualified=False,cleanupError=str(error)[:256]);raise
        finally:write_json(output/'opener-owned-dmabuf-mapping.json',evidence)


def missing_named_mappings(rows, inventory, graphics_devices):
    """Bounded failure evidence only; never adds a path to the qualified inventory."""
    missing = sorted({row['pathname'] for row in rows
                      if isinstance(row.get('pathname'), str) and row['pathname'].startswith('/')
                      and row['pathname'] not in graphics_devices
                      and (row['pathname'].endswith(' (deleted)') or row['pathname'] not in inventory)})
    return {'missingNamedPathCount': len(missing),
            'missingNamedPaths': [path[:8192] for path in missing[:256]],
            'allMissingNamesRetained': len(missing) <= 256 and all(len(path) <= 8192 for path in missing),
            'inventoryChanged': False}


CAPTURE_FILE_LIMIT = 32*1024*1024  # Existing maximum accepted PNG body, per file.


def bound_capture_output():
    # RLIMIT_FSIZE also bounds graphics memfd backing. Keep this finite and
    # exclusive to the one exact pinned grim command; no change to base guard.
    import resource
    resource.setrlimit(resource.RLIMIT_FSIZE, (CAPTURE_FILE_LIMIT,CAPTURE_FILE_LIMIT))


def command_output_bound(base, argv, assets, output):
    if argv and argv[0] == assets['grim']['path']:
        names=['actual-owned-window.png']+['menu-%02d-%s.png'%(index,row['name']) for index,row in enumerate(MENU_STEPS)]+['ui011-initial.png','ui011-opener-focused.png','ui011-menu.png','ui011-fallback.png','ui011-settled.png']
        require(len(argv)==2 and argv[1] in [str(Path(output)/name) for name in names],
                'only exact fixed grim capture may use graphics output profile')
        return bound_capture_output
    return base.bound_output


def execute(context,packet_sha):
    packet=context['packet'];assets=packet['assets'];qa=context['qa'];stage=context['stage'];journey=menu_journey_mode(packet)
    scoped=load_helper('tools/ui011_opener_journey.py','ui011_journey');at_module=load_helper('tools/ui011_owned_at_provider.py','ui011_at_provider')
    scope=qa.require_qa_scope();authority=context['authority']
    require(time.time_ns()+JOURNEY_NS+CLEANUP_NS<attempt_auth.authorization_deadline_ns(authority),'insufficient actual authorization for original28+cleanup2')
    output=ROOT/'.warlock-contributor'/('ui011-opener-closure-'+str(time.time_ns()));output.mkdir(mode=0o700)
    for name in ('home','config','cache','data'):(output/name).mkdir(mode=0o700)
    bound=packet['binding'];staging=SimpleNamespace(run_dir=str(output/'run'),duration_seconds=28,
      controller_html=assets['controller']['path'],bar_html=assets['bar']['path'],popup_html=assets['popup']['path'],
      ui_owner_bin=assets['owner']['path'],ui_backend_bin=assets['controls']['path'],catalog_root=[],application_attachment=True,
      ux003_recorder_image=assets['recorder']['path'],ux003_recorder_sha256=assets['recorder']['sha256'],
      lifetime=bound['lifetime'],session=bound['session'],frontend=bound['frontend'],locale='C')
    with (output/'staging.stdout').open('x') as stream,redirect_stdout(stream):stage.cmd_guest_config(staging)
    staged=json.loads(regular(output/'run/mvp-guest-manifest.json'),object_pairs_hook=unique)
    clock=attempt_auth.seal_clock(staging_clock(staged,Path('/proc/sys/kernel/random/boot_id').read_text().strip()),authority)
    receipt={'schema':1,'kind':'ui011-opener-closure-observation','passed':False,'packetSha256':packet_sha,
      'scope':scope,'clock':dict(clock),'commands':[],'snapshots':[],'frames':[],'forcedCleanup':False,'cleanupUnknown':True,
      'nativeAcceptance':False,'originalAcceptance':False,'fullJourneyAccepted':False,'requirementsCredit':0,'scenariosCredit':0,
      'pointerInputIssued':False,'inputScope':'Only actual-owned active-window close-gui Alt+F4; no keyboard-menu acceptance.'}
    if journey:receipt.update(inputScope='Nine fixed owned keyboard menu transactions; phase JSON schedules only, actual pixels require independent review.',journey='ux024-taskbar-menu-focus',keyboardTransactions=[])
    before=global_snapshot();stack=None;lease=None;keyboard=None;observer=None;producer=None;reader=None;phase_channel=None;at=None;case=None;wire_path=output/'observer-wire.jsonl';logs=[];nonce=os.urandom(32).hex()
    try:
        stack_output=output/'owned-stack';stack_output.mkdir(mode=0o700)
        stack=_OwnedStack(context['foundation'],qa,context['collector'],context['base'],clock,stack_output,pinned(assets['nestedConfig']),context['current'],packet['reuse']['providerSourceCorrespondence'],packet['reuse'].get('currentCursorCorrespondence'))
        stack.start();receipt['liveStack']={'hostPid':stack.host.pid,'hostBirth':stack.host_birth,'nestedPid':stack.nested.pid,'nestedBirth':stack.nested_birth,'facts':stack.facts}
        env=dict(stack.env,HOME=str(output/'home'),XDG_CONFIG_HOME=str(output/'config'),XDG_CACHE_HOME=str(output/'cache'),XDG_DATA_HOME=str(output/'data'))
        env['XDG_DATA_HOME']=str(output/'data');env[DEADLINE_ENV]=str(clock['deadline'])
        def current():require_live_stack(stack,clock['deadline'])
        def spawn(role,argv,pipe=False,asset_role=None):
            current();out_path=output/(role+'.stdout');err_path=output/(role+'.stderr')
            out=subprocess.PIPE if pipe else out_path.open('xb');err=err_path.open('xb');logs.append(err)
            if not pipe:logs.append(out)
            matches=[ref['sha256'] for role,ref in assets.items() if role in {'controls','keyboardSeat','hyprctl','wtype','grim','opener'} and ref['path']==argv[0]]
            require(len(set(matches))==1 and (asset_role is None or assets[asset_role]['path']==argv[0]),'only fixed selected executable may spawn')
            proc=context['collector'].checked_spawn(context['base'],clock,{argv[0]:matches[0]},lambda:subprocess.Popen(argv,env=env,
              stdin=subprocess.PIPE if pipe else subprocess.DEVNULL,stdout=out,stderr=err,close_fds=True,bufsize=0,start_new_session=True,preexec_fn=command_output_bound(context['base'],argv,assets,output)))
            born=context['base'].process_birth(proc.pid);stack.children.append((proc,born,role));return proc,born,out_path,err_path
        count=0
        def command(role,args):
            nonlocal count
            current();pinned(assets[role],256*1024*1024);count+=1
            proc,born,out,err=spawn('command-'+str(count),[assets[role]['path'],*args]);wait_normal(proc,clock)
            receipt['commands'].append({'role':role,'argv':[assets[role]['path'],*args],'pid':proc.pid,'birth':born,'exit':proc.returncode,'groupAbsent':True})
            require(not regular(err),'fixed command diagnostics');return regular(out,32*1024*1024)
        def clients():return json.loads(command('hyprctl',['-i',stack.instance['signature'],'clients','-j']),object_pairs_hook=unique)
        require(clients()==[],'private nested display already has clients')
        require(json.loads(command('hyprctl',['-i',stack.instance['signature'],'plugin','list','-j']))==[],'nested plugin present')
        geometry.validate_monitor(command('hyprctl',['-i',stack.instance['signature'],'monitors','-j']),(1280,720))
        # The noninput seat is held before GTK initialization; only wtype emits Alt+F4.
        keyboard_proc,_,_,keyboard_err=spawn('held-keyboard',[assets['keyboardSeat']['path']],True)
        keyboard=_HeldKeyboard(keyboard_proc,assets['keyboardSeat']['sha256'],clock,keyboard_err)
        receipt['keyboardBootstrap']=keyboard.start()
        lease=EndpointLease(stack,clock);endpoint=lease.capture(bound)
        config={'schema':1,'nonce':nonce,'binding':bound,'deadlineMonotonicNs':str(clock['deadline']),'endpoint':endpoint}
        config_path=output/'endpoint.json';write_json(config_path,config)
        observer,observer_birth,_,observer_err=spawn('connected-observer',[assets['controls']['path'],'--foreign-endpoint-observe-only',str(config_path),digest(regular(config_path))],True)
        def process_maps(role,proc,born,required,asset_role='controls'):
            current();context['base'].check_process(proc,born,assets[asset_role]['sha256'])
            rows,generated,_=context['collector'].generated_snapshot(context['base'],proc,clock)
            require(generated is None,'observer/producer has unexpected generated mappings')
            snapshot_path=output/(role+'-maps-before-check.json')
            write_json(snapshot_path,{'schema':1,'role':role,'pid':proc.pid,'birth':born,'rows':rows})
            diagnostics=missing_named_mappings(rows,packet['processInventory'],context['foundation']['graphics']['devices'])
            diagnostics.update(role=role,pid=proc.pid,birth=born,snapshot={'path':str(snapshot_path),'sha256':digest(regular(snapshot_path,32*1024*1024))})
            receipt.setdefault('mappingDiagnostics',[]).append(diagnostics)
            if role=='opener':
                mapped,evidence=owned_feedback_mappings(context,lease,endpoint,proc,born,assets[asset_role]['sha256'],rows,packet['processInventory'],required,clock,output)
                receipt['openerDmabufFormatTable']=evidence
            else:
                mapped=boot_correspondence.strict_snapshot_files(context['current'],context['base'],context['foundation']['graphics'],rows,packet['processInventory'],required,None,clock)
            context['base'].check_process(proc,born,assets[asset_role]['sha256']);return mapped
        wire=wire_path.open('xb');logs.append(wire)
        reader=ObserverPipe(observer,clock,nonce,bound,wire)
        initial=reader.command('READ_INITIAL');require(initial['rows']==[],'actual initial snapshot not empty');receipt['snapshots'].append(initial)
        receipt['observerMappings']=process_maps('observer',observer,observer_birth,[assets['controls']['path'],context['abi']['library']['path']])
        case=scoped.Journey(sys.modules[__name__],context,stack,clock,assets,bound,output,receipt)
        opener,opener_birth=case.start_opener(spawn,clients)
        receipt['openerMappings']=process_maps('opener',opener,opener_birth,[assets['opener']['path']],asset_role='opener')
        opener_observed=reader.command('READ_WINDOW');opener_row=match_mapped(opener_observed,case.window);receipt['snapshots'].append(opener_observed);receipt['callbackHandleOrdinal']=opener_row['handleOrdinal']
        at=at_module.OwnedAT(stack,sys.modules[__name__],boot_correspondence,packet['atProviderPins'],packet['processInventory'])
        issued_at=at.start()
        require(isinstance(issued_at,dict)and set(issued_at)=={'AT_SPI_BUS_ADDRESS'}and isinstance(issued_at['AT_SPI_BUS_ADDRESS'],str)and issued_at['AT_SPI_BUS_ADDRESS']==at.address,'exact issued AT environment mapping required')
        env.update(issued_at)
        config_path=output/'run/backend.json'
        if observed_producer_mode(packet):
            current()
            original_body=regular(config_path,65536)
            original=json.loads(original_body,object_pairs_hook=unique)
            selected_config=observed_producer_config(original,endpoint,bound,clock)
            selected_path=output/'run/backend-observation.json'
            write_json(selected_path,selected_config)
            current()
            require(regular(config_path,65536)==original_body,'staged original config changed')
            receipt['observationProducerConfig']={'originalPath':str(config_path),'originalSha256':digest(original_body),
                'selectedPath':str(selected_path),'selectedSha256':digest(regular(selected_path,65536)),
                'endpointSha256':canonical(endpoint),'binding':bound,'deadlineMonotonicNs':str(clock['deadline']),
                'capabilityGrantedByConfiguration':False}
            config_path=selected_path
        producer,producer_birth,producer_out,producer_err=spawn('window-producer',[assets['controls']['path'],'--foreign-endpoint-window-producer',str(config_path),digest(regular(config_path))])
        window=None
        while window is None:
            current();require(producer.poll() is None,'producer exited before mapped owned window')
            values=clients();require(isinstance(values,list) and len(values)<=2,'private display not a singleton')
            if values:
                selected=[v for v in values if v.get('pid')!=opener.pid]
                if not selected:time.sleep(min(0.01,left(clock)/1e9));continue
                require(len(selected)==1,'exact single shell descendant required beside opener')
                row=selected[0];pid=row.get('pid')
                require(type(pid) is int and pid>0 and row.get('mapped') is True and descendant(pid,producer.pid,producer_birth),'mapped client is not actual retained producer descendant')
                require(digest(regular(Path('/proc',str(pid),'exe').resolve(),256*1024*1024))==assets['owner']['sha256'],'actual mapped client image differs')
                window=row
            else:time.sleep(min(0.02,left(clock)/1e9))
        require(window.get('size')==[980,680] and re.fullmatch('0x[0-9a-f]+',window.get('address','')),'actual window geometry/address differs')
        window_birth=birth(window['pid'])[0];namespace={'engine':os.readlink('/proc/'+str(window['pid'])+'/ns/pid'),'parent':os.readlink('/proc/'+str(producer.pid)+'/ns/pid')}
        require(namespace['engine']!=namespace['parent'],'actual engine PID namespace not distinct')
        receipt['mappedWindow']=window;receipt['windowBirth']=window_birth;receipt['windowNamespace']=namespace
        receipt['producerMappings']=process_maps('producer',producer,producer_birth,[assets['controls']['path']])
        case.shell_clients(clients(),window,producer,producer_birth)
        at.bind_engine(producer,producer_birth,window['pid'],window_birth,assets['owner']['sha256'])
        def same_window():
            current();require(birth(window['pid'])[0]==window_birth and descendant(window['pid'],producer.pid,producer_birth),'input target birth/ancestry replaced')
            attest_process_image(window['pid'],window_birth,assets['owner']['sha256'])
            values=clients();case.shell_clients(values,window,producer,producer_birth,allow_closed=opener.poll()is not None);selected=[v for v in values if v.get('address')==window['address']];require(len(selected)==1 and selected[0].get('pid')==window['pid']and selected[0].get('at')==window['at']and selected[0].get('size')==window['size'],'input target/geometry replaced')
            active=json.loads(command('hyprctl',['-i',stack.instance['signature'],'activewindow','-j']),object_pairs_hook=unique)
            require(active.get('address')==window['address'] and active.get('pid')==window['pid'],'owned window is not actual active keyboard target')
        same_window()
        phase_channel=scoped.phase_channel(sys.modules[__name__],producer,producer_birth,window,window_birth,assets,clock,current,same_window,keyboard,receipt,bound,journey=False)
        case.run(phase_channel,at,command,clients,window,producer,producer_birth)
        wait_normal(producer,clock);require(not regular(producer_err),'actual producer diagnostics nonempty')
        require(clients()==[],'independent owned client disappearance absent')
        receipt['producer']=producer_observation(regular(producer_out),clock,window,window_birth,namespace,assets['owner']['sha256'])
        closed=reader.command('READ_CLOSED');require(closed['rows']==[],'same observer still publishes closed handle');receipt['snapshots'].append(closed)
        retired=reader.command('RETIRE');receipt['observerRetirement']=retired;wait_normal(observer,clock)
        require(not observer.stdout.read(1) and not regular(observer_err),'unexpected observer terminal tail/diagnostic')
        receipt['keyboardRetirement']=keyboard.finish();receipt['componentObservationsComplete']=True
    except Exception as exc:
        receipt['error']={'type':type(exc).__name__,'message':str(exc)[:2048]};receipt['componentObservationsComplete']=False
    finally:
        # Failure EOF is never interpreted as Retired. One existing original cleanup ceiling covers all children.
        if at is not None:
            receipt['atRetirement']=at.retire();receipt['ownedATProviderReceipt']=at.receipt
        if phase_channel is not None:receipt['phaseChannelRetirement']=phase_channel.close()
        if observer is not None and observer.stdin is not None:
            try:observer.stdin.close()
            except OSError:receipt['observerPipeCloseUnknown']=True
        if keyboard is not None and keyboard.final is None:
            try:
                proc=keyboard.proc;available=min(clock['deadline']+CLEANUP_NS-time.monotonic_ns(),attempt_auth.clock_authorization_deadline_ns(clock)-time.time_ns())
                require(available>0,'keyboard failure cleanup ceiling exhausted');tail,_=proc.communicate(b'',timeout=available/1e9)
                receipt['keyboardFailureRetirement']={'normal':proc.returncode==0 and not tail and not regular(keyboard.stderr_path) and input_group_absent(proc.pid)}
            except Exception as exc:receipt['keyboardFailureRetirement']={'normal':False,'error':type(exc).__name__}
        receipt['stackRetirement']=stack.retire() if stack is not None else {'normal':False}
        receipt['endpointDescriptorRetirement']=lease.close() if lease is not None and (observer is None or observer.poll() is not None) else {'closed':False,'retained':lease is not None}
        for stream in logs:stream.close()
        if wire_path.exists():receipt['actualObserverWire']={'path':str(wire_path),'sha256':digest(regular(wire_path,4*1024*1024))}
        if reader is not None:receipt['observerLastResponse']=reader.last_response
        receipt['globalRestoration']=global_restored(before,global_snapshot())
        receipt['forcedCleanup']=any(row.get('forced') is True for row in receipt['stackRetirement'].get('processes',[]))
        last_response=receipt.get('observerLastResponse') or {}
        receipt['cleanupUnknown']=not (receipt.get('atRetirement',{}).get('retired')is True and receipt.get('atRetirement',{}).get('retainedUnknown')is False and receipt['stackRetirement'].get('normal') is True and receipt['endpointDescriptorRetirement'].get('closed') is True and receipt['globalRestoration'] and last_response.get('phase')=='RETIRE' and last_response.get('status')=='Retired' and receipt.get('phaseChannelRetirement',{}).get('status')=='closed')
        try:
            require(digest(regular(PACKET))==packet_sha,'packet changed during actual attempt')
            for name,pin in {**packet['sourceHashes'],**packet['guardHashes']}.items():require(digest(regular(ROOT/name,64*1024*1024))==pin,'source changed during attempt')
            receipt['sourceInputsUnchanged']=True
        except Exception as exc:receipt['sourceInputsUnchanged']=False;receipt['sourceError']=str(exc)[:1024]
        receipt['passed']=bool(receipt.get('ui011SchedulingComplete')is True and len(receipt['atObservations'])==2 and receipt.get('componentObservationsComplete') is True and receipt['observerRetirement'].get('status')=='Retired' and receipt['keyboardRetirement'].get('normal') is True and not receipt['cleanupUnknown'] and not receipt['forcedCleanup'] and receipt['sourceInputsUnchanged'] and time.monotonic_ns()<=clock['deadline']+CLEANUP_NS and time.time_ns()<attempt_auth.clock_authorization_deadline_ns(clock))
        write_json(output/'report.json',receipt)
    return receipt,output/'report.json'


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--sha256',required=True);parser.add_argument('--preflight-only',action='store_true');args=parser.parse_args()
    context=preflight(args.sha256)
    if args.preflight_only:
        print(json.dumps({'schema':1,'passed':True,'componentOnly':True,'executionPerformed':False,'nativeAcceptance':False,'packetSha256':args.sha256}));return 0
    receipt,path=execute(context,args.sha256)
    print(json.dumps({'passed':receipt['passed'],'report':str(path),'sha256':digest(regular(path)),'nativeAcceptance':False,'originalAcceptance':False}))
    return 0 if receipt['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
