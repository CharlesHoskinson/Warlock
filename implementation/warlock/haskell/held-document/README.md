# Held Elm document snapshots

This Haskell preparation library reads a pinned Elm document through held Linux
file descriptors and returns the same verified immutable bytes used to derive its
CSP hashes. It replaces checking a pathname and reopening it later. It is not a
complete platform manifest, GUI host or accepted delivery scenario.

`Warlock.Platform.Resolver` exposes the production facade: trusted root custody,
identity/path/link pins and `resolveSnapshot`. Test hooks and alternate procfs
bootstrap remain in the internal module. `Warlock.Http.Document.prepareHtml`
requires the caller's root, reviewed pins, relative path, exact size and SHA256;
it preserves the exact supported Elm compiler wrapper and derives script/style
hashes from the returned bytes. No path is reopened after validation.

Acquire the trusted root with `withRoot`, call `prepareHtml` inside its scope,
then retain only the returned bytes and hashes. Serve those bytes and construct
policy from those hashes. The caller must establish root/pin/content authority;
checking arbitrary runtime metadata does not supply that authority. Same-user
adversarial filesystem mutation and complete loader binding remain outside the
qualified contract.

`test/Main.hs` contains thirteen directed controls for immutable bytes/CSP,
wrong hashes, FIFO and inode/symlink swaps, discriminating declared-size changes,
and synchronous/asynchronous cleanup. The internal descriptor reader returns
bytes only after consuming-handle closure succeeds. Read the bounded premises and
retained failed runs in [qualification.json](qualification.json).

The retained protected direct GHC build used GHC9.6.7, unix2.8.6.0,
cryptohash-sha2560.11.102.1, hsc2hs and installed GLib headers/libraries. The corrected Cabal definition also passed a fresh private offline build with
repositories disabled and thirteen tests. The project explicitly selected
`--with-hsc2hs=/usr/bin/hsc2hs` and dynamic GHC linking; the compiler preprocessor
remains a pinned toolchain input. The package definition no longer requires an
unavailable package-index executable for that already selected compiler tool.
This verifies the package build path using installed host dependencies; it does
not establish two clean reproducible builds, source closure or a release. Root serializes any checks through the existing protected QA launcher.
Do not run the library's tests as a native campaign or infer browser acceptance.

This README provides API reference, a caller integration how-to and the ownership
explanation. A user tutorial awaits accepted GUI behavior; the existing original
EARS/OpenSpec register, native/resource/AT/IME obligations and stopped histories
are unchanged. Qualification does not reset product progress or accept DEL003.
