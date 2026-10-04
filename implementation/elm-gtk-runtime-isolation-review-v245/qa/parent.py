import hashlib, json, resource, subprocess, time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
r = Path(__file__).resolve().parents[1]
p = r.parent / 'elm-parent-keyboard-surface-observer-v239/native/parent-input-client.c'
t = p.read_text()
body = t[t.index('static bool private_socket('):t.index('static bool send_request(')]
o = r / 'qa' / ('parent-' + str(time.time_ns()))
o.mkdir()
(o / 'actual-function.c').write_text(body)
c = r'''#define _DEFAULT_SOURCE
#include <sys/stat.h>
#include <unistd.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>
static const char *runtime,*socket;
static const char *fake_env(const char *key){if(!strcmp(key,"XDG_RUNTIME_DIR"))return runtime;if(!strcmp(key,"WAYLAND_DISPLAY"))return socket;if(!strcmp(key,"ELM_PARENT_INPUT_QA"))return "1";return NULL;}
static int fake_stat(const char *path,struct stat *st){(void)path;memset(st,0,sizeof *st);st->st_uid=geteuid();st->st_mode=S_IFSOCK|0600;return 0;}
#define getenv fake_env
#define lstat fake_stat
#include "actual-function.c"
int main(void){char paths[4][128];snprintf(paths[0],128,"/run/user/%u/wqa/isolated",getuid());snprintf(paths[1],128,"/run/user/%u/wqa/..",getuid());snprintf(paths[2],128,"/run/user/%u",getuid());snprintf(paths[3],128,"/arbitrary/runtime");for(int i=0;i<4;i++){runtime=paths[i];socket="wayland-owned";printf("%d %d %s\n",i,private_socket(),runtime);}runtime=NULL;socket="/arbitrary/owned-socket";printf("4 %d %s\n",private_socket(),socket);return 0;}
'''
(o / 'test.c').write_text(c)
a = subprocess.run(['/usr/bin/cc', '-std=c11', '-Wall', '-Wextra', '-Werror', str(o / 'test.c'), '-o', str(o / 'guard')], capture_output=True, timeout=30)
(o / 'compile.stderr').write_bytes(a.stderr)
assert a.returncode == 0, a.stderr
b = subprocess.run([str(o / 'guard')], capture_output=True, timeout=5)
(o / 'actual.stdout').write_bytes(b.stdout)
assert b.returncode == 0
rows = b.stdout.decode().splitlines()
assert [int(x.split()[1]) for x in rows] == [1] * 5
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
report = {'diagnosisConfirmed': True, 'nativeAcceptance': False, 'sourceSHA256': sha(p), 'scriptSHA256': sha(Path(__file__)), 'scope': 'Actual private_socket with environment and owned-socket stat stubs; no display connection', 'actualRows': rows}
(o / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(str(o / 'report.json'))
