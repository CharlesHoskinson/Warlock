# Explicit private X11 fixture contract

This adapter is confined to the private Qt X11 campaign. Frozen HostV4 and its default Xwayland-disabled configuration remain unchanged. The reviewed Lua is followed by explicit Xwayland enabled and create_abstract_socket=false. Parent Weston/Aquamarine, scope/core1, runtime ownership, and complete IPC readiness retain HostV4 behavior.

The compositor alone chooses the X display and creates its standard filesystem listener. A private PATH Xwayland launcher validates the exact owned QA runtime, QA scope/core1, direct Hyprland parent executable/configuration, full upstream argument shape, actual inherited listener/Wayland/WM descriptors and DISPLAY agreement. It adds only -auth with an owned0600 real MIT-MAGIC-COOKIE-1 authority file and execs the unchanged installed /usr/bin/Xwayland. No main DISPLAY or authority is inherited; no -ac and no main/global authentication fallback.

Before Qt launch the session captures direct server PID/start/PGID, unchanged executable, exact display and argv, private runtime, real authority flag/file metadata, selected lock containing this compositor PID, stable socket path/inode, and matching listening kernel FD in both compositor and server. SO_PEERCRED may identify the compositor that created the socket; that is recorded honestly and must match the captured compositor. Complete bounded X11 setup without a cookie must be refused; setup with the private cookie must return actual protocol11 success. Cookies are never included in evidence, logs or archives.

Only clients launched with this exact DISPLAY and XAUTHORITY use xcb; the pointer remains on the exact private Wayland socket. Qt platform, Xwayland native identity, and actual loaded libqxcb.so/Qt6XcbQpa loader mapping are separate strict gates. All nineteen public Qt callback/modal/family oracles remain required. This proves the private same-process X11 case only.

Cleanup is clients first, diagnostic/native unload next, compositor shutdown next. The exact registered Xwayland child must exit on its private compositor disconnect before the ordinary host cleanup handles Weston and bus. Unknown descendants, forced child termination, replaced identity/socket, retained authorization, or retained display artifacts fail cleanup. Failure cleanup is PID/start guarded and cannot target main apps. Main observations are explicit read-only snapshots; no main restoration writes occur.

Offline tests establish parser, authority encoding, refusal and ownership logic; they do not establish native X11 compatibility. A fresh frozen packet and exclusive root grant are required before any server or GUI launch.

## V2 availability precondition

Official Hyprland executableExistsInPath stops at the first regular candidate and requires its others_exec bit. The owned private launcher therefore has0755 mode within two verified0700 parent directories (runtime and bin). Other users cannot traverse either directory; private credentials remain0600. Launcher source/hash and exact0755 are validated before exec. The failedV1 availability report remains failed and immutable. This changes no installed compositor/Xwayland or default PATH. Missing launcher registration is an explicit startup timeout failure before any client launch.

The exclusive file writer applies fchmod to the already-owned descriptor so the0755 availability bit survives the harness umask077; exact-mode creation is tested. This never changes parent0700 or credential0600 requirements.
