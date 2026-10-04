# Bounded menu and receipt model proposal

One logical menu controller owns a view and a persistent operation ledger.
Provider data and native receipts arrive as external events. Selection,
dismissal, late receipt and retirement are separate atomic steps. This is a
single actor, so plain Quint applies; no distributed-message framework is needed.

Bindings include provider/capability generation and frontend epoch. Stable window
identity excludes the frontend epoch so Unknown survives a broker rebind.
Receipts require the original full dispatch binding. Symbolic identities do not
replace the compiled decoder's actual uint64 and UTF-8 boundary checks.

Check two independent targets, delayed receipts after another target completes,
wrong-binding/duplicate receipt refusal, bounded unresolved entries, and terminal
fail-closed retirement exhaustion. Repeated invalidation consumes no new slot.
No eviction may release an uncertain command. No receipt implies application
observation or issues another command. Named witnesses must reach capacity,
exhaustion, recovery through a definitive receipt, and independent-target use.

The sampled abstraction uses small finite capacities; compiled Elm fixtures
exercise the actual limits 64/64/128. The model does not qualify JSON byte size,
native authentication, actual command execution, popup focus or release behavior.
Keep the earlier V1 proof unchanged and this proposal free of transition logic
until explicit review under the Quint modeling skill.
