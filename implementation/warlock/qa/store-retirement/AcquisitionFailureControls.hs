-- Same-module QA declaration fragment, not a standalone production module.
-- Root appends these identical bytes to each isolated Store source variant
-- and adds only acquisitionFailureControls to that variant's export list.
-- No imports, CPP seam, acquisition wrapper or Store algorithm is replaced.
--
-- The acquisition counter is an independent simulated acquisition event. It
-- is not a real descriptor, a kernel acquisition receipt or physical cleanup
-- proof. A generic exception before returning a value must remain uncertain.

acquisitionFailureControls :: IO ()
acquisitionFailureControls = do
  owner@(StoreOwner gate resources) <- newStoreOwner
  acquisitions <- newIORef (0 :: Int)
  releases <- newIORef (0 :: Int)
  bodies <- newIORef (0 :: Int)
  retries <- newIORef (0 :: Int)
  let acquire = do
        modifyIORef' acquisitions (+ 1)
        -- Polymorphic ioError is deliberately the SAME action for old IO a
        -- and new IO (Acquisition a); no value or negative receipt is returned.
        ioError (userError "generic acquisition failure before returning value")
      release () = modifyIORef' releases (+ 1)
      body () = modifyIORef' bodies (+ 1)
  attempted <- try (runOwned owner (tracked owner acquire release body))
    :: IO (Either SomeException ())
  sealedBefore <- readMVar gate
  retainedBefore <- readIORef resources
  retired <- retireStoreOwner owner
  sealedAfter <- readMVar gate
  retried <- try (runOwned owner (modifyIORef' retries (+ 1)))
    :: IO (Either SomeException ())
  acquiredCount <- readIORef acquisitions
  releaseCount <- readIORef releases
  bodyCount <- readIORef bodies
  retryCount <- readIORef retries
  retainedAfter <- readIORef resources
  let genericFailure = acquisitionFailureIsIOException attempted
      retryRefused = acquisitionFailureIsIOException retried
      checks =
        [ ("genericAcquireIOExceptionObserved", genericFailure)
        , ("independentAcquisitionEventExactlyOnce", acquiredCount == 1)
        , ("noReturnedValueBodyOrRelease", bodyCount == 0 && releaseCount == 0)
        , ("actualRetireStoreOwnerIsUnconfirmed", not retired)
        , ("actualOwnerGateSealedAfterRetirement", sealedAfter)
        , ("sealedOwnerRejectsNewWork", retryRefused && retryCount == 0)
        ]
      passed = all snd checks
      fields =
        [ ("schema", "1")
        , ("case", acquisitionFailureQuote "generic-acquisition-exception-before-value")
        , ("scope", acquisitionFailureQuote "Identical same-module Store witness; simulated acquisition event only, no real FD or physical cleanup proof")
        , ("acquisitionEvents", show acquiredCount)
        , ("releaseCalls", show releaseCount)
        , ("bodyCalls", show bodyCount)
        , ("retryBodyCalls", show retryCount)
        , ("acquireResult", acquisitionFailureResult attempted)
        , ("retryResult", acquisitionFailureResult retried)
        , ("ownerSealedBeforeRetirement", acquisitionFailureBool sealedBefore)
        , ("retireStoreOwnerResult", acquisitionFailureBool retired)
        , ("ownerSealedAfterRetirement", acquisitionFailureBool sealedAfter)
        , ("retainedRecordsBeforeRetirement", show (length retainedBefore))
        , ("retainedRecordsAfterRetirement", show (length retainedAfter))
        , ("checks", acquisitionFailureObject [(name, acquisitionFailureBool good) | (name, good) <- checks])
        , ("passed", acquisitionFailureBool passed)
        , ("realDescriptorAcquisitionObserved", "false")
        , ("physicalCleanupProven", "false")
        , ("nativeAcceptance", "false")
        , ("originalRequirementAccepted", "false")
        ]
  -- Preserve the real observations on RED as well as GREEN, before assertion.
  putStrLn (acquisitionFailureObject fields)
  unless passed (ioError (userError "acquisition failure must not certify Store retirement; raw observations printed above"))

acquisitionFailureIsIOException :: Either SomeException () -> Bool
acquisitionFailureIsIOException result = case result of
  Left problem -> case fromException problem :: Maybe IOError of
    Just _ -> True
    Nothing -> False
  Right () -> False

acquisitionFailureResult :: Either SomeException () -> String
acquisitionFailureResult result = case result of
  Left problem -> acquisitionFailureObject
    [ ("kind", acquisitionFailureQuote (if acquisitionFailureIsIOException result then "IOException" else "OtherException"))
    , ("message", acquisitionFailureQuote (show problem))
    ]
  Right () -> acquisitionFailureObject [("kind", acquisitionFailureQuote "ReturnedUnit")]

acquisitionFailureBool :: Bool -> String
acquisitionFailureBool value = if value then "true" else "false"

acquisitionFailureObject :: [(String, String)] -> String
acquisitionFailureObject fields = "{" ++ joinFields fields ++ "}"
  where
    joinFields [] = ""
    joinFields ((name, value) : rest) = acquisitionFailureQuote name ++ ":" ++ value ++ case rest of
      [] -> ""
      _ -> "," ++ joinFields rest

acquisitionFailureQuote :: String -> String
acquisitionFailureQuote value = "\"" ++ concatMap escape value ++ "\""
  where
    escape '"' = "\\\""
    escape '\\' = "\\\\"
    escape char
      | char < ' ' = "\\u00" ++ [hexDigit (fromEnum char `div` 16), hexDigit (fromEnum char `mod` 16)]
      | otherwise = [char]
    hexDigit nibble = case drop nibble "0123456789abcdef" of
      digit : _ -> digit
      [] -> '0'
