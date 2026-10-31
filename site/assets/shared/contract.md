# Shared authoring contract

Load layers.css, optional runtime legacy CSS within the legacy layer, tokens.css, fonts.css, site.css, effects.css and then page-local styles. The template demonstrates the complete navigation and relative paths from a topic page. Set the root path for the page being authored. Use explicit index.html links. Do not fetch navigation at runtime.

Use the `wl-doc-*` documentation classes and `wl-specimen-*` framing. Theme specimens set `data-theme` to night, dawn or high-contrast; semantic aliases follow the containing theme. Use the semantic `--wl-sys-*` tokens and the declared cascade layers. Keep runtime selectors scoped to actual surface attributes. Keep focus, active application, candidate, recipient and selection cues distinct. CSS owns presentation; Elm owns interaction policy. The shared effect completion helper reports decoration completion only.

## Authoring checklist

- Give each page one h1, a meaningful title and description, a skip link, a main landmark, complete navigation and a page index.
- Use actual relative links and local assets. Keep essential content and navigation available without JavaScript.
- Reserve focus paint space, provide visible labels and use native buttons and links. Keep links underlined.
- Test 320px effective width, 200% zoom, keyboard operation, forced colors and reduced motion.
- Describe observed facts and outcomes accurately. Identify fixtures and evidence. Use The Elm Architecture.
- Include a package manifest with source, hash, size, license, classification, alt text and caption for each asset.
