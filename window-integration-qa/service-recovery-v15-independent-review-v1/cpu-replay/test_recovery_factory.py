import hashlib
import os
from pathlib import Path
from types import SimpleNamespace
import subprocess
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from native_runtime import NativeFactory
from service_runtime import RuntimeService,unresolved

CPU_SOURCE=r'''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(void) {
 const char* marker=getenv("OFFLINE_CPU_EXEC_MARKER");
 if(marker) {FILE* f=fopen(marker,"w");if(!f)return 4;fputs("executed",f);fclose(f);}
 puts("{\"event\":\"offlineCpuOnly\"}");fflush(stdout);
 char* line=NULL;size_t size=0;
 while(getline(&line,&size,stdin)>=0) {if(strstr(line,"\"stop\"")){free(line);return 0;}}
 free(line);return 0;
}
'''

class FactoryTests(unittest.TestCase):
    def fixture(self,root):
        source=root/'cpu.c';source.write_text(CPU_SOURCE);binary=root/'cpu-only'
        subprocess.run(['/usr/bin/cc','-O2',str(source),'-o',str(binary)],check=True,capture_output=True,timeout=10);binary.chmod(0o500)
        runtime=root/'hypr-window-motion';runtime.mkdir(mode=0o700);packet=runtime/'offline';packet.mkdir(mode=0o700)
        env=dict(os.environ,XDG_RUNTIME_DIR=str(root),HYPRLAND_INSTANCE_SIGNATURE='offline',WAYLAND_DISPLAY='never-connect',OFFLINE_CPU_EXEC_MARKER=str(root/'marker'))
        guard=SimpleNamespace(env=env,session='offline',verify=lambda:None)
        return binary,packet,env,guard
    def cleanup_failure(self,service,factory):
        service.frontend.close(close_manager=False)
        for actor in service.manager.actors:
            try:actor.controller.workers.shutdown(wait=True,cancel_futures=True)
            except Exception:pass
        if factory.keeper and factory.keeper.process.poll() is None:
            try:factory.keeper.abort()
            except Exception:pass
        service.lease.close()
    def test_actual_native_factory_receipt_gate_and_normal_cpu_retirement(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);binary,packet,env,guard=self.fixture(root)
            with patch.dict(os.environ,env,clear=True):
                digest=hashlib.sha256(binary.read_bytes()).hexdigest();factory=NativeFactory(packet,guard,producer=binary,producer_hash=digest,core=binary,core_hash=digest)
                service=RuntimeService(packet,'offline',factory,lambda request:None)
                try:
                    writes=[];original=service.store.write
                    def inspect(body):
                        for record in body['actorResources']:
                            if record['phase']=='gated':self.assertIsNotNone(record['renderer'])
                        if body['helperOwnership']['jobs'] and body['helperOwnership']['jobs'][0]['phase']=='released' and body['actorResources'][0]['phase']=='gated':
                            self.assertFalse((root/'marker').exists());self.assertEqual(body['actorResources'][0]['phase'],'gated')
                        writes.append(body['snapshot']);original(body)
                    service.store.write=inspect
                    acceptance=service.manager.reserve('minimize','0xaa','aa',41)
                    self.assertEqual(acceptance['receipt'],1);archived=service.store.read();self.assertEqual(archived['pending'][0]['actor'],1)
                    self.assertTrue(unresolved(archived));self.assertEqual(archived['helperOwnership']['jobs'][0]['kind'],'renderer')
                    service.store.write=original
                    service.close();final=service.store.read();self.assertFalse(unresolved(final));self.assertEqual(final['actorResources'][0]['phase'],'closed')
                    self.assertFalse(list((packet/'actors').iterdir()));self.assertEqual(factory.keeper.process.returncode,0);self.assertTrue(factory.keeper.read_terminal()['normalStop'])
                finally:
                    if not service.closed:self.cleanup_failure(service,factory)
    def test_actual_factory_fsync_fault_before_renderer_release_prevents_exec(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);binary,packet,env,guard=self.fixture(root)
            with patch.dict(os.environ,env,clear=True):
                digest=hashlib.sha256(binary.read_bytes()).hexdigest();factory=NativeFactory(packet,guard,producer=binary,producer_hash=digest,core=binary,core_hash=digest)
                service=RuntimeService(packet,'offline',factory,lambda request:None);original=service.store.write
                def fault(body):
                    if any(row['phase']=='gated' for row in body['actorResources']):raise OSError('actual actor ownership fsync fault')
                    original(body)
                service.store.write=fault
                try:
                    with self.assertRaisesRegex(RuntimeError,'fsync fault'):service.manager.reserve('minimize','0xaa','aa',41)
                    self.assertFalse((root/'marker').exists());self.assertTrue(service.manager.persistence_failed);self.assertFalse(service.manager.actors)
                    self.assertFalse(list((packet/'actors').iterdir()))
                finally:self.cleanup_failure(service,factory)

if __name__=='__main__':unittest.main()
