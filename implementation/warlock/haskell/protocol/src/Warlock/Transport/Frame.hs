{-# LANGUAGE OverloadedStrings #-}
-- Pure framing; no authority or native effect follows from a complete frame.
module Warlock.Transport.Frame (Framer, FrameError(..), empty, feed, eof, prefix, headerLength, prefixWithLimit, headerLengthWithLimit) where
import qualified Data.ByteString as B
import Data.Bits (shiftL, shiftR, (.&.))
import Data.Word (Word8, Word32)

data Framer = Header B.ByteString | Body Int B.ByteString deriving (Eq,Show)
data FrameError = ZeroLength | TooLarge | TruncatedHeader | TruncatedBody deriving (Eq,Show)
empty :: Framer
empty = Header B.empty
prefix :: B.ByteString -> Either FrameError B.ByteString
prefix = prefixWithLimit 65536
prefixWithLimit :: Int -> B.ByteString -> Either FrameError B.ByteString
prefixWithLimit limit bytes
  | n == 0 = Left ZeroLength
  | limit <= 0 || limit > 1048704 || n > limit = Left TooLarge
  | otherwise = Right (B.pack [octet 24,octet 16,octet 8,octet 0] <> bytes)
  where n = B.length bytes
        octet bits = fromIntegral ((n `shiftR` bits) .&. 255) :: Word8
-- Consumes at most one frame. Remaining input is returned to its owner, with
-- no growing queue or hidden copying of coalesced frames.
headerLength :: B.ByteString -> Either FrameError Int
headerLength = headerLengthWithLimit 65536
headerLengthWithLimit :: Int -> B.ByteString -> Either FrameError Int
headerLengthWithLimit limit header
  | B.length header /= 4 = Left TruncatedHeader
  | n == 0 = Left ZeroLength
  | limit <= 0 || limit > 1048704 || toInteger n > toInteger limit = Left TooLarge
  | otherwise = Right (fromIntegral n)
  where n = B.foldl' (\acc byte -> (acc `shiftL` 8) + fromIntegral byte) (0 :: Word32) header
feed :: Framer -> B.ByteString -> Either FrameError (Framer,Maybe B.ByteString,B.ByteString)
feed (Header old) input =
  let (part,rest) = B.splitAt (4 - B.length old) input
      header = old <> part
  in if B.length header < 4 then Right (Header header,Nothing,B.empty) else do
       expected <- headerLength header
       feed (Body expected B.empty) rest
feed (Body expected old) input =
  let (part,rest) = B.splitAt (expected - B.length old) input
      body = old <> part
  in if B.length body == expected then Right (empty,Just body,rest)
     else Right (Body expected body,Nothing,B.empty)
eof :: Framer -> Either FrameError ()
eof (Header h) | B.null h = Right ()
               | otherwise = Left TruncatedHeader
eof (Body _ _) = Left TruncatedBody
