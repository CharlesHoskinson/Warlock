#include <errno.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
struct command {uint64_t sequence;char operation[24];char role;};
static bool parse_command(const char *line, struct command *result) {
    if (!line || strlen(line)>511 || !result) return false;
    char text[512];strcpy(text,line);char *save=NULL;
    char *sequence=strtok_r(text," \t\r\n",&save),*operation=strtok_r(NULL," \t\r\n",&save),*role=strtok_r(NULL," \t\r\n",&save),*extra=strtok_r(NULL," \t\r\n",&save);
    if (!sequence || !*sequence || sequence[0]=='0' || !operation || extra) return false;
    for (const char *p=sequence;*p;p++) if (*p<'0' || *p>'9') return false;
    errno=0;char *end;unsigned long long number=strtoull(sequence,&end,10);
    if (errno || *end || number>INT64_MAX || !number) return false;
    bool targeted=!strcmp(operation,"minimize")||!strcmp(operation,"restore")||!strcmp(operation,"maximize")||!strcmp(operation,"unmaximize");
    bool plain=!strcmp(operation,"create-owners")||!strcmp(operation,"open-modal")||!strcmp(operation,"close-modal")||!strcmp(operation,"close-owner")||!strcmp(operation,"create-family")||!strcmp(operation,"open-nested")||!strcmp(operation,"close-nested")||!strcmp(operation,"open-popover")||!strcmp(operation,"close-popover")||!strcmp(operation,"inspect")||!strcmp(operation,"quit");
    if (false || (targeted && (!role || strlen(role)!=1 || (role[0]!='A' && role[0]!='C'))) || (plain && role)) return false;
    result->sequence=number;strcpy(result->operation,operation);result->role=role ? role[0] : 0;return true;
}
