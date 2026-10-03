# Primary architecture reference corpus

Scrapling acquisitions retain raw sources, source revisions, hashes, extraction inventories and failed responses. This is a scoped collection of Mutter/KWin source snapshots and developer documentation, not every GNOME/KDE project or website.

- [Mutter acquisition and interpretation](../contributions/gnome-layering.md). Small source references and corpus metadata live in `mutter/`; complete raw archives/extracted trees and developer pages are identified by the acquisition inventory.
- [KWin acquisition and interpretation](../contributions/kde-layering.md). Small source references and corpus metadata live in `kwin/`; complete archives/source trees and developer pages are identified by the acquisition inventory.
- [Planning format and GPU sources](planning/sources.json): OpenSpec CLI/schema, EARS author guidance, WebGPU specification/error model, pinned Qt GPU documentation and WebKit release/build references.

Pinned historical source versions remain labeled as historical. Current upstream snapshots are recorded by commit and are not silently labeled stable releases. A crawler stopping at a bound, unavailable routes or JavaScript-only shells is recorded as a coverage limitation; successful HTTP status alone does not establish substantive documentation.
