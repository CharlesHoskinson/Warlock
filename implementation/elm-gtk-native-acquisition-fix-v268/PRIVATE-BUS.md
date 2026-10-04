# Private activation lifetime correction

The failed238 private bus activated actual portals, accessibility and GVfs. Their
unregistered children cannot be ignored or labeled normal merely because they
vanish. This derivative proposes a private service-directory overlay, with the
same service names and actual Exec argv, whose activation launcher supervises
and journals each real process. Installed service definitions remain untouched.

Each launcher is an isolated process group and Linux child subreaper. It records
owned PID/start/UID, real argv and every observed descendant before signalling.
It reaps actual wait statuses; SIGTERM/SIGKILL are cancellation/fallback, never
normal exit. Its journal is retained outside runtime removal. DBus activation double-forks,
so direct wrapper-to-daemon parenthood is not assumed; exact launcher argv,
descriptor hash, private runtime and authenticated bus GUID are checked. A private-bus name
must separately authenticate with GetConnectionUnixProcessID/GetConnectionUnixUser
and match a live journaled service child. Discovery alone grants no ownership.

Before inherited host cleanup, stop only authenticated activation launchers,
wait for their terminal journals and verify no live descendants remain. Existing
unexpected-descendant detection remains active. A missing terminal, unmatched
connection, replaced PID/start, extra descendant or expired original cleanup
budget fails. No fabricated Popen proxy return code and no PID-only whitelist.

The actual private-bus CPU slice qualifies service overlay generation, actual
name/PID/start/UID authentication, real cancellation wait status and daemon exit.
Fresh owned_bus_host.py integrates activation environment update and bounded
pre-cleanup drain, but that native wiring remains unlaunched and requires review. Native3s, scenario6s and original
cleanup bounds remain. Continuous Vulkan commits retain the original capture
oracle pending an independently reviewed presentation contract.
