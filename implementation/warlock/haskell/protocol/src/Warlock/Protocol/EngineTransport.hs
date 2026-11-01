-- Narrow engine transport surface over the existing ancillary-data reader.
-- These observations and byte bounds grant no process or native authority.
module Warlock.Protocol.EngineTransport
  ( CredentialReader, CredentialError(..), CredentialChunk(..)
  , newCredentialReader, enablePassCredentials, receiveCredentialChunk
  , credentialReaderReusable, configureSocketFlags, enginePrefix, engineHeaderLength
  , startupPrefix, startupHeaderLength
  ) where

import qualified Data.ByteString as B
import qualified Warlock.Transport.PeerCredentials as Credentials
import Warlock.Transport.PeerCredentials
  ( CredentialReader, CredentialError(..), CredentialChunk(..)
  , newCredentialReader, enablePassCredentials, receiveCredentialChunk )
import Warlock.Transport.SocketFlags (configureSocketFlags)
import Warlock.Transport.Frame (FrameError, prefixWithLimit, headerLengthWithLimit)

-- Whole inner frame; its separate four-byte prefix counts header bytes only.
enginePrefix, startupPrefix :: B.ByteString -> Either FrameError B.ByteString
enginePrefix = prefixWithLimit 393732
startupPrefix = prefixWithLimit 512

engineHeaderLength, startupHeaderLength :: B.ByteString -> Either FrameError Int
engineHeaderLength = headerLengthWithLimit 393732
startupHeaderLength = headerLengthWithLimit 512

-- Read only after the sole receive owner has quiesced. This is a momentary
-- reusability observation, never child/socket/whole-cleanup acceptance.
credentialReaderReusable :: CredentialReader -> IO Bool
credentialReaderReusable reader = do
  status <- Credentials.credentialReaderStatus reader
  problems <- Credentials.readerExceptions reader
  pure (status == Credentials.ReaderReady && null problems)
