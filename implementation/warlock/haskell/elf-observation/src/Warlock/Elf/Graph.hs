module Warlock.Elf.Graph
  ( Limits(..), Input(..), EdgeKind(..), Edge(..), Graph(..), OriginWitness(..), SearchPlan(..), Unresolved(..), resolveDeclared, resolveDeclaredWithOrigins, resolveDeclaredWithSearchPlans ) where

import Data.Char (isDigit, isHexDigit)
import Data.List (intercalate, nub)
import qualified Data.Map.Strict as M
import qualified Data.Set as S
import Warlock.Elf.Readelf

data Limits = Limits { maxInputs :: Int, maxNodes :: Int, maxBytes :: Int, maxComparisons :: Int } deriving (Eq, Show)
-- Every path/alias/observation is provided by a previously qualified caller.
-- This pure library never opens paths and never validates a file descriptor.
data Input = Input { inputPath :: FilePath, searchDirectory :: FilePath, declaredName :: String
                   , sourceBytes :: Int, sourceDigest :: String, captureDigest :: String
                   , observation :: Observation } deriving (Eq, Show)
-- Caller-attested held leaf and its source digest; does not establish runtime placement.
data OriginWitness = OriginWitness { resolvedPath :: FilePath, witnessedDigest :: String } deriving (Eq, Show)
-- Caller-declared search policy, bound to the captured object, not loader evidence.
data SearchPlan = SearchPlan { planSourceDigest :: String, planRunpath :: Maybe String
                             , planDefaults :: [FilePath], planEffective :: [FilePath] } deriving (Eq, Show)
data EdgeKind = Needed String | Interpreter deriving (Eq, Show)
data Edge = Edge { edgeFrom :: FilePath, edgeTo :: FilePath, edgeKind :: EdgeKind } deriving (Eq, Show)
data Graph = Graph { visited :: [FilePath], edges :: [Edge], totalBytes :: Int, declaredBytes :: Int, comparisons :: Int
                   , runtimeObligations :: [(FilePath,String,Observation,Maybe OriginWitness)]
                   , searchObligations :: [(FilePath,Maybe SearchPlan,[FilePath])] } deriving (Eq, Show)
newtype Unresolved = Unresolved String deriving (Eq, Show)
unknown :: String -> Either Unresolved a
unknown = Left . Unresolved

-- This means only complete against this explicitly declared set/search order;
-- no dynamic loader/cache/hwcaps or system filesystem resolution is modeled.
resolveDeclared :: Limits -> [FilePath] -> [Input] -> FilePath -> Either Unresolved Graph
resolveDeclared limits search inputs root = resolveDeclaredWithOrigins limits M.empty search inputs root

resolveDeclaredWithOrigins :: Limits -> M.Map FilePath OriginWitness -> [FilePath] -> [Input] -> FilePath -> Either Unresolved Graph
resolveDeclaredWithOrigins limits witnesses search inputs root = resolveDeclaredWithSearchPlans limits witnesses M.empty search inputs root

resolveDeclaredWithSearchPlans :: Limits -> M.Map FilePath OriginWitness -> M.Map FilePath SearchPlan -> [FilePath] -> [Input] -> FilePath -> Either Unresolved Graph
resolveDeclaredWithSearchPlans limits witnesses plans search inputs root = do
  if any (<= 0) [maxInputs limits,maxNodes limits,maxBytes limits,maxComparisons limits] then unknown "invalid bounds" else Right ()
  if maxInputs limits > 4096 || maxNodes limits > 4096 || maxBytes limits > 536870912 || maxComparisons limits > 4000000 then unknown "configured bounds too large" else Right ()
  if length (take (maxInputs limits + 1) inputs) > maxInputs limits || length (take (maxInputs limits + 1) search) > maxInputs limits then unknown "declared input bound" else Right ()
  if null search || length search /= length (nub search) || any invalidDirectory search then unknown "unsupported search directory" else Right ()
  if any (invalidPath . inputPath) inputs || any (\i -> length (take 513 (declaredName i)) > 512) inputs then unknown "unsupported declared input path or name" else Right ()
  if any (\i -> sourceBytes i <= 0 || not (digest (sourceDigest i)) || not (digest (captureDigest i))) inputs then unknown "missing declared source evidence" else Right ()
  let declared = sum [toInteger (sourceBytes i) + toInteger (observedBytes (observation i)) | i <- inputs]
  if any (\i -> observedBytes (observation i) <= 0) inputs || declared > toInteger (maxBytes limits) then unknown "declared source byte bound" else Right ()
  let byPath = M.fromList [(inputPath i,i) | i <- inputs]
  if M.size byPath /= length inputs then unknown "duplicate input path" else Right ()
  if M.size witnesses > maxInputs limits || any (`M.notMember` byPath) (M.keys witnesses) then unknown "origin witness map bound or unknown key" else Right ()
  if M.size plans > maxInputs limits || any (`M.notMember` byPath) (M.keys plans) then unknown "search plan map bound or unknown key" else Right ()
  mapM_ (\(path,_) -> maybe (unknown "unknown search plan key") (\item -> effectiveSearch item >> Right ()) (M.lookup path byPath)) (M.toList plans)
  first <- maybe (unknown "missing declared root") Right (M.lookup root byPath)
  go (fromInteger declared) byPath S.empty [first] [] [] 0 0
  where
    digest d = length (take 65 d) == 64 && all (\c -> isDigit c || c `elem` ['a'..'f']) d
    invalidPath p = null p || length (take 4097 p) > 4096 || head p /= '/' || any (== '$') p || '\0' `elem` p || any (`elem` [".","..",""]) (splitSlash (drop 1 p))
    invalidDirectory p = invalidPath p || ':' `elem` p || ("glibc-hwcaps" `contains` p || "ld.so.cache" `contains` p) || any (`elem` [".","..",""]) (splitSlash (drop 1 p))
    contains needle hay = any (needle `prefix`) (tails hay)
    prefix [] _ = True
    prefix _ [] = False
    prefix (x:xs) (y:ys) = x == y && prefix xs ys
    tails [] = [[]]
    tails x@(_:xs) = x : tails xs
    splitSlash [] = [""]
    splitSlash x = case break (== '/') x of (a,[]) -> [a]; (a,_:b) -> a : splitSlash b
    splitColon value = case break (== ':') value of
      (a,[]) -> [a]
      (a,_:rest) -> a : splitColon rest
    originAllowed item = case M.lookup (inputPath item) witnesses of
      Just witness -> search == ["/usr/lib"] && searchDirectory item == "/usr/lib"
        && not (invalidPath (inputPath item)) && parent (inputPath item) == "/usr/lib"
        && not (invalidPath (resolvedPath witness)) && parent (resolvedPath witness) == "/usr/lib"
        && witnessedDigest witness == sourceDigest item
      Nothing -> False
    effectiveSearch item = case M.lookup (inputPath item) plans of
      Nothing -> case runpath (observation item) of
        Nothing -> Right search
        Just "$ORIGIN" | originAllowed item -> Right search
        Just path | path == intercalate ":" search -> Right search
        _ -> unknown "RUNPATH differs from declared search order"
      Just plan -> do
        if planSourceDigest plan /= sourceDigest item || planRunpath plan /= runpath (observation item)
          || planDefaults plan /= search || search /= ["/usr/lib"] then unknown "search plan binding mismatch" else Right ()
        if length (take 65 (planEffective plan)) > 64 || any invalidDirectory (planEffective plan) then unknown "search plan effective bound or directory" else Right ()
        paths <- case planRunpath plan of
          Nothing -> Right []
          Just "$ORIGIN" | originAllowed item -> Right ["/usr/lib"]
          Just "$ORIGIN" -> unknown "origin witness or namespace placement premise missing"
          Just raw | length (take 4097 raw) <= 4096 -> do
            let components = splitColon raw
            if length (take 65 components) > 64 || any invalidDirectory components || length components /= length (nub components)
              then unknown "unsupported RUNPATH components" else Right components
          _ -> unknown "RUNPATH bound"
        let result = nub (paths ++ search)
        if result == planEffective plan then Right result else unknown "search plan effective order mismatch"
    parent path = reverse (drop 1 (dropWhile (/= '/') (reverse path)))
    tokenSet allowed value = let tokens = words value in
      not (null tokens) && unwords tokens == value && length tokens == length (nub tokens) && all (`elem` allowed) tokens
    x86Tags = ["DT_X86_64_PLT","DT_X86_64_PLTSZ","DT_X86_64_PLTENT"]
    hexValue value = case value of
      '0':'x':digits -> not (null digits) && length digits <= 16 && all isHexDigit digits
      _ -> False
    allowedFlag (tag,value) = case tag of
      "FLAGS" -> tokenSet ["ORIGIN","SYMBOLIC","BIND_NOW","STATIC_TLS"] value
      "FLAGS_1" -> case stripFlags value of
        Just rest -> tokenSet ["ORIGIN","NOW","NODELETE","PIE"] rest
        Nothing -> False
      "SYMBOLIC" -> value == "0x0"
      _ -> tag `elem` x86Tags && hexValue value
    stripFlags value = case splitAt 7 value of
      ("Flags: ",rest) -> Just rest
      _ -> Nothing
    compatible a b = elfClass a == elfClass b && endian a == endian b && machine a == machine b
    go declared byPath _ [] order found bytes count =
      let retained = [(path,sourceDigest item,observation item,if runpath (observation item) == Just "$ORIGIN" then M.lookup path witnesses else Nothing) | path <- order, Just item <- [M.lookup path byPath]]
      in do
        searches <- mapM (\path -> case M.lookup path byPath of
          Nothing -> unknown "visited input missing"
          Just item -> do
            dirs <- effectiveSearch item
            Right (path,M.lookup path plans,dirs)) order
        Right (Graph order found bytes declared count retained searches)
    go declared byPath seen (item:queue) order found bytes count
      | S.member (inputPath item) seen = go declared byPath seen queue order found bytes count
      | otherwise = do
          let meta = observation item
              bytesInteger = toInteger bytes + toInteger (observedBytes meta) + toInteger (sourceBytes item)
              order' = order ++ [inputPath item]
              seen' = S.insert (inputPath item) seen
          if observedBytes meta <= 0 || bytesInteger > toInteger (maxBytes limits) then unknown "observation byte bound" else Right ()
          let bytes' = fromInteger bytesInteger
          if length (take 4097 (needed meta)) > 4096 || length (take 4097 (versionNeeds meta)) > 4096 || length (take 4097 (versionDefinitions meta)) > 4096 || any (\n -> length (take 4097 (needVersions n)) > 4096) (versionNeeds meta) then unknown "metadata list bound" else Right ()
          if length order' > maxNodes limits then unknown "visited node bound" else Right ()
          if any (\v -> needFile v `notElem` needed meta) (versionNeeds meta) || length (nub (map needFile (versionNeeds meta))) /= length (versionNeeds meta) || length (nub (map defIndex (versionDefinitions meta))) /= length (versionDefinitions meta) || length (nub (map defName (filter ((/= "BASE") . defFlags) (versionDefinitions meta)))) /= length (filter ((/= "BASE") . defFlags) (versionDefinitions meta)) || any (\d -> if defFlags d == "BASE" then defIndex d /= 1 else defIndex d <= 1) (versionDefinitions meta) || any (\d -> defFlags d == "BASE" && defName d `elem` map defName (filter ((/= "BASE") . defFlags) (versionDefinitions meta)) && soname meta /= Just (defName d)) (versionDefinitions meta) then unknown "inconsistent declared version observations" else Right ()
          if any (\v -> length (take 513 v) > 512) (needed meta ++ map needFile (versionNeeds meta) ++ [name | group <- versionNeeds meta, (name,_,_) <- needVersions group] ++ map defName (versionDefinitions meta)) then unknown "metadata name bound" else Right ()
          if any (\group -> any (\(_,flags,index) -> flags `notElem` ["none","WEAK"] || index <= 1) (needVersions group)) (versionNeeds meta) || any (\v -> defFlags v `notElem` ["none","BASE","WEAK"] || defIndex v < 1) (versionDefinitions meta) then unknown "unsupported version flags or index" else Right ()
          -- Only an exact declaration of this controlled namespace's search list.
          -- This does not reproduce host loader inheritance, defaults or tokens.
          if rpath meta /= Nothing then unknown "embedded RPATH semantics unqualified" else Right ()
          objectSearch <- effectiveSearch item
          -- Metadata is retained as an obligation; no relocation, TLS or unload proof.
          let flags = dynamicFlags meta
              selectedX86 = [(k,v) | (k,v) <- flags, k `elem` x86Tags]
          if any (\(tag,value) -> tag == "FLAGS_1" && "PIE" `elem` words value) flags && elfType meta /= PieExecutable
            then unknown "PIE flag on non-PIE input" else Right ()
          if length (take 17 flags) > 16 || any (\(k,v) -> length (take 65 k) > 64 || length (take 257 v) > 256) flags
            || length (nub (map fst flags)) /= length flags || any (not . allowedFlag) flags
            || (not (null selectedX86) && (machine meta /= X86_64 || length selectedX86 /= 3 || any (\tag -> length (filter ((== tag) . fst) selectedX86) /= 1) x86Tags))
            then unknown "dynamic flag semantics unqualified" else Right ()
          (deps,relations,cost) <- foldl (next objectSearch item) (Right ([],[],count)) (needed meta)
          (allDeps,allRelations,cost') <- case interpreter meta of
            Nothing -> Right (deps,relations,cost)
            Just path -> do
              if invalidPath path then unknown "interpreter path unqualified" else Right ()
              target <- maybe (unknown "interpreter not declared") Right (M.lookup path byPath)
              if elfType (observation target) /= Shared || not (compatible meta (observation target)) then unknown "interpreter ABI mismatch" else Right ()
              Right (target:deps, Edge (inputPath item) path Interpreter : relations,cost)
          go declared byPath seen' (queue ++ reverse allDeps) order' (found ++ reverse allRelations) bytes' cost'
    next objectSearch item acc requested = do
      (pending,relations,count) <- acc
      if null requested || '/' `elem` requested || '$' `elem` requested then unknown "unsupported needed name" else Right ()
      (target,cost) <- select requested count objectSearch
      let source = observation item; provider = observation target
          requirements = [n | group <- versionNeeds source, needFile group == requested, (n,_,_) <- needVersions group]
      if soname provider /= Just requested then unknown "provider SONAME missing or mismatched" else Right ()
      if elfType provider /= Shared || not (compatible source provider) then unknown "provider ABI mismatch" else Right ()
      if any (\v -> not (any ((== v) . defName) (versionDefinitions provider))) requirements then unknown "provider version definition missing" else Right ()
      Right (target:pending,Edge (inputPath item) (inputPath target) (Needed requested):relations,cost)
    select _ count [] = unknown ("declared provider missing after " ++ show count ++ " comparisons")
    select name count (directory:rest) = do
      let cost = count + length inputs
          matches = filter (\i -> searchDirectory i == directory && declaredName i == name) inputs
      if cost < count || cost > maxComparisons limits then unknown "candidate comparison bound" else Right ()
      case matches of
        [] -> select name cost rest
        [x] -> Right (x,cost)
        _ -> unknown "ambiguous declared provider"
