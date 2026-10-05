# Omarchy compatibility inventory

The user required Warlock to adopt all Omarchy keywords and keybindings on
2026-10-05. This additive requirement applies to the integrated release and
preserves the frozen baseline and original native acceptance gates.

Read-only discovery recorded 443 installed CLI commands, 370 distinct route
words and 265 effective Hyprland binding records. Hidden commands are included.
The records retain aliases, argument syntax, descriptions, modifier masks,
submaps, release/repeat/mouse/lock and consumption flags. Seventeen source files
retain the packaged binding definitions and this machine's loaded overrides.
See [inventory.json](inventory.json), [keywords.json](keywords.json),
[effective-bindings.json](effective-bindings.json) and
[the printable shortcut list](keybindings.txt).

The effective records include the user's Super+P pin, Super+Control+T pin,
Super+arrow snapping, Alt+mouse move/resize, Alt+Tab switching and Super+Home
minimize-others behavior. User overrides take precedence over packaged defaults.
Runtime `__lua` callback numbers are not portable dispatch targets. Their actual
source actions must be retained or translated into typed native intents with
equivalent behavior. The inventory does not authorize executing any command.

Implementation and native compatibility qualification remain open. The current
browser catalog has its own navigation; its shortcuts do not prove global
desktop compatibility. No installed configuration was changed or reloaded.

The [additive EARS/OpenSpec contract](../../../openspec/changes/warlock-omarchy-compatibility/specs/omarchy-compatibility/spec.md)
sets the release obligations. A new observation requires a fresh inventory
directory; historical source hashes and runtime records remain unchanged.

- [x] Record the installed vocabulary, aliases, binding flags and user overrides.
- [ ] Classify every effective binding and command route by retained external
      service, native window intent or Warlock shell surface action.
- [ ] Integrate typed action routing and command/search/help vocabulary under
      the single Elm policy and original native authority contracts.
- [ ] Preserve override precedence, collision handling, accessibility and
      global shortcut behavior while popup and IME input are active.
- [ ] Qualify every adopted mapping on the coherent owning release tuple;
      include repeat, release, locked, mouse, submap and non-consuming routes.
- [ ] Verify rollback preserves the user's configuration and shortcut choices.
