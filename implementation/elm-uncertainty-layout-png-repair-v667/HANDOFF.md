# V667 dependency repair for V662 uncertainty diagnostic

Status: **protected CPU dependency/PNG preparation passed; native execution
pending root668**. V662 remains frozen and unchanged. Root664 preserves its
launch failure: `/usr/bin/python3` could not import PIL, before a native fixture
or private session started. This derivative installs nothing and changes no
desktop configuration, backend, frontend, frozen evidence or shared state.
V663 CSS/markup correction remains deferred until controlled native diagnosis.

`qa/native.py` removes the unprovided PIL import and uses `qa/png_inspection.py`.
The inspector uses only Python's standard library. It checks PNG signature and
bounded dimensions/chunks, CRCs, exact bounded zlib decompression, supported
noninterlaced RGB/RGBA8 format and all five row filters, then counts genuine
decoded RGB pixel colors. Alpha is discarded when comparing RGB variation,
matching the original Pillow `convert('RGB')` oracle. It preserves the original
native check identity and requires exactly the DOM viewport pixel dimensions
and more than eight distinct decoded colors. Unsupported snapshot formats fail
explicitly; there is no dimensions-only or file-existence replacement, fake
pixel evidence, OCR assertion or native layout acceptance.

Protected system-Python report:
`qa/dependencies-1791156560435207072/report.json` — **34 checks passed**. Tests
every direct runner/fixture import under `/usr/bin/python3`, installed GI4.1
WebKit snapshot/evaluation and cairo export APIs, the byte-exact662 fixture,
AST-exact original six-second wait and original800x600 LUA geometry. Exercises
ten generated actual RGB/RGBA PNGs covering all filters, an independently
exported actual Cairo surface, malformed/truncated/CRC/trailing/unsupported/
inflate-bomb/bounded-pixel controls, and a one-color negative pixel oracle.
It pins the actual system Python, 220 mapped dependency files and native
keyboard helper (222 total dependency pins). Import/API and Cairo memory
rendering are CPU preparation; no Gtk window, WebKit view or native session
was constructed. The native runner verifies these dependency pins before
creating its private session.

All actual640 compiled root fixtures, packets and built Bar/Popup assets remain
selected through V662's unchanged current-preparation pointer. The native
fixture is byte-identical to662. No packet, title, disabled state, root
publication, keyboard route, observation deadline, output/viewport geometry,
PNG oracle or source finding is changed. The derivative adds dependency receipt
verification and records the PNG inspector in the native input closure. V662's
controlled fixture remains explicitly synthetic transport/title entering the
actual compiled root/actual renderer; this is not authenticated backend/proof
or full UIUX/AT acceptance.

Root alone selects a fresh668 output and launches through the serial wrapper:

```
ELM_LAYOUT_NATIVE_OUTPUT=/home/hoskinson/omarchy-windows-parity/implementation/elm-uncertainty-layout-native-v668/qa/native-1 \
/usr/bin/python3 -B implementation/elm-build-loop-v1/loop.py native \
  --runner /home/hoskinson/omarchy-windows-parity/implementation/elm-uncertainty-layout-png-repair-v667/qa/native.py
```

The output path must be absent and outside frozen667. Existing diagnostic
scope, private host cleanup, preserved source findings UX-UNC-001..003 and
`layoutAcceptance:false` / `ATCompliance:false` stay in force. Source review
must precede root launch. No requirement is marked complete.
