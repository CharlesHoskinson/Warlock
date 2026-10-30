# Warlock documentation

Warlock is an evolving Elm/native window-system integration candidate. It is not a ready-to-install release and is not installed in the user's main Omarchy session. These pages document the current contribution workflow, recorded implementation and its limits.

Choose a page for the work you are doing:

| Need | Start here |
| --- | --- |
| Learn the contribution process safely | [Tutorial: your first evidence-grounded contribution](tutorials/first-contribution.md) |
| Learn how to find a real source boundary | [Tutorial: navigate a policy-to-native route](tutorials/source-navigation.md) |
| Carry out an agreed implementation task | [How to contribute a selected slice](how-to/contribute-selected-slice.md) |
| Apply architecture and QA practices to existing code | [How to retrofit an existing boundary](how-to/retrofit-existing-code.md) |
| Build the current frontend from a reviewed lock | [How to build the current frontend](how-to/build-current-frontend.md) |
| Validate current frontend/native composition | [How to validate a current composition](how-to/validate-current-composition.md) |
| Check an explicitly selected current release build | [How to check current release reproducibility](how-to/check-current-release-reproducibility.md) |
| Prepare proportionate protected verification | [How to verify a selected change](how-to/verify-selected-change.md) |
| Look up paths, commands and machine limits | [Build and runtime reference](reference/build-and-runtime.md) |
| Understand recorded acceptance and open gates | [Status and evidence reference](reference/status-and-evidence.md) |
| Understand active and attention indicators | [Explanation: taskbar attention](explanation/taskbar-attention.md) |
| Understand application pinning and window top state | [Explanation: application pin and always-on-top](explanation/application-pin-and-always-on-top.md) |
| Understand ownership and lifecycle decisions | [Explanation: authority, presentation and lifetimes](explanation/ownership-and-lifetimes.md) |

This structure follows [Diátaxis](https://diataxis.fr/): tutorials teach through a bounded exercise; how-to guides address a concrete task; reference provides lookup facts; explanation develops the reasons behind the system. Root retrieved the official source using Scrapling. The docs are not an installation/deployment claim.

For the governing process, see [the completion loop](../warlock-build-loop/v2/INSTRUCTIONS.md), [architecture review](../warlock-build-loop/v2/ARCHITECTURE-REVIEW.md), [fuzzing and contracts](../warlock-build-loop/v2/FUZZING-CONTRACTS.md), [the contributor guide](../../CONTRIBUTING.md) and [versioned lessons/ideas](../../wiki/warlock/_index.md). Original requirements and the acceptance ledger take precedence over summaries here.
