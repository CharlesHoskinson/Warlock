# Contributing to Warlock's design language

Use the repository's [Warlock contributor plugin](../plugins/warlock-contributor/README.md), [contributor guide](../CONTRIBUTING.md) and [current implementation loop](../docs/warlock-build-loop/v2/INSTRUCTIONS.md). The shared offline Python CLI and skill work across Claude Code, Codex and Grok; host installation and hook behavior differ. Reading the package does not enable it in a client.

## Product design changes

Choose a concrete user behavior and its original EARS/OpenSpec scenario. Locate the current Elm model/update/view, handwritten surface adapters and narrow native authority through the [implementation map](../plugins/warlock-contributor/references/implementation.md). Preserve one immutable policy owner, typed intent, current identity and correlated native outcomes.

From the repository root:

```sh
python3 -B plugins/warlock-contributor/scripts/warlock.py doctor
python3 -B plugins/warlock-contributor/scripts/warlock.py capabilities
python3 -B plugins/warlock-contributor/scripts/warlock.py remaining --requirement ELM-UX-016 --markdown --limit 3
python3 -B plugins/warlock-contributor/scripts/warlock.py inspect --requirement ELM-UX-016 --scenario ux-016
```

`doctor` checks package structure and local executable availability; it does not verify client trust or product readiness. `remaining` reports recorded dispositions, and unadjudicated is not a missing-feature verdict.

Use `plan` to create an exact scenario/source plan, then `start --slice-file` with your owner and a separate record when needed. Plain `start --owner` uses the already selected `STATE.activeSlice`; it does not choose a new feature. Do not adopt another contributor's dirty files. See the plugin's [scaffold examples](../plugins/warlock-contributor/README.md#scaffold-and-resume) for exact arguments.

```sh
python3 -B docs/warlock-build-loop/v2/loop.py check
python3 -B plugins/warlock-contributor/scripts/warlock.py verify-plan
```

Implement in `implementation/warlock/`; declare supporting paths with `extend` before editing. Compile changed targets and run the decisive behavior plus a meaningful negative/lifecycle case through the protected launchers. `verify-plan` proposes checks but executes none; explicitly plan any unmapped dependency. Preserve native ABI pairing, identities, original deadlines, Unknown/no-replay and resource custody.

Record actual source changes or exact scenario verdicts, retain failures and state missing observations. Run the ending loop check. `review` checks staged bytes against declared scope; `report --markdown` prepares a bounded delivery note. Neither accepts native, accessibility, hardware or release obligations. Keep one active product behavior and stop an investigation after two qualification-only iterations or 45 minutes without product progress, as specified by the loop.

## Catalog, branding and documentation changes

For explicitly requested documentation or independent catalog work, use `check --project-only` before and after with proportional link/browser checks. No fabricated GUI scenario is needed. These changes do not count as product feature closure.

Keep frozen versioned specimens, source manifests, consensus packets and failed evidence unchanged. Add current guidance or a fresh specimen when behavior changes. Link the real implementation route, separate proposed/implemented/observed/accepted claims and show fixture authority visibly. Document all six component sections and keyboard/accessibility behavior.

## Client packaging and limits

- Claude Code can load the source plugin locally; its reminder hooks are advisory.
- Codex has its own plugin manifest and repository marketplace; installation and hook trust depend on the host surface.
- Grok uses compatible skills/packaging, but passive hook output is ignored; explicit repository checks remain required.

Use the [package's installation instructions](../plugins/warlock-contributor/README.md#local-development-and-installation) for client-specific commands. Prefer the repository checker to stale cached copies. The plugin runs no product build, installs nothing through its checker commands and cannot certify physical presentation or release acceptance. Its CI template is a template, not a running GitHub workflow.
