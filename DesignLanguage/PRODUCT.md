# Warlock product context

Warlock is an Elm desktop shell for Omarchy that brings a Windows-style taskbar and window controls to Hyprland. Its surfaces are the taskbar with application groups and pins, the Applications launcher with search, the window picker and previews, the Alt-Tab window switcher, Task View and workspace transfer, snap layouts, window and application actions, notifications, Settings, Files and the System menu. Hyprland composes the desktop and manages input, focus, workspaces and window geometry. Warlock sends window requests to Hyprland and shows the result Hyprland reports: a request reads as pending until Hyprland carries it out or refuses it.

## The Elm Architecture

Warlock's interface follows The Elm Architecture. Each program has a Model, a `Msg` type and an `update` function, and programs that render an interface have a `view`. Every change to a Model passes through `update`. Commands (`Cmd`) and subscriptions (`Sub`) describe communication with the outside world, and the compiler checks that every message case is handled. Main coordinates desktop interaction, Bar renders the taskbar for an output, and Popup renders shared panels while managing local text input and previews.

One Elm policy owner holds each domain's state. Typed messages carry intent, and correlated native observations establish what happened. Views are projections of the Model: they emit semantic elements, classes, ARIA and data attributes, and CSS owns their appearance. A receipt alone never establishes an effect, and an Unknown outcome is never replayed automatically. The production-language contract assigns GUI state to Elm and the backend and reviewed native integration to Haskell ([design](../openspec/changes/warlock-design-language-v2/design.md)); the [repository README](../README.md) describes the host and adapter the desktop build runs on.

## People and purpose

Warlock serves people doing sustained windowed work with keyboard, pointer and assistive technology. The design language keeps user intent, visible state and native behaviour in agreement. Focus, selection, application activity, preview freshness and operation outcome each have their own cue, so a pending request looks pending, a refusal shows its reason, and an unconfirmed result never looks like success.

## The website

The [Warlock website](https://charleshoskinson.github.io/Warlock/) is both the reference for the design language and a working demonstration of it. Its sections are Home, Test drive, Foundations, Styles, Components, Architecture and Get started, with Search.

- **Test drive:** a full-viewport simulated Omarchy desktop. Compiled Elm controller and renderer bundles connect through a versioned bridge to a deterministic simulated host, which validates typed identities and epochs and returns receipts separately from observations. Application interiors are local fixtures; the site never launches a native application or reads the visitor's files. A guided tour leads through the real Elm surfaces, and visible controls with a shortcut legend stand in for keys the browser intercepts.
- **Foundations and Styles:** principles, accessibility, layered windows and interaction, then colour, typography, shape, elevation and glow, motion, effects, CSS architecture and iconography.
- **Components:** one page per component with Overview, Anatomy, States, Specimen, Behavior, Accessibility, Content, Evidence and Try it sections. Try it opens the component in the test drive, and Evidence keeps the component's records separately identified.
- **Architecture:** an interactive view of components and connections driven by the verified architecture model, with accessible text and the model's scope.

The site uses relative bundled paths for its scripts, fonts, images, fixtures and links, so they resolve beneath `/Warlock/` and without network access when the files are local. Readers include people evaluating Warlock and developers building consistent controls. A reader succeeds when they find a component, understand its behaviour and limits, and exercise it in the test drive. Simulated behaviour is labelled as simulation and establishes no native acceptance.

## Sources of truth

- Product source: [implementation/warlock](../implementation/warlock/README.md).
- Identity: the [brand guide](../docs/warlock-brand/v2/BRAND-GUIDE.md), the [brand identity](../docs/warlock-brand/README.md) and the [design philosophy](../docs/warlock-brand/PHILOSOPHY.md).
- Foundations and areas: the [foundations specification](../site/design/foundations/spec.md) with its [tokens](../site/design/foundations/tokens.json), [contrast manifest](../site/design/foundations/contrast.json) and [Hyprland values](../site/design/foundations/hyprland.json), and one `spec.md` per area under `site/design/`.
- Requirements: the [EARS requirements](EARS.md) with Revision 2, the [design-language OpenSpec change](../openspec/changes/warlock-design-language-v2/proposal.md), the [design-site OpenSpec change](../openspec/changes/warlock-design-site/proposal.md) and the [stable-target requirements](INTERACTION-ADDENDUM.md). The requirement guardrails keep existing release contracts, deadlines, authority, ownership and native qualification mandatory.
- Guidance and progress: the [current guidance](CURRENT.md) and the [feature checklist](../docs/warlock-roadmap/FEATURE-COMPLETION.md). Frozen catalogs, source manifests, consensus packets and evidence stay unchanged.
