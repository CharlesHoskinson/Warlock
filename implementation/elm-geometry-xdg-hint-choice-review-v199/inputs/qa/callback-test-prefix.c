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
