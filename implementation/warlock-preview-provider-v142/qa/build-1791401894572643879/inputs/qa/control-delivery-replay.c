#include "preview-control-delivery.h"
#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>

static const char *packet(guint code) {
    switch(code){case 1:return "packet-one";case 2:return "changed-one";case 3:return "packet-two";case 4:return "packet-three";case 5:return "packet-max";default:return "";}
}
static guint bytes(const char *text) {
    for(guint i=1;i<=5;++i)if(!strcmp(text,packet(i)))return i;
    return 0;
}
int main(void) {
    PreviewControlDelivery state={0};const PreviewControlGrant owner={17,18,19,77,1};
    if(!preview_control_delivery_init(&state,owner))return 2;
    guint64 pending=0,invoked=0;guint decision=0;char event[128];
    while(fgets(event,sizeof(event),stdin)) {
        event[strcspn(event,"\r\n")]='\0';
        if(!strcmp(event,"Boundary")) {state.prefix.delivered=G_MAXUINT64-1;state.prefix.ordered=TRUE;}
        else if(!strcmp(event,"Finish"))decision=preview_control_delivery_complete(&state,pending)?3:0;
        else if(!strcmp(event,"WrongFinish"))decision=preview_control_delivery_complete(&state,pending==G_MAXUINT64?0:pending+1)?3:0;
        else if(!strcmp(event,"Reinitialize"))decision=preview_control_delivery_init(&state,owner)?3:0;
        else {
            guint64 ordinal=1;guint code=1;PreviewControlGrant actual=owner;
            const char *wire=NULL;gsize length=0;char oversized[4098];
            if(!strcmp(event,"Packet1")){}
            else if(!strcmp(event,"Packet1Changed"))code=2;
            else if(!strcmp(event,"Packet2")){ordinal=2;code=3;}
            else if(!strcmp(event,"Packet3")){ordinal=3;code=4;}
            else if(!strcmp(event,"PacketMax")){ordinal=G_MAXUINT64;code=5;}
            else if(!strcmp(event,"Wrap")){}
            else if(!strcmp(event,"WrongReceiver"))actual.receiver++;
            else if(!strcmp(event,"WrongEpoch"))actual.epoch++;
            else if(!strcmp(event,"WrongBinding"))actual.frontend++;
            else if(!strcmp(event,"Empty")){wire="";length=0;}
            else if(!strcmp(event,"Oversize")){memset(oversized,'X',4097);oversized[4097]='\0';wire=oversized;length=4097;}
            else return 2;
            if(!wire){wire=packet(code);length=strlen(wire);}
            decision=preview_control_delivery_receive(&state,actual,ordinal,wire,length);
            if(decision==PREVIEW_CONTROL_INVOKE){invoked++;pending=ordinal;}
        }
        printf("{\"delivered\":\"%" PRIu64 "\",\"pending\":\"%" PRIu64 "\",\"wire\":%u,\"latest\":%u,\"inFlight\":%s,\"invoked\":%" PRIu64 ",\"decision\":%u,\"receipt\":\"%" PRIu64 "\"}\n",
            (uint64_t)state.prefix.delivered,(uint64_t)pending,bytes(state.prefix.inFlight?state.pending:state.latest),bytes(state.latest),state.prefix.inFlight?"true":"false",(uint64_t)invoked,decision,(uint64_t)preview_control_delivery_receipt(&state));
    }
    return ferror(stdin)?2:0;
}
