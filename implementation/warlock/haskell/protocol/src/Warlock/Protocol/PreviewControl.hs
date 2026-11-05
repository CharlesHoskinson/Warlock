{-# LANGUAGE OverloadedStrings #-}
-- Validated wire data only: none of these values is native authority.
module Warlock.Protocol.PreviewControl
  ( PreviewProposal, PreviewTicket, ConsumptionConfirmation, PreviewControlError(..)
  , decodePreviewProposal, proposalBinding, proposalReceiverEpoch, proposalIdentity
  , makeTicketWire, decodePreviewTicket, encodePreviewTicket, ticketFromWire
  , ticketBinding, ticketReceiverEpoch, ticketOrdinal, ticketAlreadyDelivered, ticketOriginalWire
  , decodeConsumptionConfirmation, encodeConsumptionConfirmation
  , confirmationBinding, confirmationReceiverEpoch, confirmationOrdinal, confirmationOriginalWire
  ) where

import qualified Data.ByteString as B
import Data.Text (Text)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import Warlock.Protocol.Identity
import Warlock.Protocol.StrictJson
import Warlock.Protocol.Wire (parseBinding)

data PreviewControlError = InvalidJson | InvalidShape | InvalidVersionOrKind
  | InvalidIdentity | InvalidCounter | SizeExceeded | DomainMismatch
  | UnsupportedCommand | TicketMismatch deriving (Eq, Show)
data PreviewProposal = Proposal Binding Counter Text deriving (Eq, Show)
data PreviewTicket = Ticket Binding Counter Counter Bool B.ByteString deriving (Eq, Show)
data ConsumptionConfirmation = Confirmation Binding Counter Counter B.ByteString deriving (Eq, Show)

proposalBinding :: PreviewProposal -> Binding
proposalBinding (Proposal b _ _) = b
proposalReceiverEpoch :: PreviewProposal -> Counter
proposalReceiverEpoch (Proposal _ e _) = e
proposalIdentity :: PreviewProposal -> Text
proposalIdentity (Proposal _ _ i) = i

ticketBinding :: PreviewTicket -> Binding
ticketBinding (Ticket b _ _ _ _) = b
ticketReceiverEpoch :: PreviewTicket -> Counter
ticketReceiverEpoch (Ticket _ e _ _ _) = e
ticketOrdinal :: PreviewTicket -> Counter
ticketOrdinal (Ticket _ _ n _ _) = n
ticketAlreadyDelivered :: PreviewTicket -> Bool
ticketAlreadyDelivered (Ticket _ _ _ a _) = a
ticketOriginalWire :: PreviewTicket -> B.ByteString
ticketOriginalWire (Ticket _ _ _ _ w) = w
confirmationBinding :: ConsumptionConfirmation -> Binding
confirmationBinding (Confirmation b _ _ _) = b
confirmationReceiverEpoch :: ConsumptionConfirmation -> Counter
confirmationReceiverEpoch (Confirmation _ e _ _) = e
confirmationOrdinal :: ConsumptionConfirmation -> Counter
confirmationOrdinal (Confirmation _ _ n _) = n
confirmationOriginalWire :: ConsumptionConfirmation -> B.ByteString
confirmationOriginalWire (Confirmation _ _ _ w) = w

json :: Int -> B.ByteString -> Either PreviewControlError Json
json limit raw
  | B.length raw > limit = Left SizeExceeded
  | otherwise = case bounds limit 16 of
      Left _ -> Left InvalidJson
      Right b -> either (const (Left InvalidJson)) Right (decodeStrict b raw)
object :: [Text] -> Json -> Either PreviewControlError [(Text,Json)]
object names = either (const (Left InvalidShape)) Right . exactObject names
field :: Text -> [(Text,Json)] -> Either PreviewControlError Json
field key fields = maybe (Left InvalidShape) Right (lookup key fields)
string :: Json -> Either PreviewControlError Text
string (JString x) = Right x
string _ = Left InvalidShape
positive :: Json -> Either PreviewControlError Counter
positive value = do
  text <- string value
  either (const (Left InvalidCounter)) Right (parseCounter False text)
owner :: Json -> Either PreviewControlError Binding
owner = either (const (Left InvalidIdentity)) Right . parseBinding
fixed :: Text -> [(Text,Json)] -> Either PreviewControlError ()
fixed kind fields = do
  version <- field "previewProtocol" fields
  actual <- field "kind" fields
  if version == JNumber "3" && actual == JString kind then Right () else Left InvalidVersionOrKind
single :: Json -> Either PreviewControlError Json
single (JArray [x]) = Right x
single _ = Left InvalidShape
bindingJson :: Binding -> Json
bindingJson b = JObject [("lifetime",counterJson (lifetime b)),("session",counterJson (session b)),("frontend",counterJson (frontend b))]
counterJson :: Counter -> Json
counterJson = JString . renderCounter
identityFor :: Binding -> Text
identityFor b = "binding:" <> T.intercalate ":" (map renderCounter [lifetime b,session b,frontend b])
entryJson :: PreviewProposal -> Json
entryJson (Proposal b _ i) = JObject [("identity",JString i),("commands",JArray [JObject [("kind",JString "reconcile"),("binding",bindingJson b)]])]
entry :: Binding -> Json -> Either PreviewControlError Text
entry b value = do
  row <- object ["identity","commands"] value
  i <- field "identity" row >>= string
  if B.length (TE.encodeUtf8 i) > 512 || i /= identityFor b then Left InvalidIdentity else Right ()
  command <- field "commands" row >>= single >>= object ["kind","binding"]
  k <- field "kind" command >>= string
  if k /= "reconcile" then Left UnsupportedCommand else Right ()
  cb <- field "binding" command >>= owner
  if cb /= b then Left DomainMismatch else Right i

domain :: [(Text,Json)] -> Either PreviewControlError (Binding,Counter)
domain fields = do
  b <- field "binding" fields >>= owner
  e <- field "receiverEpoch" fields >>= positive
  pure (b,e)

decodePreviewProposal :: B.ByteString -> Either PreviewControlError PreviewProposal
decodePreviewProposal raw = do
  fields <- json 4096 raw >>= object ["previewProtocol","kind","binding","receiverEpoch","entries"]
  fixed "preview-proposals" fields
  (b,e) <- domain fields
  i <- field "entries" fields >>= single >>= entry b
  pure (Proposal b e i)

makeTicketWire :: PreviewProposal -> Counter -> Either PreviewControlError B.ByteString
makeTicketWire p n
  | isZero n = Left InvalidCounter
  | otherwise =
      let raw = encode (JObject
            [("previewProtocol",JNumber "3"),("kind",JString "preview-commands"),
             ("binding",bindingJson (proposalBinding p)),("receiverEpoch",counterJson (proposalReceiverEpoch p)),
             ("controlOrdinal",counterJson n),("entries",JArray [entryJson p])])
      in if B.length raw > 4096 then Left SizeExceeded else Right raw

inner :: B.ByteString -> Either PreviewControlError (Binding,Counter,Counter)
inner raw = do
  fields <- json 4096 raw >>= object ["previewProtocol","kind","binding","receiverEpoch","controlOrdinal","entries"]
  fixed "preview-commands" fields
  (b,e) <- domain fields
  n <- field "controlOrdinal" fields >>= positive
  _ <- field "entries" fields >>= single >>= entry b
  pure (b,e,n)

ticketFromWire :: Bool -> B.ByteString -> Either PreviewControlError PreviewTicket
ticketFromWire advisory raw = do
  (b,e,n) <- inner raw
  pure (Ticket b e n advisory raw)

encode :: Json -> B.ByteString
encode = TE.encodeUtf8 . renderJson
outer :: Text -> Binding -> Counter -> Counter -> [(Text,Json)] -> Json
outer kind b e n rest = JObject ([("previewProtocol",JNumber "3"),("kind",JString kind),
  ("binding",bindingJson b),("receiverEpoch",counterJson e),("controlOrdinal",counterJson n)] ++ rest)
wireText :: B.ByteString -> Text
wireText = TE.decodeUtf8 -- internal bytes have already passed strict UTF-8 decoding
encodePreviewTicket :: PreviewTicket -> B.ByteString
encodePreviewTicket (Ticket b e n a w) = encode (outer "preview-control-ticket" b e n [("alreadyDelivered",JBool a),("wire",JString (wireText w))])
encodeConsumptionConfirmation :: ConsumptionConfirmation -> B.ByteString
encodeConsumptionConfirmation (Confirmation b e n w) = encode (outer "preview-control-consumed" b e n [("wire",JString (wireText w))])

common :: Text -> [Text] -> B.ByteString -> Either PreviewControlError ([(Text,Json)],Binding,Counter,Counter,B.ByteString)
common kind extra raw = do
  fields <- json 32768 raw >>= object (["previewProtocol","kind","binding","receiverEpoch","controlOrdinal","wire"] ++ extra)
  fixed kind fields
  (b,e) <- domain fields
  n <- field "controlOrdinal" fields >>= positive
  w <- TE.encodeUtf8 <$> (field "wire" fields >>= string)
  (ib,ie,inn) <- inner w
  if (b,e,n) /= (ib,ie,inn) then Left TicketMismatch else pure (fields,b,e,n,w)

decodePreviewTicket :: B.ByteString -> Either PreviewControlError PreviewTicket
decodePreviewTicket raw = do
  (fields,b,e,n,w) <- common "preview-control-ticket" ["alreadyDelivered"] raw
  advisory <- field "alreadyDelivered" fields
  case advisory of
    JBool a -> Right (Ticket b e n a w)
    _ -> Left InvalidShape

decodeConsumptionConfirmation :: B.ByteString -> Either PreviewControlError ConsumptionConfirmation
decodeConsumptionConfirmation raw = do
  (_,b,e,n,w) <- common "preview-control-consumed" [] raw
  pure (Confirmation b e n w)
