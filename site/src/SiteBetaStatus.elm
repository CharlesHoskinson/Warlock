module SiteBetaStatus exposing
    ( Effect(..)
    , EvidenceTier(..)
    , Model
    , Msg(..)
    , MvpTrack(..)
    , Subscription(..)
    , TierFilter(..)
    , countForFilter
    , currentFilter
    , currentMvpTrack
    , filterDomId
    , init
    , lastFocusMiss
    , mvpTabDomId
    , step
    , stepFilter
    , stepMvpTrack
    , subscriptionPlan
    , subscriptions
    , totalBoundaries
    , update
    , view
    )

{-| Truthful runtime, formal, simulated-stage, and native-gate boundary module
for the Warlock documentation homepage.

Contract invariants:
1. Opaque `Model` keeps `TierFilter` and `MvpTrack` total and deterministic with
   zero empty views (`countForFilter filter >= 2` for every constructor) and
   records any non-stale `Dom.NotFound` focus error explicitly in `lastFocusMiss`
   as an internal bounded diagnostic only (never emitted via `aria-live` and
   never claiming assistive-technology acceptance).
   Both keyboard and pointer selection transitions increment `focusSeq` and
   emit typed `Effect` values (`step`) mapped 1-to-1 to `Dom.focus` in `update`,
   while `subscriptionPlan` returns `[]` (`Sub.none`) across every state.
   `focusSeq` only guards stale `Result Dom.Error ()` completions and cannot
   cancel an already-scheduled `Dom.focus` if focus moves to an unscheduled
   external control before the animation frame fires.
2. Zero inline `<style>` elements, zero inline style attributes, and zero
   `Debug` calls; visual presentation comes exclusively from shared Lacquer
   tokens in `site/assets/shared/landing.css`.
3. Keeps browser demonstrations, CPU/Haskell runtime suites, Quint models,
   isolated Omarchy input observations, and unaccepted native/release gates
   explicitly distinct.
-}

import Browser.Dom as Dom
import Html exposing (Html)
import Html.Attributes as Attr
import Html.Events as Events
import Json.Decode as Decode
import Task


type TierFilter
    = FilterAll
    | FilterWholeAccepted
    | FilterRuntimeAndTrials
    | FilterOpenNativeGates


type MvpTrack
    = TrackBrowserStage
    | TrackProtectedCpu
    | TrackOmarchyTrial


type EvidenceTier
    = TierWholeAccepted
    | TierRuntimeComponent
    | TierOpenNativeGate


type Model
    = State
        { filter : TierFilter
        , mvpTrack : MvpTrack
        , focusSeq : Int
        , lastFocusMiss : Maybe String
        }


type Msg
    = SelectTierFilter TierFilter
    | KeyboardStepFilter Int
    | KeyboardJumpFilter TierFilter
    | FilterFocusSettled Int (Result Dom.Error ())
    | SelectMvpTrack MvpTrack
    | KeyboardStepMvpTrack Int
    | KeyboardJumpMvpTrack MvpTrack
    | MvpFocusSettled Int (Result Dom.Error ())


type Effect
    = FocusFilterTab Int TierFilter
    | FocusMvpTab Int MvpTrack


type Subscription
    = NoSiteBetaSubscription


type alias MvpTrackSpec =
    { track : MvpTrack
    , label : String
    , badge : String
    , badgeTier : EvidenceTier
    , heading : String
    , commands : String
    , verifiedScope : String
    , nonClaim : String
    , ctaHref : String
    , ctaLabel : String
    }


type alias BoundaryRow =
    { rowId : String
    , tier : EvidenceTier
    , badge : String
    , scopeCode : String
    , title : String
    , summary : String
    , nonClaim : String
    , href : String
    , linkLabel : String
    }


init : Model
init =
    State
        { filter = FilterAll
        , mvpTrack = TrackBrowserStage
        , focusSeq = 0
        , lastFocusMiss = Nothing
        }


currentFilter : Model -> TierFilter
currentFilter (State state) =
    state.filter


currentMvpTrack : Model -> MvpTrack
currentMvpTrack (State state) =
    state.mvpTrack


lastFocusMiss : Model -> Maybe String
lastFocusMiss (State state) =
    state.lastFocusMiss


orderedFilters : List TierFilter
orderedFilters =
    [ FilterAll
    , FilterWholeAccepted
    , FilterRuntimeAndTrials
    , FilterOpenNativeGates
    ]


orderedMvpTracks : List MvpTrack
orderedMvpTracks =
    [ TrackBrowserStage
    , TrackProtectedCpu
    , TrackOmarchyTrial
    ]


stepFilter : Int -> TierFilter -> TierFilter
stepFilter delta activeFilter =
    let
        total =
            List.length orderedFilters

        currentIndex =
            findFilterIndex 0 activeFilter orderedFilters

        nextIndex =
            modBy (Basics.max 1 total) (currentIndex + delta)
    in
    filterAt nextIndex orderedFilters


stepMvpTrack : Int -> MvpTrack -> MvpTrack
stepMvpTrack delta activeTrack =
    let
        total =
            List.length orderedMvpTracks

        currentIndex =
            findMvpTrackIndex 0 activeTrack orderedMvpTracks

        nextIndex =
            modBy (Basics.max 1 total) (currentIndex + delta)
    in
    mvpTrackAt nextIndex orderedMvpTracks


findFilterIndex : Int -> TierFilter -> List TierFilter -> Int
findFilterIndex idx target remaining =
    case remaining of
        [] ->
            0

        first :: rest ->
            if first == target then
                idx

            else
                findFilterIndex (idx + 1) target rest


filterAt : Int -> List TierFilter -> TierFilter
filterAt idx remaining =
    case remaining of
        [] ->
            FilterAll

        first :: rest ->
            if idx <= 0 then
                first

            else
                filterAt (idx - 1) rest


findMvpTrackIndex : Int -> MvpTrack -> List MvpTrack -> Int
findMvpTrackIndex idx target remaining =
    case remaining of
        [] ->
            0

        first :: rest ->
            if first == target then
                idx

            else
                findMvpTrackIndex (idx + 1) target rest


mvpTrackAt : Int -> List MvpTrack -> MvpTrack
mvpTrackAt idx remaining =
    case remaining of
        [] ->
            TrackBrowserStage

        first :: rest ->
            if idx <= 0 then
                first

            else
                mvpTrackAt (idx - 1) rest


subscriptionPlan : Model -> List Subscription
subscriptionPlan _ =
    []


subscriptions : Model -> Sub Msg
subscriptions model =
    Sub.batch
        (List.map
            (\channel ->
                case channel of
                    NoSiteBetaSubscription ->
                        Sub.none
            )
            (subscriptionPlan model)
        )


step : Msg -> Model -> ( Model, List Effect )
step msg (State state) =
    case msg of
        SelectTierFilter chosenFilter ->
            let
                nextSeq =
                    state.focusSeq + 1
            in
            ( State
                { state
                    | filter = chosenFilter
                    , focusSeq = nextSeq
                    , lastFocusMiss = Nothing
                }
            , [ FocusFilterTab nextSeq chosenFilter ]
            )

        KeyboardStepFilter delta ->
            let
                nextFilter =
                    stepFilter delta state.filter

                nextSeq =
                    state.focusSeq + 1
            in
            ( State
                { state
                    | filter = nextFilter
                    , focusSeq = nextSeq
                    , lastFocusMiss = Nothing
                }
            , [ FocusFilterTab nextSeq nextFilter ]
            )

        KeyboardJumpFilter chosenFilter ->
            let
                nextSeq =
                    state.focusSeq + 1
            in
            ( State
                { state
                    | filter = chosenFilter
                    , focusSeq = nextSeq
                    , lastFocusMiss = Nothing
                }
            , [ FocusFilterTab nextSeq chosenFilter ]
            )

        FilterFocusSettled seq result ->
            if seq /= state.focusSeq then
                ( State state, [] )

            else
                case result of
                    Ok () ->
                        ( State { state | lastFocusMiss = Nothing }, [] )

                    Err (Dom.NotFound missingId) ->
                        ( State { state | lastFocusMiss = Just missingId }, [] )

        SelectMvpTrack chosenTrack ->
            let
                nextSeq =
                    state.focusSeq + 1
            in
            ( State
                { state
                    | mvpTrack = chosenTrack
                    , focusSeq = nextSeq
                    , lastFocusMiss = Nothing
                }
            , [ FocusMvpTab nextSeq chosenTrack ]
            )

        KeyboardStepMvpTrack delta ->
            let
                nextTrack =
                    stepMvpTrack delta state.mvpTrack

                nextSeq =
                    state.focusSeq + 1
            in
            ( State
                { state
                    | mvpTrack = nextTrack
                    , focusSeq = nextSeq
                    , lastFocusMiss = Nothing
                }
            , [ FocusMvpTab nextSeq nextTrack ]
            )

        KeyboardJumpMvpTrack chosenTrack ->
            let
                nextSeq =
                    state.focusSeq + 1
            in
            ( State
                { state
                    | mvpTrack = chosenTrack
                    , focusSeq = nextSeq
                    , lastFocusMiss = Nothing
                }
            , [ FocusMvpTab nextSeq chosenTrack ]
            )

        MvpFocusSettled seq result ->
            if seq /= state.focusSeq then
                ( State state, [] )

            else
                case result of
                    Ok () ->
                        ( State { state | lastFocusMiss = Nothing }, [] )

                    Err (Dom.NotFound missingId) ->
                        ( State { state | lastFocusMiss = Just missingId }, [] )


runEffect : Effect -> Cmd Msg
runEffect effect =
    case effect of
        FocusFilterTab seq chosenFilter ->
            Task.attempt (FilterFocusSettled seq) (Dom.focus (filterDomId chosenFilter))

        FocusMvpTab seq chosenTrack ->
            Task.attempt (MvpFocusSettled seq) (Dom.focus (mvpTabDomId chosenTrack))


runEffects : List Effect -> Cmd Msg
runEffects effects =
    case effects of
        [] ->
            Cmd.none

        [ single ] ->
            runEffect single

        many ->
            Cmd.batch (List.map runEffect many)


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    let
        ( nextModel, effects ) =
            step msg model
    in
    ( nextModel, runEffects effects )


totalBoundaries : Int
totalBoundaries =
    List.length boundaryRows


countForFilter : TierFilter -> Int
countForFilter chosenFilter =
    List.length (List.filter (matchesFilter chosenFilter) boundaryRows)


matchesFilter : TierFilter -> BoundaryRow -> Bool
matchesFilter chosenFilter row =
    case chosenFilter of
        FilterAll ->
            True

        FilterWholeAccepted ->
            row.tier == TierWholeAccepted

        FilterRuntimeAndTrials ->
            row.tier == TierRuntimeComponent

        FilterOpenNativeGates ->
            row.tier == TierOpenNativeGate


boolToken : Bool -> String
boolToken flag =
    if flag then
        "true"

    else
        "false"


tierBadgeClass : EvidenceTier -> String
tierBadgeClass tier =
    case tier of
        TierWholeAccepted ->
            "wl-tier-badge is-accepted"

        TierRuntimeComponent ->
            "wl-tier-badge is-runtime"

        TierOpenNativeGate ->
            "wl-tier-badge is-open"


tierCardClass : EvidenceTier -> String
tierCardClass tier =
    case tier of
        TierWholeAccepted ->
            "wl-beta-card wl-beta-boundary-row wl-home-card-stack tier-accepted"

        TierRuntimeComponent ->
            "wl-beta-card wl-beta-boundary-row wl-home-card-stack tier-runtime"

        TierOpenNativeGate ->
            "wl-beta-card wl-beta-boundary-row wl-home-card-stack tier-open"


isImeComposing : Decode.Decoder Bool
isImeComposing =
    Decode.map2
        (\composing code -> composing || code == 229)
        (Decode.oneOf [ Decode.field "isComposing" Decode.bool, Decode.succeed False ])
        (Decode.oneOf [ Decode.field "keyCode" Decode.int, Decode.succeed 0 ])


decodeFilterKey : Decode.Decoder ( Msg, Bool )
decodeFilterKey =
    Decode.map2 Tuple.pair isImeComposing (Decode.field "key" Decode.string)
        |> Decode.andThen
            (\( composing, keyName ) ->
                if composing then
                    Decode.fail "ime composing"

                else
                    case keyName of
                        "ArrowRight" ->
                            Decode.succeed ( KeyboardStepFilter 1, True )

                        "ArrowDown" ->
                            Decode.succeed ( KeyboardStepFilter 1, True )

                        "ArrowLeft" ->
                            Decode.succeed ( KeyboardStepFilter -1, True )

                        "ArrowUp" ->
                            Decode.succeed ( KeyboardStepFilter -1, True )

                        "Home" ->
                            Decode.succeed ( KeyboardJumpFilter FilterAll, True )

                        "End" ->
                            Decode.succeed ( KeyboardJumpFilter FilterOpenNativeGates, True )

                        _ ->
                            Decode.fail "unhandled filter key"
            )


decodeMvpTabKey : Decode.Decoder ( Msg, Bool )
decodeMvpTabKey =
    Decode.map2 Tuple.pair isImeComposing (Decode.field "key" Decode.string)
        |> Decode.andThen
            (\( composing, keyName ) ->
                if composing then
                    Decode.fail "ime composing"

                else
                    case keyName of
                        "ArrowRight" ->
                            Decode.succeed ( KeyboardStepMvpTrack 1, True )

                        "ArrowDown" ->
                            Decode.succeed ( KeyboardStepMvpTrack 1, True )

                        "ArrowLeft" ->
                            Decode.succeed ( KeyboardStepMvpTrack -1, True )

                        "ArrowUp" ->
                            Decode.succeed ( KeyboardStepMvpTrack -1, True )

                        "Home" ->
                            Decode.succeed ( KeyboardJumpMvpTrack TrackBrowserStage, True )

                        "End" ->
                            Decode.succeed ( KeyboardJumpMvpTrack TrackOmarchyTrial, True )

                        _ ->
                            Decode.fail "unhandled mvp tab key"
            )


browserStageTrackSpec : MvpTrackSpec
browserStageTrackSpec =
    { track = TrackBrowserStage
    , label = "1. Browser test drive"
    , badge = "Local static · Ready on any host"
    , badgeTier = TierWholeAccepted
    , heading = "Verify the site offline and run the 16-scenario simulated desktop"
    , commands =
        "python3 -B site/tools/check-site.py --root site\n"
            ++ "python3 -B site/tools/test-browser-acceptance.py\n"
            ++ "python3 -B -m http.server 8000 --bind 127.0.0.1 --directory site"
    , verifiedScope = "Serves the offline documentation and runs compiled Elm Main, Bar, and Popup across 16 deterministic seeded fixtures at http://127.0.0.1:8000/test-drive/index.html."
    , nonClaim = "Window interiors and host replies are simulated browser fixtures, never Wayland surfaces or Linux process custody."
    , ctaHref = "./test-drive/index.html"
    , ctaLabel = "Open 16-scenario test drive"
    }


mvpTracks : List MvpTrackSpec
mvpTracks =
    [ browserStageTrackSpec
    , { track = TrackProtectedCpu
      , label = "2. Protected CPU & qa_cpu"
      , badge = "Root-serialized · Host QA"
      , badgeTier = TierRuntimeComponent
      , heading = "Check requirement admission and run hash-reviewed offline CPU profiles"
      , commands =
            "python3 -B plugins/warlock-contributor/scripts/warlock.py check --project-only\n"
                ++ "python3 -B docs/warlock-build-loop/v2/loop.py check\n"
                ++ "# Root-serialized hash-bound runner (tools/check_haskell_cpu.py --ui-origin | --custody | --backend | --site):\n"
                ++ "python3 -B tools/qa_cpu.py --review \"$REVIEW_JSON\" --sha256 \"$REVIEW_SHA256\""
      , verifiedScope = "Checks contributor declaration and requirement admission rules (never GUI acceptance). Under qa_cpu.py (3G memory cap, cpu-check.lock, loopback-only bwrap), check_haskell_cpu.py --ui-origin runs the 10 focused ui-origin suites + warlock-ui-backend / ui-stream-child fixtures (64 commands), --custody passes the 3 focused persistent custody/ingress suites on published 6e6ad828c (25 owner controls, all 32 seeds 0..31 with 13 exercising bounded wait on the same owned ProcessHandle under remaining first-stop D + postcheck with zero SIGKILL, 2 direct exitRace cases, and 26 socket callback drain/bytes/refuse-new-work/once-close/EOF checks; prior failures retained), --backend passes focused r19 compiled-Main to selected Haskell backend (161 Haskell checks, 32 hostile frames, 8,010 frontend checks, 40 sessions, 401 complete frames under unchanged 5s session / 180s wrapper deadlines, zero forced cleanup), and --site compiles standalone site/src/SiteMain.elm."
      , nonClaim = "Component-level CPU checks only (19/242 whole and 42/417 scenarios unchanged; no GUI/native/AT/IME/latency/release acceptance; --ui-origin, --custody, and --backend omit Quint registration models, application persistent wiring remains incomplete, and full r18 remains a retained failed batch at 36/37 suites after ui-backend-controls 180s timeout -9—changed fixture inputs make r19 a separate focused result, not a full-suite pass). Published a327c8f7f 36-suite / 104-command common --build, Store old-RED 1 -> new-GREEN 0 acquire witness, Quint Store model report (0 violations across 14 named + 10k x 40-step uniform with retained failed twoClosed = 0 coverage vs guided 1x20 reachability), and ELM-DEL-010 real cross-user VM peer authentication are separate historical source-bound reports; source-only ELM-TEA-004 drafts remain unaccepted."
      , ctaHref = "./architecture/index.html#production-boundary"
      , ctaLabel = "Inspect Elm + Haskell boundary"
      }
    , { track = TrackOmarchyTrial
      , label = "3. Stock Omarchy MVP trial"
      , badge = "Root-serialized · Guest Wayland ABI"
      , badgeTier = TierOpenNativeGate
      , heading = "Stage the --application-only GTK4/WebKitGTK trial on Omarchy 4.0.6"
      , commands =
            "# Follow docs/warlock/how-to/run-omarchy-mvp.md (guest gtk4 + webkitgtk-6.0 ABI):\n"
                ++ "python3 -B tools/omarchy_ui_mvp.py source-manifest --repo-root . --output \"$EVIDENCE_DIR/source-manifest.json\"\n"
                ++ "mkdir -m 0700 \"$RUN_DIR\" && python3 -B /tmp/warlock-mvp-src/tools/omarchy_ui_mvp.py guest-config --run-dir \"$RUN_DIR\" --deadline-seconds 28"
      , verifiedScope = "217-input Haskell + 3-Elm guest build (17 guarded QMP acknowledgements) observes Applications search (foot), no-match footz, and footz retention across Refresh while preserving Foot and idle state."
      , nonClaim = "Exits 1 normally at 27.94s bounded launcher lifetime under the unchanged 28s timeout guard (not frame latency; no unchanged repeated trial is run to vary outcome), with selectedOperationSucceeded = false (6 of 7 checks true), strict retired-cgroup inventory Unknown, nativeOperations = [] under HOSTSTOP2, and live Pin/catalog receipts, AT/IME, and release unaccepted."
      , ctaHref = "./components/launcher/index.html"
      , ctaLabel = "Inspect Launcher specification"
      }
    ]


findMvpTrackSpec : MvpTrack -> MvpTrackSpec
findMvpTrackSpec target =
    let
        pick remaining =
            case remaining of
                [] ->
                    browserStageTrackSpec

                first :: rest ->
                    if first.track == target then
                        first

                    else
                        pick rest
    in
    pick mvpTracks


mvpTabDomId : MvpTrack -> String
mvpTabDomId targetTrack =
    case targetTrack of
        TrackBrowserStage ->
            "wl-mvp-tab-browser"

        TrackProtectedCpu ->
            "wl-mvp-tab-cpu"

        TrackOmarchyTrial ->
            "wl-mvp-tab-omarchy"


ledgerMetrics : List { value : String, label : String, detail : String }
ledgerMetrics =
    [ { value = "19 / 242"
      , label = "Whole requirements accepted"
      , detail = "Includes ELM-TEA-001, ELM-TEA-002, and ELM-DEL-010 real cross-user peer authentication."
      }
    , { value = "42 / 417"
      , label = "Original scenarios accepted"
      , detail = "Immutable source-bound verdicts; unrelated source edits do not transfer native acceptance."
      }
    , { value = "36 / 104"
      , label = "Broad Haskell CPU build"
      , detail = "Published Store/Catalog/PinStore foundation (a327c8f7f), 36 host suites / 104 commands, old/new acquire witness, and closed Backend privacy controls."
      }
    , { value = "0 binaries"
      , label = "Desktop installer status"
      , detail = "Browser stage runs 16 fixture scenarios; native GUI and release packaging remain unaccepted."
      }
    ]


boundaryRows : List BoundaryRow
boundaryRows =
    [ { rowId = "wl-boundary-tea"
      , tier = TierWholeAccepted
      , badge = "Accepted whole · Source-bound"
      , scopeCode = "ELM-TEA-001 · ELM-TEA-002"
      , title = "Pure Elm model, typed effects, and non-replaying cancellation"
      , summary = "Every GUI surface is authored in Elm with one policy authority per decision, validated port boundaries, and pending-cancel transitions that preserve prior intent without replaying uncertain effects."
      , nonClaim = "Component/reducer acceptance does not certify physical compositor input or hardware latency."
      , href = "./foundations/interaction/index.html"
      , linkLabel = "Explore Elm interaction model"
      }
    , { rowId = "wl-boundary-del010"
      , tier = TierWholeAccepted
      , badge = "Accepted whole · Kernel UID evidence"
      , scopeCode = "ELM-DEL-010"
      , title = "Haskell cross-user peer credential authentication"
      , summary = "Production peer ingress verifies kernel socket credentials across distinct user identities, admits approved current sessions, and refuses wrong-user, retired, or replayed session lifetimes within 5-second conversation deadlines."
      , nonClaim = "Peer authentication acceptance does not imply native window-effect or release closure."
      , href = "./architecture/index.html#production-boundary"
      , linkLabel = "Inspect Elm + Haskell boundary"
      }
    , { rowId = "wl-boundary-store"
      , tier = TierRuntimeComponent
      , badge = "Published foundation · CPU & Quint partial"
      , scopeCode = "ELM-ARC-002 · ownership-presentation · ELM-DEL-017 partial"
      , title = "Published Store/Catalog/PinStore retention and closed diagnostics"
      , summary = "Published Store, Catalog, and PinStore source (a327c8f7f) preregisters Acquiring, distinguishes explicit no-resource receipts, and retains uncertain acquisitions before publication (same-source old RED 1 false-clean vs new GREEN 0 retained-uncertainty witness and fault controls) alongside the 36-suite / 104-command Haskell build and closed Backend diagnostics (zero leaked stderr sentinels across 32 ordinary logs)."
      , nonClaim = "Stored Quint uniform 10k x 40-step run retains failed twoClosed = 0 positive-witness coverage (0 safety violations across 14 named traces and 10k samples); a separate guided 1x20 trace reaches dual-close, and neither CPU nor Quint proves FD cleanup or closes whole ELM-ARC-002."
      , href = "./components/status-recovery/index.html"
      , linkLabel = "Read status & recovery rules"
      }
    , { rowId = "wl-boundary-omarchy-trial"
      , tier = TierRuntimeComponent
      , badge = "Isolated VM input observation · Partial"
      , scopeCode = "--application-only · 217-input build · 17 QMP acks"
      , title = "Live Omarchy Applications search and query retention across Refresh"
      , summary = "Fresh 217-input Haskell + 3-Elm guest build records 17 guarded QMP acknowledgements with Root-inspected captures: Applications opens, typing foot lists Foot, Foot Server, and Foot Client, and typing footz shows No matching applications and retains footz across Refresh while the existing Foot window and idle-enabled state remain preserved (Pin Foot and control:close render enabled; live Pin action execution and receipts remain unverified)."
      , nonClaim = "Bounded launcher lifetime is 27.94s under the 28s timeout guard before normal child exit 1 (not a frame-latency or responsiveness metric); selectedOperationSucceeded = false (with 6 of 7 backend checks true), strict retired-cgroup cleanup inventory Unknown, catalog-generation and Pin receipts, physical input/focus/IME/AT, and disabled Open, Application actions, and six bar surfaces (nativeOperations = []) remain unconfirmed or open."
      , href = "./components/launcher/index.html"
      , linkLabel = "Inspect Launcher specification"
      }
    , { rowId = "wl-boundary-webkit-origin"
      , tier = TierOpenNativeGate
      , badge = "Open gate · Component 6e6ad828c published"
      , scopeCode = "ELM-ARC-002 · ELM-ARC-024 · ELM-DEL-014 · ELM-TEA-004"
      , title = "Published persistent custody component (6e6ad828c), next ELM-TEA-004 gate, and private WebKit origin"
      , summary = "Published persistent custody and callback-drain component (6e6ad828c) passes focused 3-suite --custody (25 owner controls, all 32 seeds 0..31 with 13 bounded waits on the same owned ProcessHandle under remaining first-stop D + postcheck with zero SIGKILL path, 2 direct exitRace cases, and 26 socket callback drain/bytes/refuse-new-work/once-close/EOF checks; prior failures retained) and focused r19 --backend (161 Haskell checks, 32 hostile frames, 8,010 compiled-Main checks, 40 sessions, 401 complete frames under unchanged 5s/180s deadlines, zero forced cleanup); application persistent wiring, private WebKit UI origin, and candidate ELM-TEA-004 remain open."
      , nonClaim = "Component verification only (19/242 whole and 42/417 scenarios unchanged; no GUI/native/AT/IME/latency/release acceptance). Full r18 remains a retained failed batch (36/37 suites passed; ui-backend-controls 180s timeout -9; changed fixture inputs make r19 a separate focused result rather than a full-suite rewrite, and models were not rerun in r19). Source-only future ELM-TEA-004 drafts are NOT accepted and still require complete HTTP wrapper full-model/effect replay and independent boundary fixtures (with PreviewPaintGate scoped Realm object drop under fix and native acceptance separate)."
      , href = "./get-started/index.html#runtime-status"
      , linkLabel = "Review current beta status"
      }
    , { rowId = "wl-boundary-native-release"
      , tier = TierOpenNativeGate
      , badge = "Open gate · Unaccepted"
      , scopeCode = "223 / 242 whole · 375 / 417 scenarios remaining"
      , title = "Native Hyprland windowing, previews, AT/IME, hardware budgets, and release"
      , summary = "Full taskbar window management, authorized live preview stream cleanup, physical OS IME composition, assistive-technology announcements, frame-pacing/resource budgets, and reversible installer deployment remain ahead."
      , nonClaim = "All historical failures, original deadlines, and HOSTSTOP2 guards remain preserved."
      , href = "./test-drive/index.html"
      , linkLabel = "Try 16-scenario simulated desktop"
      }
    ]


view : Model -> Html Msg
view (State state) =
    let
        visibleRows =
            List.filter (matchesFilter state.filter) boundaryRows

        shownCount =
            List.length visibleRows
    in
    Html.div
        [ Attr.id "beta-walkthrough"
        , Attr.class "wl-doc-card wl-home-card-stack wl-home-walkthrough-card"
        ]
        [ Html.div [ Attr.class "wl-beta-header" ]
            [ Html.div [ Attr.class "wl-home-card-stack" ]
                [ Html.p [ Attr.class "wl-doc-eyebrow" ]
                    [ Html.text "Current beta walkthrough · 19 of 242 whole requirements · 42 of 417 scenarios" ]
                , Html.h3 []
                    [ Html.text "Simulated browser test drive vs live Elm + Haskell runtime boundaries" ]
                ]
            , Html.div [ Attr.class "wl-home-actions-row" ]
                [ Html.a
                    [ Attr.class "wl-doc-button wl-home-chip"
                    , Attr.href "./get-started/index.html#mvp-repro"
                    ]
                    [ Html.text "Reproducible MVP" ]
                , Html.a
                    [ Attr.class "wl-doc-button wl-home-chip"
                    , Attr.href "./get-started/index.html#runtime-status"
                    ]
                    [ Html.text "Runtime status" ]
                , Html.a
                    [ Attr.class "wl-doc-button wl-home-chip"
                    , Attr.href "./architecture/index.html#production-boundary"
                    ]
                    [ Html.text "Elm + Haskell boundary" ]
                ]
            ]
        , Html.dl
            [ Attr.class "wl-beta-ledger"
            , Attr.attribute "aria-label" "Canonical verification and runtime telemetry"
            ]
            (List.map viewLedgerMetric ledgerMetrics)
        , Html.ol [ Attr.class "wl-home-walkthrough" ]
            [ Html.li []
                [ Html.strong [] [ Html.text "Try in browser now (simulated): " ]
                , Html.a [ Attr.href "./test-drive/index.html" ]
                    [ Html.text "Open the 16-scenario browser test drive" ]
                , Html.text " to exercise compiled Elm Main, Bar, and Popup over deterministic fixtures; client interiors are simulated fixtures and no desktop installer is published yet."
                ]
            , Html.li []
                [ Html.strong [] [ Html.text "Live Omarchy --application-only search (217-input build, 17 guarded QMP acknowledgements): " ]
                , Html.text "Root-viewed captures confirm Applications opens, typing foot lists Foot, Foot Server, and Foot Client, and typing footz shows No matching applications and retains footz across Refresh while the existing Foot window and idle-enabled state remain preserved (Pin Foot and control:close render enabled; live Pin action execution and receipts remain unverified)."
                ]
            , Html.li []
                [ Html.strong [] [ Html.text "Known unavailable operations & open trial exit (nativeOperations = []): " ]
                , Html.text "Opening entries (entry:*), Application actions (jump:open:*), and six bar window/utility surfaces remain disabled under HOSTSTOP2; the trial's 27.94s duration under the 28s timeout guard is bounded launcher lifetime before normal child exit 1 (never frame latency or responsiveness), with selectedOperationSucceeded = false (6 of 7 checks true) and strict retired-cgroup cleanup inventory Unknown, while catalog-generation receipts and physical input/focus/IME/AT remain unconfirmed."
                ]
            , Html.li []
                [ Html.strong [] [ Html.text "Published Store (a327c8f7f) & persistent custody (6e6ad828c) components vs open gates (19/242 whole, 42/417 scenarios): " ]
                , Html.text "ELM-DEL-010 cross-user peer authentication holds whole acceptance; published Store/Catalog/PinStore (a327c8f7f) retains uncertain acquisitions across the 36-suite / 104-command build (with stored failed uniform Quint twoClosed = 0 coverage vs guided 1x20 reachability), and published persistent custody/callback-drain (6e6ad828c) passes focused 3-suite --custody and focused r19 --backend (40 sessions, 401 frames) while full r18 remains a retained 36/37 failed batch and application persistent wiring, ELM-TEA-004 HTTP wrapper fixtures, native GUI, FD/provider cleanup, AT/IME, latency, and release remain open."
                ]
            ]
        , viewMvpQuickstart state.mvpTrack
        , Html.div [ Attr.class "wl-beta-explorer" ]
            [ Html.div [ Attr.class "wl-home-filter-bar wl-beta-filter-bar" ]
                [ Html.div
                    [ Attr.id "wl-beta-tier-filter"
                    , Attr.class "wl-home-tabs"
                    , Attr.attribute "role" "group"
                    , Attr.attribute "aria-label" "Filter runtime and acceptance tiers"
                    ]
                    [ viewFilterButton state.filter FilterAll "All boundaries"
                    , viewFilterButton state.filter FilterWholeAccepted "Accepted whole"
                    , viewFilterButton state.filter FilterRuntimeAndTrials "Runtime & trials"
                    , viewFilterButton state.filter FilterOpenNativeGates "Open native gates"
                    ]
                , Html.p
                    [ Attr.id "wl-beta-tier-count"
                    , Attr.class "wl-home-detail"
                    , Attr.attribute "aria-live" "polite"
                    ]
                    [ Html.text
                        ("Showing "
                            ++ String.fromInt shownCount
                            ++ " of "
                            ++ String.fromInt totalBoundaries
                            ++ " verification boundaries."
                        )
                    ]
                ]
            , Html.div [ Attr.class "wl-beta-grid" ]
                (List.map viewBoundaryCard visibleRows)
            ]
        ]


viewLedgerMetric : { value : String, label : String, detail : String } -> Html msg
viewLedgerMetric metric =
    Html.div [ Attr.class "wl-beta-metric" ]
        [ Html.dt [ Attr.class "wl-beta-metric-label" ] [ Html.text metric.label ]
        , Html.dd [ Attr.class "wl-beta-metric-value" ] [ Html.text metric.value ]
        , Html.dd [ Attr.class "wl-beta-metric-detail" ] [ Html.text metric.detail ]
        ]


filterDomId : TierFilter -> String
filterDomId targetFilter =
    case targetFilter of
        FilterAll ->
            "wl-tier-filter-all"

        FilterWholeAccepted ->
            "wl-tier-filter-accepted"

        FilterRuntimeAndTrials ->
            "wl-tier-filter-runtime"

        FilterOpenNativeGates ->
            "wl-tier-filter-open"


viewFilterButton : TierFilter -> TierFilter -> String -> Html Msg
viewFilterButton activeFilter targetFilter baseLabel =
    let
        isPressed =
            activeFilter == targetFilter

        fullLabel =
            baseLabel ++ " (" ++ String.fromInt (countForFilter targetFilter) ++ ")"
    in
    Html.button
        [ Attr.id (filterDomId targetFilter)
        , Attr.type_ "button"
        , Attr.class
            (if isPressed then
                "wl-doc-button wl-home-chip is-pressed"

             else
                "wl-doc-button wl-home-chip"
            )
        , Attr.attribute "aria-pressed" (boolToken isPressed)
        , Events.onClick (SelectTierFilter targetFilter)
        , Events.preventDefaultOn "keydown" decodeFilterKey
        ]
        [ Html.text fullLabel ]


viewBoundaryCard : BoundaryRow -> Html msg
viewBoundaryCard row =
    Html.article
        [ Attr.id row.rowId
        , Attr.class (tierCardClass row.tier)
        ]
        [ Html.div [ Attr.class "wl-home-badges" ]
            [ Html.span [ Attr.class (tierBadgeClass row.tier) ] [ Html.text row.badge ]
            , Html.code [ Attr.class "wl-beta-code" ] [ Html.text row.scopeCode ]
            ]
        , Html.h4 [ Attr.class "wl-beta-card-title" ] [ Html.text row.title ]
        , Html.p [ Attr.class "wl-beta-card-body" ] [ Html.text row.summary ]
        , Html.p [ Attr.class "wl-home-detail" ]
            [ Html.strong [] [ Html.text "Boundary: " ]
            , Html.text row.nonClaim
            ]
        , Html.a
            [ Attr.class "wl-feature-link wl-beta-card-link"
            , Attr.href row.href
            ]
            [ Html.text row.linkLabel ]
        ]


viewMvpQuickstart : MvpTrack -> Html Msg
viewMvpQuickstart activeTrack =
    let
        activeSpec =
            findMvpTrackSpec activeTrack
    in
    Html.div
        [ Attr.id "wl-mvp-quickstart"
        , Attr.class "wl-mvp-quickstart"
        ]
        [ Html.div [ Attr.class "wl-home-filter-bar wl-beta-filter-bar" ]
            [ Html.div [ Attr.class "wl-home-card-stack" ]
                [ Html.p [ Attr.class "wl-doc-eyebrow" ]
                    [ Html.text "Reproducible MVP & verification commands" ]
                , Html.h4 [ Attr.class "wl-beta-card-title" ]
                    [ Html.text "Select a verification track (Left/Right arrow keys on tabs)" ]
                ]
            , Html.div
                [ Attr.id "wl-mvp-track-tablist"
                , Attr.class "wl-home-tabs"
                , Attr.attribute "role" "tablist"
                , Attr.attribute "aria-label" "Reproducible MVP verification tracks"
                ]
                (List.map (viewMvpTab activeTrack) mvpTracks)
            ]
        , Html.div
            [ Attr.id "wl-mvp-track-panel"
            , Attr.class "wl-mvp-panel wl-home-card-stack"
            , Attr.attribute "role" "tabpanel"
            , Attr.attribute "aria-labelledby" (mvpTabDomId activeSpec.track)
            , Attr.tabindex 0
            ]
            [ Html.div [ Attr.class "wl-home-badges" ]
                [ Html.span [ Attr.class (tierBadgeClass activeSpec.badgeTier) ]
                    [ Html.text activeSpec.badge ]
                , Html.strong [] [ Html.text activeSpec.heading ]
                ]
            , Html.pre [ Attr.class "wl-mvp-code" ]
                [ Html.code [] [ Html.text activeSpec.commands ] ]
            , Html.p [ Attr.class "wl-beta-card-body" ]
                [ Html.strong [] [ Html.text "Observed / verified scope: " ]
                , Html.text activeSpec.verifiedScope
                ]
            , Html.p [ Attr.class "wl-home-detail" ]
                [ Html.strong [] [ Html.text "Boundary: " ]
                , Html.text activeSpec.nonClaim
                ]
            , Html.div [ Attr.class "wl-home-actions-row" ]
                [ Html.a
                    [ Attr.class "wl-feature-link"
                    , Attr.href "./get-started/index.html#mvp-repro"
                    ]
                    [ Html.text "Full reproducible MVP instructions" ]
                , Html.a
                    [ Attr.class "wl-feature-link"
                    , Attr.href activeSpec.ctaHref
                    ]
                    [ Html.text activeSpec.ctaLabel ]
                ]
            ]
        ]


viewMvpTab : MvpTrack -> MvpTrackSpec -> Html Msg
viewMvpTab activeTrack spec =
    let
        isSelected =
            activeTrack == spec.track
    in
    Html.button
        [ Attr.id (mvpTabDomId spec.track)
        , Attr.type_ "button"
        , Attr.class
            (if isSelected then
                "wl-doc-button wl-home-chip is-pressed"

             else
                "wl-doc-button wl-home-chip"
            )
        , Attr.attribute "role" "tab"
        , Attr.attribute "aria-selected" (boolToken isSelected)
        , Attr.attribute "aria-controls" "wl-mvp-track-panel"
        , Attr.tabindex
            (if isSelected then
                0

             else
                -1
            )
        , Events.onClick (SelectMvpTrack spec.track)
        , Events.preventDefaultOn "keydown" decodeMvpTabKey
        ]
        [ Html.text spec.label ]
