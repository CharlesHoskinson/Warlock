# Scoped Mutter source and developer documentation corpus

Acquired 2026-10-03 with Scrapling Fetcher. This directory retains provenance and the initial selected raw sources. The complete pinned source archives and raw developer HTML are stored at `/home/hoskinson/.cache/elm-roadmap-mutter/`; consult `corpus-manifest.json` for URLs, exact hashes and absolute paths.

- `manifest.json`: original small raw source subset at historical 49.0, including annotated tag resolution and COPYING.
- `49.0-source-inventory.json`: complete regular-file inventory of commit `7697a7993e92dcef3b39b67051691a8b28f0b5ce` (2,216 files).
- `main-pinned-source-inventory.json`: complete regular-file inventory of acquisition-time upstream main commit `285f54d394b6c041dcdab90d79ecdb761af655ec` (2,246 files).
- `head-commit.json`: raw official mirror commit metadata.
- `51.0-tag-status.json` and its manifest: confirmation that a newer release tag exists. 49.0 is not claimed as latest stable.
- `tags-at-acquisition.json`: one paginated mirror tag listing; ordering is not chronological, so this alone cannot establish latest stable.
- `corpus-manifest.json`: source archive hashes and scoped same-origin documentation crawl completion/failure ledger.

Archives were downloaded as raw response bytes through Scrapling, read as gzip tar, and safely extracted without executing source code. Extraction writes regular files only, rejects absolute/traversal paths and skips nonregular members. This is complete regular-file source coverage for each archive, not preservation of original symlink objects, modes or archive directory metadata. Raw archives preserve those originals.

Documentation scope starts at `https://mutter.gnome.org/` and follows reachable same-origin `.html` and directory links, stripping fragments and queries. Raw HTML bodies are preserved. The crawler has a 20,000-page safety cap; its remaining queue and failures determine the actual closure claim. It excludes external GNOME sites, historical unreachable pages, scripts/assets and arbitrary search query variants. Generated docs are acquisition-time content, not asserted to match either source commit. Cache hashes and archive records can be independently verified; this directory is not a full upstream source redistribution.

Read `../../contributions/gnome-layering.md` for confirmed source observations, product-policy differences and the derived Elm/native design. Neither acquiring source nor reading documentation establishes native acceptance on the user's desktop.

Final crawl closure: 5,747 reachable HTML URLs visited, 5,744 HTTP-200 bodies retained and three HTTP-404 bodies retained; remaining queue is empty. The earlier 5,000-page capped ledger is preserved as `corpus-initial-capped-manifest.json`, including cached response-status provenance. All final archive and page hashes were rechecked.

A portable copy of the complete source archives, regular-file extraction and raw developer pages is included in [complete/](complete/). [Portable source mapping](portable-corpus-manifest.json) uses paths relative to this directory; original cache provenance remains unchanged.
