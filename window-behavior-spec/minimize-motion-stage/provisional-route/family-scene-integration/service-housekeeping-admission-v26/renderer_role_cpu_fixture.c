#include <stdio.h>
#include <string.h>
int main(void){char line[65536];setvbuf(stdout,0,_IOLBF,0);puts("{\"event\":\"outputs\",\"outputs\":[{\"name\":\"owned-cpu\",\"generation\":1}]}");while(fgets(line,sizeof line,stdin)){if(strstr(line,"\"stop\""))return 0;puts("{\"event\":\"state\",\"observationId\":\"cpu-owned\"}");}return 0;}
