# GitHub publishing copy

This private repository publishes the local ELM/Omarchy Windows parity archive.
The full local archive and its original commit history remain unchanged at
`/home/hoskinson/omarchy-windows-parity`.

GitHub rejects ordinary Git files above 100 MiB. Those files are stored in Git
LFS here. Install Git LFS and run `git lfs pull` after cloning to retrieve the
original logs and build artifacts. LFS checkout restores their original paths
and SHA-256 hashes. The repository's existing proof inventories remain intact.

Publishing rewrites commit IDs to introduce LFS pointers and tracking attributes.
`original-commit-map.csv` maps the original commits to their publishing IDs;
`publication-verification.json` records verification of every file in the
published ELM source commit. Additional publication metadata is stored only in
this `.github` directory. The original local archive must not be force-pushed
over this converted history.

ELM development and qualification continue. This archive includes failed
experiments and pending candidates. Publishing does not certify a finished
release or deploy anything to the desktop.
