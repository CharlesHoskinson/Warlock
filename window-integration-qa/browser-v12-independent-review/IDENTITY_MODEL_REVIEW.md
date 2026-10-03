# Strengthened identity model review

The strengthened model SHA
`1af76f5364debc29e56feb2e4ebbb7b7f839f2e9de93e4d4074e396a0862f555`
adds concrete FD/device/inode/mount/profile/parent/root/executable/captured
snapshot/VMA/full-flags tokens and an observation epoch. Changed observations
and invalidation clear partial and usable authority. These changes resolve the
original abstract identity gap; 35 named cases plus2,000×100 are retained by
the implementer before classifier edits.

Final requested refinements:

1. Explicit required `noOPath` guard. `fdAccess=2` is the O_ACCMODE abstraction;
   `fullFlags>=0` does not exclude O_PATH. The saved model and additive named
   counterexample show a witness with fullFlags2097154 can reach inputUsable.
   This is a real current-model admission, not evidence of an actual FD or
   runtime acceptance. Runtime must derive both guards from the same fdinfo.
2. Exact selected FD readlink target token. The contract requires target
   equality before/after; preserve that distinct witness in the model.
3. Verify and post-disk confirm valid replacements for each concrete identity
   token, plus required guard refusal. Existing token tests cover verify;
   confirmation currently tests only changed root lifetime.

The captured snapshot token binds the original raw root-map hash and selected
line to proof consumption. Fresh whole-map hashes need not be equal when
unrelated legitimate mappings change; fresh selected VMA must be exact and
all bounded executable-alias checks must pass. Writable data/file-position and
mtime/ctime intentionally are not part of the immutable projection. No global
or continuous unchanged-object claim follows from these observations.

No root files were edited. Runtime/native authority remains root-owned.
