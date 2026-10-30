"""Fresh tuple adapter for original taskbar journey; static checks are not GUI acceptance."""
import hashlib, importlib.util, json, os, re, shlex, socket, struct, time
from pathlib import Path

REPO = Path('/home/charles/Warlock')
BASE = Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild')
PARENT = BASE/'parent-host/fresh_weston.py'
COLLECTOR = BASE/'taskbar-qa/measured_inspection.py'
COLLECTOR_SHA = '559775d3a39c14b1cea2b5747773665a4817c5b9850d08afc4782d2919a11f9e'
PARENT_SHA = 'e045634bd023f07977c398ef0057b9fdee3a1e1718d51c879e221ee353e28ae9'
TUPLE_SHA = 'bc225242e30baf4a5b8b1182cef6fdc716cc9c67de90dc35674f90c5fa87830b'
PREFLIGHT_SHA = '56e50f6a488b39fadf72064586422c33d0162d78aa36e9b88e7ca8dee0a83a3e'
REVIEW_SHA = 'c73693f0aa11091b3788e30f5e699f491293f43c005fa4977f03b27e5ff61e6b'
FOUNDATION_SHA = '08b24bd93cbb63ec097900915379b32e90d9dcca7156d04fe8ee959efaff264f'
HELPERS = {
 'qa/session_bus.py':'d8f945a68a8e772ffd26458e8e60beac8c8ad79849f08a2daf4110f5c8178916',
 'qa/system_isolation.py':'029a41bc8aae39936c69dc591857795aabd43df17b1f9a86b02b6c6a83dddc0e',
 'qa/isolation.py':'95e6999ccb1528311e950d95bf855a00bc29327458152eb7943f1f01bce1ceb8',
 'qa/inspection.py':'051d44430a49319389781d12bc0389732d76412ef1cf7f59f352f5e78f67bdd2',
 'qa/input_helper.py':'4599a448fff3a14ff88291acba3b6204882a985be36ef657b11c0acd881a0bf6',
 'fixture.py':'c6628d141b75bb20cc2fa526d85ef2a14025a28b832ebae57f1d996c76552f06'}
RUNTIME=REPO/'implementation/warlock-client-provider-native-v204'
# Exact protected current-source build receipt; frozen old evidence stays intact.
ASSET_REPORT = BASE/'launcher-pending-visibility-fix/assets-build-v1/report.json'
ASSET_REPORT_SHA = 'd31ddf1174986d902e8c2cecfcbc25bc5e0d9e743c465afadb6d159208eec606'
CURRENT_ASSET_REPORT = BASE/'context-keyup-assets-v1/output/report.json'
CURRENT_ASSET_REPORT_SHA = '69d5b85ad1137c3e851127c2cf5b4d9dcfe16f16e46568cbf106d2f165c77955'
OLD_CONTEXT_SHA = '2ff41ca906dc4e42ae76f65d486cf119b400414dee41ca886f5589709d2b9333'
CURRENT_CONTEXT_SHA = 'e843e72479a6e499a99f4369f145530e8e097c576e7d08926a6a912dbd50bc8d'
HOST_REPORT = BASE/'taskbar-host-rebuild-v1/output/report.json'
HOST_REPORT_SHA = '13b8a65807161faed1766a68df680d4a892f556449eb361dedc0d50a6fc3b46a'
NEW_HOST_SHA = 'e0a2f0464b090f77c744c7fe7fc8e356a9d0f1ce2ad8a648040379dd2f7c0558'
CURRENT_HOST_SOURCE_SHA = 'f78d1ba337dff920e50e79e7324d5467cfbfe240a3b4d03c7d4239f52b17850a'
OLD_HOST_SOURCE_SHA = 'cde6230199756dfaa193d5e8af5a41470f8b65de3cdd1942e0e0224ab458ccbf'
CURRENT_DESKTOP_SHA = 'a503d926599b5aa194956a1208fdc0004fb829442cd523c5372d41fd1fab0404'
OLD_DESKTOP_SHA = '1b5b48fc5ca71c6e11bd54ea6ab723f5a37f4d383d6a59c99d14d83b005d5033'


def digest(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def checked(path, expected):
    if digest(path)!=expected:raise RuntimeError('Pinned input changed: '+str(path))

VERIFY_CURRENT_SHA='07bb955b9f0e7171230f441c805651a27abd7393cbb97e25910a21658761a476'
def verify_tuple():
    import sys
    adapter=REPO/'implementation/warlock/adapter'
    for name,expected in [('current_build','d4e5af280a275f9a777322ee60f1f34bf21751b6726edcaa4e4105a02da4dbc7'),('current_native','4d22ddd511a69bb10caa4c624d030cf69953591024e0d38bd99dc0c1d9ab4edc')]:
        path=adapter/(name+'.py');body=path.read_bytes()
        if hashlib.sha256(body).hexdigest()!=expected:raise RuntimeError('Composition source changed '+name)
        spec=importlib.util.spec_from_loader(name,loader=None);module=importlib.util.module_from_spec(spec);module.__file__=str(path)
        sys.modules[name]=module;exec(compile(body,str(path),'exec'),module.__dict__)
    current_native=sys.modules['current_native']
    receipt=BASE/'pin-scrollport-build-root-v1/report.json'
    lock=BASE/'current-native-capture-1793324986522396247/native-lock.json'
    value=current_native.validate_composition(receipt,'65b909422a1866a9df8f118b134ea42778fd69564aed070bdb92c0975f3818d8',lock,'ba97d48eaa4f8c093c63f4b6b6e46d9d2ad602f95ffae16cda226af550d8bcd0')
    for name,h in HELPERS.items():checked(RUNTIME/name,h)
    checked(COLLECTOR,COLLECTOR_SHA)
    checked(REPO/'installed/home/.local/share/hypr-window-controls/qa/virtual-pointer','b092c3369d88b4d61fce80607614a5ec02258e0b774f0b10504a23385cb24434')
    checked(REPO/'window-integration-qa/orca-reader/physical-commands/evdev-keyboard','7bb54790faf1c47ab3a4184d84fa07fc1ab34c44d762ef457696f147777e95c0')
    old=BASE/'fresh-pair/tuple.json';raw=old.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=TUPLE_SHA:raise RuntimeError('Historical tuple changed')
    tup=json.loads(raw)
    for name in ('core','authority','aquamarine'):
        if value['slots'][name]!=tup['slots'][name]:raise RuntimeError('Native slot differs '+name)
    tup['slots']['host']=dict(value['slots']['host'])
    directory=Path(value['assets']['directory']);outputs=value['assets']['files']
    tup['slots']['host']['assets']={'assets/'+name:{'path':str(directory/name),'sha256':outputs[name]} for name in ('elm.js','bar.js','popup.js')}
    tup['sourceQualification']={'kind':'production current native composition','nativeLockSHA256':'ba97d48eaa4f8c093c63f4b6b6e46d9d2ad602f95ffae16cda226af550d8bcd0','frontendReportSHA256':'65b909422a1866a9df8f118b134ea42778fd69564aed070bdb92c0975f3818d8','nativeAcceptance':False}
    return tup

checked(PARENT,PARENT_SHA)
spec=importlib.util.spec_from_file_location('fresh_weston_parent',PARENT)
original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
original.qa.require_qa_scope()
tuple_data=verify_tuple()
collector_spec=importlib.util.spec_from_file_location("measured_taskbar_collector",COLLECTOR)
collector_module=importlib.util.module_from_spec(collector_spec);collector_spec.loader.exec_module(collector_module)
Collector=collector_module.Collector

class ReviewedWestonHost(original.PrivateWestonHost):
    def verify(self):
        super().verify(); verify_tuple()
        self.evidence['freshTupleSHA256']=TUPLE_SHA
    def launch(self,name,command,env=None):
        if name=='weston':
            packet=original.verify_fresh();module=packet['module']
            checked(module,packet['moduleSHA256'])
            for path,h in packet['owningModuleFiles'].items():checked(path,h)
            if not command or str(command[0])!=str(original.PREFIX/'usr/bin/weston') or '--backend=headless' not in command or '--fake-seat' not in command:raise RuntimeError('Parent input requires exact headless/fake-seat')
            selected=dict(self.env if env is None else env);selected['ELM_PARENT_INPUT_QA']='1'
            self.evidence['parentInputProbe']={'module':module,'moduleSHA256':packet['moduleSHA256']}
            return super().launch(name,[*command,'--modules='+module],selected)
        if name=='hyprland':
            tup=verify_tuple();core=tup['slots']['core'];aq=tup['slots']['aquamarine']
            if not command or str(command[0])!='/usr/bin/Hyprland' or env is None or env.get('AQ_BACKENDS')!='wayland':raise RuntimeError('Child requires reviewed Wayland backend')
            selected=dict(env);selected['WAYLAND_DEBUG']='client';selected['LD_LIBRARY_PATH']=str(Path(aq['path']).parent)+':'+selected.get('LD_LIBRARY_PATH','')
            self.evidence['privateAquamarine']={'path':aq['path'],'sha256':aq['sha256'],'childLibraryPath':selected['LD_LIBRARY_PATH']}
            return super().launch(name,[core['path'],*command[1:]],selected)
        return super().launch(name,command,env)

    def wait_socket(self,name,proc):
        # Leave the parent/Wayland readiness protocol unchanged. Never guess an IPC target.
        parts=Path(name).parts
        if not parts or parts[-1]!='.socket.sock':
            return super().wait_socket(name,proc)
        original.qa.require_qa_scope()
        runtime=original.qa.verify_runtime(self.runtime)
        if len(parts)!=3 or parts[0]!='hypr' or not re.fullmatch(r'[A-Za-z0-9_]+',parts[1]) or Path(name).is_absolute():
            raise RuntimeError('Invalid private IPC readiness path')
        records=[row for owned,row in self.processes if owned is proc and row.get('name')=='hyprland' and row.get('command',[None])[0]==tuple_data['slots']['core']['path']]
        if len(records)!=1:
            raise RuntimeError('IPC readiness requires exact registered child')
        expected=records[0]
        def live():
            if proc.poll() is not None or not original.same_process(expected):
                raise RuntimeError('Private IPC child exited or changed identity')
        live()
        path=runtime/name
        deadline=time.monotonic()+12
        while True:
            live()
            if time.monotonic()>=deadline:raise RuntimeError('Private IPC readiness timed out')
            try:
                before=original.socket_identity(path,runtime)
                # Every intermediate path must remain inside the owned runtime without symlinks.
                if any(part.is_symlink() for part in (path.parent,path.parent.parent)):
                    raise RuntimeError('Private IPC path contains symlink')
                connection=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
                connection.settimeout(min(2,max(.001,deadline-time.monotonic())))
                try:connection.connect(str(path))
                except (ConnectionRefusedError,FileNotFoundError):
                    connection.close();time.sleep(.03);continue
                except BaseException:
                    connection.close();raise
            except FileNotFoundError:
                time.sleep(.03);continue
            # Once connected, a bad peer/protocol response is terminal; never retry it.
            with connection:
                pid,uid,gid=struct.unpack('3i',connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize('3i')))
                if pid!=expected['pid'] or uid!=os.getuid():raise RuntimeError('Private IPC peer identity mismatch')
                if original.socket_identity(path,runtime)!=before:raise RuntimeError('Private IPC socket replaced')
                live();connection.sendall(b'j/version')
                reply=bytearray()
                while True:
                    connection.settimeout(min(2,max(.001,deadline-time.monotonic())))
                    chunk=connection.recv(4096)
                    if not chunk:break
                    reply.extend(chunk)
                    if len(reply)>65536:raise RuntimeError('Private IPC version reply too large')
                    if time.monotonic()>=deadline:raise RuntimeError('Private IPC reply timed out')
                version=json.loads(reply.decode('utf-8'))
                if not isinstance(version,dict) or not version:raise RuntimeError('Private IPC version reply must be a nonempty JSON object')
                live()
                if original.socket_identity(path,runtime)!=before:raise RuntimeError('Private IPC socket replaced after reply')
                self.evidence.setdefault('ipcReadiness',[]).append({'path':str(path),'socket':before,'peer':{'pid':pid,'uid':uid,'gid':gid},'request':'j/version','replyBytes':len(reply),'replySHA256':hashlib.sha256(reply).hexdigest(),'completeServerEOF':True,'version':version})
                return


class PrivateHyprSession(original.PrivateHyprSession):
    def __init__(self,output,main_env,width,height,nested_lua,dri_prime=None,mesa_vendor=False):
        # Match the hardware renderer verified by the fresh parent foundation.
        dri_prime=dri_prime or 'pci-0000_00_02_0'
        super().__init__(output,main_env,width,height,nested_lua,dri_prime,mesa_vendor)
        self.host=ReviewedWestonHost(output,main_env,width,height,dri_prime,mesa_vendor)
        self.evidence=self.host.evidence
    def __enter__(self):
        super().__enter__()
        try:
            aq=verify_tuple()['slots']['aquamarine']
            selected={path:value for path,value in self.evidence['hyprlandMaps']['files'].items() if Path(path).name.startswith('libaquamarine.so')}
            if selected!={str(Path(aq['path']).resolve()):aq['sha256']}:raise RuntimeError('Mapped AQ differs from reviewed tuple: '+repr(selected))
            self.evidence['privateAquamarine']['mappedVerified']=True
            self.evidence['privateAquamarine']['mappedFiles']=selected
            return self
        except BaseException:
            self.host.close();raise
