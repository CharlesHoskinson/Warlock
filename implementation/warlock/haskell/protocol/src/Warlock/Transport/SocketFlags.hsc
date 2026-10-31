{-# LANGUAGE ForeignFunctionInterface #-}
-- Header-derived descriptor flags. This module neither adopts nor closes a socket.
module Warlock.Transport.SocketFlags
  ( configureSocketFlags, socketFlagsVerified ) where

#include <fcntl.h>

import Data.Bits ((.&.), (.|.))
import Foreign.C.Error (throwErrnoIfMinus1, throwErrnoIfMinus1_)
import Foreign.C.Types (CInt(..))
import qualified Network.Socket as Socket

foreign import ccall unsafe "fcntl"
  c_fcntl :: CInt -> CInt -> CInt -> IO CInt

getDescriptor, setDescriptor, getStatus, setStatus, closeOnExec, nonBlocking :: CInt
getDescriptor = #{const F_GETFD}
setDescriptor = #{const F_SETFD}
getStatus = #{const F_GETFL}
setStatus = #{const F_SETFL}
closeOnExec = #{const FD_CLOEXEC}
nonBlocking = #{const O_NONBLOCK}

-- Preserve unrelated bits. Caller retains ownership throughout configuration,
-- including partially applied flags if a later syscall fails.
configureSocketFlags :: Socket.Socket -> IO ()
configureSocketFlags socket = Socket.withFdSocket socket $ \descriptor -> do
  flags <- throwErrnoIfMinus1 "F_GETFD" (c_fcntl descriptor getDescriptor 0)
  throwErrnoIfMinus1_ "F_SETFD" (c_fcntl descriptor setDescriptor (flags .|. closeOnExec))
  status <- throwErrnoIfMinus1 "F_GETFL" (c_fcntl descriptor getStatus 0)
  throwErrnoIfMinus1_ "F_SETFL" (c_fcntl descriptor setStatus (status .|. nonBlocking))
  verified <- verifyDescriptor descriptor
  if verified then pure () else ioError (userError "required socket flags not retained")

-- An observation only: it grants no peer identity, custody or native authority.
socketFlagsVerified :: Socket.Socket -> IO Bool
socketFlagsVerified socket = Socket.withFdSocket socket verifyDescriptor

verifyDescriptor :: CInt -> IO Bool
verifyDescriptor descriptor = do
  flags <- throwErrnoIfMinus1 "observe F_GETFD" (c_fcntl descriptor getDescriptor 0)
  status <- throwErrnoIfMinus1 "observe F_GETFL" (c_fcntl descriptor getStatus 0)
  pure (flags .&. closeOnExec == closeOnExec && status .&. nonBlocking == nonBlocking)
