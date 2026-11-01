-- A trusted owner selects a profile before offering a socket. Wire data cannot.
module Warlock.Protocol.Profile
  (CodecProfile, nativeProfile, desktopProfile, clientLimit, serverLimit) where

data CodecProfile = Native | Desktop deriving (Eq, Show)

nativeProfile, desktopProfile :: CodecProfile
nativeProfile = Native
desktopProfile = Desktop

clientLimit, serverLimit :: CodecProfile -> Int
clientLimit profile = if profile == nativeProfile then 65536 else 131072
serverLimit profile = if profile == nativeProfile then 65536 else 1048704
