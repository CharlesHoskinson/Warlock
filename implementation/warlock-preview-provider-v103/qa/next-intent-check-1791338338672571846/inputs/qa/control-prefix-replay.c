#include "preview-control.h"
#include <stdio.h>
#include <string.h>
#include <inttypes.h>
int main(void) {
 PreviewControl state={0,FALSE,FALSE};guint64 offered=0;unsigned begun=0;char event[32];
 while(fgets(event,sizeof(event),stdin)) {
  event[strcspn(event,"\n")]=0;
  if(!strcmp(event,"Boundary")){state.delivered=G_MAXUINT64-1;state.ordered=TRUE;}
  else if(!strcmp(event,"Finish")){preview_control_delivered(&state,offered);}
  else {
   guint64 ordinal=!strcmp(event,"Begin1") || !strcmp(event,"Wrap")?1:
    !strcmp(event,"Begin2")?2:!strcmp(event,"Begin3")?3:G_MAXUINT64;
   if(preview_control_next(&state,ordinal)){preview_control_begin(&state,ordinal);offered=ordinal;++begun;}
  }
  printf("{\"delivered\":\"%" PRIu64 "\",\"offered\":\"%" PRIu64 "\",\"begun\":%u,\"inFlight\":%s,\"ordered\":%s}\n",
   (uint64_t)state.delivered,(uint64_t)offered,begun,state.inFlight?"true":"false",state.ordered?"true":"false");
 }
 return 0;
}
