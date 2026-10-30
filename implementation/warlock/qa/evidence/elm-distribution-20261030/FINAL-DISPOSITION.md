# Elm npm distribution correspondence: final bounded disposition

Disposition: PASS for the exact factual distribution/installed-byte correspondence check and its 28 recorded positive/refusal assertions. DEL005 remains PARTIAL; this is not acceptance of the original complete SBOM/notices/redistribution scenario or a change to any unknown disposition.

## Reviewed identities and execution evidence

- Public checker: `400c78e596344762ca73760d881cfa8d88f7e473fac4383a7281a85f3a8ff8be`.
- Private check_cases.py: `ccce795b5d1989db3892db71b2ff7cb99e2c9560fba012c383dace8ab73f605a`.
- cases-report.json: `3a12bb66c03a31f5a2c0e8c0ab344b795e40cd2f0805574a7225010987a5c92a`.
- proof.stdout: `cc32906b3de27ea42a616e58e59f556d49333324eb8a49e86c511e18ca61b725`.
- Empty proof.stderr: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

Reports are retained under `native-rebuild/elm-distribution-root-v1`. Both the direct checker output and driver report identify protected scope `qa-harness-1121ce8e8a684d7a971f192e74f56ca6.scope` with coreLimit 1. The driver records normal direct-checker exit, all 28 checks true, and unchanged executed checker source; the present source hashes equal the reviewed versions. Root reports terminal exit 0 and invocation `67f151f39fac4b7b92038d172b2349b0`; no independent process execution was performed by this reviewer.

## What the actual result establishes

The checker reads pinned raw primary-response bodies once, checks the exact held package-lock identity, joins all four response identities/URLs/statuses/body hashes/sizes/Content-Length and encoding/redirect facts, and verifies SHA512 SRI over each saved compressed archive. Metadata and archived package names/versions match the locked elm and @elm_binaries/linux_x64 distributions, both version 0.19.2-0.

Actual elm archive SHA256 is `a3aea90afb69d755eb889253a3361cc03a4f924990323c27ea527c70da68d518` with five regular files. Actual linux_x64 archive SHA256 is `ea998aa56c892bf174c055059dde6c55f6fa42239569bc13b4cfa4b36745a0fd` with three regular files. The exact eight-member inventories are retained in proof.stdout. No separately named LICENSE/COPYING member appears in those inventories; both package manifests declare BSD-3-Clause. These are observed metadata facts, not license conclusions.

All eight current installed regular files are accounted for by the independent archive map with exactly one explicitly permitted content placement. Four installer files and all three platform-package files byte-match their archive counterparts. The installer archive bin/elm is a 1038-byte JavaScript wrapper (`5eac6b132f8365dad041b683dd0b23bad99fac4b8537bd6c27cd274a1b8d93e2`). Its installed path instead contains the exact 47976272-byte platform archive ELF (`c4db5a7ef59fc582a1df29c16383520015e9cefb0802e6eb49955e49211d7948`), which also equals the installed platform binary. The pinned binary.js/install.js and package manifest document this placement. Present device/inode facts show the two installed binary paths are not currently hardlinked (same device 58, inodes 615718/615713, nlink 1 each).

The actual refusals cover changed lock/archive/SRI, duplicate JSON keys, FIFO input without a blocking read, requested/response URL, status, body size, Content-Length, encoding, metadata version after a coherent updated body receipt, invalid prefix/traversal/absolute/duplicate archive paths, link/contiguous/directory member types, and oversized declared member size. Synthetic archives carry matching SRI, so these checks reach the structural guards. The copied installed layout passes first; changing ELF byte 100 from 0 to 1 then reaches the actual installed inventory/byte guard and is refused. The altered-copy SHA256 is `ead748e287b74b07501209c2366c212e2e72e44725606f05a707529ffdfe0bec`. The original toolchain validates afterward. This is a fixed bounded contract set, not exhaustive fuzzing or a proof of every malformed archive case.

## Limits preserved

No downloaded script, compiler, installation, network request or native runtime was executed in this protected check. It establishes bytes and current layout, not who built the compiler, upstream Git/source-build correspondence, historical installer execution or past hardlinking. No publisher signature authentication is claimed. The producer inventory is retained research provenance rather than the correctness oracle. The retrieval source was edited after capture; its present hash is not an attested executed fetch-source identity, and response headers include explicit cookie redaction.

Only these two platform-selected packages were inspected; other optional platform packages are outside scope. No project grant, upstream notice completeness/applicability, reviewed redistribution disposition, native acceptance, release acceptance, or complete DEL005 acceptance follows. Existing unresolved package and compiler/runtime obligations and the current release compliance block remain in force.

Independent review consisted of source and retained report inspection and read-only hashing. No QA or public edits were performed by this reviewer.
