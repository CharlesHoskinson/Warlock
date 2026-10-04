#define main fixture_main
#define surface_configure archived_surface_configure
#include "xdg-origin-client.c"
#undef surface_configure
#undef main
static unsigned acks, commits, failures, checks;
static uint32_t ackserial;
static bool qa_commit(struct client *c){(void)c;++commits;return true;}
static void qa_ack(struct xdg_surface *s,uint32_t serial){(void)s;++acks;ackserial=serial;}
#define commit_buffer qa_commit
#define xdg_surface_ack_configure qa_ack
static void surface_configure(void *data, struct xdg_surface *surface, uint32_t serial) {
    struct client *client = data;
    if (client->quit) return;
    client->serial = serial;
    client->maximized = client->pending_maximized; client->fullscreen = client->pending_fullscreen;
    client->resizing=client->pending_resizing;
    const int fallback_width=client->maximized || client->fullscreen || client->resizing ? client->width : client->ordinary_width;
    const int fallback_height=client->maximized || client->fullscreen || client->resizing ? client->height : client->ordinary_height;
    int chosen_width,chosen_height;
    if(!choose_geometry(&client->profile,client->staged_width,client->staged_height,fallback_width,fallback_height,
        client->maximized,client->fullscreen,client->resizing,&chosen_width,&chosen_height)) {
        char rejected[160];snprintf(rejected,sizeof rejected,",\"configuredWidth\":%d,\"configuredHeight\":%d",client->staged_width,client->staged_height);
        event(client,"configure-refused",rejected);refuse(client,"configure-choice-incompatible");return;
    }
    client->width=chosen_width;client->height=chosen_height;
    if (!client->maximized && !client->fullscreen && !client->resizing) { client->ordinary_width = client->width; client->ordinary_height = client->height; }
    char extra[120];
    snprintf(extra, sizeof extra, ",\"configuredWidth\":%d,\"configuredHeight\":%d", client->staged_width, client->staged_height);
    event(client, "configure", extra);
    xdg_surface_ack_configure(surface, serial);
    client->acked = serial;
    event(client,"ack-configure",NULL);
    if (!commit_buffer(client)) return;
    if (!client->ready) { client->ready = true; char identity[180]; snprintf(identity,sizeof identity,",\"title\":\"%s\",\"appId\":\"elm-xdg-origin-probe\"",client->title); event(client,"ready",identity); }
}
#undef commit_buffer
#undef xdg_surface_ack_configure
#define CHECK(n,c) do{++checks;if(!(c)){++failures;fprintf(stderr,"FAIL %s\n",n);}}while(0)
int main(void){
 struct profile p={.scale=1,.x=16,.y=24,.right=16,.bottom=24,.maxw=400,.maxh=300};
 struct client c={.profile=p,.width=320,.height=180,.ordinary_width=320,.ordinary_height=180,.staged_width=800,.staged_height=600,.ready=true};
 surface_configure(&c,NULL,77);
 CHECK("actual-callback-finite-choice",c.width==400 && c.height==300 && c.staged_width==800 && c.staged_height==600);
 CHECK("actual-callback-exact-ACK",acks==1 && ackserial==77 && c.acked==77 && commits==1 && c.sequence==2 && !c.failed);
 CHECK("actual-callback-ordinary-fallback",c.ordinary_width==400 && c.ordinary_height==300);
 acks=commits=0;c=(struct client){.profile=p,.width=320,.height=180,.ordinary_width=320,.ordinary_height=180,.staged_width=800,.staged_height=600,.ready=true,.pending_maximized=true};
 surface_configure(&c,NULL,78);
 CHECK("actual-callback-MAX-refused-before-ACK",c.failed && c.quit && acks==0 && commits==0 && c.acked==0);
 CHECK("actual-callback-MAX-no-choice-application",c.width==320 && c.height==180 && c.sequence==2);
 acks=commits=0;p.minw=p.maxw=320;p.minh=p.maxh=180;c=(struct client){.profile=p,.width=320,.height=180,.ordinary_width=320,.ordinary_height=180,.staged_width=800,.staged_height=600,.ready=true};
 surface_configure(&c,NULL,79);CHECK("actual-callback-fixed-choice",c.width==320 && c.height==180 && acks==1 && commits==1 && c.acked==79 && !c.failed);
 acks=commits=0;c=(struct client){.profile=p,.width=320,.height=180,.ordinary_width=320,.ordinary_height=180,.staged_width=100,.staged_height=50,.ready=true,.pending_resizing=true};
 surface_configure(&c,NULL,80);CHECK("actual-callback-resize-refused-before-ACK",c.resizing && c.failed && acks==0 && commits==0);
 printf("{\"callbackChecks\":%u,\"failures\":%u}\n",checks,failures);return failures?1:0;
}
