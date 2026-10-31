{-# LANGUAGE OverloadedStrings #-}
-- Untrusted inventory data only; validation never grants enqueue or native ACK.
module Warlock.Native.Cancellation.AdmissionShape
 (Admission,Companion,ShapeError(..),decodeAdmission,decodeCompanion,
  admissionSchema,admissionBinding,admissionTarget,admissionKey,companionAdmission,companionSelection) where
import Control.Monad (unless)
import qualified Crypto.Hash.SHA256 as SHA
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import qualified Data.ByteString.Builder as Builder
import qualified Data.ByteString.Lazy as Lazy
import Data.Char (isDigit)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import GHC.Float (castDoubleToWord64)
import Numeric (showHex)
import Text.Read (readMaybe)
import Warlock.Protocol.StrictJson
import Warlock.Protocol.Identity

data ShapeError = InvalidRecord deriving (Eq,Show)
data Admission = Admission !Int !Binding !Counter !B.ByteString deriving (Eq,Show)
data Companion = Companion !Admission !T.Text deriving (Eq,Show)
admissionSchema :: Admission -> Int
admissionSchema (Admission value _ _ _) = value
admissionBinding :: Admission -> Binding
admissionBinding (Admission _ value _ _) = value
admissionTarget :: Admission -> Counter
admissionTarget (Admission _ _ value _) = value
admissionKey :: Admission -> B.ByteString
admissionKey (Admission _ _ _ value) = value
companionAdmission :: Companion -> Admission
companionAdmission (Companion value _) = value
companionSelection :: Companion -> T.Text
companionSelection (Companion _ value) = value
bad :: Either ShapeError a
bad = Left InvalidRecord
checked :: Either a b -> Either ShapeError b
checked = either (const bad) Right
object :: [T.Text] -> Json -> Either ShapeError [(T.Text,Json)]
object names value = checked (exactObject names value)
field :: T.Text -> [(T.Text,Json)] -> Either ShapeError Json
field name values = maybe bad Right (lookup name values)
text :: Json -> Either ShapeError T.Text
text (JString value) = Right value
text _ = bad
counter :: Bool -> Json -> Either ShapeError Counter
counter zero value = text value >>= checked . parseCounter zero
intTag :: Json -> Either ShapeError Int
intTag (JNumber "1") = Right 1
intTag (JNumber "2") = Right 2
intTag _ = bad
parse :: Int -> B.ByteString -> Either ShapeError Json
parse cap raw = do
 limit <- checked (bounds cap 6)
 checked (decodeStrict limit raw)
hex :: B.ByteString -> B.ByteString
hex = C.pack . concatMap (\byte -> let h=showHex byte "" in if length h==1 then '0':h else h) . B.unpack
quoted :: T.Text -> B.ByteString
quoted value = TE.encodeUtf8 ("\"" <> value <> "\"")
-- Every key string below is a validated decimal, finite enum or binary hex;
-- no arbitrary string or second general JSON renderer enters this hash input.
q :: Counter -> B.ByteString
q = quoted . renderCounter

-- Normalize the exponent before parsing Double. Even a 4096-digit exponent
-- cannot cause an enormous power computation. Values that can fit the original
-- geometry bound retain all significand digits for correct binary rounding.
coordinate :: Json -> Either ShapeError Double
coordinate (JNumber raw) = do
 let source=T.unpack raw
     (negative,unsigned)=case source of '-':rest -> (True,rest); _ -> (False,source)
     (mantissa,suffix)=break (\ch -> ch=='e' || ch=='E') unsigned
     (whole,_)=break (=='.') mantissa
     digits=filter isDigit mantissa
     significant=dropWhile (=='0') digits
 decimalExponent <- case suffix of
  [] -> Right 0
  _:value -> maybe bad Right (readMaybe (case value of '+':rest -> rest; _ -> value) :: Maybe Integer)
 if null significant then Right 0 else do
  let magnitude=decimalExponent+toInteger (length whole)-toInteger (length digits-length significant)-1
  if magnitude>9 then bad else if magnitude < -324 then Right 0 else do
   normalized <- case significant of
    first:rest -> Right ((if negative then "-" else "") ++ [first] ++ "." ++ (if null rest then "0" else rest) ++ "e" ++ show magnitude)
    [] -> bad
   value <- maybe bad Right (readMaybe normalized :: Maybe Double)
   if isNaN value || isInfinite value || abs value>2147483647 then bad else Right value
coordinate _ = bad
placement :: Json -> Either ShapeError [B.ByteString]
placement value = do
 fields <- object ["region","geometry","monitor","outputOwnershipGeneration","workAreaRevision","workspaceGeneration"] value
 region <- field "region" fields >>= text
 unless (region `elem` ["left-half","right-half","top-left","top-right","bottom-left","bottom-right"]) bad
 monitor <- field "monitor" fields >>= counter True
 ownership <- field "outputOwnershipGeneration" fields >>= counter False
 revision <- field "workAreaRevision" fields >>= counter False
 workspace <- field "workspaceGeneration" fields >>= counter False
 geometry <- field "geometry" fields
 values <- case geometry of JArray [x,y,w,h] -> mapM coordinate [x,y,w,h]; _ -> bad
 case values of
  [_,_,w,h] | w>0 && h>0 -> pure ()
  _ -> bad
 let binary n=hex (Lazy.toStrict (Builder.toLazyByteString (Builder.word64BE (castDoubleToWord64 (if n==0 then 0 else n)))))
 pure ([quoted region,q monitor,q ownership,q revision,q workspace] ++ map (\n -> "\"" <> binary n <> "\"") values)
transfer :: Json -> Either ShapeError [B.ByteString]
transfer value = do
 fields <- object ["source","sourceGeneration","destination"] value
 source <- field "source" fields >>= counter False
 generation <- field "sourceGeneration" fields >>= counter False
 destination <- field "destination" fields >>= counter False
 upper <- checked (parseCounter False "9223372036854775807")
 unless (source<=upper && destination<=upper && source/=destination) bad
 pure [q source,q generation,q destination]

decodeAdmission :: B.ByteString -> Either ShapeError Admission
decodeAdmission raw = parse 4096 raw >>= admission
admission :: Json -> Either ShapeError Admission
admission value = do
 schema <- case value of JObject values -> field "schema" values >>= intTag; _ -> bad
 fields <- object (["schema","binding","intent","status"] ++ if schema==2 then ["effectProtocol"] else []) value
 protocol <- if schema==1 then Right 1 else field "effectProtocol" fields >>= intTag
 status <- field "status" fields >>= text
 unless (status=="Pending") bad
 boundFields <- field "binding" fields >>= object ["lifetime","session","frontend"]
 life <- field "lifetime" boundFields >>= counter False
 sessionValue <- field "session" boundFields >>= counter False
 front <- field "frontend" boundFields >>= counter False
 bound <- checked (binding life sessionValue front)
 intentValue <- field "intent" fields
 op <- case intentValue of JObject values -> field "operation" values >>= text; _ -> bad
 let extra=if protocol==2 && op=="snap" then ["placement"] else if protocol==2 && op=="transfer-workspace" then ["transfer"] else []
 intentFields <- object (["request","generation","incarnation","operation","context"] ++ extra) intentValue
 unless (op `elem` (if protocol==1 then ["minimize","restore","activate"] else ["maximize","restore-geometry","snap","transfer-workspace","pin","unpin","exit-fullscreen"])) bad
 request <- field "request" intentFields >>= counter False
 generation <- field "generation" intentFields >>= counter False
 incarnation <- field "incarnation" intentFields >>= counter False
 ctx <- field "context" intentFields >>= object ["lifetime","epoch","output","revision"]
 contextLife <- field "lifetime" ctx >>= counter False
 epoch <- field "epoch" ctx >>= counter False
 output <- field "output" ctx >>= counter False
 revision <- field "revision" ctx >>= counter False
 _ <- checked (context bound contextLife epoch output revision)
 extras <- if protocol==2 && op=="snap" then field "placement" intentFields >>= placement else if protocol==2 && op=="transfer-workspace" then field "transfer" intentFields >>= transfer else Right []
 let parts=[q life,q sessionValue,q front,C.pack (show protocol),q request,q generation,q incarnation,quoted op,q contextLife,q epoch,q output,q revision] ++ extras
 pure (Admission schema bound incarnation (hex (SHA.hash ("[" <> B.intercalate "," parts <> "]"))))

decodeCompanion :: B.ByteString -> Either ShapeError Companion
decodeCompanion raw = do
 fields <- parse 8192 raw >>= object ["schema","kind","state","key","admission","selection"]
 schema <- field "schema" fields >>= intTag
 kind <- field "kind" fields >>= text
 phase <- field "state" fields >>= text
 unless (schema==1 && kind=="host-cancellation-admission" && phase `elem` ["Reserved","Submitted"]) bad
 recordValue <- field "admission" fields
 record <- admission recordValue
 recordFields <- object ["schema","effectProtocol","binding","intent","status"] recordValue
 protocol <- field "effectProtocol" recordFields >>= intTag
 op <- field "intent" recordFields >>= object ["request","generation","incarnation","operation","context"] >>= field "operation" >>= text
 unless (protocol==1 && op=="restore") bad
 key <- field "key" fields >>= text
 unless (TE.encodeUtf8 key==admissionKey record) bad
 selected <- field "selection" fields >>= object ["selectionId","scope","publication","lease","controlId","clock","acceptedMonotonicNs","deadlineMonotonicNs"]
 ident <- field "selectionId" selected >>= text
 unless (T.length ident==32 && T.all (\c -> c>='0' && c<='9' || c>='a' && c<='f') ident) bad
 scope <- field "scope" selected >>= object ["id","generation"]
 _ <- field "id" scope >>= counter False
 _ <- field "generation" scope >>= counter False
 _ <- field "publication" selected >>= counter False
 _ <- field "lease" selected >>= counter False
 control <- field "controlId" selected >>= text
 unless (not (T.null control) && not (T.any (=='\0') control) && B.length (TE.encodeUtf8 control)<=512) bad
 clock <- field "clock" selected >>= text
 unless (clock=="CLOCK_MONOTONIC") bad
 accepted <- field "acceptedMonotonicNs" selected >>= counter False
 deadline <- field "deadlineMonotonicNs" selected >>= counter False
 expected <- checked (addCounter accepted 2000000000)
 unless (deadline==expected) bad
 pure (Companion record ident)
