# Why terminal storage is insufficient for an ACK

A cancellation receipt must tell the truth after an interrupted operation.
Returning a terminal response and releasing its native slot are different
decisions. The frontend can lose a response, and the host can restart between
writing a file and retiring the pending admission. Releasing the slot too early
would discard the evidence needed to distinguish an old retry from a new action.

The existing durability model requires a sequence of independently confirmed
barriers: store the correlated terminal, sync its file, publish it by rename,
sync the containing directory, retire the exact pending admission, sync the
admissions directory, persist AdmissionRetired, then persist AckPending. Only
then may a matching native ACK release the active slot. Persisting Acknowledged
records the later ACK outcome. A visible rename does not prove its directory
entry is durable. An unlink does not prove its absence is durable.

The terminal identity includes its original owner, complete intent, prepared ID
and deadline. A current delivery binding does not rewrite those originals.
Unknown is diagnostic uncertainty, not a terminal certificate or permission to
repeat an operation. Restart recovery may report retained information; it must
never replay a native mutation automatically.

After ACK, an exact retry must still return its retained terminal until a valid
higher request supersedes it. Reusing an active slot therefore cannot erase its
replay fence. Bounded history must refuse new admission when retaining the fence
is impossible. Persistent generations and a validated restart format are needed
to preserve that property across a process restart; an in-memory list cannot do it.

An actual filesystem regression illustrates another distinction. The first
Haskell storage draft synced an open file and later renamed its staging name.
A replacement at that name could publish a different inode while checks of the
original descriptor still succeeded. The corrected component retains the final
directory entry and compares it with the original inode before reporting storage
success. The same regression now passes. This establishes the checked join at
that instant under the private-directory premise, not future immutability or
hardware power-loss behavior.

The current Haskell `TerminalReceipt` deliberately expresses only the narrower
same-process storage observation. The genuine host-retirement/AckPending witness,
generation-bound durable ACK issuer and restart recovery remain unfinished.
Keeping the ACK issuer unavailable preserves the contract while those parts are
implemented; it is not completion of the required behavior.

See the [component reference](../reference/haskell-cancellation.md) for current
interfaces and source-bound evidence. Native event-thread execution, a fresh
deadline check at the first window mutation, physical resource retirement and
the complete Elm receipt route require their own observations.
