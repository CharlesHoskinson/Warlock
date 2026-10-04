/* A single-use native receipt; independent of the seat-grab event. */
typedef struct {
    GtkWidget *source;
    guint64 publication,lease,epoch;
    gint64 captured;
    double px,py,x,y;
    guint key;
    gboolean pointer,pressed,available;
} ContextProof;
static ContextProof context_proof;
static guint held_context_keys;
static guint64 context_epoch;
static GdkRectangle context_anchor;
static gboolean has_context_anchor;
static void context_cancel(void) {
    if(context_epoch<G_MAXUINT64) context_epoch++;
    context_proof.available=FALSE;
    context_proof.pressed=FALSE;
    has_context_anchor=FALSE;
}
