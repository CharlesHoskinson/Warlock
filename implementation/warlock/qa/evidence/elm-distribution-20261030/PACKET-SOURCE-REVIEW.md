# Elm distribution packet: factual scope and source review

Disposition: packet suitable for the bounded factual correspondence task; original offline-proof.py remains an unexecuted proposal, not an approved protected checker. Root is adapting it; review the resulting exact source before execution.

Read BRIEF.md, offline-proof.py, retained registry metadata and inventory, response records, fetch-primary.py, and actual installer binary.js source. Graph-first lookup identified DEL005 and release_compliance; graph reported one stale source, so actual files govern. No network, QA, compiler, npm, Node, package script, or downloaded code was executed.

Independently hashed retained bodies: elm.tgz a3aea90afb69d755eb889253a3361cc03a4f924990323c27ea527c70da68d518; linux-x64.tgz ea998aa56c892bf174c055059dde6c55f6fa42239569bc13b4cfa4b36745a0fd; elm.json 6b82a9030dc678326c68484f65e8892f414370edd23f82b753f0484aee0d1fd9; linux-x64.json 3802386554ca42a2807265fbae5ea415c6b91772308cbeefb8f9f678ce2c55c4; inventory.json 47b4920cd1e7e8495237c44b333190ea1cac91f58950ff0f2ff4b3e42b89921f; responses.json b7f736d16d2b7bccdfbcbf6c0c19562a191ad00f9230eaf43c4976945bfa3409. Four retained response rows have matching requested/response URLs, status 200, no Content-Encoding, recorded identity request encoding, disabled redirects, and matching actual body SHA256 and Content-Length/size. These records are retrieval evidence, not independently authenticated signatures or source-to-binary provenance.

The installer source resolves the platform package and, outside Windows/Yarn Berry, links its binary to a temporary pathname and renames that over bin/elm. This supports the documented allowed JS-wrapper-to-native-binary transformation. It does not prove this code ran during the historical installation. Different current inode values/nlink=1 mean the two installed files are not currently hardlinked; no past-history inference follows.

Concrete proposal gaps already sent to root:

- safe() must enforce the exact package/ prefix in addition to traversal, empty-component, absolute, backslash and duplicate refusal.
- Member type/size/link-field constraints should be explicit, with bounded member counts, declared sizes and aggregate expansion; no filesystem extraction is needed.
- Hold each pinned raw body once and decode/inspect those same bytes instead of hashing then reopening.
- Pinning responses.json is not semantic validation: join each unique expected response to its package/kind/file, exact URL, status, encoding/redirect facts and actual held body size/hash.
- The original installed-bytes negative only compares sha(altered) with the expected digest. Exercise the actual installed-byte validator with an altered input instead; likewise exercise the actual tar reader for malformed member cases if those are claimed.

DEL005 requires package files, SBOM components, upstream notices and reviewed dispositions. This packet can reduce a specific npm distribution-byte correspondence gap only. Archive package.json BSD-3-Clause metadata and the absence of a named LICENSE member do not establish a grant, complete attribution, notice applicability, or redistribution disposition. No compiler Git-tag/build correspondence, publisher signature verification, other-platform review, installation history, release or native acceptance is claimed. All existing unknown decisions remain unknown until separately reviewed.

The retained fetch-primary.py SHA256 fd7f392aa64574ce8b28121f2ad730f2d8d3bf88a2533312921bcd4f1c14e265 is post-retrieval edited source for cookie redaction. Do not label it the actual executed retrieval-source identity. The brief explicitly preserves that limitation.
