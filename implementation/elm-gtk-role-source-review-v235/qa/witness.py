import hashlib,json,resource,shlex,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=Path(__file__).resolve().parents[1];o=r.parent/'elm-gtk-role-journal-fixture-v233';p=o/'native/gtk-role-client.c';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(o/'component-manifest.json')=='58d33306a1234548059ff9ec36975f1c8c0cbd8d1fe5c676f735ed379739bc1d'
text=p.read_text();body=text[text.index('static gboolean private_environment('):text.index('\nint main(')]
out=r/'qa'/('witness-'+str(time.time_ns()));out.mkdir();(out/'actual-function.c').write_text(body+'\n')
source='''#define _POSIX_C_SOURCE 200809L
#include <glib.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
static const char *runtime;
static gboolean protected_scope(void){return TRUE;}
static const char *fake_env(const char *key){if(!strcmp(key,"XDG_RUNTIME_DIR"))return runtime;if(!strcmp(key,"WAYLAND_DISPLAY"))return "wayland-owned";if(!strcmp(key,"ELM_GTK_ROLE_QA"))return "1";if(!strcmp(key,"GDK_BACKEND"))return "wayland";if(!strcmp(key,"WAYLAND_DEBUG"))return "client";return NULL;}
static int fake_stat(const char *path,struct stat *st){memset(st,0,sizeof *st);st->st_uid=getuid();st->st_mode=(!strcmp(path,runtime)?S_IFDIR|0700:S_IFSOCK|0600);return 0;}
#define getenv fake_env
#define lstat fake_stat
#include "actual-function.c"
int main(void){char paths[4][128];snprintf(paths[0],128,"/run/user/%u/wqa/isolated",getuid());snprintf(paths[1],128,"/run/user/%u/wqa/.",getuid());snprintf(paths[2],128,"/run/user/%u/wqa/..",getuid());snprintf(paths[3],128,"/run/user/%u",getuid());for(unsigned i=0;i<4;i++){runtime=paths[i];printf("%u %d %s\\n",i,private_environment(),runtime);}return 0;}
'''
(out/'test.c').write_text(source);flags=shlex.split(subprocess.check_output(['/usr/bin/pkg-config','--cflags','--libs','glib-2.0']).decode());cmd=['/usr/bin/cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(out/'test.c'),*flags,'-o',str(out/'actual-private')]
a=subprocess.run(cmd,capture_output=True,timeout=30);(out/'compile.stdout').write_bytes(a.stdout);(out/'compile.stderr').write_bytes(a.stderr);assert a.returncode==0,a.stderr
b=subprocess.run([str(out/'actual-private')],capture_output=True,timeout=5);(out/'actual.stdout').write_bytes(b.stdout);(out/'actual.stderr').write_bytes(b.stderr);assert b.returncode==0
rows=[line.split(' ',2) for line in b.stdout.decode().splitlines()];assert [int(row[1]) for row in rows]==[1,1,1,0]
report={'diagnosisConfirmed':True,'nativeAcceptance':False,'scope':'Actual private_environment function compiled with protected-scope/environment/stat precondition stubs; no GTK/display/socket interaction','ownerSourceSHA256':sha(p),'scriptSHA256':sha(Path(__file__)),'cases':[{'runtime':row[2],'actualAccepted':bool(int(row[1])),'expectedPrivateLeaf':i==0} for i,row in enumerate(rows)],'artifacts':{str(p.relative_to(out)):sha(p) for p in out.iterdir() if p.is_file()}}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'diagnosisConfirmed':True,'report':str(out/'report.json'),'acceptedDotComponents':2}))
