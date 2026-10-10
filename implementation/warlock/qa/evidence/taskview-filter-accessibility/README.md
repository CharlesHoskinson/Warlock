# Task View filter accessibility

The selected Task View workspace filter now exposes its existing immutable Elm state through `aria-pressed`. AT-SPI observes toggle buttons and exactly one pressed filter. Browsing remains observation-only; native effects continue through the original typed action admission.

[The current build](build-report.json) passes the original Task View assertions and two new selection projection checks, strict native admission positives/negatives, host compile/link, and the unchanged task-view/navigation/focus models through quint-llm-kit's existing-spec workflow. [The C admission output](surface-admission.stdout) includes conflicting selection, missing filter state, foreign identity and action-field injection negatives. Legacy overview frames remain admitted without checked fields.

[The current native journey](current-keyboard-failed.report.json) is **failed**. Its initial actual AT snapshot observes All windows as a pressed toggle button; the corresponding baseline snapshot exposed no selected state. The physical Tab sequence then crashes the WebKit renderer after reaching Browse workspace 2. The pre-cleanup snapshot records the lost real accessible host and Orca focus moving to the fixture application. The host reports renderer termination reason 0, retires input, and enters recovery; the normal-client-exit assertion fails. Protected session cleanup completes, but that does not make the client exit or journey pass. Earlier input variants and their failures are retained separately.

The kernel recorded `RLIMIT_CORE is set to 1, aborting core` at 2026-10-10 13:42:05 America/Denver. There is no retained backtrace establishing the crash mechanism, and no OOM event in the matching journal window. The main desktop and protected limits were unchanged.

Original ELM-UI-006 overview-select and overview-cancel remain partial. Native keyboard/Orca restore and eligible-opener dismissal on this updated tuple, the renderer crash, other-output/partial-navigation-refusal cases and independent original review remain open. This packet establishes the selection projection and a bounded actual native selected-state observation. It accepts neither the full AT journey nor a requirement or release.

Exact source, native tuple, toolchain, retained artifacts and scope are in [manifest.json](manifest.json). Runtime evidence is retained locally at the original paths in the native reports; it is not replaced by model or DOM assertions.
