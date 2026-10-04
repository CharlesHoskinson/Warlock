"""Compile actual ancestor/candidate teardown block with deterministic API doubles.

No GTK/display/process launch: witnesses ordering, one cap and forced uncertainty,
not actual compositor protocol or child exit acceptance.
"""
import hashlib,json,resource,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
REPO=next(p for p in ROOT.parents if (p/'AGENTS.md').is_file())
OLD=REPO/'implementation/elm-shared-context-disposition-wire-v132/native/host.c'
NEW=ROOT/'native/host.c'
OUT=ROOT/'qa'/('shutdown-'+str(time.time_ns()));OUT.mkdir()
shutil.copy2(__file__,OUT/'test.py')
def block(path):
 text=path.read_text();start=text.rindex('    if (backend) {')
 return text[start:text.index('\n    g_queue_clear_full',start)]
prelude='''
#include <assert.h>
#include <stddef.h>
#include <stdio.h>
typedef long long gint64;
#define FALSE 0
#define TRUE 1
static int backend=1,backend_done,backend_source,failed,forced,closed,io_cancel=1;
static char *active_request;
static gint64 now,completes;
static int needs_drain,storm;
static gint64 g_get_monotonic_time(void){return now;}
static void g_cancellable_cancel(int value){(void)value;}
static void g_source_remove(int value){(void)value;backend_source=0;}
static void g_usleep(int value){now+=value;}
static int g_main_context_iteration(void *context,int wait){
 (void)context;(void)wait;
 if(storm){now+=1000;return 1;}
 if(now>=completes && (!needs_drain || backend_source))backend_done=1;
 return 0;
}
static int g_subprocess_get_stdin_pipe(int child){return child;}
static void g_output_stream_close(int fd,void *cancel,void *error){(void)fd;(void)cancel;(void)error;closed=1;}
static void g_subprocess_force_exit(int child){(void)child;forced=1;}
static void g_subprocess_wait(int child,void *cancel,void *error){(void)child;(void)cancel;(void)error;}
static void run(void){
'''
report={'passed':False,'scope':'Actual C host teardown blocks with deterministic time/drain API doubles; no GUI or native process claim','checks':[]}
def check(name,condition):report['checks'].append({'name':name,'passed':bool(condition)});assert condition,name
try:
 for name,path in [('ancestor',OLD),('candidate',NEW)]:
  shutil.copy2(path,OUT/(name+'-host.c'))
  program=prelude+block(path)+'''\n}
int main(int argc,char **argv){
 (void)argv;
 if(argc==2){storm=1;completes=5000000;active_request="queued";backend_source=1;run();assert(forced && now<=4002000);return 0;}
 completes=2900000;backend_source=1;needs_drain=0;run();
 printf("native3 closed=%d forced=%d done=%d now=%lld\\n",closed,forced,backend_done,now);
 now=0;closed=0;forced=0;failed=0;backend_done=0;backend_source=1;needs_drain=1;run();
 printf("drain closed=%d forced=%d done=%d now=%lld\\n",closed,forced,backend_done,now);
 now=0;closed=0;forced=0;failed=0;backend_done=0;backend_source=1;needs_drain=1;completes=5000000;active_request="unsent";run();
 printf("held closed=%d forced=%d done=%d now=%lld\\n",closed,forced,backend_done,now);
 return 0;
}
'''
  c=OUT/(name+'.c');c.write_text(program);binary=OUT/name
  command=['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(c),'-o',str(binary)]
  result=subprocess.run(command,capture_output=True,text=True,timeout=30)
  (OUT/(name+'.compile.stderr')).write_text(result.stderr);check(name+' actual block compiles',result.returncode==0)
  result=subprocess.run([str(binary)],capture_output=True,text=True,timeout=2)
  (OUT/(name+'.stdout')).write_text(result.stdout)
  rows=[]
  for line in result.stdout.splitlines():
   row={k:int(v) for k,v in (part.split('=') for part in line.split()[1:])};rows.append(row)
  if name=='ancestor':
   check('owning ancestor two-second budget prematurely forces legal native request',rows[0]['forced']==1 and rows[0]['done']==0 and rows[0]['closed']==1)
   check('owning ancestor removed reader before bounded completion',rows[1]['forced']==1 and rows[1]['done']==0)
   timed_out=False
   try:subprocess.run([str(binary),'storm'],capture_output=True,timeout=.3)
   except subprocess.TimeoutExpired:timed_out=True
   check('ancestor ready-callback storm bypasses its outer time cap',timed_out)
  else:
   check('candidate allows existing native3 deadline completion',rows[0]['forced']==0 and rows[0]['done']==1 and rows[0]['closed']==1)
   check('candidate drains while awaiting normal completion',rows[1]['forced']==0 and rows[1]['done']==1)
   check('one global shutdown bound including write-close stays below original five-second fixture cap',rows[2]['now']<=4000000)
   check('receipt withheld beyond shutdown is forced uncertainty not normal completion',rows[2]['forced']==1 and rows[2]['done']==0 and rows[2]['closed']==1)
   storm=subprocess.run([str(binary),'storm'],capture_output=True,timeout=1)
   check('candidate inner drain loops enforce the same global cap under callback storm',storm.returncode==0)
 report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'report':str(OUT/'report.json'),'error':report.get('error')}))
raise SystemExit(not report['passed'])
