module GeometrySizePolicy exposing (Policy, decoder, coherent, supported, permits)

import Json.Decode as D

type alias Pair = ( Float, Float )
type alias Box = { x : Float, y : Float, width : Float, height : Float }
type alias Inputs =
    { rawMinimum : Pair, rawMaximum : Pair, layoutMinimum : Pair, layoutMaximum : Pair
    , origin : Pair, topLeft : Pair, bottomRight : Pair, scale : Float }
type alias Projection = { logical : Box, visual : Maybe Box, real : Box, configure : Pair }
type alias Policy = { inputs : Maybe Inputs, maximize : Maybe Projection, restoreGeometry : Maybe Projection }

strict fields body = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs)==List.sort fields then body else D.fail "Size policy schema")
finite x = not (isNaN x || isInfinite x)
pair nonnegative = D.list D.float |> D.andThen (\values -> case values of
    [x,y] -> if finite x && finite y && (not nonnegative || (x>=0 && y>=0)) then D.succeed (x,y) else D.fail "Size vector"
    _ -> D.fail "Size vector shape")
box = D.list D.float |> D.andThen (\values -> case values of
    [x,y,w,h] -> if List.all finite values && List.all (\v -> abs v<=2147483647) values && w>0 && h>0 then D.succeed {x=x,y=y,width=w,height=h} else D.fail "Prospective box"
    _ -> D.fail "Prospective box shape")
interval raw (lx,ly) (ux,uy) =
    let axis lo hi = (raw && hi==0) || (hi>0 && lo<hi)
    in axis lx ux && axis ly uy
fixed inputs =
    let axis rawLo rawHi layoutLo layoutHi =
            let lower=max 1 (max (toFloat (ceiling rawLo)) (toFloat (floor layoutLo)))
                upper=min 2147483647 (min (if rawHi==0 then 2147483647 else toFloat (floor rawHi)) (toFloat (floor layoutHi)))
            in lower>=upper
        (rx,ry)=inputs.rawMinimum
        (ux,uy)=inputs.rawMaximum
        (lx,ly)=inputs.layoutMinimum
        (hx,hy)=inputs.layoutMaximum
    in axis rx ux lx hx || axis ry uy ly hy
inputsDecoder = strict ["profile","rawMinimum","rawMaximum","layoutMinimum","layoutMaximum","geometryOrigin","reservedTopLeft","reservedBottomRight","monitorScale"]
    (D.map2 (\_ inputs -> inputs)
        (D.field "profile" D.string |> D.andThen (\profile -> if profile=="wayland-zero-origin-v1" then D.succeed () else D.fail "Conversion profile"))
        (D.map8 (\rawMin rawMax layoutMin layoutMax origin tl br scale -> {rawMinimum=rawMin,rawMaximum=rawMax,layoutMinimum=layoutMin,layoutMaximum=layoutMax,origin=origin,topLeft=tl,bottomRight=br,scale=scale})
            (D.field "rawMinimum" (pair True)) (D.field "rawMaximum" (pair True))
            (D.field "layoutMinimum" (pair True)) (D.field "layoutMaximum" (pair True))
            (D.field "geometryOrigin" (pair False)) (D.field "reservedTopLeft" (pair True))
            (D.field "reservedBottomRight" (pair True)) (D.field "monitorScale" D.float)))
    |> D.andThen (\inputs -> if finite inputs.scale && inputs.scale>0 && interval True inputs.rawMinimum inputs.rawMaximum && interval False inputs.layoutMinimum inputs.layoutMaximum then D.succeed inputs else D.fail "Size intervals")
projectionDecoder = strict ["logical","visual","real","configure"]
    (D.map4 Projection (D.field "logical" box) (D.field "visual" (D.nullable box)) (D.field "real" box) (D.field "configure" (pair True)))
decoder = strict ["inputs","maximize","restoreGeometry"]
    (D.map3 Policy (D.field "inputs" (D.nullable inputsDecoder)) (D.field "maximize" (D.nullable projectionDecoder)) (D.field "restoreGeometry" (D.nullable projectionDecoder)))

supported policy = case policy.inputs of
    Nothing -> False
    Just inputs -> inputs.origin==(0,0) && not (fixed inputs)
roundNative x = if x>=0 then toFloat (floor x) + (if x-toFloat (floor x)>=0.5 then 1 else 0) else toFloat (ceiling x) - (if toFloat (ceiling x)-x>=0.5 then 1 else 0)
rounded value = {x=roundNative value.x,y=roundNative value.y,width=roundNative (value.x+value.width)-roundNative value.x,height=roundNative (value.y+value.height)-roundNative value.y}
fromList values = case values of
    [x,y,w,h] -> Just {x=x,y=y,width=w,height=h}
    _ -> Nothing
within inputs projection =
    let (cx,cy)=projection.configure
        (rx,ry)=inputs.rawMinimum
        (ux,uy)=inputs.rawMaximum
        (lx,ly)=inputs.layoutMinimum
        (hx,hy)=inputs.layoutMaximum
        axis configured real rawLo rawHi lo hi = configured>=1 && configured<=2147483647 && configured>=rawLo && (rawHi==0 || configured<=rawHi) && real>=lo && real<=hi
    in projection.configure==(toFloat (floor projection.real.width),toFloat (floor projection.real.height)) && axis cx projection.real.width rx ux lx hx && axis cy projection.real.height ry uy ly hy
projectionValid maximize workArea inputs projection =
    let (tx,ty)=inputs.topLeft
        (bx,by)=inputs.bottomRight
        logical=projection.logical
        real=projection.real
        converted=if maximize then {x=logical.x+tx,y=logical.y+ty,width=logical.width-(tx+bx),height=logical.height-(ty+by)} else logical
        source=if maximize then Maybe.andThen fromList workArea |> Maybe.map (rounded >> (==) logical) |> Maybe.withDefault False else projection.visual==Just real
    in logical==rounded logical && (projection.visual |> Maybe.map (\v -> v==rounded v) |> Maybe.withDefault True) && real==converted && within inputs projection && source && (not maximize || projection.visual==Nothing)
coherent policy workArea constrained fixedSize = case policy.inputs of
    Nothing -> policy.maximize==Nothing && policy.restoreGeometry==Nothing
    Just inputs ->
        let values (x,y) = [x,y]
            expected=List.any ((<) 1) (values inputs.rawMinimum ++ values inputs.layoutMinimum) || List.any ((<) 0) (values inputs.rawMaximum) || List.any ((>) 1.7976931348623157e308) (values inputs.layoutMaximum)
            valid maximize projection = projection |> Maybe.map (\p -> supported policy && projectionValid maximize workArea inputs p) |> Maybe.withDefault True
        in constrained==expected && fixedSize==fixed inputs && valid True policy.maximize && valid False policy.restoreGeometry
permits maximize policy = supported policy && (if maximize then policy.maximize/=Nothing else policy.restoreGeometry/=Nothing)
