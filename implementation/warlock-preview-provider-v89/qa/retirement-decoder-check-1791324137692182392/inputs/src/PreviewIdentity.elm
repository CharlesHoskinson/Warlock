module PreviewIdentity exposing (Identity, Lifetime, Session, Frontend, Incarnation, Output, Privacy, Rendering, Scene, Content, Observation, Receipt, Clock, Request, Origin, MonotonicTime, positive, encode, string, compare, zeroRequest, nextRequest)

import Json.Decode as D
import Json.Encode as E
import UInt64

-- Phantom domains prevent exchanging a source identity, clock, request or
-- revision accidentally. Constructors stay private; wire values stay lossless.
type Identity domain = Identity UInt64.Counter
type Lifetime = LifetimeTag
type Session = SessionTag
type Frontend = FrontendTag
type Incarnation = IncarnationTag
type Output = OutputTag
type Privacy = PrivacyTag
type Rendering = RenderingTag
type Scene = SceneTag
type Content = ContentTag
type Observation = ObservationTag
type Receipt = ReceiptTag
type Clock = ClockTag
type Request = RequestTag
type Origin = OriginTag
type MonotonicTime = MonotonicTimeTag

positive : D.Decoder (Identity domain)
positive = UInt64.decoder |> D.andThen (\counter -> if counter == UInt64.zero then D.fail "Positive native identity" else D.succeed (Identity counter))

string : Identity domain -> String
string (Identity counter) = UInt64.string counter

encode : Identity domain -> E.Value
encode = string >> E.string

compare : Identity domain -> Identity domain -> Order
compare (Identity a) (Identity b) = UInt64.compare a b

zeroRequest : Identity Request
zeroRequest = Identity UInt64.zero

nextRequest : Identity Request -> Maybe (Identity Request)
nextRequest (Identity counter) = UInt64.next counter |> Maybe.map Identity
