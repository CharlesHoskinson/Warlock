"""Fresh V8 private host: corrected exact core/plugin and reviewed private AQ tuple."""
import hashlib
import importlib.util
import json
import os
import re
import socket
import struct
import time
from pathlib import Path

STAGE=Path('/home/hoskinson/window-integration-qa/private-weston-aq-host-v4')
BASE=STAGE.parent/'private-weston-host-v2'
PARENT_AQ=STAGE.parent/'aquamarine-nested-lifecycle-v1'
ROOT=Path(__file__).resolve().parent
def aq_tuple():
    row=json.loads((ROOT/'aq-tuple.json').read_text())
    manifest=Path(row['manifest'])
    if digest(manifest)!=row['manifestSHA256']:raise RuntimeError('New AQ component manifest changed')
    packet=json.loads(manifest.read_text())
    if not packet['passed']:raise RuntimeError('New AQ component is not reviewed')
    base=manifest.parent
    for entry in packet['files']:
        path=base/entry['path']
        if 'symlink' in entry:
            if not path.is_symlink() or str(path.readlink())!=entry['symlink']:raise RuntimeError('New AQ loader symlink changed: '+str(path))
        elif digest(path)!=entry['sha256']:raise RuntimeError('New AQ component input changed: '+str(path))
    lib=Path(row['library'])
    if digest(lib)!=row['librarySHA256']:raise RuntimeError('New AQ library changed')
    return row,lib
spec=importlib.util.spec_from_file_location('reviewed_original_weston_host_v2',BASE/'weston_host.py')
original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def verify_inputs():
    row=json.loads((STAGE/'frozen-inputs.json').read_text())
    for path,value in row['inputs'].items():
        if digest(path)!=value:raise RuntimeError('Host compatibility input changed: '+path)
    candidate=json.loads((PARENT_AQ/'frozen-inputs.json').read_text())
    for path,value in candidate['inputs'].items():
        if digest(path)!=value:raise RuntimeError('Aquamarine compatibility input changed: '+path)
    for path,value in candidate['symlinks'].items():
        target=Path(path)
        if not target.is_symlink() or str(target.readlink())!=value:raise RuntimeError('Aquamarine loader symlink changed: '+path)

class ReviewedWestonHost(original.PrivateWestonHost):
    def __init__(self,output,main_env,width=1600,height=1000,dri_prime=None,mesa_vendor=False):
        private_parent=dict(main_env)
        private_parent['GSETTINGS_BACKEND']='memory'
        super().__init__(output,private_parent,width,height,dri_prime,mesa_vendor)
        self.evidence['privateSettingsBackend']='memory'

    def verify(self):
        super().verify();verify_inputs()
        row,lib=aq_tuple()
        self.evidence['privateAquamarine']={'path':str(lib),'sha256':digest(lib),'scope':'nested Hyprland child only; no installed replacement','contractManifestSHA256':row['manifestSHA256']}

    def launch(self,name,command,env=None):
        if name=='weston':
            probe=json.loads((ROOT/'parent-probe-build.json').read_text())
            build=Path(probe['buildReport'])
            if digest(build)!=probe['buildReportSHA256']:raise RuntimeError('Parent input build report changed')
            packet=json.loads(build.read_text())
            if not packet['passed'] or digest(packet['module'])!=packet['moduleSHA256']:raise RuntimeError('Parent input module changed')
            for path,value in packet['owningFiles'].items():
                if digest(path)!=value:raise RuntimeError('Parent input owning ABI file changed: '+path)
            if not command or str(command[0])!=str(original.PREFIX/'usr/bin/weston') or '--backend=headless' not in command or '--fake-seat' not in command:
                raise RuntimeError('Parent input module requires exact private headless/fake-seat host')
            selected=dict(self.env if env is None else env);selected['ELM_PARENT_INPUT_QA']='1'
            self.evidence['parentInputProbe']={'module':packet['module'],'moduleSHA256':packet['moduleSHA256'],'buildReportSHA256':probe['buildReportSHA256']}
            return original.PrivateWestonHost.launch(self,name,[*command,'--modules='+packet['module']],selected)
        if name=='hyprland':
            pair_root=Path(__file__).resolve().parent
            report=json.loads((pair_root/'native-build-report.json').read_text())
            if report['result']!='pass' or digest(report['binary'])!=report['sha256']:raise RuntimeError('Candidate binary is not reviewed build')
            verify_inputs()
            if not command or str(command[0])!='/usr/bin/Hyprland' or env is None or env.get('AQ_BACKENDS')!='wayland':
                raise RuntimeError('Private library selection requires explicit reviewed child command/env')
            selected=dict(env)
            selected['WAYLAND_DEBUG']='client'
            _,lib=aq_tuple()
            selected['LD_LIBRARY_PATH']=str(lib.parent)+':'+selected.get('LD_LIBRARY_PATH','')
            self.evidence['privateAquamarine']['childLibraryPath']=selected['LD_LIBRARY_PATH']
            return original.PrivateWestonHost.launch(self,name,[report['binary'],*command[1:]],selected)
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
        records=[row for owned,row in self.processes if owned is proc and row.get('name')=='hyprland' and row.get('command',[None])[0]==json.loads((Path(__file__).resolve().parent/'native-build-report.json').read_text())['binary']]
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
        super().__init__(output,main_env,width,height,nested_lua,dri_prime,mesa_vendor)
        self.host=ReviewedWestonHost(output,main_env,width,height,dri_prime,mesa_vendor)
        self.evidence=self.host.evidence

    def __enter__(self):
        super().__enter__()
        try:
            row,lib=aq_tuple()
            expected=str(lib.resolve())
            actual=self.evidence['hyprlandMaps']['files']
            selected={path:value for path,value in actual.items() if Path(path).name.startswith('libaquamarine.so')}
            if selected!={expected:row['librarySHA256']}:
                raise RuntimeError('Mapped AQ library differs from exact reviewed tuple: '+repr(selected))
            self.evidence['privateAquamarine']['mappedVerified']=True
            self.evidence['privateAquamarine']['mappedFiles']=selected
            return self
        except BaseException:
            self.host.close()
            raise


def core_tuple():
    descriptor=json.loads((ROOT/'native-build-report.json').read_text())
    report_path=Path(descriptor['buildReport'])
    if descriptor['result']!='pass' or digest(descriptor['binary'])!=descriptor['sha256'] or digest(report_path)!=descriptor['buildReportSHA256']:
        raise RuntimeError('Owning core descriptor changed')
    build=json.loads(report_path.read_text())
    if not build['passed'] or build['binary']!=descriptor['binary'] or build['binarySHA256']!=descriptor['sha256'] or build['unchangedArchiveMembers']!=432 or len(build['owningHeaders'])!=694:
        raise RuntimeError('Owning merged core archive/header closure mismatch')
    for rel,sha in build['inputs'].items():
        if digest(report_path.parent/'inputs'/rel)!=sha:raise RuntimeError('Captured core input changed: '+rel)
    for rel,sha in build['owningHeaders'].items():
        if digest(report_path.parent/'owning-headers'/rel)!=sha:raise RuntimeError('Owning ABI header changed: '+rel)
    for section in ['dependencies','linkDependencies','retainedPolicyHeaders','tools','linkedLibraries']:
        for path,sha in build[section].items():
            if digest(path)!=sha:raise RuntimeError('Core compile/link dependency changed: '+path)
    return descriptor
