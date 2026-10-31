# Warlock design catalog

The final browser catalog is `v6/index.html`. It contains 14 current source component families across all 49 selected Elm modules, six consistent sections per component, searchable navigation, deep links, dark/light/system appearance, semantic/component tokens, proposed controls, reference decisions and exact source/content inventories. Menu, preview and taskbar demonstrations run the compiled real Elm modules with explicit fixture data; they never connect to the compositor.

To serve the self-contained catalog locally, from the repository:

```bash
python3 -m http.server 8012 --bind 127.0.0.1 --directory DesignLanguage/catalog/v6
```

Open `http://127.0.0.1:8012`. All assets and fonts are local; no external service is required. External reference links are optional.

The pinned Elm build, 42 source/token checks and 104 browser checks passed. Seven confirmation captures cover dark desktop, light tokens/menu, 390px/320px widths and forced colors. A fresh independent finish review accepted with corrections; B1–B3 were resolved in one correction batch and verified in the confirmation receipt. See `../finish-receipt.json`. Previous compile, test-expression and fixture-observation failures are preserved in v1–v5.

The selected source closure, source copy and catalog styling are distinct. Fixture row details are explicitly labeled fixture copy. Popup h1 nesting, checked semantics, keyed popup identity, single announcement routing and full native focus/input/AT/IME remain product findings. Browser checks do not grant native acceptance or complete the GUI release. Local browser profiles and mutable copies of the separately pinned package cache are preserved locally but excluded from publication inputs.
