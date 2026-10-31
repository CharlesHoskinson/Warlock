# Warlock Design Language

Warlock's design language is **Lacquer**: mineral black, warm ivory, deep red action surfaces and luminous red details. Black and red are the primary colours. Secondary colours convey information: focus, information, positive outcomes, warnings and danger, each with its own shape and words, and danger stays distinct from brand red. The folded W keeps neutral facets and one red focal diamond. Space Grotesk, Inter and JetBrains Mono set the type. The Elm view sets classes and data attributes, and CSS owns the visuals. The tagline is **Crafted for flow.**

The [Warlock website](https://charleshoskinson.github.io/Warlock/) publishes the language with live specimens, component pages and a test drive of the compiled Elm interface on a simulated Omarchy desktop. Its source is the repository's `site/` folder.

## Documents

- [Visual system](DESIGN.md): colour roles, contrast, typography, identity, the focused-window treatment, depth, the signature portal and the CSS architecture.
- [Product context](PRODUCT.md): what Warlock is, who it serves, The Elm Architecture and the sources of truth.
- [Current guidance](CURRENT.md): how the language applies to each window and surface, with the evidence record for Warlock's behaviour.
- [Stable targets and observed toggles](INTERACTION-ADDENDUM.md): picker geometry and the Always on top control.
- [EARS requirements](EARS.md): the thirty design contracts and Revision 2, which specifies Lacquer, the attention vocabulary, elevation, the portal and the CSS and Elm presentation contract.
- [Implementation workplan](WORKPLAN.md) and the [consensus summary](CONSENSUS.md) for the thirty contracts.
- [Design contributions](CONTRIBUTING.md) and the [Warlock contributor plugin](../plugins/warlock-contributor/README.md).
- [Remaining product implementation](../docs/warlock-roadmap/FEATURE-COMPLETION.md).

## Sources of truth

- [Brand guide](../docs/warlock-brand/v2/BRAND-GUIDE.md) with its [design tokens](../docs/warlock-brand/v2/tokens.json), the [brand identity](../docs/warlock-brand/README.md) and the [design philosophy](../docs/warlock-brand/PHILOSOPHY.md).
- Foundations: the [foundations specification](../site/design/foundations/spec.md), [tokens](../site/design/foundations/tokens.json), [contrast manifest](../site/design/foundations/contrast.json) and [Hyprland values](../site/design/foundations/hyprland.json).
- Area specifications: [taskbar](../site/design/taskbar/spec.md), [Applications launcher](../site/design/launcher/spec.md), [window switcher](../site/design/window-switcher/spec.md), [Task View and workspaces](../site/design/task-view/spec.md), [window previews and snap layouts](../site/design/previews-snap/spec.md), [System and menus](../site/design/system-menus/spec.md), [notifications](../site/design/notifications/spec.md), [Settings](../site/design/settings/spec.md) and [Files](../site/design/files/spec.md).
- OpenSpec: [warlock-design-language-v2](../openspec/changes/warlock-design-language-v2/proposal.md) specifies Lacquer, its states and its presentation contract, and [warlock-design-site](../openspec/changes/warlock-design-site/proposal.md) specifies the website and its simulated desktop. The [warlock-design-language](../openspec/changes/warlock-design-language/proposal.md) change holds the thirty design contracts and their scenarios; Revision 2 modifies the affected requirements by identity.
- [EARS requirements](EARS.md), Revision 2.

## Versioned packets

- `catalog/v1` to `catalog/v6` are frozen specimen catalogs. The [catalog entrance](catalog/index.html) links to them, [catalog v6](catalog/v6/index.html) is the last frozen catalog, and the [catalog closure record](catalog/WORKPLAN.md) is its checklist. Their checks apply to their frozen specimens.
- `layered-windows/v1` is the first layered-window language packet: its [overview](layered-windows/v1/README.md), [roles](layered-windows/v1/DECISIONS.md) and [EARS](layered-windows/v1/EARS.md). It uses the schema-1 palette, which Revision 2 preserves in its versioned baseline; Lacquer supplies the colours for the same roles.
- `research/` holds the review record for the thirty contracts, including the [consensus receipt](research/v1/consensus-receipt-v2.json) with each ballot and its hash.

## Viewing locally

Serve the catalog entrance and frozen specimens from the repository root:

```sh
python3 -m http.server 8012 --bind 127.0.0.1 --directory .
```

Open `http://127.0.0.1:8012/DesignLanguage/catalog/`. Browser specimens and assets are local, and Markdown links open repository documents. View Markdown through GitHub or an editor for formatted prose. No desktop effects run from the catalog.
