-- Bounded wire framing only; no endpoint, authentication or authority factory.
module Warlock.Protocol.Framing (FrameError(..), prefix, headerLength) where
import Warlock.Transport.Frame (FrameError(..), prefix, headerLength)
