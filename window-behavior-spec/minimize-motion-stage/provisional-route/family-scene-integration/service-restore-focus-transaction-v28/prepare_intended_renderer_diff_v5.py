"""Build an intended review diff without modifying copied runtime."""
from pathlib import Path
import ast,difflib,hashlib,json,os
B=Path(__file__).resolve().parent;sha=lambda raw:hashlib.sha256(raw).hexdigest();old=(B/'batch_preview.py').read_text()
new=old.replace('from scene_controller import key, rectangle','from scene_controller import key, rectangle\nfrom pipe_transport import PipeTransport\nfrom owned_launch import OwnedLaunch\nfrom helper_supervisor import Keeper\nfrom recovery_resources import checked_renderer, verify_process, process_start')
new=new.replace('self.staging={};self.staging_serial=0','self.staging={};self.staging_serial=0\n        self.renderer_binding=None')
start=new.index('    def _closed(self):');end=new.index('    @staticmethod',start)
replacement='''    @staticmethod
    def _typed_equal(left,right):
        if type(left) is not type(right):return False
        if type(left) is dict:
            return (all(type(k) is str for k in left) and all(type(k) is str for k in right) and left.keys()==right.keys()
                and all(BatchPreviews._typed_equal(left[k],right[k]) for k in left))
        if type(left) is list:
            return len(left)==len(right) and all(BatchPreviews._typed_equal(a,b) for a,b in zip(left,right))
        return type(left) in (str,int,bool,type(None)) and left==right
    def _renderer_matches(self,binding):
        # Only in-memory exact-object/registration comparisons under keeper lock.
        transport=binding['transport'];launch=binding['launch'];process=binding['process'];keeper=binding['keeper']
        expected={'job':binding['job'],'kind':'renderer','actor':binding['actor'],'phase':'released','ownership':binding['ownership']}
        row=keeper.jobs.get(binding['job'])
        return (type(transport) is PipeTransport and type(launch) is OwnedLaunch and type(keeper) is Keeper
            and self.commands.keeper is keeper and type(self.commands.actor) is int and self.commands.actor==binding['actor']
            and {k:self.commands.env.get(k) for k in binding['environment']}==binding['environment']
            and transport.owned_launch is launch and transport.process is process and launch.process is process and launch.keeper is keeper
            and type(process) is subprocess.Popen and type(process.pid) is int and process.pid==binding['ownership']['pid']
            and launch.job==binding['job'] and self._typed_equal(launch.ownership,binding['ownership'])
            and type(row) is dict and type(row.get('actor')) is int and self._typed_equal(row,expected) and keeper.children.get(binding['job']) is process
            and not launch.closed and not transport.closed and not transport.closing and not transport.failed and process.returncode is None)
    def bind_renderer(self,transport,producer_sha256):
        # NativeFactory supplies its actual transport and reviewed selected digest.
        if type(transport) is not PipeTransport or type(producer_sha256) is not str or not re.fullmatch('[0-9a-f]{64}',producer_sha256):
            raise ValueError('exact selected renderer binding required')
        launch=transport.owned_launch;keeper=self.commands.keeper
        if (type(launch) is not OwnedLaunch or type(keeper) is not Keeper or type(self.commands.actor) is not int
                or self.commands.actor<1 or launch.keeper is not keeper):raise ValueError('exact renderer owner objects required')
        ownership=deepcopy(launch.ownership)
        environment={k:self.commands.env[k] for k in ('XDG_RUNTIME_DIR','HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY')}
        if ownership['producer']['sha256']!=producer_sha256 or ownership['environment']!=environment:
            raise ValueError('renderer selected producer/session differs')
        binding={'transport':transport,'launch':launch,'process':transport.process,'keeper':keeper,
            'job':launch.job,'actor':self.commands.actor,'ownership':ownership,'producerSHA256':producer_sha256,'environment':environment}
        # Constructor-authenticated ownership is captured without new I/O.
        # The execution/kernel proof is mandatory at every later exemption.
        # No open/read/hash/check/close/process observation holds either lock.
        with self.lock,keeper.lock:
            self.require_idle()
            if self.renderer_binding is not None or self.pending or self.staging:raise ValueError('renderer binding must precede preparation exactly once')
            if not self._renderer_matches(binding):raise ValueError('renderer registered ownership differs')
            self.renderer_binding=binding
    @staticmethod
    def _renderer_witness(binding):
        objects=tuple(id(binding[n]) for n in ('transport','launch','process','keeper'))
        data={k:v for k,v in binding.items() if k not in ('transport','launch','process','keeper')}
        return objects,json.dumps(data,sort_keys=True,separators=(',',':'),allow_nan=False)
    def _closed(self):
        keeper=self.commands.keeper
        keeper.verify() # Source/process I/O stays outside the registry lock.
        with keeper.lock:
            own=[deepcopy(row) for row in keeper.jobs.values() if row.get('actor')==self.commands.actor]
            binding=self.renderer_binding
            if binding is None:return not own
            if len(own)!=1 or not self._renderer_matches(binding):return False
            before=own[0];witness=self._renderer_witness(binding)
            ownership=deepcopy(binding['ownership']);producer_sha256=binding['producerSHA256']
        # Exemption authenticates the actual executed sealed producer, not kind.
        checked_renderer(ownership)
        if ownership['producer']['sha256']!=producer_sha256:return False
        if verify_process(ownership)!='executed':return False
        process=binding['process']
        if process.poll() is not None or Path(f"/proc/{ownership['pid']}/cmdline").read_bytes().split(b'\\0')[:-1]!=[v.encode() for v in ownership['targetArgv']]:return False
        if process_start(ownership['pid'])!=ownership['start']:return False
        keeper.verify()
        with keeper.lock:
            current=[row for row in keeper.jobs.values() if row.get('actor')==self.commands.actor]
            return (self.renderer_binding is binding and len(current)==1 and self._typed_equal(current[0],before)
                and self._renderer_witness(binding)==witness and self._renderer_matches(binding))
'''
new=new[:start]+replacement+new[end:];ast.parse(new)
native=(B/'native_runtime.py').read_text();needle="            resource['phase']='launched';self.publish_resource()";assert native.count(needle)==1
native_new=native.replace(needle,"            desktop.preview_batch.bind_renderer(transport,self.producer_hash)\n"+needle);ast.parse(native_new)
patch=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='V23/batch_preview.py',tofile='intended-V24/batch_preview.py'))+''.join(difflib.unified_diff(native.splitlines(True),native_new.splitlines(True),fromfile='V23/native_runtime.py',tofile='intended-V24/native_runtime.py'))
with os.fdopen(os.open(B/'INTENDED_RENDERER_ROLE_PATCH-v5.diff',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:f.write(patch)
row=dict(runtimeChanged=False,changedProductFilesOnly=['batch_preview.py','native_runtime.py'],sources={n:dict(beforeSHA256=sha(a.encode()),proposedSHA256=sha(z.encode()))for n,a,z in [('batch_preview.py',old,new),('native_runtime.py',native,native_new)]},patchSHA256=sha(patch.encode()),proposedSyntaxCheckedWithoutExecution=True,nativeLaunch=False)
with os.fdopen(os.open(B/'RENDERER_ROLE_SOURCE_PLAN-v5.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(row,f,indent=2);f.write('\n')
print(json.dumps(row))
