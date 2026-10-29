---
title: "Warlock versioned knowledge space"
created: 2026-10-29
updated: 2026-10-29
---

# Scope and upkeep

The user requested wiki-llm lessons and ideas inside the Warlock repository. This space records portable engineering knowledge and links existing versioned source, original requirements, reviews and bounded evidence. The separate local journal at `~/wiki/topics/warlock/` remains maintained; this is a curated versioned space, not a bulk copy of that journal or private QA state.

Append dated immutable observations under `raw/notes/`, maintain article sources and indexes, and append `log.md`. Keep facts, source-derived hypotheses, proposed ideas, adopted decisions, implementation and original acceptance separate. Record failed outcomes and the observation still missing. Root reviews and publishes owned changes normally; do not make separate Git receipt commits.

Do not store credentials, identity bindings, full transcripts, raw private QA trees, system resources or password prompts. Cite report hashes and versioned canonical evidence when available. Source and `docs/warlock-build-loop/v2/requirement-ledger.json` govern acceptance; this wiki never grants it. Preserve protected QA, one production/native WIP, original deadlines, drafts and concurrent dirty files.

User web-research requirement: always use Scrapling to browse or download web sources. Root verifies uv tool `scrapling[fetchers,rag]` version 0.5 with `scrapling` and `scrapling-mcp` executables. An actual Scrapling GET 200 captures official Elm modules markdown; the initial missing markdownify dependency is resolved through the rag extra. Preserve already acquired primary sources without unnecessary refetch. Report actual fetch limitations rather than silently substituting another client. Do not commit full copyrighted papers.

User development requirement: follow [Fuzzing and contracts](../../docs/warlock-build-loop/v2/FUZZING-CONTRACTS.md), including explicit original preconditions/postconditions/invariants, validated opaque types, actual production-route properties and reproducible bounded fuzzing. Documentation alone does not install a runner or add product dependencies.
