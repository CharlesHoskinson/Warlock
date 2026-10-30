# Warlock language skills

The repo-owned Codex plugin supplies elm-engineering and haskell-engineering.
All GUI is Elm; the backend and reviewed native integration are Haskell.

Install with codex plugin marketplace add /absolute/path/to/Warlock, then
codex plugin add warlock-languages@warlock. Verify installed/enabled with
codex plugin list --json. Skills are available on the next turn; a running worker
must explicitly read current instructions rather than assume a cache refreshed.

Compilers, HLS, HLint and Fourmolu are development tools. OpenSpec1.15.0 uses the
verified official standalone distribution. Versions are in tooling/languages.
The full repository workflow plugin is being developed by the assigned team.
Skill installation and bounded tooling checks do not accept production behavior.
