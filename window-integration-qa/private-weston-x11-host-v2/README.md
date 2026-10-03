# Explicit X11 host adapter

Fresh campaign only; no native acceptance yet. Default HostV4 and all preceding frozen packets remain unchanged. This adapter subclasses HostV4 for the same AQ/Weston/scope/read-only IPC behavior. Its isolated entry method preserves the base discovery sequence while adding X11-only config, private PATH launcher and exact server registration.

Source: official Hyprland v0.56.2 Server.cpp (captured here) forks a direct child and uses `/bin/sh -c 'exec Xwayland …'`; PATH therefore selects the owned runtime launcher. Upstream supplies no authentication file. Installed Xwayland help confirms `-auth file`; this adapter adds a real private authority instead of claiming upstream auth. Listener credentials identify the private compositor that created the listeners, not an invented server credential identity.

Preparation: 21 scoped offline checks including exact primary availability predicate and umask077 creation, actual help-only Xwayland query, no server/client startup. Final report offline-report-2.json retains earlier V2 report. FailedV1 reports remain immutable. The accepted QtV9 actual proof is Wayland; X11 authentication, XCB delivery, modal routing and disconnect cleanup are pending actual reviewed native execution.

The runner uses only the display captured from this exact direct launcher/server. It captures both standard filesystem sockets (abstract sockets disabled), exact compositor-owned lock, stable device/inode plus listening kernel inode present in both processes, actual unchanged executable/argv/core1 and own private environment. It requires missing-cookie refusal and correct-cookie success. Never print cookies; remove QA credentials before runtime archival.

Cleanup calls the compositor stop only after all fixture clients exit and native modules unload. The exact X server must disappear on its parent disconnect. A surviving child is a failure and remains subject to the base exact-identity fallback; no global process-name whitelist is added. Main observations are read-only and no main input/state restoration is performed.
