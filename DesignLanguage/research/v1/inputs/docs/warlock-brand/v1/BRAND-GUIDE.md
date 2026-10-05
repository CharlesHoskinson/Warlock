# Warlock brand guide

Warlock makes the desktop's behavior understandable and gives everyday work continuity. Its visual identity uses arcane craft, folded geometry and event streams. The tagline is “Crafted for flow.” It expresses a design intention, not a measured performance claim.

## The flow sigil

The W uses two folded valleys and a separate central diamond. The facets express composition; the diamond gives changing paths a stable point of reference. A few event dots and restrained ribbons extend the identity into illustrations. These are metaphors, not a diagram of the native ownership protocol.

Use the supplied vector mark for interface assets. The GPT-generated identity board and wallpaper establish the art direction; the transparent raster mark remains useful for large illustrations. The editable vector companion follows that direction with crisp planar geometry.

Keep at least one diamond-width of clear space around the mark. Use the full-color mark at32px and above. At24–31px use a monochrome silhouette; remove color-dependent detail. Below24px use a simple W letterform. Keep the diamond visible wherever the full sigil is used. On light backgrounds use a dark monochrome mark. The app icon supplies its own dark field.

## Color

| Token | Value | Use |
| --- | --- | --- |
| Ink | `#10111A` | Background and icon field |
| Parchment | `#F5F0E8` | Main text and a pale logo facet |
| Lilac | `#B7A2FF` | Primary brand accent |
| Stream mint | `#7DE2C1` | Event paths and supporting accent |
| Ember gold | `#F0BE75` | State diamond and sparse highlights |
| Muted slate | `#ABB1C4` | Secondary text on ink |

The light theme uses separately specified darker accents; do not place the dark-theme pastels on parchment as text. `tokens.json` and `tokens.css` define both sets. Use words and control states alongside status colors. Decorative gold and mint never constitute evidence that a request committed or a frame presented.

## Typography

Space Grotesk Bold is the display face and wordmark basis. Inter handles readable body text and controls. JetBrains Mono is for examples and technical metadata. All three fonts are bundled with their upstream license and commit-bound provenance. The artwork's generated wordmark is a concept rendering; the offline preview uses real font glyphs for exact spelling and dependable layout.

Write the name as Warlock in prose and WARLOCK in the display wordmark. Avoid blackletter, ornamental rune alphabets and distorted body text. Let the imagery carry the fantasy association while the interface remains easy to read.

## Illustration and motion

Keep wallpapers dark and spacious, with the most detailed forms away from likely text and icon areas. Use sparse ribbons, folded translucent planes and a small warm center. The supplied wallpaper establishes this approach. Keep glows out of the small logo and ordinary controls.

The brand preview starts still. Animation requires an explicit toggle, stops when the document is hidden, and obeys reduced-motion preference changes. Product animation must follow native presented geometry and the frozen S02 policy. The brand does not define response deadlines, capture cadence or accepted frame rates.

## Voice

Use direct descriptions: “The window is unavailable,” “The result is still unconfirmed,” and “Reconnect.” Keep operational controls in familiar language. Warlock's name and artwork supply the atmosphere; errors should help the person act.

Avoid promises of flawless behavior, magic fixes or guaranteed superiority. Say which behavior has actually been qualified. Pending, committed, refused, cancelled, presented and unconfirmed remain distinct.

## Community concepts

[ReactiveX's observable documentation](https://reactivex.io/documentation/observable.html) uses marble diagrams to show event sequences and transformations. Warlock borrows that visual grammar for ribbons and event dots. ReactiveX is one part of the wider reactive-programming community, not a definition of all FRP.

[The Elm Architecture](https://guide.elm-lang.org/architecture/) describes Model, View and Update. Warlock's stable core and composed facets are visual interpretations of coherent state and explicit transformations. Modern Elm Architecture is the implementation model here; the artwork does not imply that we use historical Elm Signals or adopt ReactiveX as a runtime dependency.

## Assets and provenance

The built-in GPT image-generation tool produced the three raster assets. Exact prompts live in `prompts/`. Vector companions, design tokens and the offline preview are deterministic source assets. `asset-manifest.json` records dimensions, transparency, hashes and generation provenance. Font licenses stay with the font files when the package is redistributed.
