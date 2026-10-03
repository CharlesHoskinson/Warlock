# V12 exact selected process disappearance

V11 root actual failed before the first feature case when an already-registered
helper disappeared during /proc/PID/stat reading. The actual read raised ESRCH,
which still_live did not handle. Five helper starts/terminals were normal0 and
one QS diagnostic completed; full52/evaluation completion remained false. All18
main, normal native unload and recorded process closure passed. Preserve V11.

A fresh process registration remains strict: process(pid) must obtain actual
owned UID plus PID/start/PGID/parent stat; a missing process, unknown error or
malformed identity does not register anything. Do not add catches to process().

Only still_live's observation of an already-captured PID/start/PGID recognizes
kernel ENOENT or ESRCH as that selected observation no longer available. It
returns false; this is neither a successful helper exit nor registration proof.
A different observed lifetime also remains false; same PID/start/PGID remains
true, including Z until the original normal wait/terminal and cleanup checks.
Other OSError classes/errnos, owner/schema/read failures and unknown results
propagate and refuse. Normal exit0/one exact terminal, full EOF, all recorded
processes, original helper/query/evaluation budgets and all52 oracles remain
independent mandatory gates. Disappearance cannot accept missing/nonzero output.

The formal model represents strict registration versus selected observations,
actual identity states, exact errno and separate terminal acceptance. Kernel
regression must open the actual owned CPU child's proc stat while alive, allow
its normal exit, then read the already-open FD and observe actual ESRCH; no
synthetic error-only test substitutes for this. Original observer behavior and
strict process() registration must be retained as counterexample/refusal, then
the fresh still_live correction must pass the same kernel disappearance. Tests
must cover ENOENT, ESRCH, wrong/unknown errno, permission/I/O error, reused/live/Z,
malformed/foreign evidence and abnormal/missing/duplicate terminal. Model first,
then the one narrow source change, exact inherited source reconstruction/full
closure and all existing CPU/formal gates. Root alone reviews/freezes/launches.
