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
