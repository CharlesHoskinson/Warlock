# Private IPC readiness V4

Preserve the V3 mandatory-Wayland/AQ lifecycle binary and unmodified original host V2. Override only the exact owned `hypr/<signature>/.socket.sock` readiness probe. The public `PrivateHyprSession` API and original parent Wayland and other socket readiness remain unchanged.

Before connecting, require the dedicated QA scope, owned short `/run/user/$UID/wqa/<4hex>` runtime, live recorded child PID/start/PGID, exact child launch registration, relative non-symlink IPC path and owned socket inode. Verify `SO_PEERCRED` PID and UID against that exact child. Send only the read-only `j/version` request, consume the complete bounded JSON object reply through server EOF, and verify process/socket identity again before closing and succeeding. No environment variable, inherited selector or main endpoint is used.

Refuse invalid paths, unregistered/dead/replaced processes, replaced socket/peer, non-JSON/truncated/oversized replies and timeouts. Connection readiness may retry before the bounded overall deadline; once connected, malformed response or identity mismatch fails without reconnecting. Owned read-only probes are recorded with request, peer, inode and complete reply hash. No global environment writes.

Tests cover the actual Linux Unix socket/credentials/read/EOF exchange within the scope using an owned Python socket fixture, plus adversarial parser/identity/path cases. They do not establish a real compositor startup; native proof still requires root grant.
