{-# LANGUAGE OverloadedStrings #-}
-- Byte ingress validation before envelope decoding or effect admission.
module Warlock.Protocol.StrictJson
  ( Json(..), DecodeError(..), Bounds, bounds, decodeStrict, exactObject, renderJson, utf16Length ) where

import qualified Data.ByteString as BS
import Data.Char (chr, ord)
import qualified Data.Set as Set
import Data.Text (Text)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import Numeric (showHex)

utf16Length :: Text -> Int
utf16Length = T.foldl' (\total c -> total + if ord c > 65535 then 2 else 1) 0

renderJson :: Json -> Text
renderJson json = case json of
  JObject pairs -> "{" <> T.intercalate "," [quote key <> ":" <> renderJson value | (key,value) <- pairs] <> "}"
  JArray values -> "[" <> T.intercalate "," (map renderJson values) <> "]"
  JString value -> quote value
  JNumber value -> value
  JBool True -> "true"
  JBool False -> "false"
  JNull -> "null"
  where
    quote value = "\"" <> T.concatMap escaped value <> "\""
    escaped c = case c of
      '"' -> "\\\""
      '\\' -> "\\\\"
      _ | ord c < 32 -> let h = showHex (ord c) "" in "\\u" <> T.pack (replicate (4 - length h) '0' ++ h)
        | otherwise -> T.singleton c

data Json = JObject [(Text, Json)] | JArray [Json] | JString Text
          | JNumber Text | JBool Bool | JNull deriving (Eq, Show)
data DecodeError = InvalidBounds | ByteLimit | InvalidUtf8 | Nul | DepthLimit
                 | MalformedJson | DuplicateKey Text | UnexpectedFields
                 deriving (Eq, Show)
data Bounds = Bounds Int Int deriving (Eq, Show)
bounds :: Int -> Int -> Either DecodeError Bounds
bounds bytes depth | bytes > 0 && depth > 0 = Right (Bounds bytes depth)
                   | otherwise = Left InvalidBounds

decodeStrict :: Bounds -> BS.ByteString -> Either DecodeError Json
decodeStrict (Bounds maxBytes maxDepth) raw
  | BS.length raw > maxBytes = Left ByteLimit
  | BS.elem 0 raw = Left Nul
  | otherwise = case TE.decodeUtf8' raw of
      Left _ -> Left InvalidUtf8
      Right text -> do
        (value, rest) <- valueAt maxDepth (space (T.unpack text))
        if null (space rest) then Right value else Left MalformedJson

space :: String -> String
space = dropWhile (`elem` [' ', '\n', '\r', '\t'])

valueAt :: Int -> String -> Either DecodeError (Json, String)
valueAt n input = case input of
  '{':rest | n > 0 -> object (n-1) Set.empty [] (space rest)
           | otherwise -> Left DepthLimit
  '[':rest | n > 0 -> array (n-1) [] (space rest)
           | otherwise -> Left DepthLimit
  '"':rest -> do (s, tail') <- string [] rest; Right (JString (T.pack s), tail')
  't':'r':'u':'e':rest -> Right (JBool True, rest)
  'f':'a':'l':'s':'e':rest -> Right (JBool False, rest)
  'n':'u':'l':'l':rest -> Right (JNull, rest)
  _ -> do (digits, rest) <- number input; Right (JNumber (T.pack digits), rest)

object :: Int -> Set.Set Text -> [(Text,Json)] -> String -> Either DecodeError (Json,String)
object _ _ values ('}':rest) = Right (JObject (reverse values), rest)
object n seen values ('"':rest) = do
  (keyChars, afterKey) <- string [] rest
  let key = T.pack keyChars
  if Set.member key seen then Left (DuplicateKey key) else case space afterKey of
    ':':afterColon -> do
      (v, afterValue) <- valueAt n (space afterColon)
      let next = (key,v):values; seen' = Set.insert key seen
      case space afterValue of
        '}':tail' -> Right (JObject (reverse next),tail')
        ',':tail' -> case space tail' of
          '"':remaining -> object n seen' next ('"':remaining)
          _ -> Left MalformedJson
        _ -> Left MalformedJson
    _ -> Left MalformedJson
object _ _ _ _ = Left MalformedJson

array :: Int -> [Json] -> String -> Either DecodeError (Json,String)
array _ values (']':rest) = Right (JArray (reverse values),rest)
array n values input = do
  (v, afterValue) <- valueAt n input
  case space afterValue of
    ']':rest -> Right (JArray (reverse (v:values)),rest)
    ',':rest -> case space rest of
      ']':_ -> Left MalformedJson
      next -> array n (v:values) next
    _ -> Left MalformedJson

string :: String -> String -> Either DecodeError (String,String)
string acc input = case input of
  [] -> Left MalformedJson
  '"':rest -> Right (reverse acc,rest)
  '\\':'"':rest -> string ('"':acc) rest
  '\\':'\\':rest -> string ('\\':acc) rest
  '\\':'/':rest -> string ('/':acc) rest
  '\\':'b':rest -> string ('\b':acc) rest
  '\\':'f':rest -> string ('\f':acc) rest
  '\\':'n':rest -> string ('\n':acc) rest
  '\\':'r':rest -> string ('\r':acc) rest
  '\\':'t':rest -> string ('\t':acc) rest
  '\\':'u':a:b:c:d:rest -> do
    u <- hex4 [a,b,c,d]
    if u == 0 then Left Nul else
      if u >= 0xD800 && u <= 0xDBFF then case rest of
        '\\':'u':e:f:g:h:tail' -> do
          v <- hex4 [e,f,g,h]
          if v >= 0xDC00 && v <= 0xDFFF
            then string (chr (0x10000 + (u-0xD800)*1024 + v-0xDC00):acc) tail'
            else Left MalformedJson
        _ -> Left MalformedJson
      else if u >= 0xDC00 && u <= 0xDFFF then Left MalformedJson
      else string (chr u:acc) rest
  '\\':_ -> Left MalformedJson
  c:rest | ord c < 32 || (ord c >= 0xD800 && ord c <= 0xDFFF) -> Left MalformedJson
         | otherwise -> string (c:acc) rest

hex4 :: String -> Either DecodeError Int
hex4 = foldl step (Right 0)
  where step acc c = do
          n <- acc
          hexDigitValue <- if c >= '0' && c <= '9' then Right (ord c - ord '0')
                   else if c >= 'a' && c <= 'f' then Right (10 + ord c - ord 'a')
                   else if c >= 'A' && c <= 'F' then Right (10 + ord c - ord 'A')
                   else Left MalformedJson
          Right (n*16+hexDigitValue)

digit :: Char -> Bool
digit c = c >= '0' && c <= '9'
number :: String -> Either DecodeError (String,String)
number input = do
  let (sign, a) = case input of '-':r -> ("-",r); _ -> ("",input)
  (integer, b) <- case a of
    '0':r -> Right ("0",r)
    c:r | c >= '1' && c <= '9' -> let (xs,z) = span digit r in Right (c:xs,z)
    _ -> Left MalformedJson
  (fraction,c) <- case b of
    '.':r -> case span digit r of ([],_) -> Left MalformedJson; (xs,z) -> Right ('.':xs,z)
    _ -> Right ("",b)
  (exponentText,d) <- case c of
    e:r | e == 'e' || e == 'E' ->
      let (sg,r') = case r of '+':t -> ("+",t); '-':t -> ("-",t); _ -> ("",r)
      in case span digit r' of ([],_) -> Left MalformedJson; (xs,z) -> Right (e:sg++xs,z)
    _ -> Right ("",c)
  Right (sign++integer++fraction++exponentText,d)

exactObject :: [Text] -> Json -> Either DecodeError [(Text,Json)]
exactObject names (JObject pairs)
  | Set.fromList names == Set.fromList (map fst pairs) && length names == length pairs = Right pairs
exactObject _ _ = Left UnexpectedFields
