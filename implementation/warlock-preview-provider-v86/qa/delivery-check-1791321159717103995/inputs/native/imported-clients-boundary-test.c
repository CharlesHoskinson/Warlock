#include "imported-clients.h"
#include <gio/gio.h>
#include <stdio.h>
static unsigned checks;
static gboolean check(gboolean value){if(!value)return FALSE;++checks;return TRUE;}
int main(void) {
    GError *error=NULL;char *events=(char*)1;void *endpoint=(void*)1;
    if(!check(warlock_imported_clients_open(NULL,(gpointer)1,1,2,1,1,&events,&endpoint,&error)==NULL && !events && !endpoint && error!=NULL))return 1;
    g_clear_error(&error);
    if(!check(!warlock_imported_clients_command(NULL,"family:1","{}",&events,&error) && !events && error!=NULL))return 2;
    g_clear_error(&error);
    if(!check(!warlock_imported_clients_poll(NULL,"family:1",&events,&error) && !events && error!=NULL))return 3;
    g_clear_error(&error);
    if(!check(!warlock_imported_clients_uri(NULL,"family:1",&events,&error) && !events && error!=NULL))return 4;
    g_clear_error(&error);
    if(!check(!warlock_imported_clients_status(NULL,&events,&error) && !events && error!=NULL))return 5;
    g_clear_error(&error);
    if(!check(!warlock_imported_clients_empty(NULL) && warlock_imported_clients_close(NULL,&error) && !error))return 6;
    printf("{\"passed\":true,\"checks\":%u,\"nativeAcceptance\":false,\"scope\":\"Actual C ABI missing-owner rejection; actual native two-entry bridge remains separately required\"}\n",checks);
    return 0;
}
