module Main (main) where
import Control.Monad (unless)
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import qualified Data.Map.Strict as M
import GoldenNames (goldenNeeded)
import Paths_warlock_elf_observation_proposal (getDataFileName)
import Warlock.Elf.Readelf
import Warlock.Elf.Graph

expect :: String -> Bool -> IO ()
expect label value = unless value (ioError (userError label))
rejected :: Either a b -> Bool
rejected (Left _) = True
rejected _ = False
replaceOnce :: B.ByteString -> B.ByteString -> B.ByteString -> B.ByteString
replaceOnce from to input = let (before,after) = B.breakSubstring from input in
  if B.null after then input else B.concat [before,to,B.drop (B.length from) after]
complete :: Capture
complete = Capture GnuReadelf247 True True True True True True
obs :: Maybe String -> [String] -> [VersionNeed] -> [VersionDef] -> Observation
obs name dependencies ns ds = Observation Elf64 Little X86_64 Shared Nothing name dependencies Nothing Nothing [] ns ds 200 [] Nothing []
sampleVersion :: String -> VersionDef
sampleVersion name = VersionDef name "none" 2 []
limits :: Limits
limits = Limits 10 10 10000 1000
syntheticDefs :: B.ByteString
syntheticDefs = C.pack $ unlines
  [ "ELF Header:"
  , "  Magic: 7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00"
  , "  Class: ELF64", "  Data: 2's complement, little endian", "  Version: 1 (current)"
  , "  Type: DYN (Shared object file)", "  Machine: Advanced Micro Devices X86-64"
  , "  Version: 0x1", "  Number of program headers: 1", ""
  , "Program Headers:", "  Type Offset VirtAddr PhysAddr FileSiz MemSiz Flg Align"
  , "  PHDR 0x0 0x0 0x0 0x0 0x0 R 0x8", ""
  , "Dynamic section at offset 0x0 contains 4 entries:"
  , "  Tag Type Name/Value", " 0x1 (VERSYM) 0x1", " 0x2 (VERDEF) 0x2"
  , " 0x3 (VERDEFNUM) 2", " 0x0 (NULL) 0x0", ""
  , "Version symbols section '.gnu.version' contains 1 entry:"
  , " Addr: 0x1 Offset: 0x1 Link: 1 (.dynsym)", "  000: 2 (EXAMPLE_1)", ""
  , "Version definition section '.gnu.version_d' contains 2 entries:"
  , " Addr: 0x1 Offset: 0x1 Link: 1 (.dynstr)"
  , "  0x0000: Rev: 1 Flags: BASE Index: 1 Cnt: 1 Name: libexample.so"
  , "  0x0010: Rev: 1 Flags: none Index: 2 Cnt: 2 Name: EXAMPLE_1"
  , "  0x0020: Parent 1: BASE_VER", "" ]
fixture :: FilePath -> IO B.ByteString
fixture name = getDataFileName ("test/fixtures/" ++ name) >>= B.readFile
main :: IO ()
main = do
  raw <- fixture "owner.readelf"
  webkit <- fixture "webkit.readelf"
  case parseReadelf complete webkit of
    Left failure -> ioError (userError ("retained WebKit rejected: " ++ show failure))
    Right value -> do
      expect "WebKit identity" (soname value == Just "libwebkit2gtk-4.1.so.0" && elfType value == Shared)
      expect "WebKit nonempty dependencies and version needs" (not (null (needed value)) && not (null (versionNeeds value)))
  expect "WebKit malformed hex version rejected" (rejected (parseReadelf complete (replaceOnce (C.pack "a (GLIBCXX_3.4.11)") (C.pack "q (GLIBCXX_3.4.11)") webkit)))
  ghcLib <- fixture "ghc.readelf"
  jscLib <- fixture "jsc.readelf"
  gccLib <- fixture "gcc.readelf"
  sframeLib <- fixture "sframe.readelf"
  expect "GHC RELACOUNT retained" (case parseReadelf complete ghcLib of Right x -> relaCount x == Just 933; _ -> False)
  expect "JSC RELACOUNT retained" (case parseReadelf complete jscLib of Right x -> relaCount x == Just 4655; _ -> False)
  expect "libgcc compact hidden hex version" (case parseReadelf complete gccLib of Right x -> VersionSymbol 12 True "GCC_4.8.0" `elem` versionSymbols x; _ -> False)
  expect "x86 PLT metadata retained without graph qualification" (case parseReadelf complete sframeLib of Right x -> length [() | (k,_) <- dynamicFlags x, k `elem` ["DT_X86_64_PLT","DT_X86_64_PLTSZ","DT_X86_64_PLTENT"]] == 3; _ -> False)
  expect "GNU SFRAME retained" (case parseReadelf complete sframeLib of Right x -> any (\h -> programKind h == "GNU_SFRAME" && programOffset h == "0x122d48" && programAlignment h == "0x8") (programHeaders x); _ -> False)
  expect "malformed compact hex rejected" (rejected (parseReadelf complete (replaceOnce (C.pack "ch(GCC_4.8.0)") (C.pack "qh(GCC_4.8.0)") gccLib)))
  expect "compact wrong owner rejected" (rejected (parseReadelf complete (replaceOnce (C.pack "ch(GCC_4.8.0)") (C.pack "ch(GCC_7.0.0)") gccLib)))
  expect "invalid RELACOUNT rejected" (rejected (parseReadelf complete (replaceOnce (C.pack "(RELACOUNT)          933") (C.pack "(RELACOUNT)          9x3") ghcLib)))
  expect "malformed x86 PLT rejected" (rejected (parseReadelf complete (replaceOnce (C.pack "(DT_X86_64_PLT)      0x10040") (C.pack "(DT_X86_64_PLT)      0xq0040") sframeLib)))
  expect "unsupported SFRAME header rejected" (rejected (parseReadelf complete (replaceOnce (C.pack "GNU_SFRAME") (C.pack "GNU_UNKNOWN") sframeLib)))
  jsonGlib <- fixture "json-glib.readelf"
  expect "BASE1 and nonbase2 may share SONAME version name" (case parseReadelf complete jsonGlib of
    Right value -> [(defName d,defFlags d,defIndex d) | d <- versionDefinitions value] == [("libjson-glib-1.0.so.0","BASE",1),("libjson-glib-1.0.so.0","none",2)]
    _ -> False)
  expect "same index still refused" (rejected (parseReadelf complete (replaceOnce (C.pack "Index: 2") (C.pack "Index: 1") jsonGlib)))
  expect "BASE must use index1" (rejected (parseReadelf complete (replaceOnce (C.pack "Index: 1") (C.pack "Index: 8") jsonGlib)))
  mapM_ (\index -> do
    helper <- fixture ("helper-" ++ show index ++ ".readelf")
    expect "actual WebKit helper remains executable not provider library" (case parseReadelf complete helper of
      Right value -> elfType value == PieExecutable && interpreter value == Just "/lib64/ld-linux-x86-64.so.2" && needed value == ["libwebkit2gtk-4.1.so.0","libc.so.6"]
      _ -> False)) ([0,1,2] :: [Int])
  let parsed = parseReadelf complete raw
  case parsed of
    Left _ -> ioError (userError "actual retained readelf golden rejected")
    Right value -> do
      expect "44 exact ordered NEEDED" (length goldenNeeded == 44 && needed value == goldenNeeded)
      expect "actual header" (elfClass value == Elf64 && endian value == Little && elfType value == Executable && machine value == X86_64)
      expect "actual interp and search" (interpreter value == Just "/lib64/ld-linux-x86-64.so.2" && runpath value == Just "/usr/lib" && rpath value == Nothing && soname value == Nothing)
      expect "actual version needs" (case versionNeeds value of [VersionNeed file versions] -> file == "libc.so.6" && map (\(v,_,_) -> v) versions == ["GLIBC_2.4","GLIBC_2.34","GLIBC_2.2.5"]; _ -> False)
  expect "unreviewed tool profile rejected" (rejected (parseReadelf (complete { toolProfile = UnsupportedTool }) raw))
  expect "reserved global index name rejected" (rejected (parseReadelf complete (replaceOnce (C.pack "1 (*global*)") (C.pack "1 (WRONG)") webkit)))
  expect "reserved local index name rejected" (rejected (parseReadelf complete (replaceOnce (C.pack "0 (*local*)") (C.pack "0 (WRONG)") raw)))
  expect "incomplete capture rejected" (rejected (parseReadelf (complete { outputComplete = False }) raw))
  expect "duplicate header rejected" (rejected (parseReadelf complete (replaceOnce (C.pack "  Class:") (C.pack "  Class: ELF64\n  Class:") raw)))
  expect "unsupported class rejected" (rejected (parseReadelf complete (replaceOnce (C.pack "ELF64") (C.pack "ELF32") raw)))
  expect "dynamic count rejected" (rejected (parseReadelf complete (replaceOnce (C.pack "contains 68 entries:") (C.pack "contains 69 entries:") raw)))
  expect "version index and name mismatch rejected" (rejected (parseReadelf complete (replaceOnce (C.pack "2 (GLIBC_2.4)") (C.pack "2 (BAD_VERSION)") raw)))
  expect "unknown dynamic tag rejected" (rejected (parseReadelf complete (replaceOnce (C.pack "(RUNPATH)") (C.pack "(BADPATH)") raw)))
  expect "version needs count rejected" (rejected (parseReadelf complete (replaceOnce (C.pack "Cnt: 3") (C.pack "Cnt: 4") raw)))
  expect "truncated capture rejected" (rejected (parseReadelf complete (B.take 1200 raw)))
  expect "unsupported program columns rejected" (rejected (parseReadelf complete (replaceOnce (C.pack "  PHDR ") (C.pack "  BOGUS ") raw)))
  expect "definition and parent parsed" (case parseReadelf complete syntheticDefs of Right x -> map defName (versionDefinitions x) == ["libexample.so","EXAMPLE_1"] && map defParents (versionDefinitions x) == [[],["BASE_VER"]]; _ -> False)
  let duplicateSoname = replaceOnce (C.pack "contains 4 entries:") (C.pack "contains 6 entries:") $
        replaceOnce (C.pack " 0x0 (NULL) 0x0") (C.pack " 0x4 (SONAME) Library soname: [one.so]\n 0x5 (SONAME) Library soname: [two.so]\n 0x0 (NULL) 0x0") syntheticDefs
  expect "duplicate soname rejected" (rejected (parseReadelf complete duplicateSoname))
  expect "unknown definition revision rejected" (rejected (parseReadelf complete (replaceOnce (C.pack "Rev: 1") (C.pack "Rev: 2") syntheticDefs)))
  let digest = replicate 64 'a'
      root = Input "/app/root" "/app" "root" 200 digest digest (obs Nothing ["liba.so","libb.so"] [VersionNeed "liba.so" [("A_1","none",2)]] [])
      a = Input "/lib/liba.so" "/lib" "liba.so" 200 digest digest (obs (Just "liba.so") ["libb.so"] [] [sampleVersion "A_1"])
      b = Input "/lib/libb.so" "/lib" "libb.so" 200 digest digest (obs (Just "libb.so") ["liba.so"] [] [])
      inputs = [root,a,b]
      run xs = resolveDeclared limits ["/lib"] xs "/app/root"
  expect "ordered cyclic declared graph" (case run inputs of Right g -> visited g == ["/app/root","/lib/liba.so","/lib/libb.so"] && map edgeKind (edges g) == [Needed "liba.so",Needed "libb.so",Needed "libb.so",Needed "liba.so"]; _ -> False)
  expect "PIE root flag retained as executable obligation" (case run [root { observation = (observation root) { elfType = PieExecutable, dynamicFlags = [("FLAGS_1","Flags: NOW PIE")] } },a,b] of Right _ -> True; _ -> False)
  expect "PIE flag on shared input refused" (rejected (run [root { observation = (observation root) { dynamicFlags = [("FLAGS_1","Flags: NOW PIE")] } },a,b]))
  expect "PIE cannot satisfy a shared provider role" (rejected (run [root,a { observation = (observation a) { elfType = PieExecutable } },b]))
  expect "missing provider" (rejected (run [root,a]))
  expect "soname mismatch" (rejected (run [root,a { observation = (observation a) { soname = Just "other.so" } },b]))
  expect "version mismatch" (rejected (run [root,a { observation = (observation a) { versionDefinitions = [] } },b]))
  expect "ABI mismatch" (rejected (run [root,a { observation = (observation a) { endian = Big } },b]))
  expect "machine mismatch" (rejected (run [root,a { observation = (observation a) { machine = UnsupportedMachine "different" } },b]))
  expect "class mismatch" (rejected (run [root,a { observation = (observation a) { elfClass = Elf32 } },b]))
  expect "ambiguous provider" (rejected (run (inputs ++ [a { inputPath = "/lib/another" }])))
  expect "no undeclared search" (rejected (resolveDeclared limits ["/elsewhere"] inputs "/app/root"))
  expect "relative and ORIGIN search unqualified" (rejected (resolveDeclared limits ["relative"] inputs "/app/root") && rejected (resolveDeclared limits ["/$ORIGIN"] inputs "/app/root"))
  expect "embedded RUNPATH unqualified" (rejected (run [root { observation = (observation root) { runpath = Just "/usr/lib" } },a,b]))
  expect "exact declared RUNPATH supported" (case run [root { observation = (observation root) { runpath = Just "/lib" } },a,b] of Right _ -> True; _ -> False)
  mapM_ (\path -> expect ("unqualified RUNPATH rejected: " ++ path) (rejected (run [root { observation = (observation root) { runpath = Just path } },a,b])))
    ["",":/lib","/lib:","/lib:/lib","relative","$ORIGIN","/lib/../lib","/lib/glibc-hwcaps/x86-64-v3"]
  expect "provider RUNPATH checked independently" (rejected (run [root,a { observation = (observation a) { runpath = Just "/elsewhere" } },b]))
  expect "node bound" (rejected (resolveDeclared (limits { maxNodes = 2 }) ["/lib"] inputs "/app/root"))
  expect "byte bound" (rejected (resolveDeclared (limits { maxBytes = 300 }) ["/lib"] inputs "/app/root"))
  expect "comparison bound" (rejected (resolveDeclared (limits { maxComparisons = 1 }) ["/lib"] inputs "/app/root"))
  let sameNamed = [VersionDef "liba.so" "BASE" 1 [],VersionDef "liba.so" "none" 2 []]
      aSame = a { observation = (observation a) { versionDefinitions = sameNamed } }
      noVersionRoot = root { observation = (observation root) { versionNeeds = [] } }
  expect "BASE and nonbase SONAME name permitted" (case run [noVersionRoot,aSame,b] of Right _ -> True; Left _ -> False)
  expect "BASE collision with non-SONAME refused" (rejected (run [noVersionRoot,aSame { observation = (observation aSame) { versionDefinitions = [VersionDef "unrelated" "BASE" 1 [],VersionDef "unrelated" "none" 2 []] } },b]))
  expect "two nonbase duplicate names refused" (rejected (run [noVersionRoot,aSame { observation = (observation aSame) { versionDefinitions = sameNamed ++ [VersionDef "liba.so" "none" 3 []] } },b]))
  expect "unsupported dynamic flags" (rejected (run [root { observation = (observation root) { dynamicFlags = [("FLAGS_1","Flags: NODEFLIB")] } },a,b]))
  expect "observed eager binding flags preserve declared graph" (case run [root { observation = (observation root) { dynamicFlags = [("FLAGS","BIND_NOW"),("FLAGS_1","Flags: NOW")] } },a,b] of Right _ -> True; _ -> False)
  expect "duplicate dynamic flag tag refused" (rejected (run [root { observation = (observation root) { dynamicFlags = [("FLAGS","BIND_NOW"),("FLAGS","BIND_NOW")] } },a,b]))
  expect "ORIGIN flag retained without loader proof" (case run [root { observation = (observation root) { dynamicFlags = [("FLAGS","ORIGIN BIND_NOW")] } },a,b] of
    Right graph -> any (\(path,sha,meta,_) -> path == "/app/root" && sha == digest && dynamicFlags meta == [("FLAGS","ORIGIN BIND_NOW")]) (runtimeObligations graph)
    Left _ -> False)
  let originItem = Input "/usr/lib/liborigin.so" "/usr/lib" "liborigin.so" 200 digest digest
        ((obs (Just "liborigin.so") [] [] []) { runpath = Just "$ORIGIN" })
      originWitness = OriginWitness "/usr/lib/liborigin.so.1" digest
      originMap = M.singleton (inputPath originItem) originWitness
      originRun ws dirs item = resolveDeclaredWithOrigins limits ws dirs [item] (inputPath item)
      accepts value = case value of Right _ -> True; Left _ -> False
  expect "legacy ORIGIN remains refused" (rejected (resolveDeclared limits ["/usr/lib"] [originItem] (inputPath originItem)))
  expect "exact witness accepts same-directory alias" (accepts (originRun originMap ["/usr/lib"] originItem))
  expect "missing witness refused" (rejected (originRun M.empty ["/usr/lib"] originItem))
  expect "wrong witness key refused" (rejected (originRun (M.singleton "/usr/lib/other" originWitness) ["/usr/lib"] originItem))
  expect "wrong witness digest refused" (rejected (originRun (M.singleton (inputPath originItem) (originWitness { witnessedDigest = replicate 64 'b' })) ["/usr/lib"] originItem))
  expect "wrong resolved parent refused" (rejected (originRun (M.singleton (inputPath originItem) (originWitness { resolvedPath = "/other/liborigin.so" })) ["/usr/lib"] originItem))
  let wrongLogical = originItem { inputPath = "/other/liborigin.so" }
  expect "wrong logical parent refused" (rejected (originRun (M.singleton (inputPath wrongLogical) originWitness) ["/usr/lib"] wrongLogical))
  expect "wrong searchDirectory refused" (rejected (originRun originMap ["/usr/lib"] (originItem { searchDirectory = "/other" })))
  expect "multiple search directories refused" (rejected (originRun originMap ["/usr/lib","/other"] originItem))
  mapM_ (\path -> expect ("unsupported token refused: " ++ path) (rejected (originRun originMap ["/usr/lib"] (originItem { observation = (observation originItem) { runpath = Just path } }))))
    ["${ORIGIN}","$ORIGIN/lib","$ORIGIN:/usr/lib","/usr/lib:$ORIGIN","$LIB"]
  let flagRun flags = run [root { observation = (observation root) { dynamicFlags = flags } },a,b]
      x86 = [("DT_X86_64_PLT","0x10040"),("DT_X86_64_PLTSZ","0x10"),("DT_X86_64_PLTENT","0x10")]
  expect "all supported flag families" (accepts (flagRun [("FLAGS","ORIGIN SYMBOLIC BIND_NOW STATIC_TLS"),("FLAGS_1","Flags: ORIGIN NOW NODELETE"),("SYMBOLIC","0x0")]))
  expect "actual x86 triple retained" (case flagRun x86 of Right graph -> any (\(path,sha,meta,_) -> path == "/app/root" && sha == digest && dynamicFlags meta == x86) (runtimeObligations graph); Left _ -> False)
  expect "actual captured x86 tags accepted" (case parseReadelf complete sframeLib of
    Right value -> accepts (flagRun (dynamicFlags value))
    Left _ -> False)
  mapM_ (\flags -> expect ("unsupported flags rejected: " ++ show flags) (rejected (flagRun flags)))
    [[("FLAGS","")],[("FLAGS","ORIGIN ORIGIN")],[("FLAGS","ORIGIN  BIND_NOW")],[("FLAGS","ORIGIN UNKNOWN")],
     [("FLAGS_1","Flags: NOW NODELETE NODELETE")],[("FLAGS_1","NOW")],[("TEXTREL","0x0")],
     [("BIND_NOW","0x0")],[("SYMBOLIC","0x1")],take 2 x86,x86 ++ [head x86],
     [("DT_X86_64_PLT","0xg"),("DT_X86_64_PLTSZ","0x10"),("DT_X86_64_PLTENT","0x10")]]
  expect "hwcaps directories unqualified" (rejected (resolveDeclared limits ["/lib/glibc-hwcaps/x86-64-v3"] inputs "/app/root"))
  expect "declared input bound" (rejected (resolveDeclared (limits { maxInputs = 2 }) ["/lib"] inputs "/app/root"))
  let alternative = a { inputPath = "/other/liba.so", searchDirectory = "/other" }
  expect "declared directory order selects explicit first match" (case resolveDeclared limits ["/other","/lib"] (inputs ++ [alternative]) "/app/root" of
    Right graph -> case edges graph of
      Edge _ path (Needed "liba.so") : _ -> path == "/other/liba.so"
      _ -> False
    Left _ -> False)
  expect "unlisted interpreter" (rejected (run [root { observation = (observation root) { interpreter = Just "/lib64/ld.so" } },a,b]))
  expect "missing source digest" (rejected (run [root,a { sourceDigest = "" },b]))
  expect "loader cache is not a directory search" (rejected (resolveDeclared limits ["/etc/ld.so.cache"] inputs "/app/root"))
  expect "embedded RPATH unqualified" (rejected (run [root { observation = (observation root) { rpath = Just "/lib" } },a,b]))
  let prefix = "/usr/lib/tinysparql-3.0"
      defaults = ["/usr/lib"]
      parentItem = Input "/usr/lib/libtinysparql-3.0.so.0" "/usr/lib" "libtinysparql-3.0.so.0" 200 digest digest
        ((obs (Just "libtinysparql-3.0.so.0") ["libchild.so"] [] []) { runpath = Just prefix })
      child = Input (prefix ++ "/libchild.so") prefix "libchild.so" 200 digest digest (obs (Just "libchild.so") [] [] [])
      childDefault = child { inputPath = "/usr/lib/libchild.so", searchDirectory = "/usr/lib" }
      plan = SearchPlan digest (Just prefix) defaults [prefix,"/usr/lib"]
      planMap = M.singleton (inputPath parentItem) plan
      graphPlan ps xs = resolveDeclaredWithSearchPlans limits M.empty ps defaults xs (inputPath parentItem)
      chosen result = case result of
        Right graph -> case edges graph of Edge _ path (Needed "libchild.so") : _ -> Just path; _ -> Nothing
        Left _ -> Nothing
  expect "old API refuses prefix" (rejected (resolveDeclared limits defaults [parentItem,child] (inputPath parentItem)))
  expect "observed prefix chosen before default" (chosen (graphPlan planMap [parentItem,child,childDefault]) == Just (inputPath child))
  expect "declared absence permits default" (chosen (graphPlan planMap [parentItem,childDefault]) == Just (inputPath childDefault))
  expect "plan retained with computed order" (case graphPlan planMap [parentItem,child] of
    Right graph -> (inputPath parentItem,Just plan,[prefix,"/usr/lib"]) `elem` searchObligations graph
    Left _ -> False)
  expect "missing plan refuses prefix" (rejected (graphPlan M.empty [parentItem,child]))
  expect "unknown plan key refused" (rejected (graphPlan (M.singleton "/usr/lib/wrong" plan) [parentItem,child]))
  mapM_ (\p -> expect ("bad plan refused: " ++ show p) (rejected (graphPlan (M.singleton (inputPath parentItem) p) [parentItem,child])))
    [plan { planSourceDigest = replicate 64 'b' },plan { planRunpath = Nothing },plan { planDefaults = [prefix] },
     plan { planEffective = ["/usr/lib",prefix] },plan { planEffective = [prefix,"/usr/lib","/other"] },
     plan { planEffective = [prefix] }]
  expect "changed source invalidates plan" (rejected (graphPlan planMap [parentItem { sourceDigest = replicate 64 'b' },child]))
  let badChild = child { observation = (observation child) { endian = Big } }
      duplicateChild = child { inputPath = prefix ++ "/other-child" }
  expect "bad first provider never falls back" (rejected (graphPlan planMap [parentItem,badChild,childDefault]))
  let requiring = parentItem { observation = (observation parentItem) { versionNeeds = [VersionNeed "libchild.so" [("CHILD_1","none",2)]] } }
      goodDefault = childDefault { observation = (observation childDefault) { versionDefinitions = [sampleVersion "CHILD_1"] } }
  expect "wrong first provider version never falls back" (rejected (graphPlan planMap [requiring,child,goodDefault]))
  expect "ambiguous first provider refused" (rejected (graphPlan planMap [parentItem,child,duplicateChild,childDefault]))
  let grand = Input (prefix ++ "/libgrand.so") prefix "libgrand.so" 200 digest digest (obs (Just "libgrand.so") [] [] [])
      childNeeds = child { observation = (observation child) { needed = ["libgrand.so"] } }
      childOwn = childNeeds { observation = (observation childNeeds) { runpath = Just prefix } }
      bothPlans = M.insert (inputPath childOwn) plan planMap
  expect "child does not inherit parent prefix" (rejected (graphPlan planMap [parentItem,childNeeds,grand]))
  expect "child own plan finds grandchild" (case graphPlan bothPlans [parentItem,childOwn,grand] of
    Right graph -> Edge (inputPath childOwn) (inputPath grand) (Needed "libgrand.so") `elem` edges graph
    Left _ -> False)
  mapM_ (\bad -> let badItem = parentItem { observation = (observation parentItem) { runpath = Just bad } }
                     badPlan = SearchPlan digest (Just bad) defaults [bad,"/usr/lib"]
                 in expect ("bad prefix refused: " ++ bad) (rejected (graphPlan (M.singleton (inputPath badItem) badPlan) [badItem,child])))
    ["",":/usr/lib","/usr/lib:","relative","/usr/lib/../lib","/usr/lib/glibc-hwcaps/x","${ORIGIN}","$ORIGIN/lib",prefix ++ ":" ++ prefix]
  let sameDefault = parentItem { observation = (observation parentItem) { runpath = Just "/usr/lib" } }
      sameDefaultPlan = SearchPlan digest (Just "/usr/lib") defaults defaults
  expect "duplicate default appended once" (chosen (graphPlan (M.singleton (inputPath sameDefault) sameDefaultPlan) [sameDefault,childDefault]) == Just (inputPath childDefault))
  let originPlan = SearchPlan digest (Just "$ORIGIN") defaults defaults
      originPlans = M.singleton (inputPath originItem) originPlan
  expect "planned origin retains prior witness requirement" (rejected (resolveDeclaredWithSearchPlans limits M.empty originPlans defaults [originItem] (inputPath originItem)) &&
    accepts (resolveDeclaredWithSearchPlans limits originMap originPlans defaults [originItem] (inputPath originItem)))
  expect "planned search still enforces comparison cap" (rejected (resolveDeclaredWithSearchPlans (limits { maxComparisons = 1 }) M.empty planMap defaults [parentItem,child] (inputPath parentItem)))
