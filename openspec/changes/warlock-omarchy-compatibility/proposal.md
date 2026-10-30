# Omarchy vocabulary and shortcut compatibility

> Current production-language decision (2026-10-30): Warlock-authored production uses Elm and Haskell only; all GUI elements are Elm. Haskell owns native/runtime capabilities, Haskell supplies pure policy where selected, and Elm owns GUI presentation with one authoritative policy owner per domain. Only Elm and Haskell authored production components may ship, including behind an allowed-language wrapper. Development/formal tooling and separately inventoried third-party libraries are distinct. Preserve original IDs, scenarios, behavior, deadlines and historical evidence; old passes do not accept replacements. Implementation remains paused pending readiness and root/Muse authorization. See `warlock-production-language-migration`.

Warlock must retain Omarchy's commands, terminology and keybindings, including
the user's overrides. The installed read-only inventory is captured in
`docs/warlock-compatibility/omarchy-v1/`; implementation and native qualification
remain open. This is additive to the original S01–S16 and right-click contracts.
It does not amend frozen requirements, scenario identities or deadlines.

Preserve the existing Omarchy CLI and external services where they already own
an action. Translate shell/window actions only through the established typed
Elm/native boundaries. Runtime callback IDs cannot become portable commands.
No installed changes or main-session activation are part of this inventory.
