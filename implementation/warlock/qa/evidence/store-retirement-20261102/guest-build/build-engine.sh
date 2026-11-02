#!/usr/bin/env bash
set -euo pipefail
umask 077
WARLOCK_STAGE_ROOT=/home/charl/warlock-mvp-20261101T1058Z
WARLOCK_OLD_BUILD="$WARLOCK_STAGE_ROOT/build-dynamic"
WARLOCK_NEW_BUILD="$(cd "$(dirname "$0")" && pwd)"
WARLOCK_HASKELL_ROOT="$WARLOCK_STAGE_ROOT/source/implementation/warlock/haskell"
export GHC_ENVIRONMENT=- CABAL_DIR="$WARLOCK_OLD_BUILD/cabal-home"
cd "$WARLOCK_HASKELL_ROOT"
sha256sum "$WARLOCK_HASKELL_ROOT/mvp-dynamic.project" "$WARLOCK_OLD_BUILD/cabal.config" /usr/bin/ghc /usr/bin/hsc2hs
cabal --version
cabal --config-file="$WARLOCK_OLD_BUILD/cabal.config" build --offline --enable-shared --disable-library-vanilla --enable-executable-dynamic --flags=vm-security --project-file="$WARLOCK_HASKELL_ROOT/mvp-dynamic.project" --builddir="$WARLOCK_NEW_BUILD/dist" --with-hsc2hs=/usr/bin/hsc2hs warlock-runtime:exe:warlock-ui-owner warlock-runtime:exe:warlock-ui-backend
mkdir -m0700 "$WARLOCK_NEW_BUILD/assets"
for WARLOCK_TARGET in warlock-ui-owner warlock-ui-backend; do
 WARLOCK_EXECUTABLE=$(cabal --config-file="$WARLOCK_OLD_BUILD/cabal.config" list-bin --offline --flags=vm-security --project-file="$WARLOCK_HASKELL_ROOT/mvp-dynamic.project" --builddir="$WARLOCK_NEW_BUILD/dist" "warlock-runtime:exe:$WARLOCK_TARGET")
 install -m0755 "$WARLOCK_EXECUTABLE" "$WARLOCK_NEW_BUILD/assets/$WARLOCK_TARGET"
 sha256sum "$WARLOCK_NEW_BUILD/assets/$WARLOCK_TARGET"
 readelf -d "$WARLOCK_NEW_BUILD/assets/$WARLOCK_TARGET"
 ldd "$WARLOCK_NEW_BUILD/assets/$WARLOCK_TARGET"
done
