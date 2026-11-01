{-# LANGUAGE OverloadedStrings #-}
-- Only the owning Wayland transport crosses startup, not arbitrary env.
-- This transport selection does not authenticate compositor effects.
module Warlock.Ui.Display
 (DisplayEnvironment, captureDisplayEnvironment, captureDisplayTransport,
  displayEnvironmentPairs, readDisplayEnvironment, resolveDisplayEnvironment) where
import Control.Exception (IOException, try)
import Control.Monad (unless)
import Data.Bits ((.&.))
import Data.Text (Text)
import System.Environment (lookupEnv)
import System.Posix.Files (fileMode, fileOwner, getSymbolicLinkStatus, isDirectory, isSocket)
import System.Posix.User (getRealUserID, getEffectiveUserID)

-- Capture before entering the private user namespace. Its single UID mapping
-- changes how root-owned outer /run ancestors are represented; rechecking
-- their numeric owners there would reject an already validated transport.
-- These immutable settings grant no compositor or window-effect authority.
newtype DisplayEnvironment = DisplayEnvironment [(String,String)]

displayEnvironmentPairs :: DisplayEnvironment -> [(String,String)]
displayEnvironmentPairs (DisplayEnvironment pairs) = pairs

captureDisplayEnvironment :: IO (Either Text DisplayEnvironment)
captureDisplayEnvironment = do
 runtime <- lookupEnv "XDG_RUNTIME_DIR"
 display <- lookupEnv "WAYLAND_DISPLAY"
 captureDisplayTransport runtime display

captureDisplayTransport :: Maybe FilePath -> Maybe String -> IO (Either Text DisplayEnvironment)
captureDisplayTransport runtime display = fmap (fmap DisplayEnvironment) (resolveDisplayEnvironment runtime display)

readDisplayEnvironment :: IO (Either Text [(String,String)])
readDisplayEnvironment = fmap (fmap displayEnvironmentPairs) captureDisplayEnvironment

resolveDisplayEnvironment :: Maybe FilePath -> Maybe String -> IO (Either Text [(String,String)])
resolveDisplayEnvironment Nothing Nothing = pure (Right [])
resolveDisplayEnvironment (Just runtime) (Just display) = do
 observed <- try $ do
  uid <- getRealUserID
  effective <- getEffectiveUserID
  let suffix = drop 8 display
      ascii c = c >= 'a' && c <= 'z' || c >= 'A' && c <= 'Z' || c >= '0' && c <= '9'
      validName = take 8 display == "wayland-" && not (null suffix) && length display <= 64
               && all (\c -> ascii c || c == '-' || c == '_') suffix
      require good = unless good (ioError (userError "private UI display transport refused"))
  require (uid /= 0 && uid == effective && runtime == "/run/user/" ++ show uid && validName)
  mapM_ (\path -> do
    status <- getSymbolicLinkStatus path
    require (isDirectory status && fileOwner status `elem` [0,uid] && fileMode status .&. 0o022 == 0)) ["/run", "/run/user"]
  directory <- getSymbolicLinkStatus runtime
  require (isDirectory directory && fileOwner directory == uid && fileMode directory .&. 0o777 == 0o700)
  socket <- getSymbolicLinkStatus (runtime ++ "/" ++ display)
  require (isSocket socket && fileOwner socket == uid)
  pure [("XDG_RUNTIME_DIR",runtime),("WAYLAND_DISPLAY",display)]
 pure (either (const (Left "private UI display transport unavailable")) Right (observed :: Either IOException [(String,String)]))
resolveDisplayEnvironment _ _ = pure (Left "incomplete private UI display transport")
