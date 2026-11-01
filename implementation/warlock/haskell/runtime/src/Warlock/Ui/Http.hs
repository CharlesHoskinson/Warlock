{-# LANGUAGE OverloadedStrings #-}
-- One bounded HTTP message per owned connection. No URL is a filesystem path.
module Warlock.Ui.Http
 (Request(..),HttpError(..),decodeRequest,readRequest,sendResponse) where
import Control.Monad (unless)
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Data.Char (toLower)
import qualified Data.Set as Set
import qualified Network.Socket as S
import qualified Network.Socket.ByteString as N
import System.Timeout (timeout)
import Text.Read (readMaybe)
import Warlock.Capture.Process.Bootstrap (AdmissionDeadline,remainingMicros)

data Request = Request {requestMethod :: B.ByteString,requestTarget :: B.ByteString,requestHeaders :: [(B.ByteString,B.ByteString)],requestBody :: B.ByteString} deriving (Eq,Show)
data HttpError = HeaderLimit | InvalidRequest | Truncated | BodyLimit | ExtraBytes | Deadline deriving (Eq,Show)

trim :: B.ByteString -> B.ByteString
trim = C.dropWhileEnd white . C.dropWhile white where white c=c==' ' || c=='\t'
header :: B.ByteString -> Either HttpError (Request,Int)
header raw = do
 unless (B.length raw<=16384 && not (B.elem 0 raw)) (Left HeaderLimit)
 let rows=B.split 10 raw
 unless (all (\row -> not (B.null row) && B.last row==13) rows) (Left InvalidRequest)
 let clean=map B.init rows
 (line,rest) <- case clean of x:xs -> Right (x,xs); _ -> Left InvalidRequest
 unless (B.length line<=2048) (Left HeaderLimit)
 (method,target) <- case C.split ' ' line of [a,b,"HTTP/1.1"] | not (B.null a) && not (B.null b) -> Right (a,b); _ -> Left InvalidRequest
 unless (length rest<=32 && all (\row -> not (B.null row) && B.head row/=32 && B.head row/=9) rest) (Left InvalidRequest)
 fields <- mapM pair rest
 let names=map fst fields
 unless (Set.size (Set.fromList names)==length names && all (`notElem` names) ["transfer-encoding","trailer","te","upgrade","expect","proxy-connection"]) (Left InvalidRequest)
 count <- case lookup "content-length" fields of
  Nothing -> Right 0
  Just text -> case readMaybe (C.unpack text) of
   Just n | n>=0 && n<=131072 && text==C.pack (show (n::Int)) -> Right n
   _ -> Left BodyLimit
 pure (Request method target fields B.empty,count)
 where
  pair row = let (name,suffix)=B.break (==58) row
                 token c=c>='a' && c<='z' || c>='A' && c<='Z' || c>='0' && c<='9' || c `elem` ("!#$%&'*+-.^_`|~"::String)
             in if B.null name || B.length name>128 || not (C.all token name) || B.null suffix then Left InvalidRequest else
                 let value=trim (B.tail suffix)
                 in if B.length value>4096 || not (B.all (\c -> c==9 || c>=32 && c<=126) value) then Left InvalidRequest else Right (C.map toLower name,value)

splitHeader :: B.ByteString -> Either HttpError (Maybe (Request,Int,B.ByteString))
splitHeader raw =
 let (prefix,suffix)=B.breakSubstring "\r\n\r\n" raw
 in if B.null suffix then if B.length raw>16384 then Left HeaderLimit else Right Nothing else do
  unless (B.length prefix+4<=16384) (Left HeaderLimit)
  (request,count) <- header (prefix<>"\r")
  pure (Just (request,count,B.drop 4 suffix))

decodeRequest :: B.ByteString -> Either HttpError Request
decodeRequest raw = do
 part <- splitHeader raw
 case part of
  Nothing -> Left Truncated
  Just (request,count,body) ->
   if B.length body<count then Left Truncated else if B.length body>count then Left ExtraBytes else Right request {requestBody=body}

readRequest :: AdmissionDeadline -> S.Socket -> IO (Either HttpError Request)
readRequest deadline socket = do
 left <- remainingMicros deadline
 if left<=0 then pure (Left Deadline) else do
  result <- timeout left (headers B.empty)
  pure (maybe (Left Deadline) id result)
 where
  headers raw = case splitHeader raw of
   Left err -> pure (Left err)
   Right Nothing -> do
    part <- N.recv socket 4096
    if B.null part then pure (Left Truncated) else headers (raw<>part)
   Right (Just (request,count,body)) -> consume request count body
  consume request count body
   | B.length body>count = pure (Left ExtraBytes)
   | B.length body==count = pure (Right request {requestBody=body})
   | otherwise = do
      part <- N.recv socket (min 4096 (count-B.length body+1))
      if B.null part then pure (Left Truncated) else consume request count (body<>part)

sendResponse :: AdmissionDeadline -> S.Socket -> Int -> [(B.ByteString,B.ByteString)] -> B.ByteString -> IO Bool
sendResponse deadline socket code headers body = do
 let phrase=case code of 200 -> "OK"; 204 -> "No Content"; 400 -> "Bad Request"; 403 -> "Forbidden"; 503 -> "Service Unavailable"; _ -> "Internal Server Error"
     wire="HTTP/1.1 "<>C.pack (show code)<>" "<>phrase<>"\r\nConnection: close\r\nContent-Length: "<>C.pack (show (B.length body))<>"\r\n"<>B.concat [name<>": "<>value<>"\r\n" | (name,value)<-headers]<>"\r\n"<>body
 left <- remainingMicros deadline
 if left<=0 then pure False else maybe False (const True) <$> timeout left (N.sendAll socket wire)
