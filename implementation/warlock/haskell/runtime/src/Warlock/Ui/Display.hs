{-# LANGUAGE OverloadedStrings #-}
-- Only selected private Wayland and optional AT transports cross startup.
-- This transport selection does not authenticate compositor effects.
module Warlock.Ui.Display
 (DisplayEnvironment, captureDisplayEnvironment, captureDisplayTransport,
  displayEnvironmentPairs, readDisplayEnvironment, resolveDisplayEnvironment) where
import Control.Exception (IOException, try)
import Control.Monad (unless)
import Data.Bits ((.&.))
import Data.List (intercalate, inits, isPrefixOf)
import Data.Text (Text)
import System.Environment (lookupEnv)
import System.Posix.Files (fileMode, fileOwner, getSymbolicLinkStatus, isDirectory, isSocket, deviceID, fileID)
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
 accessibility <- lookupEnv "AT_SPI_BUS_ADDRESS"
 fmap (fmap DisplayEnvironment) (resolveSelectedTransports runtime display accessibility)

captureDisplayTransport :: Maybe FilePath -> Maybe String -> IO (Either Text DisplayEnvironment)
captureDisplayTransport runtime display = fmap (fmap DisplayEnvironment) (resolveDisplayEnvironment runtime display)

readDisplayEnvironment :: IO (Either Text [(String,String)])
readDisplayEnvironment = fmap (fmap displayEnvironmentPairs) captureDisplayEnvironment

resolveDisplayEnvironment :: Maybe FilePath -> Maybe String -> IO (Either Text [(String,String)])
resolveDisplayEnvironment runtime display = resolveSelectedTransports runtime display Nothing

-- The optional address selects a transport, not an authenticated AT provider.
-- Both socket and ancestor identities must stay stable during this capture.
resolveSelectedTransports :: Maybe FilePath -> Maybe String -> Maybe String -> IO (Either Text [(String,String)])
resolveSelectedTransports Nothing Nothing Nothing = pure (Right [])
resolveSelectedTransports (Just runtime) (Just display) accessibility = do
 observed <- try $ do
  uid <- getRealUserID
  effective <- getEffectiveUserID
  let suffix = drop 8 display
      ascii c = c >= 'a' && c <= 'z' || c >= 'A' && c <= 'Z' || c >= '0' && c <= '9'
      validName = take 8 display == "wayland-" && not (null suffix) && length display <= 64
               && all (\c -> ascii c || c == '-' || c == '_') suffix
      require good = unless good (ioError (userError "private UI display transport refused"))
      base = "/run/user/" ++ show uid
      splitComponents value = case break (=='/') value of
       (part,[]) -> [part]
       (part,_:rest) -> part : splitComponents rest
      components = if runtime == base then [] else splitComponents (drop (length base + 1) runtime)
      validComponent part = not (null part) && length part <= 64 && all (\c -> ascii c || c == '-' || c == '_') part
      validRuntime = runtime == base || (base ++ "/") `isPrefixOf` runtime
                      && length components <= 8 && all validComponent components
      privatePaths = base : [base ++ "/" ++ intercalate "/" prefix | prefix <- tail (inits components)]
      inspectPrivate path = do
       status <- getSymbolicLinkStatus path
       require (isDirectory status && fileOwner status == uid && fileMode status .&. 0o777 == 0o700)
       pure (deviceID status,fileID status)
      inspectSocket leaf = do
       status <- getSymbolicLinkStatus (runtime ++ "/" ++ leaf)
       require (isSocket status && fileOwner status == uid)
       pure (deviceID status,fileID status)
      inspectAccessibility = case accessibility of
       Nothing -> pure Nothing
       Just address -> do
        require (runtime /= base && address == "unix:path=" ++ runtime ++ "/a11y-bus")
        Just <$> inspectSocket "a11y-bus"
  require (uid /= 0 && uid == effective && validRuntime && validName)
  mapM_ (\path -> do
    status <- getSymbolicLinkStatus path
    require (isDirectory status && fileOwner status `elem` [0,uid] && fileMode status .&. 0o022 == 0)) ["/run", "/run/user"]
  before <- mapM inspectPrivate privatePaths
  endpoint <- inspectSocket display
  accessibilityEndpoint <- inspectAccessibility
  after <- mapM inspectPrivate privatePaths
  endpointAfter <- inspectSocket display
  accessibilityAfter <- inspectAccessibility
  require (before == after && endpoint == endpointAfter && accessibilityEndpoint == accessibilityAfter)
  pure ([("XDG_RUNTIME_DIR",runtime),("WAYLAND_DISPLAY",display)]
    ++ maybe [] (\address -> [("AT_SPI_BUS_ADDRESS",address)]) accessibility)
 pure (either (const (Left "private UI display transport unavailable")) Right (observed :: Either IOException [(String,String)]))
resolveSelectedTransports _ _ _ = pure (Left "incomplete private UI display transport")
