-- Bounded wire framing only; no endpoint, authentication or authority factory.
module Warlock.Protocol.Framing (FrameError(..), prefix, headerLength, desktopCommitPrefix, desktopCommitHeaderLength, desktopGatewayPrefix, desktopGatewayHeaderLength) where
import qualified Data.ByteString as B
import Warlock.Transport.Frame (FrameError(..), prefix, headerLength, prefixWithLimit, headerLengthWithLimit)

-- Explicit application wrappers; existing native defaults remain fixed.
desktopCommitPrefix, desktopGatewayPrefix :: B.ByteString -> Either FrameError B.ByteString
desktopCommitPrefix = prefixWithLimit 131072
desktopGatewayPrefix = prefixWithLimit 1048704
desktopCommitHeaderLength, desktopGatewayHeaderLength :: B.ByteString -> Either FrameError Int
desktopCommitHeaderLength = headerLengthWithLimit 131072
desktopGatewayHeaderLength = headerLengthWithLimit 1048704
