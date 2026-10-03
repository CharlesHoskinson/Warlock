# Registration replacement audit

The failed third native attempt is retained with report SHA
c79239381278698dd4ac4da76119ab2eb9fcfc1af4e3d36ee29fba976849ad15.
It passed 29 reached checks and all 14 main preservation gates. It failed the
signal count after release/reclaim/motion. That check did not retain actual
before/after signal lists, wire serials or owner event times. Its cause cannot
be established retrospectively from the report. Neither a pass nor a product
fix may be inferred from that missing evidence.

Two distinct source paths are possible:

1. The independent Gio caller returns signals() from a GLib stdin IO callback.
   It does not drain queued signal subscription callbacks. A signal already
   received on its GDBus worker may become visible in a later main-context
   callback. The caller's cumulative list alone does not date bridge emission.
2. The native motion hook directly queues a signal using cached registrations
   and pointer epochs. The separate five-millisecond timer dispatches actual
   NameOwnerChanged events and clears pending old epochs. Thus a motion before
   that dispatch can queue a stale notification. The actual extracted source
   test reproduces this possible scheduler order, using the unchanged helper
   and function bodies. It does not identify the order in the native attempt.

libdbus explicitly separates incoming read, outgoing write and incoming dispatch;
dbus_connection_send only enqueues an outgoing message. Gio subscriptions deliver
callbacks in the subscriber's thread-default GLib main context. Primary sources:

- https://dbus.freedesktop.org/doc/api/html/group__DBusConnection.html
- https://docs.gtk.org/gio/method.DBusConnection.signal_subscribe.html

The existing root State correctly clears old epoch pending state when owner
change is applied. The integration scheduler must preserve that contract; a new
model must not permit stale signals to make the current implementation pass.
