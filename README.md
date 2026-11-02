# Warlock

![Warlock banner](docs/warlock-brand/readme/banner.png)

**Crafted for flow.**

Warlock is an Elm desktop shell for Omarchy, bringing a Windows-style taskbar and window controls to Hyprland. It brings applications, windows, workspaces, and desktop controls together in one interface.

**[Try the live test drive](https://charleshoskinson.github.io/Warlock/test-drive/) · [Visit the Warlock website](https://charleshoskinson.github.io/Warlock/)**

The test drive is the quickest way to try Warlock: the real compiled Elm interface on a simulated Omarchy desktop, right in your browser. Contributors build the native shell from source against matching Hyprland components, and a packaged Omarchy install is on the roadmap.

The current Elm/Haskell native host is still under development. The website and browser test drive are available; a persistent Warlock desktop on Omarchy has not yet met native or release acceptance. The [delivery ledger](docs/warlock-build-loop/v2/requirement-ledger.json) preserves all 242 requirements and 417 scenarios, including 19 whole-requirement verdicts with their original source and verification scope. Component checks and isolated VM runs do not extend those verdicts to the current host.

The Haskell host renders the compiled Elm interface in isolated Omarchy trials. The [current trial](docs/warlock-build-loop/v2/backend-private-diagnostics-20261102.json) shows Foot search results, no-match feedback and query retention after Refresh through real guest input. The overall trial still fails: the selected UI child exits with code 1, and strict QA cannot confirm inventory after the owned cgroup retires. The earlier toolbar-readiness failures remain retained. Persistent desktop operation, native window controls and application launch remain unavailable on the stock VM profile.

[Whole TEA005 acceptance](docs/warlock-build-loop/v2/tea-narrow-interop-acceptance-20261101.json) verifies the actual Elm/Haskell adapter, seven optimized Elm roots, adversarial HTTP delivery, and complete policy replay. [Whole TEA002 acceptance](docs/warlock-build-loop/v2/tea-pure-update-acceptance-20261101.json) separately binds pure reducer behavior to its tested source. TEA001, native GUI, provider cleanup and release remain open.

![The Warlock desktop in the test drive: taskbar across the top and Task View open over the workspace](docs/warlock-brand/readme/test-drive-task-view.png)

Open an application and Warlock's portal brings it in: a ring of red ember fragments ignites, expands and resolves into the new window.

![Warlock's portal opening a Browser window in the test drive: a ring of red ember fragments expands as the new window is revealed](docs/warlock-brand/readme/portal.gif)

## Why Warlock

Hyprland is a fast tiling compositor, and Omarchy makes it a pleasure to drive from the keyboard. Warlock adds the desktop layer around it: a taskbar that groups windows by application, a launcher, an Alt-Tab switcher, Task View across workspaces, window previews, a snap chooser, notification history, Settings, Files and a system menu. Warlock's own surfaces share one Elm interface, one design language and the same keyboard navigation, and Files opens in Omarchy's file explorer.

Window requests go to Hyprland, and Warlock shows the result Hyprland reports. When you pick a window, the taskbar marks the request as pending, Hyprland carries it out or refuses it, and the taskbar updates from what Hyprland reports.

Hyprland keeps doing what it does best: composing the desktop and managing input, focus, workspaces and window geometry.

## What it does

### Taskbar

A taskbar on each display keeps pinned applications and running window groups in reach. Open a group to find its windows and bring one forward.

### Launcher and application search

Open Applications from the taskbar and type a name to find an installed application. The top result has an Actions button with the application's own actions and its recent files.

### Window switcher

Use Alt-Tab to move through open windows. A clear highlight shows the selected window before you switch.

![The Alt-Tab window switcher with window cards and the selected window marked in red](docs/warlock-brand/readme/test-drive-switcher.png)

### Task View and workspaces

Open Task View from the taskbar to see windows organized by workspace. Select a window or move it to another workspace using the controls beside it.

### Window previews and snap layouts

Open a window group to recognize its windows by their previews, with icons when previews are unavailable. The snap chooser offers half-screen and quarter-screen positions for supported windows; Hyprland applies the resulting placement.

### Notifications

Open Notifications from the taskbar to read messages and their history. Act on a live notification, dismiss it, or turn on do not disturb.

![Notifications with do not disturb tiles and a live notification card with its actions](docs/warlock-brand/readme/test-drive-notifications.png)

### Settings

Open Settings from the taskbar to change appearance, text size, and motion. Review changes before saving them.

![Warlock Settings with theme and text size choices](docs/warlock-brand/readme/test-drive-settings.png)

### Files

Open Files from the taskbar to reach Home, collections, or a folder you enter. Warlock opens the location in Omarchy Files and can reuse its existing window.

![Warlock Files with quick-access tiles for Home, Recent and the collections](docs/warlock-brand/readme/test-drive-files.png)

### System menu

Open System from the taskbar for volume, network, and session controls. The menu shows service state and asks for confirmation before actions such as restart, shutdown, logout, or disabling networking.

### Context menus and dialogs

Open a window's context menu for actions such as moving or arranging it. Dialogs identify consequential system actions and give you a way to cancel.

## Features

Checked items describe implemented interface paths; they do not certify the current Elm/Haskell native host. In the test drive, clicks, searches and settings run compiled Elm, and a simulated desktop answers in place of Hyprland and your applications.

### Taskbar and applications

- [x] Show a taskbar on each display
- [x] Group running windows by application
- [x] Pin applications to the taskbar
- [x] Reorder pinned applications
- [x] Mark active applications and applications needing attention
- [x] Search installed applications as you type
- [x] Launch an application from search
- [x] Open the first search result's application actions and recent files

### Windows and workspaces

- [x] Switch between windows with Alt-Tab
- [x] Select a window from its application group
- [x] Show windows by workspace in Task View
- [x] Move a window to another workspace
- [x] Show window previews with icon fallbacks
- [x] Choose a half-screen snap position
- [x] Choose a quarter-screen snap position
- [x] Open window actions from a context menu

### Desktop utilities

- [x] Read current notifications and notification history
- [x] Use actions on live notifications
- [x] Turn on do not disturb
- [x] Open Home and collections in Files
- [x] Open an entered folder in Files
- [x] Adjust volume and mute
- [x] View networking state
- [x] Confirm power and session actions

### Appearance and input

- [x] Choose the Night or Dawn theme
- [x] Change the shell text size
- [x] Adjust motion and visual effects
- [x] Navigate shell controls with the keyboard
- [x] Dismiss popups with Escape

## Try the test drive

Open the [live test drive](https://charleshoskinson.github.io/Warlock/test-drive/) in your browser. Search for an application, switch between windows, move a window in Task View, and explore the appearance settings without changing your desktop.

## How it works

### Architecture

Current authored production uses Elm and Haskell. Elm owns every GUI element and ordinary interaction policy. Haskell owns the local HTTP boundary, authenticated transport, backend and reviewed native integration. WebKitGTK, GTK and Hyprland are separately inventoried system libraries.

```mermaid
flowchart LR
  subgraph private["Private UI network"]
    main["HttpMain · Elm state and effects"]
    views["HttpBar / HttpPopup · Elm GUI"]
    owner["Haskell UI owner · role origins and admission"]
    main --> owner
    views --> owner
  end
  owner <-->|"Authenticated inherited endpoint"| backend["Haskell backend"]
  backend --> catalog["Installed application catalog"]
  backend --> pins["Durable pin store"]
  owner --> webkit["GTK / WebKitGTK system libraries"]
```

The controlled bridge runs real catalog and pin traffic. The current protected Haskell profile passes ten selected suites. The standalone Omarchy app presents its window and supports bounded search/Refresh journeys; its process lifetime and native window operations remain unfinished. See the [current source-bound observation](docs/warlock-build-loop/v2/backend-private-diagnostics-20261102.json) and [Omarchy trial instructions](docs/warlock/how-to/run-omarchy-mvp.md) for the verified scope and retained failures.

The Haskell catalog/pin store now retains uncertain acquisitions before publication and refuses to certify them as clean retirement. [The component report](docs/warlock-build-loop/v2/store-retirement-component-20261102.json) records the real old/new regression, 36 passing production suites and bounded lifecycle models. This supports persistent ownership; it does not establish native GUI or release acceptance.

Backend result JSON now includes `attempt`, seven `checks`, `failureStages`, a redacted `selectedOperationError` and three `retirement` classes. These report the retained outcome without changing success criteria. A real authenticated child-exit test injects synthetic confidential stderr data; none appears in its result JSON or 32 collected ordinary logs. This verifies the selected diagnostic boundary; system credential services and other native integrations still need their original verification.

A fresh Omarchy run now retains actual cross-user bridge-credential evidence: the same selected child changes UID0 to UID1, and its next effect request is refused with `ForeignUser` before another policy callback. All 15 authentication cases passed with unchanged five-second conversation deadlines. The [source-bound component report](docs/warlock-build-loop/v2/persistent-auth-cross-user-20261102.json) preserves the measured identity maps, namespace and capability change. [Whole original DEL010 is independently accepted](docs/warlock-build-loop/v2/persistent-auth-cross-user-acceptance-20261102.json) on immutable source `02b0aba0b`. This accepts the authentication boundary; native GUI and release acceptance remain separate.

The original `architecture-024` capability-denial scenario is [independently accepted on actual bridge evidence](docs/warlock-build-loop/v2/arc024-capability-scenario-acceptance-20261101.json). Whole ARC024 remains partial for navigation and resource decision integration. The ledger contains 42 accepted scenarios on their recorded source tuples; whole-requirement acceptance is 19 of 242, with all 417 scenarios preserved.

#### Archived host design

The following diagram and walkthrough describe the preserved prototype. Its authored C/C++ host, JavaScript adapters and Python services remain historical reference paths. Current development follows the Elm/Haskell architecture above.

```mermaid
flowchart TB
  subgraph L_gui["Elm interface"]
    g_main["Main controller<br/><small>Elm</small>"]
    g_bar["Bar<br/><small>Elm</small>"]
    g_popup["Popup<br/><small>Elm</small>"]
    g_previews["Preview policy worker<br/><small>Elm</small>"]
  end
  subgraph L_bridge["Browser adapters"]
    g_adapters["Browser adapters<br/><small>JavaScript</small>"]
  end
  subgraph L_host["Desktop host"]
    g_host["Native host<br/><small>C and C++, GTK</small>"]
    g_webkit_renderer["WebKitGTK renderer<br/><small>C/C++</small>"]
    g_python["Adapter daemon and<br/>notification service<br/><small>Python</small>"]
  end
  subgraph L_compositor["Hyprland"]
    g_authority_plugin["Hyprland observation authority plugin<br/><small>C++</small>"]
    g_hyprland["Hyprland on Omarchy<br/><small>Aquamarine, XWayland</small>"]
  end
  subgraph L_library["Haskell packages (standalone libraries)"]
    g_haskell["elf-observation, held-document,<br/>process-custody, protocol, runtime,<br/>native-authority<br/><small>Haskell</small>"]
  end
  subgraph L_external["Applications and desktop services"]
    g_services["Applications and<br/>desktop services"]
  end
  g_bar <-->|"Elm ports"| g_adapters
  g_main <-->|"Elm ports"| g_adapters
  g_popup <-->|"Elm ports"| g_adapters
  g_previews <-->|"JavaScript calls"| g_host
  g_adapters <-->|"script messages / evaluate JavaScript"| g_host
  g_adapters -->|"theme attributes"| g_webkit_renderer
  g_host <-->|"JSON lines over pipes"| g_python
  g_host <-->|"library calls / callbacks"| g_webkit_renderer
  g_host <-->|"Hyprland IPC"| g_authority_plugin
  g_host -->|"layer-shell surfaces"| g_hyprland
  g_python <-->|"Hyprland IPC"| g_authority_plugin
  g_python ~~~ g_hyprland
  g_hyprland -->|"Hyprland events"| g_python
  g_host <-->|"D-Bus"| g_services
  g_python <-->|"D-Bus"| g_services
  g_authority_plugin <-->|"plugin API / callbacks"| g_hyprland
  g_hyprland ~~~ g_services
  g_services -->|"Wayland and XDG"| g_hyprland
  classDef gui fill:#1a1416,stroke:#e34234,color:#f2ede4
  classDef base fill:#161112,stroke:#7a6f6a,color:#f2ede4
  class g_main,g_bar,g_popup,g_adapters,g_previews gui
  class g_host,g_webkit_renderer,g_python,g_authority_plugin,g_hyprland,g_haskell,g_services base
```

[Explore the interactive architecture](https://charleshoskinson.github.io/Warlock/architecture/)

In the archived prototype, follow one click. When you click the taskbar button of a window that is not focused, Bar checks the click against what it shows and passes it through its JavaScript adapter to the native host. The host routes it to Main, which turns it into an activation request and marks it pending. The host records the request and hands it to the Python adapter, which asks the Hyprland plugin to focus the window. The plugin focuses it inside Hyprland, checks the result and reports back along the same path. Main settles the request, and the taskbar shows the window as active once Hyprland's next window report arrives.

**Elm interface.** Main coordinates desktop interaction from a hidden controller document. Bar renders each display's taskbar, and Popup renders the shared menus and panels. Popup manages the window preview thumbnails, and a headless Elm worker inside the native host applies the preview policy.

**Browser adapters.** JavaScript connects Elm ports to browser input, native callbacks, appearance settings, and preview transport. The adapters start the Elm programs and pass messages between them and the host.

**Desktop host.** A shared GTK host written in C and C++ places the taskbars and popup. WebKitGTK runs compiled Elm and JavaScript and renders their HTML and CSS. A Python adapter subprocess connects the host to Hyprland and desktop services; a Python notification service receives application notifications and keeps their history.

**Hyprland integration.** A C++ plugin runs inside the matching Hyprland build, reports window state, handles window operations and shortcuts, and supplies captures. A C++ preview provider receives captures from the plugin and passes images through the host to the popup. Hyprland manages focus, input, workspaces, and window geometry; its C++ Aquamarine backend supplies display buffers and presentation.

**Applications and services.** Installed applications provide windows and desktop entries. XWayland connects X11 applications to the Wayland desktop. Omarchy Files, the audio service, NetworkManager, systemd-logind, desktop preferences, and local storage supply the services and data Warlock presents.

The archived diagram records the earlier standalone package work.

### Elm

![The Elm Architecture in Warlock](docs/warlock-brand/readme/elm-architecture.png)

The Elm Architecture gives each program a Model, messages, and an update function; programs that render an interface also have a view. Every change to a program's Model goes through update. Commands and subscriptions describe communication with the outside world, and the compiler checks that every case of every message is handled.

Main coordinates desktop interaction, Bar renders the taskbar for an output, and Popup renders shared panels while managing local text input and previews. This structure gives window state and user actions a clear place to meet.

### Haskell

Current authored production uses Elm and Haskell. Elm owns everything you see and touch. Haskell supervises processes, prepares the interface's verified HTML, checks binary dependencies and speaks a checked protocol with authenticated peers. The C/C++ host and Python adapter above are retained prototype designs. Strong types, explicit effects and pure functions make the current boundaries precise and testable.

Six packages in `implementation/warlock/haskell` provide the current library components, and the roadmap connects them into the persistent Haskell runtime the desktop runs on.

- `elf-observation` parses captured GNU `readelf` output and resolves declared dependency graphs.
- `held-document` reads identity-checked file snapshots and prepares HTML with verified content and script and style hashes.
- `process-custody` runs selected tools and child-process sessions with deadlines, controlled file descriptors, and cleanup tracking.
- `protocol` checks bounded bytes into a versioned envelope, records a refusal reason for rejected input, and provides a caller-owned framed socket transport.
- `runtime` is a controlled bootstrap that selects a held executable, keeps custody of the process it starts, and authenticates the current session's peer before admitting a frame.

### Warlock Design Language

![Warlock Design Language overview](docs/warlock-brand/readme/design-language.png)

The [Warlock website](https://charleshoskinson.github.io/Warlock/) documents every colour, type style, shape, motion and component. The test drive applies the design language to the real Elm interface, portal transitions included.

Black and red define Warlock's primary palette. Secondary colours communicate focus, status, positive outcomes, and warnings. A focused window stays subtly distinguishable from the windows around it, and depth and shadows remain legible on near-black surfaces.

The design language gives window opening and closing a signature portal transition: a ring of red ember sparks resolves into the window. Reduced-motion and effects-off versions provide quieter alternatives. Elm sets classes and data attributes; CSS owns the visuals. The typefaces are Space Grotesk, Inter, and JetBrains Mono.

## Roadmap

- [ ] Package Warlock for installation on Omarchy
- [ ] Provide an installation and rollback path
- [ ] Build the Haskell backend and native runtime integration
- [ ] Complete new-instance and window-pinning controls
- [ ] Expand input method support
- [ ] Extend screen reader and braille support
- [ ] Broaden multi-display and hardware coverage
- [ ] Complete reproducible release builds

## Build and contribute

Start with the offline contributor checker. It requires Python 3.9 or newer and Git. From the repository root, run:

```sh
python3 -B plugins/warlock-contributor/scripts/warlock.py status
python3 -B plugins/warlock-contributor/scripts/warlock.py check --project-only
```

The [frontend build instructions](docs/warlock/how-to/build-current-frontend.md) build Main, Bar, and Popup together. The documented build uses a compiler, package cache, and build launcher at paths on the development machine. A contributor on another machine needs equivalent inputs and a launcher. The [desktop build instructions](implementation/warlock/RELEASE.md) cover the native host and matching Hyprland components.

Current development now preserves window-action feedback while Applications is open, including older unresolved recovery; the narrow taskbar keeps the action-state prefix visible. See the [source-bound component evidence](implementation/warlock/qa/evidence/applications-window-feedback-20261031/report.json) and [feedback reference](docs/warlock/reference/applications-window-feedback.md). This is compiled Elm/browser component verification. Original native keyboard/AT and release acceptance remain open. New authored production is Elm/Haskell with every GUI element in Elm; the current replacement Haskell/native runtime remains under integration.

Original ARC005 authority-tuple serialization is [accepted on its permitted bridge oracle](docs/warlock-build-loop/v2/authority-tuple-acceptance-20261031.json), including source-bound traces and independent review. This does not qualify native mutation or the Haskell port.

The contributor checker now [blocks incomplete requirement mappings before admission](docs/warlock/reference/requirement-admission.md). Original REV005 is accepted on actual positive/negative admission evidence; this is administrative verification.

The current private GHC 9.6.7/Cabal 3.12.1.0 SDK now passes the offline production build and all 24 controlled Haskell suites (36 fixture invocations). [The source-bound preparation record](docs/warlock-build-loop/v2/haskell-toolchain-readiness-20261031.json) retains dependency revisions, plans and the initial resolver failure. That historical package tuple had a one-frame bootstrap; the bounded authenticated follow-up now supports multiple frames, while persistent desktop/native integration and original native acceptance remain open. Historical package instructions remain available for [elf-observation](implementation/warlock/haskell/elf-observation/README.md), [held-document](implementation/warlock/haskell/held-document/README.md), and [process-custody](implementation/warlock/haskell/process-custody/README.md).

Run the checks for the components you change using their instructions and the [verification guide](docs/warlock/how-to/verify-selected-change.md). See the [contribution guide](CONTRIBUTING.md) for the workflow.

## License

Warlock is licensed under the [Apache License 2.0](LICENSE).


Original ARC007 is now [accepted on all five receipt scenarios](docs/warlock-build-loop/v2/receipt-state-acceptance-20261031.json). A valid correlated `Cancelled` outcome now reaches the existing cancellation state instead of remaining Pending; only its matching local reservations retire. The actual desktop-route regression passes 2,451 assertions with80 matching bridge receipts. [The receipt reference](docs/warlock/reference/receipt-states.md) separates this verified behavior from native cancellation, the Haskell protocol port and release obligations.


The current [desktop application stream](docs/warlock/reference/desktop-application-stream.md) now connects the actual single-input/single-output Elm Main to a called Haskell catalog and durable pin backend. Applications retains all2,048 entries through explicit paging; a compact fallback keeps long names and32pins reachable under the unchanged byte limit. The [retained evidence](implementation/warlock/qa/evidence/ui-backend-20261101/report.json) passes27Haskell suites/39invocations,8,010 actualMain/CLI checks and401complete frames in order, with real pin save/restart and malicious-input refusal. [Whole original ARC003 and DEL011, including all three scenarios, are independently accepted](docs/warlock-build-loop/v2/ui-backend-acceptance-20261101.json) on source `5818e78f436554a951f1b90f5c9b417e406404b6`; private HTTP/WebKit, persistent UI lifecycle, native GUI/AT/IME and release remain unfinished.
