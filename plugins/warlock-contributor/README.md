# Warlock contributor

One shared offline Python checker and implementation skill, with thin Claude Code, Codex and Grok packaging. It helps contributors deliver actual GUI behavior against Warlock's original requirements. It cannot certify a physical/native/AT oracle or release acceptance. Linux, Python 3.9+ and Git in the repository are sufficient for checker use; product builds retain their existing protected QA tools.

From the repository root:

```sh
python3 -B plugins/warlock-contributor/scripts/warlock.py status
python3 -B plugins/warlock-contributor/scripts/warlock.py inspect --requirement ELM-UX-004
python3 -B plugins/warlock-contributor/scripts/warlock.py start --owner your-name
python3 -B docs/warlock-build-loop/v2/loop.py check
python3 -B plugins/warlock-contributor/scripts/warlock.py record --outcome production-fix --summary 'Describe the actual source behavior and observations'
```

`start` uses `STATE.activeSlice`; it does not select the next feature. The default local record is `.warlock-contributor/slice.json`; Git must ignore `.warlock-contributor/` before `start` (this repository supplies the ignore). On a new development checkout add that narrow ignore or choose an already-ignored `--record` location. Record updates are serialized with a POSIX lock and written atomically. Global `--repo`, `--record`, and `--json` precede the subcommand. For resumed own drafts, explicitly list each declared dirty path with repeatable `start --adopt-dirty <path>` and supply `--ownership-note`; undeclared and unadopted foreign drafts stay protected. See `--help` and [contract.json](references/contract.json). Zero exit means structural compliance; 1 is a structural policy violation and 2 invalid/unavailable inputs. Explicit loop checks and repository contributor instructions remain required even when no host hook runs.

## Local development and installation

Claude Code can load the source directly without installing:

```sh
claude --plugin-dir ./plugins/warlock-contributor
claude plugin validate ./plugins/warlock-contributor
```

For a reviewed marketplace installation, use `/plugin marketplace add .` and `/plugin install warlock-contributor@warlock` in Claude Code.

Invoke `/warlock-contributor:warlock-contribute`. Grok reads Claude-compatible plugins and skills; use its documented local install command after reviewing the package:

```sh
grok plugin validate ./plugins/warlock-contributor
grok plugin install ./plugins/warlock-contributor
```

Use `/skills` to inspect/invoke `warlock-contribute`, and `/hooks` to inspect loaded hooks. Do not bypass trust. Local install is a user configuration change; these instructions do not perform it.

Codex uses `.codex-plugin/plugin.json` and shared `skills/`. This repository includes `.agents/plugins/marketplace.json`, exposing `./plugins/warlock-contributor`. Register the repository marketplace with `codex plugin marketplace add .`, then install through the desktop Plugins Directory. The official packaging page documents marketplace shape and cache refresh. This repository's contributor instructions also permit reading the skill and invoking the CLI directly without installation. No fabricated Codex validate command or universal CLI hook activation is assumed.

Installed plugins may be cached copies; prefer the repository checker with explicit `--repo` for contributions. A cached checker whose bytes differ from the repository checker reports an error; refresh the installed package and inspect its skill/manifest before use. Merely seeing this source folder does not prove it is enabled. No installation, trust decision, global configuration change, remote service, secret or new dependency is performed by checker commands.

## Hook scope and limits

Claude's default `hooks/hooks.json` and Codex's explicit `hooks/codex.json` run a read-only checker at SessionStart (including resume/compaction when supplied by the host) and UserPromptSubmit. They add a concise reminder at session start or when a prompt check needs attention for recognized Warlock repositories. They never block prompts/tools/Stop or write contribution records; correction loops and unrelated work remain usable. A five-second checker timeout is advisory, so explicit checks must still run. They do not inspect transcripts or execute builds.

Grok uses the Claude-compatible manifest but has different semantics: passive event stdout is ignored. The adapter detects Grok's documented environment and returns immediately; its passive hook cannot deliver context. Explicit loop calls still run the checker. The shared skill and mandatory repository loop carry the instruction to call it. There is no Grok blocking tool hook.

Codex bundled hooks require manual desktop installation and review/trust of the current hook definitions; enabled is not trusted. Support on other Codex surfaces must be verified, and hooks are not eligible for the public directory. Cross-client discovery/validation does not prove live hook execution or GUI acceptance.

## Verified host contracts

Checked October 7, 2026 against primary documentation and installed CLI help:

- [OpenAI packaging](https://developers.openai.com/plugins/build/plugins): compatibility manifest, relative skill/hook paths, manually installed desktop hooks and plugin-root variables.
- [Codex hooks](https://learn.chatgpt.com/docs/hooks): SessionStart/UserPromptSubmit JSON additional context and trust rules.
- [Claude plugin reference](https://code.claude.com/docs/en/plugins-reference) and [hooks reference](https://code.claude.com/docs/en/hooks): default hook discovery, plugin paths and lifecycle context.
- [Grok plugins](https://docs.x.ai/build/features/skills-plugins-marketplaces) and [hooks](https://docs.x.ai/build/features/hooks): Claude compatibility, camelCase event input, GROK environment and passive stdout limitation.

See [the six-agent review and dispositions](../../docs/warlock-workflow-review/contributor-plugin-20261007/consensus.md), [the implementation skill](skills/warlock-contribute/SKILL.md) and [protected execution](references/workflow.md) for contributor work. Host manifests describe loading only; the v2 delivery contract and original EARS/OpenSpecs determine the product work.

## What is enforced

The v2 product-loop wrapper requires a participant record before and after native execution; session hooks remain advisory. For explicitly requested documentation/plugin/support work, run the shared `check --project-only` directly before and after without inventing a GUI slice. The [CI template](references/warlock-contributions.yml) uses project checks on a clean checkout and compares PR changes against the base revision; ignored local ownership records are not available to CI. Copy it to `.github/workflows/warlock-contributions.yml` to activate GitHub Actions when the publishing credential has `workflow` permission. The existing GitHub credential lacks that permission, so this package publishes the reviewed template rather than claiming live CI.

Local records are self-attested, not a tamper-proof audit or proof of independent review. The checker detects contradictions and stale/current evidence but cannot tell whether changed code improves behavior, whether a reviewer is honest, or whether pixels/AT match the original oracle. Work in separate Git worktrees when concurrent ownership is unclear. Record reports must describe observable behavior and unresolved obligations.
