"""Generate review text only. Never import or edit a collector/product candidate."""
import ast
import difflib
import hashlib
import json
import os
from pathlib import Path
import stat

QA=Path('/home/hoskinson/window-integration-qa')
D=Path(__file__).parent
B=QA/'family-preparation-thumbnail-v8'
SERVICE=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-family-preparation-v24')
S='b017d8d2a126f76c637429fffc2d77d510161fb89d3f3826795abb47d30b9f2c'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,data):
    raw=data.encode() if isinstance(data,str) else (json.dumps(data,indent=2)+'\n').encode()
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    try:
        view=memoryview(raw)
        while view:view=view[os.write(fd,view):]
        os.fsync(fd)
    finally:os.close(fd)
def replace(text,old,new):
    if text.count(old)!=1:raise ValueError('intended replacement not unique: '+old[:120])
    return text.replace(old,new,1)

handoff=QA/'thumbnail-v8-terminal-source-handoff-v1.json'
assert sha(handoff)=='4a9bb60a64b884cbe87a747446757336e646600a588a7d06e16e1f8511aac5aa'
v8=json.loads(handoff.read_text())
for name,digest in v8['inputs'].items():
    p=Path(name)
    assert not p.is_symlink() and sha(p)==digest and stat.S_IMODE(p.stat().st_mode)==v8['inputModes'][name]
assert sha(SERVICE/'manifest-family-preparation-v24.json')==S

# Retained actual/failure and V8 external evidence snapshot. This file is itself
# an explicit selected input; the future freezer cannot silently refresh it.
dirs=[QA/'family-preparation-thumbnail-v7/attempt-baseline-1',
      QA/'terminal-confirmation-v8-design',QA/'thumbnail-v8-terminal-full-proof-v1']
extras=[handoff,QA/'renderer-role-v24-root-review-v1.json',
        QA/'renderer-role-v7-failure-replay-v1/review.json']
evidence={'inputs':{},'inputModes':{},'symlinks':{}}
for p in [*extras,*(p for directory in dirs for p in sorted(directory.rglob('*')))]:
    if '__pycache__'in p.parts or p.is_dir()and not p.is_symlink():continue
    if p.is_symlink():evidence['symlinks'][str(p)]=os.readlink(p)
    elif p.is_file():
        evidence['inputs'][str(p)]=sha(p);evidence['inputModes'][str(p)]=stat.S_IMODE(p.stat().st_mode)
    else:raise ValueError('unknown retained evidence type: '+str(p))
save(D/'retained-components.json',evidence)

closure='''"""Exact selected closure union. Import starts no resources."""
import hashlib,json,os,stat
from pathlib import Path
QA=Path('/home/hoskinson/window-integration-qa')
DESIGN=QA/'thumbnail-v9-renderer-binding-design-v1'
SERVICE=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-family-preparation-v24')
PACKETS=((SERVICE/'manifest-family-preparation-v24.json','SERVICE_SHA','links'),
 (QA/'family-preparation-thumbnail-v7/frozen-inputs.json','d066ecf9b9ec94f0fe096d117464ba0f611f5b4d655792c0f1f8c6c339cd90eb','symlinks'),
 (QA/'thumbnail-v8-terminal-source-handoff-v1.json','4a9bb60a64b884cbe87a747446757336e646600a588a7d06e16e1f8511aac5aa','symlinks'),
 (DESIGN/'retained-components.json','EVIDENCE_SHA','symlinks'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def retain(inputs,modes,links):
    def add_file(name,digest,mode):
        path=Path(name);info=path.lstat()
        if not stat.S_ISREG(info.st_mode)or path.is_symlink()or sha(path)!=digest or stat.S_IMODE(info.st_mode)!=mode:raise ValueError('selected retained file changed: '+name)
        if name in links or name in inputs and inputs[name]!=digest or name in modes and modes[name]!=mode:raise ValueError('selected closure file alias conflict: '+name)
        inputs[name]=digest;modes[name]=mode
    for path,expected,link_key in PACKETS:
        if path.is_symlink()or sha(path)!=expected:raise ValueError('selected closure packet changed: '+str(path))
        packet=json.loads(path.read_text())
        if set(packet['inputs'])!=set(packet['inputModes']):raise ValueError('complete selected input modes required')
        for name,digest in packet['inputs'].items():add_file(name,digest,packet['inputModes'][name])
        for name,target in packet[link_key].items():
            if not Path(name).is_symlink()or os.readlink(name)!=target or name in inputs or name in modes or name in links and links[name]!=target:raise ValueError('selected retained link changed/conflicts: '+name)
            links[name]=target
        add_file(str(path),expected,stat.S_IMODE(path.stat().st_mode))
'''.replace('SERVICE_SHA',S).replace('EVIDENCE_SHA',sha(D/'retained-components.json'))

old=(B/'module_binding.py').read_text();new=old
new=replace(new,'import os\n','import os\nimport re\nfrom copy import deepcopy\n')
new=new.replace('service-family-preparation-v23','service-family-preparation-v24').replace('manifest-family-preparation-v23.json','manifest-family-preparation-v24.json').replace('frozen V23','frozen V24').replace('0d2b7b231eaa26c6618783b1cb2305c2a989586b3a7cb371716e2d67603c82e2',S)
new=replace(new,"('batch_preview','rectangle','scene_controller','rectangle'))","('batch_preview','rectangle','scene_controller','rectangle'),('batch_preview','PipeTransport','pipe_transport','PipeTransport'),('batch_preview','OwnedLaunch','owned_launch','OwnedLaunch'),('batch_preview','Keeper','helper_supervisor','Keeper'),('batch_preview','checked_renderer','recovery_resources','checked_renderer'),('batch_preview','verify_process','recovery_resources','verify_process'),('batch_preview','process_start','recovery_resources','process_start'))")
new=replace(new,'def actor_callbacks(factory,desktop,transport,controller):',(D/'proposed_renderer_observer.py.txt').read_text()+'\n\ndef actor_callbacks(factory,desktop,transport,controller):')
new=replace(new,"('batch.require_disposable',batch.require_disposable)]","('batch.require_disposable',batch.require_disposable),('batch.bind_renderer',batch.bind_renderer),('batch._closed',batch._closed),('batch._renderer_matches',batch._renderer_matches),('batch._typed_equal',batch._typed_equal),('batch._renderer_witness',batch._renderer_witness)]")
new=replace(new,"        result.append({'actor':number,'batch':instance,'relations':relations,'callbacks':callbacks})", "        renderer=renderer_observation(factory,number,controller.desktop,controller.transport,packet,terminal=True)\n        if renderer['errors']or typed_json(renderer['stable'])!=typed_json(selected[0]['renderer']['stable']):raise ValueError('actual retained renderer identity or normal closure differs')\n        result.append({'actor':number,'batch':instance,'relations':relations,'callbacks':callbacks,'renderer':renderer})")
new=replace(new,"        raw['batch']=batch_identity(desktop)\n", "        raw['batch']=batch_identity(desktop)\n        raw['renderer']=renderer_observation(factory,number,desktop,transport,packet)\n        raw['relations'].update(raw['renderer']['relations'])\n        if raw['renderer']['errors']:raise ValueError('actual renderer link refused; raw evidence retained')\n")
new=replace(new,"        confirmation['batchRelations']=batch_relations(factory,number,desktop)\n", "        confirmation['batchRelations']=batch_relations(factory,number,desktop)\n        confirmation['renderer']=renderer_observation(factory,number,desktop,transport,packet)\n        if confirmation['renderer']['errors']or typed_json(confirmation['renderer']['stable'])!=typed_json(raw['renderer']['stable']):raise ValueError('actual renderer binding changed after disk')\n")
proposals={'module_binding.py':new,'collector_v9_closure.py':closure}
nf=(B/'native_faults.py').read_text();proposals['native_faults.py']=replace(nf,"SERVICE.name!='service-family-preparation-v23'","SERVICE.name!='service-family-preparation-v24'")
ni=(B/'native_integration.py').read_text();proposals['native_integration.py']=replace(ni,"    row = {'inputs': inputs, 'symlinks': links,","    from collector_v9_closure import retain\n    retain(inputs,modes,links)\n    row = {'inputs': inputs, 'symlinks': links,")

# Exact proposed nongraphical actor fixture refinements. Outcome assertions and
# original test deadlines are never modified.
fixture='''"""Test only: genuine confined CPU renderer/keeper. No native GUI."""
import hashlib,subprocess,tempfile,time
from pathlib import Path
import module_binding as binding
from helper_supervisor import Keeper
from owned_commands import SealedFile
from pipe_transport import PipeTransport
def prepare(test,factory):
    build=tempfile.TemporaryDirectory();test._renderer_fixtures.append({'factory':factory,'build':build,'transport':None})
    source=binding.SERVICE/'renderer_role_cpu_fixture.c'
    packet=__import__('json').loads(binding.MANIFEST.read_text())
    if hashlib.sha256(source.read_bytes()).hexdigest()!=packet['inputs'][str(source)]:raise ValueError('exact frozen nongraphical fixture source required')
    executable=Path(build.name)/'renderer-cpu'
    subprocess.run(['/usr/bin/gcc','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(executable)],check=True,timeout=10)
    factory._fixture_executable=executable;factory.producer_hash=hashlib.sha256(executable.read_bytes()).hexdigest()
    if factory.keeper is not None:raise ValueError('fixture actor keeper already exists')
    factory.keeper=Keeper(factory.root,test.env,lambda row:None)
    return factory.keeper
def transport(test,factory,desktop):
    from native_runtime import FailureBinding
    with SealedFile(factory._fixture_executable) as executable:
        result=PipeTransport('/proc/self/fd/'+str(executable.fd),env=test.env,failure=FailureBinding(),pass_fds=(executable.fd,),keeper=factory.keeper,actor=1)
    test._renderer_fixtures[-1]['transport']=result
    desktop.preview_batch.bind_renderer(result,factory.producer_hash)
    deadline=time.monotonic()+2
    while not result.outputs()and time.monotonic()<deadline:time.sleep(.002)
    if not result.outputs()or result.failed:raise AssertionError('genuine CPU renderer not ready within original output bound')
    return result
def normal_close(factory):
    for number,controller in getattr(factory,'observed_controllers',[]):
        if not controller.transport.closed:
            if controller.transport.close()!=0:raise AssertionError('fixture renderer did not close normally')
    factory.close()
def cleanup(test):
    errors=[]
    for row in reversed(test._renderer_fixtures):
        try:
            if row['transport']is not None and not row['transport'].closed:
                if row['transport'].close()!=0:raise AssertionError('fixture renderer cleanup nonzero')
            keeper=row['factory'].keeper
            if keeper is not None and not keeper.closed:keeper.stop()
        except BaseException as failure:errors.append(failure)
        finally:row['build'].cleanup()
    if errors:raise errors[0]
'''
proposals['renderer_binding_fixture.py']=fixture
t=(B/'test_actual_binding.py').read_text()
t=replace(t,' setUp=cpu.ReadonlyKernelTests.setUp\n tearDown=cpu.ReadonlyKernelTests.tearDown\n'," def setUp(self):\n  cpu.ReadonlyKernelTests.setUp(self);self._renderer_fixtures=[]\n def tearDown(self):\n  import renderer_binding_fixture as fixture\n  try:fixture.cleanup(self)\n  finally:cpu.ReadonlyKernelTests.tearDown(self)\n")
t=replace(t,"  desktop=object.__new__(native_runtime.PinnedNativeDesktop);desktop.commands=owned_commands.OwnedCommands(None,self.env,1,readonly=self.reader);", "  import renderer_binding_fixture as fixture\n  keeper=fixture.prepare(self,factory)\n  desktop=object.__new__(native_runtime.PinnedNativeDesktop);desktop.commands=owned_commands.OwnedCommands(keeper,self.env,1,readonly=self.reader);")
t=replace(t,'controller=object.__new__(scene_manager.ManagedController);transport=object.__new__(pipe_transport.PipeTransport);','controller=object.__new__(scene_manager.ManagedController);transport=fixture.transport(self,factory,desktop);')
# Preserve the actual FailureBinding used by the genuine launched transport.
t=replace(t,'  transport.failure=native_runtime.FailureBinding();code=', '  code=')
proposals['test_actual_binding.py']=t
t=(B/'test_batch_binding.py').read_text()
t=replace(t,'    def terminal(self,factory,initial,destination):\n        self.query()', '    def terminal(self,factory,initial,destination):\n        import renderer_binding_fixture as fixture\n        fixture.normal_close(factory)\n        self.query()')
proposals['test_batch_binding.py']=t

def segment(source,name):
    tree=ast.parse(source);node=next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name==name)
    return ast.get_source_segment(source,node)
checks={}
checks['all19SelectorsUnchanged']=segment(old,'_observe').replace('frozen V23','frozen V24')==segment(proposals['module_binding.py'],'_observe')
for name in ('batch_relations','batch_identity','archive_final','validate_evidence','validate_ledger','data_probe','bind_recovery','validate_recovery_evidence'):
    checks['wholeOriginal.'+name]=segment(old,name)==segment(proposals['module_binding.py'],name)
checks['baselineMainWholeExact']=segment(ni,'main')==segment(proposals['native_integration.py'],'main')
checks['faultMainInverseExact']=segment(nf,'main').replace('service-family-preparation-v23','service-family-preparation-v24')==segment(proposals['native_faults.py'],'main')
for name in ('test_actual_binding.py','test_batch_binding.py'):
    def assertions(source):
        return [ast.dump(n,include_attributes=False)for n in ast.walk(ast.parse(source))if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr.startswith('assert')]
    checks['allOriginalOutcomeAssertions.'+name]=assertions((B/name).read_text())==assertions(proposals[name])
if not all(checks.values()):raise ValueError('intended source preservation failed: '+str(checks))
out=D/'intended';out.mkdir(mode=0o700)
patches=[];mapping={}
for name,source in proposals.items():
    ast.parse(source,filename=name)
    save(out/(name+'.txt'),source)
    previous=(B/name).read_text()if(B/name).exists()else''
    patches.extend(difflib.unified_diff(previous.splitlines(keepends=True),source.splitlines(keepends=True),fromfile='V8/'+name,tofile='V9/'+name))
    mapping[name]={'oldSHA256':sha(B/name)if(B/name).exists()else None,'intendedSHA256':sha(out/(name+'.txt')),'intendedPath':str(out/(name+'.txt'))}
save(D/'intended-v9.patch',''.join(patches))
save(D/'intended-source-map.json',{'result':'design-only-pass','runtimeEdited':False,'nativeLaunch':False,'sources':mapping,'checks':checks,'patchSHA256':sha(D/'intended-v9.patch'),'retainedEvidenceSHA256':sha(D/'retained-components.json')})
print(json.dumps({'result':'design-only-pass','files':len(proposals),'checks':checks,'patchSHA256':sha(D/'intended-v9.patch')}))
