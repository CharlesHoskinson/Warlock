"""Protected CPU build of the actual xdg-shell SHM maximize client fixture."""
import hashlib
import json
from pathlib import Path
import shutil
import shlex
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = Path('/usr/share/wayland-protocols/stable/xdg-shell/xdg-shell.xml')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def state_tests(source, out, generated, compiler, flags, run, report):
    def cut(start, end):
        return source[source.index(start):source.index(end, source.index(start))]
    client = cut('struct client {', 'static uint64_t stamp(')
    logging = cut('static uint64_t stamp(', 'static void refuse(')
    configure = cut('static void surface_configure(', 'static const struct xdg_surface_listener')
    staged = cut('static void toplevel_configure(', 'static void close_toplevel(')
    registry = cut('static void registry_global(', 'static void global_removed(')
    test = r'''
#define _POSIX_C_SOURCE 200809L
#include <stdbool.h>
#include <stdint.h>
#include <inttypes.h>
#include <string.h>
#include <stdio.h>
#include <time.h>
#include <wayland-client.h>
#include "xdg-shell-client.h"
struct buffer;struct barrier;
''' + client + logging + r'''
static uint32_t ack;
static unsigned commits, refused_count, bindings, bound_version;
static void refuse(struct client *client,const char *reason){(void)reason;++refused_count;client->failed=true;client->quit=true;}
static void test_ack(struct xdg_surface *surface,uint32_t serial){(void)surface;ack=serial;}
#define xdg_surface_ack_configure test_ack
static bool commit_buffer(struct client *client){if(client->acked!=ack)return false;++commits;event(client,"buffercommit",NULL);return true;}
''' + configure + staged + r'''
static const struct xdg_wm_base_listener wm_listener={0};
static void *test_bind(struct wl_registry *registry,uint32_t name,const struct wl_interface *interface,uint32_t version){(void)registry;(void)name;(void)interface;++bindings;bound_version=version;return (void *)(uintptr_t)1;}
#define wl_registry_bind test_bind
static int test_listener(struct xdg_wm_base *wm,const struct xdg_wm_base_listener *listener,void *data){(void)wm;(void)listener;(void)data;return 0;}
#define xdg_wm_base_add_listener test_listener
''' + registry + r'''
static unsigned checks;
static bool check(bool value,const char *name){++checks;if(!value)fprintf(stderr,"FAIL %s\n",name);return value;}
#define CHECK(v,n) if(!check((v),(n)))return 1
int main(void){
 struct client c={.width=320,.height=180,.ordinary_width=320,.ordinary_height=180};
 for(uint32_t version=1;version<6;++version){registry_global(&c,NULL,4,"xdg_wm_base",version);CHECK(!c.wm&&!bindings,"pre-v6 cannot qualify suspend readiness");}
 registry_global(&c,NULL,4,"xdg_wm_base",6);CHECK(c.wm&&bindings==1&&bound_version==6,"actual v6 bound exactly");
 registry_global(&c,NULL,4,"xdg_wm_base",7);CHECK(bindings==1,"duplicate registry announcement cannot replace bound role");
 struct client newer={0};registry_global(&newer,NULL,4,"xdg_wm_base",9);CHECK(newer.wm&&bound_version==6,"newer role bounded to supported v6");
 uint32_t max_suspended[]={XDG_TOPLEVEL_STATE_MAXIMIZED,XDG_TOPLEVEL_STATE_SUSPENDED};
 struct wl_array states={.size=sizeof max_suspended,.alloc=sizeof max_suspended,.data=max_suspended};
 toplevel_configure(&c,NULL,798,598,&states);
 CHECK(c.pending_maximized&&!c.pending_fullscreen&&c.pending_suspended&&!c.maximized&&!c.suspended&&c.width==320,"staged flags cannot alter current before surface ACK");
 surface_configure(&c,NULL,41);
 CHECK(c.maximized&&!c.fullscreen&&c.suspended&&c.serial==41&&c.acked==41&&ack==41&&commits==1,"MAX plus SUSPENDED promotes only with ACK");
 uint32_t full_suspended[]={XDG_TOPLEVEL_STATE_FULLSCREEN,XDG_TOPLEVEL_STATE_SUSPENDED};states.data=full_suspended;states.size=sizeof full_suspended;
 toplevel_configure(&c,NULL,800,600,&states);CHECK(c.maximized&&c.suspended&&c.pending_fullscreen&&!c.pending_maximized,"next stage retains prior committed snapshot");
 surface_configure(&c,NULL,42);CHECK(!c.maximized&&c.fullscreen&&c.suspended&&commits==2,"FULLSCREEN and SUSPENDED independently promoted");
 uint32_t max_only[]={XDG_TOPLEVEL_STATE_MAXIMIZED};states.data=max_only;states.size=sizeof max_only;
 toplevel_configure(&c,NULL,798,598,&states);surface_configure(&c,NULL,43);
 CHECK(c.maximized&&!c.fullscreen&&!c.suspended&&!c.pending_suspended&&commits==3,"restore-minimized MAX clears suspended at fresh ACK");
 states.data=NULL;states.size=0;toplevel_configure(&c,NULL,320,180,&states);surface_configure(&c,NULL,44);
 CHECK(!c.maximized&&!c.fullscreen&&!c.suspended&&c.width==320&&c.height==180&&commits==4,"ordinary geometry clears all flags");
 states.size=1;toplevel_configure(&c,NULL,320,180,&states);CHECK(c.failed&&refused_count==1,"malformed state array refused");
 surface_configure(&c,NULL,45);CHECK(commits==4,"refused lifecycle cannot create new queued buffer");
 fprintf(stderr,"checks %u\n",checks);return 0;
}
'''
    variants = [('actual',test),
        ('unsafe-ignore-suspended',test.replace('client->pending_suspended |= value == XDG_TOPLEVEL_STATE_SUSPENDED;', '')),
        ('unsafe-omit-ACK-promotion',test.replace('client->suspended = client->pending_suspended;', '')),
        ('unsafe-retain-suspended-stage',test.replace('client->pending_suspended = false;', '')),
        ('unsafe-v5-readiness',test.replace('!client->wm && version >= 6)', '!client->wm && version >= 1)'))]
    results=[]
    for name, text in variants:
        if name!='actual' and text==test: raise RuntimeError('Mutation did not change actual extraction: '+name)
        directory=out/name;directory.mkdir();path=directory/'state-test.c';path.write_text(text)
        binary=directory/'test'
        run(name+'-compile',[str(compiler),'-std=c11','-O2','-Wall','-Wextra','-Werror','-I'+str(generated),str(path),str(generated/'xdg-shell-protocol.c'),*flags,'-o',str(binary)])
        result=subprocess.run([str(binary)],capture_output=True,text=True,timeout=5)
        (directory/'stdout').write_text(result.stdout);(directory/'stderr').write_text(result.stderr)
        expected=0 if name=='actual' else 1
        if result.returncode!=expected:raise RuntimeError('State witness mismatch '+name+': '+result.stderr)
        if name=='actual':
            packets=[json.loads(line) for line in result.stdout.splitlines()]
            configurations=[x for x in packets if x['event']=='configure']
            buffers=[x for x in packets if x['event']=='buffercommit']
            wanted=[(True,False,True),(False,True,True),(True,False,False),(False,False,False)]
            for rows in [configurations,buffers]:
                if len(rows)!=4 or [(x['maximized'],x['fullscreen'],x['suspended']) for x in rows]!=wanted or [x['ackedSerial'] for x in rows]!=[41,42,43,44]:
                    raise RuntimeError('Actual emitted configure/buffer state JSON mismatch')
        results.append({'name':name,'passed':True,'exitCode':result.returncode,'stderr':result.stderr})
    report['stateTests']={'passed':True,'scope':'Actual extracted client callbacks/event serializer/registry gate with mocked ACK/commit wire calls; no server or GUI', 'checks':results}


def main():
    sys.path.insert(0, '/home/hoskinson/window-integration-qa')
    from qa_launch import require_qa_scope
    qa_scope = require_qa_scope()
    out = ROOT / 'qa' / ('client-build-' + str(time.time_ns()))
    out.mkdir(mode=0o700)
    inputs = out / 'inputs'
    inputs.mkdir(mode=0o700)
    paths = [ROOT / 'qa/xdg-max-client.c', Path(__file__).resolve(), ROOT/'upstream.json', PROTOCOL]
    hashes = {str(path): digest(path) for path in paths}
    for path in paths:
        target = inputs / path.name
        shutil.copy2(path, target)
        target.chmod(0o400)
    scanner = Path('/usr/bin/wayland-scanner').resolve()
    compiler = Path('/usr/bin/cc').resolve()
    report = {'passed': False, 'scope': 'real Wayland/xdg-shell client compile only; no server/GUI/native geometry claim',
              'qaScope': qa_scope, 'inputs': hashes, 'commands': [],
              'tools': {str(path): digest(path) for path in [scanner, compiler, Path('/usr/bin/pkg-config').resolve()]}}
    generated = out / 'generated'
    generated.mkdir(mode=0o700)
    def run(name, command):
        result = subprocess.run(command, capture_output=True, text=True, cwd=out, timeout=60)
        (out / (name + '.stdout')).write_text(result.stdout)
        (out / (name + '.stderr')).write_text(result.stderr)
        report['commands'].append({'name': name, 'command': list(map(str, command)), 'exitCode': result.returncode})
        if result.returncode:
            raise RuntimeError(name + ' failed')
        return result.stdout
    try:
        run('scanner-version', [str(scanner), '--version'])
        run('compiler-version', [str(compiler), '--version'])
        run('client-header', [str(scanner), 'client-header', str(inputs / PROTOCOL.name), str(generated / 'xdg-shell-client.h')])
        run('protocol-code', [str(scanner), 'private-code', str(inputs / PROTOCOL.name), str(generated / 'xdg-shell-protocol.c')])
        flags = shlex.split(run('client-flags', ['/usr/bin/pkg-config', '--cflags', '--libs', 'wayland-client']))
        binary = out / 'xdg-max-client'
        run('client-build', [str(compiler), '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror', '-Wl,-z,defs',
                            '-I' + str(generated), '-MD', '-MF', str(out / 'client.d'),
                            str(inputs / 'xdg-max-client.c'), str(generated / 'xdg-shell-protocol.c'), *flags, '-o', str(binary)])
        state_tests((inputs/'xdg-max-client.c').read_text(), out, generated, compiler, flags, run, report)
        # Separate compile dependencies for both translation units; combined -MF
        # reports only the final unit on GCC, so obtain each exact dependency set.
        dependency_files = []
        for name, source in [('client', inputs / 'xdg-max-client.c'), ('protocol', generated / 'xdg-shell-protocol.c')]:
            target = out / (name + '-dependencies.d')
            run(name + '-dependencies', [str(compiler), '-std=c11', '-I' + str(generated), '-M', '-MF', str(target), str(source), *[flag for flag in flags if flag.startswith('-I')]])
            dependency_files.append(target)
        dependencies = set()
        for path in dependency_files:
            text = path.read_text().replace('\\\n', ' ')
            dependencies.update(text.split(':', 1)[1].split())
        report['dependencies'] = {str(Path(path).resolve()): digest(path) for path in sorted(dependencies)}
        linked = run('linked-libraries', ['/usr/bin/ldd', str(binary)])
        libraries = []
        for line in linked.splitlines():
            for word in line.split():
                if word.startswith('/') and Path(word).is_file():
                    libraries.append(Path(word).resolve())
        report['linkedLibraries'] = {str(path): digest(path) for path in sorted(set(libraries))}
        for path, expected in hashes.items():
            if digest(path) != expected:
                raise RuntimeError('Live fixture source changed during build: ' + path)
        report.update(client=str(binary), clientSHA256=digest(binary), generated={str(path.relative_to(out)): digest(path) for path in generated.iterdir()}, passed=True)
    except Exception as error:
        report['error'] = repr(error)
    report['artifacts'] = {str(path.relative_to(out)): digest(path) for path in sorted(out.rglob('*')) if path.is_file()}
    target = out / 'report.json'
    target.write_text(json.dumps(report, indent=2) + '\n')
    if report['passed']:
        descriptor=ROOT/'client-build-report.json'
        if descriptor.exists():raise RuntimeError('Selected client descriptor already exists')
        descriptor.write_text(json.dumps({'result':'pass','client':report['client'],'clientSHA256':report['clientSHA256'],'buildReport':str(target),'buildReportSHA256':digest(target),'nativeAcceptance':False,'requiresXdgVersion':6,'suspendedStateObserved':True},indent=2)+'\n')
    print(json.dumps({'passed': report['passed'], 'report': str(target), 'client': report.get('client'), 'error': report.get('error')}), flush=True)
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
