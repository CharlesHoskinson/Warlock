module NativeFamilyPreviewSource exposing (Observation, decoder, scope, summary)

import Json.Decode as D
import Json.Encode as E
import PreviewLifecycle as Preview
import Set
import UInt64 exposing (Counter)

type Observation = Observation { native : Preview.Scope, raw : D.Value, crop : Crop, members : List Member, styles : List Style, request : Counter, maximum : Counter }
type alias Crop = { x : String, y : String, width : Int, height : Int, scale : Float }
type alias Member = { incarnation : Counter, parent : Maybe Counter, content : Counter, order : Int, flags : Int, geometry : List Float }
type alias Style = { incarnation : Counter, flags : Int, channels : List Float, gradients : List Gradient }
type alias Gradient = { angle : Float, colors : Int }

strict : List String -> D.Decoder a -> D.Decoder a
strict fields decode = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs) == List.sort fields then decode else D.fail "Native family fields")

positive : D.Decoder Counter
positive = UInt64.decoder |> D.andThen (\value -> if value /= UInt64.zero then D.succeed value else D.fail "Native family positive identity")

binding : D.Decoder (Counter, Counter, Counter)
binding = strict [ "lifetime", "session", "frontend" ] (D.map3 (\a b c -> (a,b,c)) (D.field "lifetime" positive) (D.field "session" positive) (D.field "frontend" positive))

finite : D.Decoder Float
finite = D.float |> D.andThen (\value -> if isNaN value || isInfinite value then D.fail "Finite native family value" else D.succeed value)

boundedInt : Int -> Int -> D.Decoder Int
boundedInt lower upper = D.int |> D.andThen (\value -> if value >= lower && value <= upper then D.succeed value else D.fail "Native family integer bound")

fixed : Int -> D.Decoder a -> D.Decoder (List a)
fixed size decode = D.list decode |> D.andThen (\values -> if List.length values == size then D.succeed values else D.fail "Native family vector shape")

signedPixel : D.Decoder String
signedPixel = D.string |> D.andThen (\value ->
    let negative = String.startsWith "-" value
        digits = if negative then String.dropLeft 1 value else value
        limit = if negative then "2147483648" else "2147483647"
    in if not (String.isEmpty digits) && String.all (\c -> c >= '0' && c <= '9') digits && (digits == "0" || not (String.startsWith "0" digits)) && not (negative && digits == "0") && String.length digits <= 10 && (String.length digits < 10 || digits <= limit) then D.succeed value else D.fail "Canonical signed native crop origin")

cropDecoder : D.Decoder Crop
cropDecoder = strict [ "pixelX", "pixelY", "width", "height", "scale" ]
    (D.map5 Crop (D.field "pixelX" signedPixel) (D.field "pixelY" signedPixel) (D.field "width" (boundedInt 1 4096)) (D.field "height" (boundedInt 1 4096)) (D.field "scale" (finite |> D.andThen (\value -> if value > 0 then D.succeed value else D.fail "Native positive scale"))))

memberDecoder : D.Decoder Member
memberDecoder = strict [ "incarnation", "parent", "content", "renderOrder", "flags", "geometry" ]
    (D.map6 Member (D.field "incarnation" positive) (D.field "parent" (D.nullable positive)) (D.field "content" positive) (D.field "renderOrder" (boundedInt 0 2147483647)) (D.field "flags" (boundedInt 0 511)) (D.field "geometry" (fixed 8 finite)))

gradientDecoder : D.Decoder Gradient
gradientDecoder = strict [ "angle", "colors" ] (D.map2 Gradient (D.field "angle" finite) (D.field "colors" (boundedInt 0 65536)))

styleDecoder : D.Decoder Style
styleDecoder = strict [ "incarnation", "flags", "channels", "gradients" ]
    (D.map4 Style (D.field "incarnation" positive) (D.field "flags" (boundedInt 0 4095)) (D.field "channels" (fixed 18 finite)) (D.field "gradients" (fixed 6 gradientDecoder)))

reachesRoot : Counter -> List Member -> Int -> Counter -> Bool
reachesRoot root members remaining current =
    if remaining <= 0 then False
    else case List.filter (\member -> member.incarnation == current) members |> List.head of
        Nothing -> False
        Just member ->
            if current == root then member.parent == Nothing
            else member.parent |> Maybe.map (reachesRoot root members (remaining - 1)) |> Maybe.withDefault False

decoder : D.Decoder Observation
decoder = strict [ "protocolVersion", "kind", "binding", "requestId", "scope", "maximumTransferBytes", "previewEligible", "scopeKind", "members", "styles", "crop" ]
    (D.map8 (\version kind owner request raw maximum eligible label -> { version=version, kind=kind, owner=owner, request=request, raw=raw, maximum=maximum, eligible=eligible, label=label })
        (D.field "protocolVersion" D.int) (D.field "kind" D.string) (D.field "binding" binding) (D.field "requestId" positive)
        (D.field "scope" D.value) (D.field "maximumTransferBytes" positive) (D.field "previewEligible" D.bool) (D.field "scopeKind" D.string)
        |> D.andThen (\wire -> D.map3 (\members styles crop -> (members,styles,crop)) (D.field "members" (D.list memberDecoder)) (D.field "styles" (D.list styleDecoder)) (D.field "crop" cropDecoder)
            |> D.andThen (\(members,styles,crop) ->
                let facts = D.map4 (\own lifetime clock root -> { own=own, lifetime=lifetime, clock=clock, root=root }) (D.field "binding" binding) (D.at [ "context", "lifetime" ] positive) (D.field "clock" positive) (D.at [ "context", "incarnation" ] positive)
                    ids = List.map (.incarnation >> UInt64.string) members
                    styleIds = List.map (.incarnation >> UInt64.string) styles
                    aligned = String.foldl (\digit remainder -> modBy 4096 (remainder * 10 + Char.toCode digit - 48)) 0 (UInt64.string wire.maximum) == 0
                    maximum = UInt64.string wire.maximum
                    withinBudget = String.length maximum < 9 || (String.length maximum == 9 && maximum <= "134217728")
                in case (D.decodeValue Preview.scopeDecoder wire.raw,D.decodeValue facts wire.raw) of
                    (Ok native,Ok current) ->
                        if wire.version == 3 && wire.kind == "preview-family-style-crop-scope" && wire.label == "native-family-style-crop-channels-unqualified" && not wire.eligible && wire.owner == current.own && current.lifetime == current.clock && aligned && withinBudget &&
                            List.length ids > 0 && List.length ids <= 256 && Set.size (Set.fromList ids) == List.length ids && List.sort ids == List.sort styleIds && List.all (\member -> reachesRoot current.root members (List.length members) member.incarnation) members then
                            D.succeed (Observation { native=native, raw=wire.raw, crop=crop, members=members, styles=styles, request=wire.request, maximum=wire.maximum })
                        else D.fail "Native family correlation"
                    _ -> D.fail "Native family scope")))

scope : Observation -> Preview.Scope
scope (Observation value) = value.native

summary : Observation -> E.Value
summary (Observation value) = E.object
    [ ("source",E.string "native-style-cropped-family-unqualified"), ("scope",value.raw), ("request",E.string (UInt64.string value.request)), ("maximumTransferBytes",E.string (UInt64.string value.maximum)), ("previewEligible",E.bool False)
    , ("memberCount",E.int (List.length value.members)), ("styleCount",E.int (List.length value.styles))
    , ("crop",E.object [ ("pixelX",E.string value.crop.x), ("pixelY",E.string value.crop.y), ("width",E.int value.crop.width), ("height",E.int value.crop.height), ("scale",E.float value.crop.scale) ]) ]
