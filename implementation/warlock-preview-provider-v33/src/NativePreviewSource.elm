module NativePreviewSource exposing (Observation, Source(..), decoder, source, scope, encodeSummary)

import Json.Decode as D
import Json.Encode as E
import PreviewLifecycle as Preview
import NativeFamilyPreviewSource
import UInt64 exposing (Counter)

type Source = MonitorPlane | ClientMain | StyleCroppedFamily
type Observation = Observation { source : Source, native : Preview.Scope, raw : D.Value, request : Counter, maximumTransferBytes : Counter }

strict : List String -> D.Decoder a -> D.Decoder a
strict fields decoder_ = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs) == List.sort fields then decoder_ else D.fail "Native source fields")

positive : D.Decoder Counter
positive = UInt64.decoder |> D.andThen (\n -> if n /= UInt64.zero then D.succeed n else D.fail "Positive native source identity")

binding : D.Decoder (Counter, Counter, Counter)
binding = strict ["lifetime","session","frontend"] (D.map3 (\a b c -> (a,b,c)) (D.field "lifetime" positive) (D.field "session" positive) (D.field "frontend" positive))

decoder : D.Decoder Observation
decoder = D.field "kind" D.string |> D.andThen (\kind ->
    if kind == "preview-family-style-crop-scope" then
        D.map (\family -> Observation { source=StyleCroppedFamily, native=NativeFamilyPreviewSource.scope family, raw=NativeFamilyPreviewSource.rawScope family, request=NativeFamilyPreviewSource.request family, maximumTransferBytes=NativeFamilyPreviewSource.maximum family }) NativeFamilyPreviewSource.decoder
    else legacyDecoder)

legacyDecoder : D.Decoder Observation
legacyDecoder = strict ["protocolVersion","kind","binding","requestId","scope","maximumTransferBytes","previewEligible","scopeKind"]
    (D.map8 (\version kind owner request raw maximum eligible label -> {version=version,kind=kind,owner=owner,request=request,raw=raw,maximum=maximum,eligible=eligible,label=label})
        (D.field "protocolVersion" D.int) (D.field "kind" D.string) (D.field "binding" binding) (D.field "requestId" positive)
        (D.field "scope" D.value) (D.field "maximumTransferBytes" positive) (D.field "previewEligible" D.bool) (D.field "scopeKind" D.string)
    |> D.andThen (\wire ->
        let source_ = case (wire.kind,wire.label) of
                ("preview-capture-probe-scope","root-surface-commit-monitor-plane-unqualified") -> Just MonitorPlane
                ("preview-client-scope","isolated-root-client-unqualified") -> Just ClientMain
                _ -> Nothing
            facts = D.map3 (\own lifetime clock -> (own,lifetime,clock)) (D.field "binding" binding) (D.at ["context","lifetime"] positive) (D.field "clock" positive)
        in case (source_,D.decodeValue Preview.scopeDecoder wire.raw,D.decodeValue facts wire.raw) of
            (Just admitted,Ok native,Ok (own,lifetime,clock)) ->
                if wire.version == 3 && not wire.eligible && wire.owner == own && lifetime == clock &&
                    String.foldl (\digit remainder -> modBy 4096 (remainder * 10 + Char.toCode digit - 48)) 0 (UInt64.string wire.maximum) == 0 then
                    D.succeed (Observation {source=admitted,native=native,raw=wire.raw,request=wire.request,maximumTransferBytes=wire.maximum})
                else D.fail "Native source grant/clock/eligibility"
            _ -> D.fail "Typed native source kind/scope"))

source : Observation -> Source
source (Observation value) = value.source

scope : Observation -> Preview.Scope
scope (Observation value) = value.native

encodeSummary : Observation -> E.Value
encodeSummary (Observation value) = E.object [("source",E.string (case value.source of
    MonitorPlane -> "monitor"
    ClientMain -> "client"
    StyleCroppedFamily -> "style-cropped-family-unqualified")),("request",E.string (UInt64.string value.request)),("maximumTransferBytes",E.string (UInt64.string value.maximumTransferBytes)),("previewEligible",E.bool False),("scope",value.raw)]
