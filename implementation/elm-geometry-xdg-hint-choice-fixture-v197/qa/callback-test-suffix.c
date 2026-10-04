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
