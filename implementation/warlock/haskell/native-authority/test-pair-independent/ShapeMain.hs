{-# LANGUAGE OverloadedStrings #-}
module Main (main) where
import Control.Monad (forM_, unless)
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import System.Environment (getArgs)
import System.FilePath ((</>))
import Warlock.Native.Cancellation.AdmissionShape (admissionKey, decodeAdmission)

record :: B.ByteString -> B.ByteString -> B.ByteString -> B.ByteString
record protocol op extras = C.concat
 ["{\"schema\":2,\"effectProtocol\":",protocol,",\"binding\":{\"lifetime\":\"2\",\"session\":\"3\",\"frontend\":\"4\"},\"intent\":{\"request\":\"6\",\"generation\":\"7\",\"incarnation\":\"8\",\"operation\":\"",op,"\",\"context\":{\"lifetime\":\"2\",\"epoch\":\"4\",\"output\":\"9\",\"revision\":\"10\"}",extras,"},\"status\":\"Pending\"}"]
placement :: B.ByteString -> B.ByteString
placement geometry = C.concat [",\"placement\":{\"region\":\"left-half\",\"geometry\":",geometry,",\"monitor\":\"0\",\"outputOwnershipGeneration\":\"1\",\"workAreaRevision\":\"2\",\"workspaceGeneration\":\"3\"}"]
transfer :: B.ByteString -> B.ByteString -> B.ByteString
transfer source dest = C.concat [",\"transfer\":{\"source\":\"",source,"\",\"sourceGeneration\":\"1\",\"destination\":\"",dest,"\"}"]
rows :: [(String,B.ByteString,Bool)]
rows = [("p1-"++C.unpack op,record "1" op "",True) | op <- ["minimize","restore","activate"]]
 ++ [("legacy-schema1-restore", C.concat ["{\"schema\":1,\"binding\":{\"lifetime\":\"2\",\"session\":\"3\",\"frontend\":\"4\"},\"intent\":{\"request\":\"6\",\"generation\":\"7\",\"incarnation\":\"8\",\"operation\":\"restore\",\"context\":{\"lifetime\":\"2\",\"epoch\":\"4\",\"output\":\"9\",\"revision\":\"10\"}},\"status\":\"Pending\"}"],True)]
 ++ [("p2-"++C.unpack op,record "2" op "",True) | op <- ["maximize","restore-geometry","pin","unpin","exit-fullscreen"]]
 ++ [("snap-normal",record "2" "snap" (placement "[0,0,1,2]"),True)
    ,("snap-negative-zero",record "2" "snap" (placement "[-0.0,0,1,2]"),True)
    ,("snap-bound",record "2" "snap" (placement "[2147483647,-2147483647,1,2]"),True)
    ,("snap-over-bound",record "2" "snap" (placement "[2147483648,0,1,2]"),False)
    ,("snap-overflow",record "2" "snap" (placement "[1e9999,0,1,2]"),False)
    ,("snap-zero-width",record "2" "snap" (placement "[0,0,-0.0,2]"),False)
    ,("transfer-valid",record "2" "transfer-workspace" (transfer "1" "2"),True)
    ,("transfer-max",record "2" "transfer-workspace" (transfer "1" "9223372036854775807"),True)
    ,("transfer-over",record "2" "transfer-workspace" (transfer "1" "9223372036854775808"),False)
    ,("transfer-same",record "2" "transfer-workspace" (transfer "1" "1"),False)]
main :: IO ()
main = do
 args <- getArgs
 root <- case args of [p] -> pure p; _ -> ioError (userError "expected owned empty output directory")
 forM_ rows $ \(label,raw,expected) -> do
  let decoded=decodeAdmission raw
  B.writeFile (root </> label ++ ".json") raw
  case decoded of
   Right admission -> B.writeFile (root </> label ++ ".key") (admissionKey admission)
   Left _ -> pure ()
  B.writeFile (root </> label ++ ".observed") (if either (const False) (const True) decoded then "accepted" else "rejected")
  B.writeFile (root </> label ++ ".expected") (if expected then "accepted" else "rejected")
 C.writeFile (root </> "rows.tsv") (C.unlines [C.pack label <> "\t" <> if ok then "accepted" else "rejected" | (label,_,ok) <- rows])
 unless (all (\(_,raw,expected) -> either (const False) (const True) (decodeAdmission raw)==expected) rows) (ioError (userError "shape differs from expected; all rows retained"))
