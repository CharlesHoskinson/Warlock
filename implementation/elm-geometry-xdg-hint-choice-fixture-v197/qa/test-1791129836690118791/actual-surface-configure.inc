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
