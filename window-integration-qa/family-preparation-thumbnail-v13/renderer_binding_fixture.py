"""Test only: genuine confined CPU renderer/keeper. No native GUI."""
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
