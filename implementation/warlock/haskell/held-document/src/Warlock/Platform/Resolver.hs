-- Public facade intentionally excludes test hooks and alternate proc bootstrap.
module Warlock.Platform.Resolver
 (Root, Identity(..), Kind(..), Pin(..), Link(..), Resolution(..), ResolveError(..), withRoot, resolveSnapshot) where
import Warlock.Platform.Resolver.Internal
