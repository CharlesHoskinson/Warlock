module Warlock.Elf.Readelf
  ( ToolProfile(..), Capture(..), ElfClass(..), Endian(..), Machine(..), ElfType(..), VersionNeed(..)
  , VersionDef(..), ProgramHeader(..), VersionSymbol(..), Observation(..), ParseFailure(..), parseReadelf ) where

import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Data.Char (isDigit, isHexDigit, isSpace)
import Data.List (foldl', isPrefixOf, nub, stripPrefix)
import Numeric (readHex)

-- Capture completeness is asserted by the reviewed process owner, never by text.
data ToolProfile = GnuReadelf247 | UnsupportedTool deriving (Eq, Show)
data Capture = Capture { toolProfile :: ToolProfile, processSucceeded :: Bool, outputComplete :: Bool, headerRequested :: Bool
                       , programRequested :: Bool, dynamicRequested :: Bool, versionsRequested :: Bool }
  deriving (Eq, Show)
data ElfClass = Elf64 | Elf32 deriving (Eq, Show)
data Endian = Little | Big deriving (Eq, Show)
data Machine = X86_64 | UnsupportedMachine String deriving (Eq, Show)
data ElfType = Executable | PieExecutable | Shared deriving (Eq, Show)
data VersionNeed = VersionNeed { needFile :: String, needVersions :: [(String,String,Int)] } deriving (Eq, Show)
data VersionDef = VersionDef { defName :: String, defFlags :: String, defIndex :: Int, defParents :: [String] } deriving (Eq, Show)
data ProgramHeader = ProgramHeader { programKind :: String, programOffset :: String, programVirtual :: String
  , programPhysical :: String, programFileSize :: String, programMemorySize :: String
  , programFlags :: [String], programAlignment :: String } deriving (Eq, Show)
data VersionSymbol = VersionSymbol { symbolIndex :: Int, symbolHidden :: Bool, symbolName :: String } deriving (Eq, Show)
data Observation = Observation { elfClass :: ElfClass, endian :: Endian, machine :: Machine, elfType :: ElfType
  , interpreter :: Maybe String, soname :: Maybe String, needed :: [String], rpath :: Maybe String, runpath :: Maybe String
  , dynamicFlags :: [(String,String)], versionNeeds :: [VersionNeed], versionDefinitions :: [VersionDef], observedBytes :: Int
  , programHeaders :: [ProgramHeader], relaCount :: Maybe Integer, versionSymbols :: [VersionSymbol] } deriving (Eq, Show)
newtype ParseFailure = ParseFailure String deriving (Eq, Show)
failP :: String -> Either ParseFailure a
failP = Left . ParseFailure
trim :: String -> String
trim = reverse . dropWhile isSpace . reverse . dropWhile isSpace
single :: String -> [a] -> Either ParseFailure a
single _ [x] = Right x
single label _ = failP (label ++ " missing or duplicated")
number :: String -> Either ParseFailure Int
number x | not (null x) && all isDigit x && length x <= 8 = Right (foldl' (\n c -> n * 10 + fromEnum c - fromEnum '0') 0 x)
number _ = failP "invalid decimal count"
hex :: String -> Either ParseFailure Int
hex x | not (null x) && all isHexDigit x && length x <= 8 = case readHex x of [(n,"")] -> Right n; _ -> failP "invalid hex"
hex _ = failP "invalid hex"
field :: String -> [String] -> Either ParseFailure String
field key rows = single key [trim (drop (length key) t) | row <- rows, let t = trim row, (key ++ " ") `isPrefixOf` t]
section :: String -> [String] -> Either ParseFailure [String]
section prefix rows = case dropWhile (not . isPrefixOf prefix . trim) rows of
  [] -> failP ("missing " ++ prefix)
  (_:rest) -> Right (takeWhile (not . null . trim) rest)
countHeading :: String -> String -> Either ParseFailure Int
countHeading prefix row = case words (trim row) of
  ws | prefix `isPrefixOf` trim row -> case dropWhile (/= "contains") ws of
    ("contains":n:unit:_) | unit == "entry:" || unit == "entries:" -> number n
    _ -> failP "unsupported section heading"
  _ -> failP "wrong section heading"
heading :: String -> [String] -> Either ParseFailure String
heading prefix rows = single prefix [trim row | row <- rows, prefix `isPrefixOf` trim row]
bracketed :: String -> String -> Either ParseFailure String
bracketed prefix value = case stripPrefix prefix (trim value) of
  Just ('[':xs) -> case reverse xs of
    ']':back | not (null back) && '[' `notElem` back && ']' `notElem` back -> Right (reverse back)
    _ -> failP "malformed bracketed value"
  _ -> failP "unsupported dynamic value"

type Dyn = (String,String)
dynamicLine :: String -> Either ParseFailure Dyn
dynamicLine row = case words row of
  (address:tag:rest) | "0x" `isPrefixOf` address && all isHexDigit (drop 2 address) ->
    case tag of
      '(':xs -> case reverse xs of
        ')':back | not (null back) && not (null rest) -> Right (reverse back, unwords rest)
        _ -> failP "malformed dynamic tag"
      _ -> failP "malformed dynamic entry"
  _ -> failP "malformed dynamic entry"
optionalOne :: String -> [String] -> Either ParseFailure (Maybe String)
optionalOne _ [] = Right Nothing
optionalOne _ [x] = Right (Just x)
optionalOne label _ = failP (label ++ " duplicated")

parseReadelf :: Capture -> B.ByteString -> Either ParseFailure Observation
parseReadelf capture input = do
  if toolProfile capture /= GnuReadelf247 || not (and [processSucceeded capture,outputComplete capture,headerRequested capture,programRequested capture,dynamicRequested capture,versionsRequested capture]) then failP "capture completeness unproved" else Right ()
  if B.null input || B.length input > 1048576 || B.last input /= 10 || B.any (\w -> w /= 10 && w /= 9 && (w < 32 || w > 126)) input then failP "invalid text bytes or bound" else Right ()
  let rows = lines (C.unpack input)
  if length rows > 20000 || null rows || trim (head rows) /= "ELF Header:" then failP "invalid header framing" else Right ()
  let versions = [trim (drop (length "Version:") t) | row <- rows, let t = trim row, "Version: " `isPrefixOf` t]
  if versions /= ["1 (current)","0x1"] then failP "unsupported or duplicate ELF header version" else Right ()
  magic <- words <$> field "Magic:" rows
  if length magic /= 16 || take 7 magic /= ["7f","45","4c","46","02","01","01"] || any (\x -> length x /= 2 || any (not . isHexDigit) x) magic then failP "unsupported or malformed ELF magic" else Right ()
  cls <- field "Class:" rows
  klass <- case cls of "ELF64" -> Right Elf64; _ -> failP "unsupported ELF class"
  dat <- field "Data:" rows
  order <- case dat of "2's complement, little endian" -> Right Little; "2's complement, big endian" -> Right Big; _ -> failP "unsupported endian"
  mach <- field "Machine:" rows
  if mach /= "Advanced Micro Devices X86-64" || order /= Little then failP "unsupported machine or endian combination" else Right ()
  typ <- field "Type:" rows
  kind <- case typ of "EXEC (Executable file)" -> Right Executable; "DYN (Position-Independent Executable file)" -> Right PieExecutable; "DYN (Shared object file)" -> Right Shared; _ -> failP "unsupported ELF type"
  nprog <- field "Number of program headers:" rows >>= number
  _ <- heading "Program Headers:" rows
  let programRows = drop 1 $ dropWhile ((/= "Program Headers:") . trim) rows
      actualProgram = [row | row <- takeWhile (not . null . trim) (dropWhile (null . trim) programRows), case words row of (t:_) -> t /= "Type" && all (\c -> c /= '[') t; _ -> False]
  types <- mapM programLine actualProgram
  if length types /= nprog then failP "program header count mismatch" else Right ()
  interp <- optionalOne "interpreter" [take (length v - 1) v | row <- rows, Just v <- [stripPrefix "[Requesting program interpreter: " (trim row)], not (null v), last v == ']']
  if length (filter ((== "INTERP") . programKind) types) /= maybe 0 (const 1) interp then failP "interpreter header mismatch" else Right ()
  dynHead <- heading "Dynamic section at offset " rows
  count <- countHeading "Dynamic section at offset " dynHead
  dynSection <- section "Dynamic section at offset " rows
  dyn <- mapM dynamicLine (drop 1 dynSection)
  if length dyn /= count || null dyn || fst (last dyn) /= "NULL" || length [() | (k,_) <- dyn, k == "NULL"] /= 1 then failP "dynamic count or terminator mismatch" else Right ()
  let tagged k = [v | (name,v) <- dyn, name == k]
      known = ["NEEDED","SONAME","RPATH","RUNPATH","NULL","PLTGOT","PLTRELSZ","JMPREL","PLTREL","RELA","RELASZ","RELAENT","DEBUG","SYMTAB","SYMENT","STRTAB","STRSZ","GNU_HASH","INIT","FINI","INIT_ARRAY","INIT_ARRAYSZ","FINI_ARRAY","FINI_ARRAYSZ","VERSYM","VERNEED","VERNEEDNUM","VERDEF","VERDEFNUM","FLAGS","FLAGS_1","HASH","REL","RELSZ","RELENT","RELR","RELRSZ","RELRENT","RELACOUNT","DT_X86_64_PLT","DT_X86_64_PLTSZ","DT_X86_64_PLTENT","BIND_NOW","TEXTREL","SYMBOLIC"]
  if any (\(k,_) -> k `notElem` known) dyn then failP "unsupported dynamic tag" else Right ()
  rc <- case tagged "RELACOUNT" of
    [] -> Right Nothing
    [value] | not (null value) && length value <= 20 && all isDigit value ->
      let n = foldl' (\a c -> a * 10 + toInteger (fromEnum c - fromEnum '0')) 0 value
      in if n <= 18446744073709551615 then Right (Just n) else failP "RELACOUNT overflow"
    _ -> failP "invalid or duplicate RELACOUNT"
  let x86Tags = ["DT_X86_64_PLT","DT_X86_64_PLTSZ","DT_X86_64_PLTENT"]
      x86Values = concatMap tagged x86Tags
      validHexValue value = case stripPrefix "0x" value of
        Just digits -> not (null digits) && length digits <= 16 && all isHexDigit digits
        Nothing -> False
  if null x86Values || (all ((== 1) . length . tagged) x86Tags && all validHexValue x86Values)
    then Right () else failP "incomplete or malformed x86 PLT tags"
  deps <- mapM (bracketed "Shared library: ") (tagged "NEEDED")
  name <- mapM (bracketed "Library soname: ") (tagged "SONAME") >>= optionalOne "SONAME"
  rp <- mapM (bracketed "Library rpath: ") (tagged "RPATH") >>= optionalOne "RPATH"
  rnp <- mapM (bracketed "Library runpath: ") (tagged "RUNPATH") >>= optionalOne "RUNPATH"
  if any (\k -> length (tagged k) > 1) ["VERSYM","VERNEED","VERNEEDNUM","VERDEF","VERDEFNUM"] then failP "duplicate version dynamic tag" else Right ()
  if any (\value -> case stripPrefix "0x" value of Just digits -> null digits || any (not . isHexDigit) digits; Nothing -> True) (concatMap tagged ["VERSYM","VERNEED","VERDEF"]) then failP "invalid version table address" else Right ()
  if any (\row -> let t = trim row in "Version " `isPrefixOf` t && not (any (`isPrefixOf` t) ["Version symbols section ","Version needs section ","Version definition section "])) rows then failP "unknown version section" else Right ()
  if (not (null (tagged "VERNEED")) || not (null (tagged "VERDEF"))) && null (tagged "VERSYM") then failP "version table missing" else Right ()
  symbols <- validateSymbols rows (not (null (tagged "VERSYM")))
  if null (tagged "VERNEED") /= null (tagged "VERNEEDNUM") || null (tagged "VERDEF") /= null (tagged "VERDEFNUM") then failP "incomplete version dynamic tags" else Right ()
  ns <- parseNeeds rows (tagged "VERNEEDNUM")
  ds <- parseDefs rows (tagged "VERDEFNUM")
  if any (\n -> needFile n `notElem` deps) ns then failP "version-need file is not NEEDED" else Right ()
  if length (nub (map needFile ns)) /= length ns || length (nub (map defIndex ds)) /= length ds || length (nub (map defName (filter ((/= "BASE") . defFlags) ds))) /= length (filter ((/= "BASE") . defFlags) ds) || any (\d -> if defFlags d == "BASE" then defIndex d /= 1 else defIndex d <= 1) ds then failP "duplicate version group identity" else Right ()
  let indexed = [(index,versionName) | group <- ns, (versionName,_,index) <- needVersions group] ++ [(defIndex item,defName item) | item <- ds]
      matches (VersionSymbol index _ versionName)
        | index == 0 = versionName == "*local*"
        | index == 1 = versionName == "*global*"
        | otherwise = nub [n | (i,n) <- indexed, i == index] == [versionName]
  if length (nub (map fst indexed)) /= length indexed then failP "version index has multiple owners" else Right ()
  if all matches symbols then Right () else failP "version symbol references unresolved or inconsistent"
  pure (Observation klass order X86_64 kind interp name deps rp rnp [(k,v) | (k,v) <- dyn, k `elem` ["FLAGS","FLAGS_1","BIND_NOW","TEXTREL","SYMBOLIC","DT_X86_64_PLT","DT_X86_64_PLTSZ","DT_X86_64_PLTENT"]] ns ds (B.length input) types rc symbols)

validateSymbols :: [String] -> Bool -> Either ParseFailure [VersionSymbol]
validateSymbols rows expected = do
  let hs = [trim r | r <- rows, "Version symbols section " `isPrefixOf` trim r]
  case (expected, hs) of
    (False, []) -> Right []
    (True, [h]) -> do
      total <- countHeading "Version symbols section " h
      entries <- section "Version symbols section " rows
      case entries of
        (address:body) | "Addr:" `isPrefixOf` trim address -> do
          (count, backwards) <- foldl symbolRow (Right (0,[])) body
          if count == total then Right (reverse backwards) else failP "version symbol count mismatch"
        _ -> failP "missing version symbol address"
    _ -> failP "version symbol section inconsistency"
  where
    symbolRow acc row = do
      (count, backwards) <- acc
      case words row of
        (off:xs) | not (null off) && last off == ':' -> do
          n <- hex (init off)
          if n /= count then failP "version symbol offset mismatch" else do
            more <- pairs xs
            Right (count + length more, reverse more ++ backwards)
        _ -> failP "malformed version symbol row"
    pairs [] = Right []
    pairs (token:rest) = do
      let (prefix, attached) = break (== '(') token
          hidden = not (null prefix) && last prefix == 'h'
          digits = if hidden then init prefix else prefix
      n <- hex digits
      (name, remaining) <- case attached of
        [] -> case rest of
          (next:xs) -> Right (next,xs)
          [] -> failP "missing version symbol name"
        _ -> Right (attached,rest)
      if length name < 3 || head name /= '(' || last name /= ')' || any (`elem` "()") (init (tail name))
        then failP "malformed version symbol" else do
          more <- pairs remaining
          Right (VersionSymbol n hidden (init (tail name)) : more)

parseNeeds :: [String] -> [String] -> Either ParseFailure [VersionNeed]
parseNeeds rows counts = do
  let headings = [trim r | r <- rows, "Version needs section " `isPrefixOf` trim r]
  case (counts, headings) of
    ([],[]) -> Right []
    ([raw],[h]) -> do
      expected <- number raw
      announced <- countHeading "Version needs section " h
      block <- section "Version needs section " rows
      body <- case block of (x:xs) | "Addr:" `isPrefixOf` trim x -> Right xs; _ -> failP "missing needs address"
      groups <- needsGroups body
      if expected > 0 && expected == announced && length groups == expected then Right groups else failP "needs group count mismatch"
    _ -> failP "needs section inconsistency"
  where
    needsGroups [] = Right []
    needsGroups (row:rest) = case words row of
      [offset,"Version:","1","File:",file,"Cnt:",n] | validOffset offset && not (null file) -> do
        count <- number n
        if count <= 0 || length rest < count then failP "truncated needs group" else do
          versions <- mapM needLine (take count rest)
          more <- needsGroups (drop count rest)
          Right (VersionNeed file versions : more)
      _ -> failP "unsupported needs group"
    needLine row = case words row of
      [offset,"Name:",name,"Flags:",flags,"Version:",index] | validOffset offset && flags `elem` ["none","WEAK"] -> do
        n <- number index
        if null name || n <= 1 then failP "invalid need version" else Right (name,flags,n)
      _ -> failP "unsupported need version"

parseDefs :: [String] -> [String] -> Either ParseFailure [VersionDef]
parseDefs rows counts = do
  let headings = [trim r | r <- rows, "Version definition section " `isPrefixOf` trim r]
  case (counts, headings) of
    ([],[]) -> Right []
    ([raw],[h]) -> do
      expected <- number raw
      announced <- countHeading "Version definition section " h
      block <- section "Version definition section " rows
      body <- case block of (x:xs) | "Addr:" `isPrefixOf` trim x -> Right xs; _ -> failP "missing definition address"
      groups <- defGroups body
      if expected > 0 && expected == announced && length groups == expected then Right groups else failP "definition group count mismatch"
    _ -> failP "definition section inconsistency"
  where
    defGroups [] = Right []
    defGroups (row:rest) = case words row of
      [offset,"Rev:","1","Flags:",flags,"Index:",index,"Cnt:",cnt,"Name:",name]
        | validOffset offset && flags `elem` ["none","BASE","WEAK"] -> do
          i <- number index; n <- number cnt
          if n < 1 || length rest < n - 1 then failP "truncated definition" else do
            parents <- mapM parentLine (zip [1..] (take (n-1) rest))
            more <- defGroups (drop (n-1) rest)
            Right (VersionDef name flags i parents : more)
      _ -> failP "unsupported version definition"
    parentLine (expected,row) = case words row of
      [offset,"Parent",index,name] | validOffset offset && not (null index) && last index == ':' -> do
        n <- number (init index)
        if n == expected && not (null name) then Right name else failP "invalid definition parent"
      _ -> failP "unsupported definition parent"

validOffset :: String -> Bool
validOffset x = not (null x) && last x == ':' &&
  let raw = init x; digits = case stripPrefix "0x" raw of Just ys -> ys; Nothing -> raw
  in not (null digits) && all isHexDigit digits

programLine :: String -> Either ParseFailure ProgramHeader
programLine row = case words row of
  (kind:offset:virtual:physical:fileSize:memorySize:rest)
    | kind `elem` ["PHDR","INTERP","LOAD","DYNAMIC","NOTE","TLS","GNU_EH_FRAME","GNU_STACK","GNU_RELRO","GNU_PROPERTY","GNU_SFRAME"] &&
      all isAddress [offset,virtual,physical,fileSize,memorySize] && validFlags rest -> Right (ProgramHeader kind offset virtual physical fileSize memorySize (init rest) (last rest))
  _ -> failP "unsupported program header columns"
  where
    isAddress x = case stripPrefix "0x" x of Just y -> not (null y) && all isHexDigit y; _ -> False
    validFlags xs = case reverse xs of
      (align:flags) -> (align == "0" || isAddress align) && not (null flags) && all (`elem` ["R","W","E","RW","RE","RWE"]) flags
      _ -> False
