"""Compile the actual callback and reject the previous unsafe callback body."""
import hashlib,json,resource,shutil,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('seat-retirement-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=ROOT/'native/parent-input-module.c';text=source.read_text();start=text.index('static void seat_destroyed(');end=text.index('\nstatic void compositor_destroyed',start);body=text[start:end]
old=ROOT.parent/'elm-parent-input-probe-v12/native/parent-input-module.c';oldtext=old.read_text();oldbody=oldtext[oldtext.index('static void seat_destroyed('):oldtext.index('\nstatic void compositor_destroyed')]
# Independent retirement oracle: pointer delivery is forbidden after owning
# Weston seat retirement, and all held records/listener membership retire.
fixture='''#include <wayland-util.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>
struct probe { void *seat; bool held[3]; struct wl_listener_placeholder { struct wl_list link; } seat_destroy; };
struct wl_listener { struct wl_list link; };
static unsigned deliveries;
static void release_all(struct probe *p) { (void)p; deliveries++; }
'''
# Production wl_listener is layout-compatible for container arithmetic; imported
# wl_list functions/container macro come from actual installed Wayland headers.
fixture=fixture.replace('struct wl_listener_placeholder { struct wl_list link; } seat_destroy;', 'struct wl_listener { struct wl_list link; } seat_destroy;').replace('struct wl_listener { struct wl_list link; };\n','')
main='''
int main(void) {
 for (unsigned mask=0; mask<8; ++mask) {
  struct wl_list listeners; wl_list_init(&listeners);
  struct probe p={.seat=(void*)1};
  for (unsigned i=0;i<3;i++) p.held[i]=(mask & (1u<<i))!=0;
  wl_list_init(&p.seat_destroy.link); wl_list_insert(&listeners,&p.seat_destroy.link);
  deliveries=0; seat_destroyed(&p.seat_destroy,NULL);
  if(deliveries||p.seat||p.held[0]||p.held[1]||p.held[2]||!wl_list_empty(&listeners)||!wl_list_empty(&p.seat_destroy.link)) return 1;
 }
 puts("8 held-button retirement states passed");return 0;
}
'''
checks=[]
for label,actual in [('actual',body),('previous-unsafe',oldbody)]:
 c=OUT/(label+'.c');c.write_text(fixture+actual+main)
 exe=OUT/label;proc=subprocess.run(['/usr/bin/cc','-std=c11','-Wall','-Wextra',str(c),'-lwayland-server','-o',str(exe)],capture_output=True,text=True,timeout=60)
 (OUT/(label+'-compile.log')).write_text(proc.stdout+proc.stderr);assert proc.returncode==0,proc.stderr
 run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=5);(OUT/(label+'-run.log')).write_text(run.stdout+run.stderr)
 checks.append({'name':label,'passed':run.returncode==(0 if label=='actual' else 1),'exitCode':run.returncode,'extractedCallbackSHA256':hashlib.sha256(actual.encode()).hexdigest()})
shutil.copy2(source,OUT/'parent-input-module.c');shutil.copy2(old,OUT/'previous-parent-input-module.c')
report={'passed':all(c['passed'] for c in checks),'nativeAcceptance':False,'scope':'Actual extracted seat-retirement callback, all eight held records and previous unsafe body rejected; not real seat hot-unplug','inputs':{str(source):sha(source),str(old):sha(old),str(Path(__file__)):sha(__file__)},'checks':checks}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json')}));raise SystemExit(not report['passed'])
