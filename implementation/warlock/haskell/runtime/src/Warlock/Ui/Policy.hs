{-# LANGUAGE OverloadedStrings #-}
-- The listener owns the role. No request field can select another authority.
module Warlock.Ui.Policy
 (Role(..), Origin, makeOrigin, originBytes, hostBytes, documentUri
 ,Route(..), Refusal(..), admitRequest, navigationAllowed, resourceAllowed
 ,contentSecurityPolicy, resourceFilter) where

import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Data.Char (toLower)
import qualified Data.Set as Set

data Role = Controller | Bar | Popup deriving (Eq, Ord, Show)
newtype Origin = Origin Int deriving (Eq, Ord, Show)
data Route = Document | Events | Commit | Actions deriving (Eq, Show)
data Refusal = InvalidOrigin | InvalidHeaders | WrongHost | WrongOrigin
             | WrongRoute | WrongMethod | WrongLength | WrongType | InvalidHash
             deriving (Eq, Show)

makeOrigin :: Int -> Either Refusal Origin
makeOrigin port
 | port >= 1024 && port <= 65535 = Right (Origin port)
 | otherwise = Left InvalidOrigin

hostBytes :: Origin -> B.ByteString
hostBytes (Origin port) = "127.0.0.1:" <> C.pack (show port)
originBytes :: Origin -> B.ByteString
originBytes origin = "http://" <> hostBytes origin
documentUri :: Origin -> B.ByteString
documentUri origin = originBytes origin <> "/index.html"

routes :: Role -> [(B.ByteString, B.ByteString, Route)]
routes role = [("GET", "/index.html", Document), ("GET", "/events", Events)] ++
 case role of
  Controller -> [("POST", "/commit", Commit)]
  Bar -> [("POST", "/actions", Actions)]
  Popup -> [("POST", "/actions", Actions)]

require :: Bool -> Refusal -> Either Refusal ()
require True _ = Right ()
require False reason = Left reason

-- Headers are parsed without folding by the wire reader. Validate again here:
-- ambiguous header names/lengths never reach a domain callback, even if called
-- through another production entry point. Header values must already be OWS-trimmed.
admitRequest :: Origin -> Role -> B.ByteString -> B.ByteString
             -> [(B.ByteString, B.ByteString)] -> B.ByteString -> Either Refusal Route
admitRequest origin role method target supplied body = do
 require (length supplied <= 32 && sum [B.length k+B.length v+4 | (k,v) <- supplied] <= 16384) InvalidHeaders
 let token c = c >= 'a' && c <= 'z' || c >= 'A' && c <= 'Z' || c >= '0' && c <= '9' || c `elem` ("!#$%&'*+-.^_`|~" :: String)
     valid (name,value) = not (B.null name) && B.length name <= 128 && C.all token name
       && B.length value <= 4096 && B.all (\c -> c == 9 || c >= 32 && c <= 126) value
       && (B.null value || B.head value /= 32 && B.head value /= 9 && B.last value /= 32 && B.last value /= 9)
 require (all valid supplied) InvalidHeaders
 let headers = [(C.map toLower name,value) | (name,value) <- supplied]
     names = map fst headers
     forbidden = ["transfer-encoding","trailer","te","upgrade","proxy-connection","expect"]
 require (Set.size (Set.fromList names) == length names && all (`notElem` names) forbidden) InvalidHeaders
 require (lookup "host" headers == Just (hostBytes origin)) WrongHost
 require (maybe True (== originBytes origin) (lookup "origin" headers)) WrongOrigin
 route <- case [value | (verb,path,value) <- routes role, verb == method, path == target] of
  [value] -> Right value
  _ -> Left (if any (\(_,path,_) -> path == target) (routes role) then WrongMethod else WrongRoute)
 case route of
  Document -> emptyBody headers
  Events -> do
   require (lookup "x-warlock-api" headers == Just "1") WrongOrigin
   emptyBody headers
  Commit -> postedBody headers 131072
  Actions -> postedBody headers 8192
 pure route
 where
  emptyBody headers = require (B.null body && maybe True (== "0") (lookup "content-length" headers)
                   && lookup "content-type" headers == Nothing) WrongLength
  postedBody headers capacity = do
   require (lookup "x-warlock-api" headers == Just "1") WrongOrigin
   require (lookup "origin" headers == Just (originBytes origin)) WrongOrigin
   require (lookup "content-type" headers `elem` [Just "application/json",Just "application/json; charset=utf-8"]) WrongType
   require (not (B.null body) && B.length body <= capacity
         && lookup "content-length" headers == Just (C.pack (show (B.length body)))) WrongLength

navigationAllowed :: Origin -> B.ByteString -> Bool
navigationAllowed origin uri = uri == documentUri origin

resourceAllowed :: Origin -> Role -> B.ByteString -> Bool
resourceAllowed origin role uri = any (\(_,path,_) -> uri == originBytes origin <> path) (routes role)

-- prepareHtml supplies these hashes from the held immutable compiler bytes.
-- Canonical SHA256 base64 contains 43 alphabet characters followed by one '='.
validHash :: B.ByteString -> Bool
validHash value = B.length value == 44 && B.last value == 61
 && C.all (\c -> c >= 'A' && c <= 'Z' || c >= 'a' && c <= 'z' || c >= '0' && c <= '9' || c == '+' || c == '/') (B.take 43 value)
 && C.index value 42 `elem` ("AEIMQUYcgkosw048" :: String)

contentSecurityPolicy :: Origin -> B.ByteString -> B.ByteString -> Either Refusal B.ByteString
contentSecurityPolicy origin script style = do
 require (validHash script && validHash style) InvalidHash
 pure ("default-src 'none'; script-src 'sha256-" <> script
    <> "'; style-src 'sha256-" <> style <> "'; connect-src " <> originBytes origin
    <> "; img-src 'none'; font-src 'none'; object-src 'none'; base-uri 'none'; frame-src 'none'; frame-ancestors 'none'; form-action 'none'; worker-src 'none'")

-- Real pre-request blocking, installed by the native host before loading any
-- page. WebKit resource notifications are observations, not deny callbacks.
-- Only trusted ports and fixed literal paths enter this JSON/regular expression.
resourceFilter :: Origin -> Role -> B.ByteString
resourceFilter (Origin port) role = "[{\"trigger\":{\"url-filter\":\".*\"},\"action\":{\"type\":\"block\"}},"
 <> C.intercalate "," [allow path | (_,path,_) <- routes role] <> "]"
 where
  allow path = "{\"trigger\":{\"url-filter\":\"^http://127\\\\.0\\\\.0\\\\.1:"
    <> C.pack (show port) <> escaped path <> "$\"},\"action\":{\"type\":\"ignore-previous-rules\"}}"
  escaped = B.concatMap (\c -> if c == 46 then "\\\\." else B.singleton c)
