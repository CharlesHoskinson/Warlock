module GeometryProjection exposing (Capabilities, Context, Mode(..), Snapshot, Window, capabilitiesDecoder, decode, window, modeName)

import Binding
import Char
import Json.Decode as D
import UInt64 exposing (Counter)

type Mode = Ordinary | Maximized | Fullscreen
type alias Context = { lifetime : Counter, epoch : Counter, output : Counter, revision : Counter }
type alias Capabilities = { effects : Bool, operations : List String }
type alias Window =
    { incarnation : Counter, owner : Maybe Counter, workspace : Maybe String, workspaceGeneration : Maybe Counter
    , monitor : Maybe Counter, outputOwnershipGeneration : Maybe Counter, workAreaRevision : Maybe Counter
    , workArea : Maybe (List Float), logicalGeometry : List Float, visualGeometry : List Float
    , nativeMode : Mode, clientMode : Mode, minimized : Bool, floating : Bool, grouped : Bool
    , fixedSize : Bool, constrainedSize : Bool, eligible : Bool, placementKnown : Bool
    , maximize : Bool, restoreGeometry : Bool }
type alias Snapshot = { binding : Binding.Binding, request : Counter, sequence : Counter, context : Context, focused : Maybe Counter, blocked : Bool, windows : List Window }
strict fields body = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs)==List.sort fields then body else D.fail "Geometry schema")
positive = UInt64.decoder |> D.andThen (\x -> if x==UInt64.zero then D.fail "Zero geometry identity" else D.succeed x)
exact name decoder value = D.field name decoder |> D.andThen (\x -> if x==value then D.succeed () else D.fail "Geometry version")
modeDecoder = D.string |> D.andThen (\x -> case x of
    "ordinary" -> D.succeed Ordinary
    "maximized" -> D.succeed Maximized
    "fullscreen" -> D.succeed Fullscreen
    _ -> D.fail "Geometry mode")
modeName mode = case mode of
    Ordinary -> "ordinary"
    Maximized -> "maximized"
    Fullscreen -> "fullscreen"
rect = D.list D.float |> D.andThen (\xs -> case xs of
    [x,y,w,h] -> if List.all (\n -> not (isNaN n || isInfinite n)) [x,y,w,h,x+w,y+h] && w>0 && h>0 then D.succeed xs else D.fail "Geometry rectangle"
    _ -> D.fail "Geometry rectangle shape")
workspace = D.string |> D.andThen (\value ->
    let negative=String.startsWith "-" value
        digits=if negative then String.dropLeft 1 value else value
        limit=if negative then "9223372036854775808" else "9223372036854775807"
        valid=not (String.isEmpty digits) && String.all Char.isDigit digits && (digits=="0" || not (String.startsWith "0" digits)) && not (negative && digits=="0") && (String.length digits<19 || (String.length digits==19 && digits<=limit))
    in if valid then D.succeed value else D.fail "Workspace identity")
capabilitiesDecoder = strict ["observe","effects","effectProtocol","operations","placementCapacity","canonicalScene"]
    (D.map6 (\_ effects _ operations _ _ -> {effects=effects,operations=operations})
        (exact "observe" D.bool True) (D.field "effects" D.bool) (exact "effectProtocol" D.int 2)
        (D.field "operations" (D.list D.string)) (exact "placementCapacity" D.int 256) (exact "canonicalScene" D.bool False))
    |> D.andThen (\caps -> if List.length caps.operations<=2 && List.all (\op -> List.member op ["maximize","restore-geometry"]) caps.operations && List.length caps.operations==List.length (List.foldl (\x xs -> if List.member x xs then xs else x::xs) [] caps.operations) && caps.effects==not (List.isEmpty caps.operations) then D.succeed caps else D.fail "Geometry capabilities")
windowDecoder =
    let identities = D.map8 (\inc owner ws wg mon og wr wa -> {inc=inc,owner=owner,ws=ws,wg=wg,mon=mon,og=og,wr=wr,wa=wa})
            (D.field "incarnation" positive) (D.field "owner" (D.nullable positive)) (D.field "workspace" (D.nullable workspace))
            (D.field "workspaceGeneration" (D.nullable positive)) (D.field "monitor" (D.nullable UInt64.decoder))
            (D.field "outputOwnershipGeneration" (D.nullable positive)) (D.field "workAreaRevision" (D.nullable positive)) (D.field "workArea" (D.nullable rect))
        state = D.map8 (\logical visual native client minimized floating grouped fixed -> {logical=logical,visual=visual,native=native,client=client,minimized=minimized,floating=floating,grouped=grouped,fixed=fixed})
            (D.field "logicalGeometry" rect) (D.field "visualGeometry" rect) (D.field "nativeMode" modeDecoder) (D.field "clientMode" modeDecoder)
            (D.field "minimized" D.bool) (D.field "floating" D.bool) (D.field "grouped" D.bool) (D.field "fixedSize" D.bool)
        policy = D.map4 (\constrained eligible known caps -> {constrained=constrained,eligible=eligible,known=known,caps=caps})
            (D.field "constrainedSize" D.bool) (D.field "geometryEligible" D.bool) (D.field "ordinaryPlacementKnown" D.bool)
            (D.field "capabilities" (strict ["maximize","restoreGeometry"] (D.map2 Tuple.pair (D.field "maximize" D.bool) (D.field "restoreGeometry" D.bool))))
    in strict ["incarnation","owner","workspace","workspaceGeneration","monitor","outputOwnershipGeneration","workAreaRevision","workArea","logicalGeometry","visualGeometry","nativeMode","clientMode","minimized","floating","grouped","fixedSize","constrainedSize","geometryEligible","ordinaryPlacementKnown","capabilities"]
        (D.map3 (\i s p -> {incarnation=i.inc,owner=i.owner,workspace=i.ws,workspaceGeneration=i.wg,monitor=i.mon,outputOwnershipGeneration=i.og,workAreaRevision=i.wr,workArea=i.wa,logicalGeometry=s.logical,visualGeometry=s.visual,nativeMode=s.native,clientMode=s.client,minimized=s.minimized,floating=s.floating,grouped=s.grouped,fixedSize=s.fixed,constrainedSize=p.constrained,eligible=p.eligible,placementKnown=p.known,maximize=Tuple.first p.caps,restoreGeometry=Tuple.second p.caps}) identities state policy)
window incarnation snapshot = List.filter (\row -> row.incarnation==incarnation) snapshot.windows |> List.head
validRows caps blocked rows =
    let ids=List.map .incarnation rows
        unique=List.length ids==List.length (List.foldl (\x xs -> if List.member x xs then xs else x::xs) [] ids)
        rowValid row =
            let known=List.map identity [row.workspace/=Nothing,row.workspaceGeneration/=Nothing,row.monitor/=Nothing,row.outputOwnershipGeneration/=Nothing,row.workAreaRevision/=Nothing,row.workArea/=Nothing]
                paired=List.all ((==) True) known || List.all ((==) False) known
                eligible=not row.eligible || (row.workspace/=Nothing && not blocked && not row.minimized && not row.grouped && not row.constrainedSize && row.floating && row.owner==Nothing && row.nativeMode==row.clientMode && row.nativeMode/=Fullscreen)
                ownership=case row.owner of
                    Nothing -> True
                    Just _ -> walk [] row.incarnation
            in paired && eligible && ownership && (not row.maximize || List.member "maximize" caps.operations) && (not row.restoreGeometry || List.member "restore-geometry" caps.operations)
        walk visited id = if List.member id visited then False else case List.filter (\row -> row.incarnation==id) rows |> List.head of
            Nothing -> False
            Just row -> case row.owner of
                Nothing -> True
                Just parent -> walk (id::visited) parent
        coherent a b =
            (a.outputOwnershipGeneration==Nothing || a.outputOwnershipGeneration/=b.outputOwnershipGeneration || a.monitor==b.monitor)
            && (a.workspaceGeneration==Nothing || a.workspaceGeneration/=b.workspaceGeneration || (a.workspace==b.workspace && a.outputOwnershipGeneration==b.outputOwnershipGeneration && a.workAreaRevision==b.workAreaRevision && a.workArea==b.workArea))
    in List.length rows<=256 && unique && List.all rowValid rows && List.all (\a -> List.all (coherent a) rows) rows

decoder caps = strict ["protocolVersion","kind","geometryProtocol","binding","requestId","sequence","revision","outputGeneration","facts"]
    (D.map8 (\_ _ _ binding request sequence revision rest ->
        let (output,facts)=rest
            context=case D.decodeValue (D.map2 Tuple.pair (D.field "lifetime" positive) (D.field "frontend" positive)) (Binding.encode binding) of
                Ok (life,epoch) -> {lifetime=life,epoch=epoch,output=output,revision=revision}
                Err _ -> {lifetime=UInt64.zero,epoch=UInt64.zero,output=output,revision=revision}
        in {binding=binding,request=request,sequence=sequence,context=context,focused=facts.focused,blocked=facts.blocked,windows=facts.windows})
        (exact "protocolVersion" D.int 3) (exact "kind" D.string "geometry-facts") (exact "geometryProtocol" D.int 1)
        (D.field "binding" Binding.decoder) (D.field "requestId" positive) (D.field "sequence" positive) (D.field "revision" positive)
        (D.map2 Tuple.pair (D.field "outputGeneration" positive)
            (D.field "facts" (strict ["focused","inputBlocked","windows"] (D.map3 (\focus blocked rows -> {focused=focus,blocked=blocked,windows=rows}) (D.field "focused" (D.nullable positive)) (D.field "inputBlocked" D.bool) (D.field "windows" (D.list windowDecoder))))))
    |> D.andThen (\snapshot -> if validRows caps snapshot.blocked snapshot.windows && (snapshot.focused |> Maybe.map (\id -> List.any (\row -> row.incarnation==id) snapshot.windows) |> Maybe.withDefault True) then D.succeed snapshot else D.fail "Geometry facts coherence")
decode caps raw = D.decodeValue (decoder caps) raw |> Result.mapError (\_ -> "Invalid geometry projection")
