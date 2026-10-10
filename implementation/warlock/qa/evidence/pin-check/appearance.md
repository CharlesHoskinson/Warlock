# Shipped appearance fixture follow-up

The first packet records native pointer/keyboard pin/MAX behavior and the checkbox shape. Its browser page manually initialized the same Popup/adapter and did not load the shipped appearance projector, so its high-contrast-shaped capture did not qualify actual palette/text scaling.

This follow-up uses the shipped `assets/popup.html`, its UTF-8 declaration and `appearance.js`, with only the native message receiver mocked. All 21 existing checks pass; the high-contrast check now also requires the actual root theme, 200%/32px font scaling and black control background. The checked and high-contrast captures have different hashes and retain the checkbox shape. This is component evidence, not native AT or a whole contrast/reflow audit.

The complete verified production source, compiled Elm assets and native host binary hashes are unchanged from the original native report, so its physical keyboard/pointer, MAX geometry and pixel/GTK-hit observations are reused by exact identity. Only the browser fixture and current build reference changed after the first claim. Original recorded evidence is preserved; the contributor record marks its old source observation historical and records this follow-up separately.
