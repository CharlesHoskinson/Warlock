# Settings migration evidence and limits

Original scope: ELM-DEL-015 delivery-015, invalid-settings, interrupted-settings
and migration-failure. Original identities/oracles remain unchanged and are not
accepted by this packet.

The baseline source 333895ca upgrades a real schema-1 file to schema2, returns
Saved and leaves no exact original copy. The baseline script/report preserves
this RED observation. Protected scope 4b20716cb27c4d3a96cfe18cce599414,
invocation 454c78e4c0664e15978baf1f8f76077a, exited 0 because the expected defect
was reproduced, not because migration satisfied its oracle.

Corrected store 702f110efc7db1c5ab45df0fc2910a06891eb0abce5fc4183271dd3538b2bdb4
passes the unchanged 47 settings checks and 327 migration checks. Final protected
scope 76cb1e8e70dc4aac91b146c3e06122f0,
invocation dd7d278edae84adcb63c456be73a4fa6, exited 0. Initial corrected run and
subsequent justified FIFO/restart witness additions remain separately recorded.

Tests execute the production Store against private temporary files. Seven
injected syscall failure points check backup file sync/publication/unlink/directory
sync and active file sync/rename/directory sync. A published backup exists before
active rename; exact original formatting survives restart and later saves.
Unsafe backup paths refuse. FIFO refusal uses child processes with a two-second
observation bound. 100 seeded parameter sequences use seed 0xDE1015 and exercise
invalid proposal, valid upgrade/restart and stale write. This is bounded
parameter/route coverage, not arbitrary event-interleaving fuzz.

Interruption after backup link but before temporary unlink leaves a two-link
backup. Original bytes remain recoverable and active remains old; subsequent
upgrades fail closed. Automatic recovery/cleanup is not implemented. A final
active directory-sync error returns Unknown with complete new visible data;
it is not claimed rolled back or proof of durable commit.

No physical process-kill/power-loss campaign, whole-filesystem guarantee,
frontend/native/keyboard/AT settings journey, deployment or release acceptance
is established. Quint/model correspondence is pending separate evidence.

Diataxis dispositions: reference settings-storage.md added; retrofit how-to and
loop template updated; source-navigation tutorial unaffected because read-only
navigation does not change; ownership-and-lifetimes explanation unaffected
because Elm/native authority is unchanged. Links/commands are checked separately.
Cancellation investigation remains stopped for missing complete durable V7 store;
this independent mandatory settings fix does not reset that investigation.
