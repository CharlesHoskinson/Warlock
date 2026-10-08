# Warlock Design Language

Warlock's design language, branding, visual library and widget catalog live here. Five actual Opus 5.5/high reviewers reached unanimous agreement on 30 contracts after researching the named references and checking the selected Elm/style/bridge closure. The [consensus](CONSENSUS.md) preserves the existing [identity](../docs/warlock-brand/README.md), [philosophy](../docs/warlock-brand/PHILOSOPHY.md) and original release obligations.

- [Product context](PRODUCT.md) and [visual system](DESIGN.md)
- [Implementation workplan](WORKPLAN.md)
- [EARS requirements](EARS.md) and [OpenSpec change](../openspec/changes/warlock-design-language/proposal.md)
- [Exact voted candidate and ballots](research/v1/consensus-receipt-v2.json)
- [Current design guidance](CURRENT.md) and [browser catalog entrance](catalog/index.html)
- [Frozen v6 browser specimens](catalog/v6/index.html) and [catalog closure record](catalog/WORKPLAN.md)
- [Layered-window language](layered-windows/v1/README.md): color, glow, shadow and shading
- [Design contributions and new contributor plugin](CONTRIBUTING.md)
- [Stable-target and observed-toggle EARS/OpenSpec clarification](INTERACTION-ADDENDUM.md)
- [Remaining product implementation](../docs/warlock-roadmap/FEATURE-COMPLETION.md)

The v6 catalog is published and qualified for its frozen 49-module/14-family browser scope. Later product surfaces are documented in the current guidance; complete current widget coverage and native design adoption remain open. The new catalog entrance includes a contributor-plugin section. Source, proposals, browser demos and native qualification remain distinct; no full WCAG, native GUI or release acceptance follows from catalog checks.

Serve the current documentation entrance and frozen specimens locally from the repository:

```sh
python3 -m http.server 8012 --bind 127.0.0.1 --directory .
```

Open `http://127.0.0.1:8012/DesignLanguage/catalog/`. Browser specimens and assets are local; Markdown links display repository documents. View Markdown through GitHub or your editor for formatted prose. No desktop effects run from the catalog.
