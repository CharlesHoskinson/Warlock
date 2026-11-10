# GTK keyboard menu routing

Warlock disables `menu.popup` on the hidden GtkTextView that WebKitGTK uses for keyboard command translation. The host checks that this widget is the unique direct GtkTextView child of each owned visible WebView. Elm retains menu policy. Text and IME forwarding remain unchanged.

The retained native failure shows a Bar popover after Shift+F10. Its diagnostic prefix is incomplete. Matching WebKit 2.54.2 source identifies the hidden translator route. The prefix alone does not identify every callback or focused widget type.

Source commit `6062be95be9cc0ecdf657c97ea863b9cd148c08e` passes eight source/header contracts and the ordinary two-target build with both CPU control programs. The original native UX-024 journey remains open at this observation. No original acceptance follows from these component checks.

## Documentation disposition

| Documentation | Disposition |
| --- | --- |
| Tutorial: `docs/warlock/tutorials/first-contribution.md` | Unchanged. Developer setup and contribution steps remain the same. |
| How-to: `docs/warlock/how-to/verify-selected-change.md` | Unchanged. The existing protected CPU and native routes still apply. |
| Reference: `docs/warlock/reference/build-and-runtime.md` | Unchanged. Build targets, runtime protocol and timing bounds remain the same. |
| Explanation | This page records the internal keyboard route and the targeted action change. |

`inventory.json` binds the source, controls, retained diagnostic failure and actual build evidence. All original failure and cleanup flags remain unchanged.
