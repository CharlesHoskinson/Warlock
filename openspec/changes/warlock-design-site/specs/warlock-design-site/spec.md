## ADDED Requirements

### Requirement: WARLOCK-SITE-001 — Full-viewport simulated Omarchy desktop

When a visitor enters the test drive, the site SHALL present a full-viewport Omarchy-style desktop with wallpaper, workspaces and real compiled Elm controller and renderer bundles connected to a deterministic simulated host; it SHALL identify application interiors as local fixtures and distinguish simulated behavior from native operation.

Guardrail: Browser simulation and publication do not constitute native GUI acceptance.

#### Scenario: WARLOCK-SITE-001-01

- **GIVEN** the visitor opens the test drive
- **WHEN** the desktop initializes
- **THEN** compiled Elm renders the taskbar and shell on a simulated desktop with labeled fixture clients

#### Scenario: WARLOCK-SITE-001-02

- **GIVEN** a visitor opens a fixture application
- **WHEN** the client appears
- **THEN** the site does not claim to launch a native application or access the visitor filesystem

### Requirement: WARLOCK-SITE-002 — Simulated host receipts and observations

When Elm sends an operation through the simulated host, the host SHALL validate typed identity and epoch, return a receipt separately from any observation, publish coherent world snapshots, and preserve Pending, refused, cancelled and Unknown semantics without automatic mutation replay.

Guardrail: Browser simulation and publication do not constitute native GUI acceptance.

#### Scenario: WARLOCK-SITE-002-01

- **GIVEN** a receipt is returned before an observation
- **WHEN** Elm receives the receipt
- **THEN** the receipt alone does not establish the effect

#### Scenario: WARLOCK-SITE-002-02

- **GIVEN** a host reset retires an epoch
- **WHEN** a late response arrives
- **THEN** the stale response cannot update the current world

### Requirement: WARLOCK-SITE-003 — Omarchy placement and tiling

While the desktop is simulated, the site SHALL use the host geometry contract: reserve 3rem plus 8px for the top taskbar, use 10px snap gaps and a 24px default client titlebar allowance, retain coherent workspaces and window incarnations, and support tiling and configured floating and snap operations. Popup allocation SHALL be at most 700 by 420px, bounded by output width minus 8px and output height minus the taskbar and 4px, with slide and flip constraints; an unanchored popup SHALL begin at x=50 beneath the top bar and a context popup SHALL use its captured anchor.

Guardrail: Browser simulation and publication do not constitute native GUI acceptance.

#### Scenario: WARLOCK-SITE-003-01

- **GIVEN** a popup opens with a captured context anchor near an output edge
- **WHEN** placement is calculated
- **THEN** slide and flip honor that anchor and the 700 by 420px maximum and output bounds; an unanchored popup starts at x=50 beneath the reserved top bar

#### Scenario: WARLOCK-SITE-003-02

- **GIVEN** a window is tiled, snapped or moved to a workspace
- **WHEN** a valid simulated observation is published
- **THEN** the matching incarnation uses the work area after the 3rem plus 8px taskbar reservation, 10px snap gaps and 24px default client titlebar allowance

### Requirement: WARLOCK-SITE-004 — Shortcuts and in-page alternatives

When an effective Omarchy shortcut is available in the simulation, the site SHALL implement the effective bindings inventory and provide a visible in-page equivalent and shortcut legend. Alt+Tab and Shift+Alt+Tab SHALL choose windows and Alt release SHALL commit where delivered; Super+Tab SHALL open Task View, Super+Z snap layouts, Alt+Space window actions, and configured Super+number overrides SHALL activate taskbar applications. Escape and explicit Cancel SHALL dismiss navigation, and numeric workspace bindings SHALL NOT be assumed where user overrides replace them.

Guardrail: Browser simulation and publication do not constitute native GUI acceptance.

#### Scenario: WARLOCK-SITE-004-01

- **GIVEN** the browser intercepts Super+Tab, Super+Z, Alt+Space or a configured Super+number taskbar override
- **WHEN** the visitor chooses the corresponding visible in-page control
- **THEN** the matching Task View, snap layouts, window actions or taskbar application action opens, and the legend identifies the effective binding

#### Scenario: WARLOCK-SITE-004-02

- **GIVEN** the Alt+Tab chooser is open
- **WHEN** the visitor releases Alt where delivered or presses Escape or chooses Cancel
- **THEN** Alt release commits the selected window; Escape and Cancel dismiss without inventing a focus operation

#### Scenario: WARLOCK-SITE-004-03

- **GIVEN** a Super+number binding is overridden for a taskbar application
- **WHEN** the visitor invokes it or its visible in-page equivalent
- **THEN** the configured taskbar application activates and no numeric workspace binding is assumed

### Requirement: WARLOCK-SITE-005 — Portal follows observed window lifecycle

When the simulated host observes an application window map or removal of the same incarnation, the site SHALL present the signature portal under the design language effects and motion limits, without treating intent or receipt as observation or delaying live input.

Guardrail: Browser simulation and publication do not constitute native GUI acceptance.

#### Scenario: WARLOCK-SITE-005-01

- **GIVEN** a launch receipt arrives without a mapped window
- **WHEN** the desktop renders
- **THEN** no portal starts

#### Scenario: WARLOCK-SITE-005-02

- **GIVEN** an observed window closes with reduced motion enabled
- **WHEN** the removal is applied
- **THEN** input retires immediately and no animated portal runs

### Requirement: WARLOCK-SITE-006 — Guided desktop tour

When a visitor starts the guided tour, the site SHALL lead through the desktop and its real Elm surfaces with accessible controls to advance, stop and return to normal interaction.

Guardrail: Browser simulation and publication do not constitute native GUI acceptance.

#### Scenario: WARLOCK-SITE-006-01

- **GIVEN** the visitor starts the first-run tour
- **WHEN** a tour step opens
- **THEN** the visitor can identify its subject and proceed with keyboard or pointer

#### Scenario: WARLOCK-SITE-006-02

- **GIVEN** the visitor stops the tour
- **WHEN** the tour closes
- **THEN** desktop controls remain available

### Requirement: WARLOCK-SITE-007 — Interactive verified architecture

When a visitor opens the architecture page, the site SHALL render an interactive component and connection view driven by the verified architecture model, provide accessible textual details, and identify the scope and source of the model.

Guardrail: Browser simulation and publication do not constitute native GUI acceptance.

#### Scenario: WARLOCK-SITE-007-01

- **GIVEN** a visitor selects a model component
- **WHEN** its details open
- **THEN** the page displays the matching model information and connections

#### Scenario: WARLOCK-SITE-007-02

- **GIVEN** the architecture model lacks a claimed component or connection
- **WHEN** the page builds
- **THEN** the view does not invent it or portray historical implementation as the current production policy

### Requirement: WARLOCK-SITE-008 — Design language pages and desktop links

When a visitor reads a component page, the site SHALL provide Overview, Anatomy, States, Behaviour and keyboard, Accessibility, Content and Try it information, link the component to its actual simulated desktop context, and expose the foundations and style specifications.

Guardrail: Browser simulation and publication do not constitute native GUI acceptance.

#### Scenario: WARLOCK-SITE-008-01

- **GIVEN** a visitor reads a component page
- **WHEN** Try it is activated
- **THEN** the related desktop surface or scenario is reachable

#### Scenario: WARLOCK-SITE-008-02

- **GIVEN** a visitor opens color, motion or focus guidance
- **WHEN** the page renders
- **THEN** the applicable theme, state and accessibility guidance is available

### Requirement: WARLOCK-SITE-009 — Offline relative assets and deployment path

When the site is served beneath /Warlock/ or opened without network access after local assets are available, it SHALL resolve all required runtime scripts, fonts, images, fixtures and internal links from relative bundled paths without requiring a remote service.

Guardrail: Browser simulation and publication do not constitute native GUI acceptance.

#### Scenario: WARLOCK-SITE-009-01

- **GIVEN** the site is served beneath /Warlock/
- **WHEN** a visitor opens the desktop and a component page
- **THEN** local bundles and assets resolve beneath the deployment path

#### Scenario: WARLOCK-SITE-009-02

- **GIVEN** the network is unavailable with the site assets available locally
- **WHEN** the visitor navigates core pages and the test drive
- **THEN** required assets and fixtures do not depend on remote requests

### Requirement: WARLOCK-SITE-010 — Accessible desktop and documentation

While a visitor uses the site, it SHALL support keyboard navigation, visible focus, measured text and essential-boundary contrast, reduced motion and forced colors, preserving accessible names, usable focus return and non-color state cues.

Guardrail: Browser simulation and publication do not constitute native GUI acceptance.

#### Scenario: WARLOCK-SITE-010-01

- **GIVEN** a visitor navigates the desktop and tour using a keyboard
- **WHEN** focus moves between controls
- **THEN** focus remains visible and actions and dismissal remain reachable

#### Scenario: WARLOCK-SITE-010-02

- **GIVEN** reduced motion or forced colors is active
- **WHEN** the site renders effects and state
- **THEN** motion is suppressed or system colors are respected while essential cues remain visible

### Requirement: WARLOCK-SITE-011 — GitHub Pages publication

When the site is published, GitHub Pages SHALL serve the contents of site/ at https://charleshoskinson.github.io/Warlock/ with working relative navigation and assets; publication SHALL use a reproducible deployment and verify the deployed sub-path.

Guardrail: Browser simulation and publication do not constitute native GUI acceptance.

#### Scenario: WARLOCK-SITE-011-01

- **GIVEN** the site deployment completes
- **WHEN** the published home and desktop are opened
- **THEN** both load under /Warlock/ and their local resources resolve

#### Scenario: WARLOCK-SITE-011-02

- **GIVEN** a nested component page is opened directly
- **WHEN** the browser loads it
- **THEN** its styles, scripts and internal navigation resolve under the same sub-path
