
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
    if (backend) {
        if (io_cancel) g_cancellable_cancel(io_cancel);
        /* Keep draining stdout while the child handles normal stdin EOF.
         * Removing the reader first can itself block delivery and child exit. */
        gint64 write_until=g_get_monotonic_time()+500000;
        while (active_request && g_get_monotonic_time()<write_until) { while (g_get_monotonic_time()<write_until && g_main_context_iteration(NULL,FALSE)) {} g_usleep(1000); }
        g_output_stream_close(g_subprocess_get_stdin_pipe(backend),NULL,NULL);
        /* One process-drain cap, not a fresh deadline for queued operations.
         * Native requests retain their own 3s deadline. A receipt held past
         * this cap remains conservative journal uncertainty, never replay. */
        gint64 backend_until=g_get_monotonic_time()+3500000;
        while (!backend_done && g_get_monotonic_time()<backend_until) { while (!backend_done && g_get_monotonic_time()<backend_until && g_main_context_iteration(NULL,FALSE)) {} g_usleep(1000); }
        if (!backend_done) { failed=TRUE;g_subprocess_force_exit(backend);g_subprocess_wait(backend,NULL,NULL); }
        if (backend_source) { g_source_remove(backend_source);backend_source=0; }
    }
}
int main(int argc,char **argv){
 (void)argv;
 if(argc==2){storm=1;completes=5000000;active_request="queued";backend_source=1;run();assert(forced && now<=4002000);return 0;}
 completes=2900000;backend_source=1;needs_drain=0;run();
 printf("native3 closed=%d forced=%d done=%d now=%lld\n",closed,forced,backend_done,now);
 now=0;closed=0;forced=0;failed=0;backend_done=0;backend_source=1;needs_drain=1;run();
 printf("drain closed=%d forced=%d done=%d now=%lld\n",closed,forced,backend_done,now);
 now=0;closed=0;forced=0;failed=0;backend_done=0;backend_source=1;needs_drain=1;completes=5000000;active_request="unsent";run();
 printf("held closed=%d forced=%d done=%d now=%lld\n",closed,forced,backend_done,now);
 return 0;
}
