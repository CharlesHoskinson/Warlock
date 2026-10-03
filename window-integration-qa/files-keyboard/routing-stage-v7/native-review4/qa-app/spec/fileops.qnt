// fileops.qnt — formal model of ~/.local/share/omarchy-files/scripts/ops.sh
//
// The file system is a map Path -> Node. Every ops.sh invocation is one step:
// it always runs and returns an exit code, so each action computes (next fs,
// exit code) with pure functions. A failing invocation is a real, observable
// transition (the explorer reacts to its exit code) — not a no-op fallback.
//
// `asRoot` models running the operation as root (sudo / elevated): permission
// checks are bypassed, everything else is identical.
//
// The state records the exact call (lastCall) and its outcome (lastCode,
// lastCreated) so `quint run --mbt` traces can be replayed against the real
// script by spec/mbt.py.
module fileops {

  // ------------------------------------------------------------------ types
  type Kind = File | Dir

  // A file name, kept structured so the collision rule is exact without string
  // ops: rendered as  base + " (copy)" / " (copy k)" per entry + ext.
  type Name = { base: str, ext: str, copies: List[int] }
  type Path = List[Name]                     // List() is the sandbox root

  // locked = folder without write permission (chmod 555); files ignore it
  type Node = { kind: Kind, content: int, locked: bool }

  type TrashEntry = { id: int, orig: Path, rel: Path, node: Node }

  type Call = { op: str, dst: Path, srcs: List[Path], name: Name, asRoot: bool }

  // Exit codes (must match ops.sh)
  pure val OK = 0
  pure val FAIL = 1
  pure val EXISTS = 2
  pure val INTO_SELF = 3
  pure val INVALID = 4
  pure val DENIED = 13

  // ------------------------------------------------------------- constants
  pure def nm(b: str, e: str): Name = { base: b, ext: e, copies: List() }
  pure val DOCS = nm("docs", "")
  pure val LOCKED = nm("locked", "")
  pure val SUB = nm("d", "")
  pure val A = nm("a", ".txt")
  pure val B = nm("b", "")
  pure val C = nm("c", "")
  pure val BAD = nm("bad/name", "")           // invalid: contains a slash
  pure val NEW_NAMES = Set(nm("n", ""), nm("n", ".md"), BAD, A)
  pure val MISSING: Path = List(nm("zz", ""))

  pure val ROOT: Path = List()
  pure val dirNode = { kind: Dir, content: 0, locked: false }
  pure def fileNode(c: int): Node = { kind: File, content: c, locked: false }

  // Initial tree:  /docs/a.txt (1)  /docs/d/b (2)  /locked/ (555) with c (3)
  pure val INIT_FS: Path -> Node = Map(
    ROOT -> dirNode,
    List(DOCS) -> dirNode,
    List(DOCS, A) -> fileNode(1),
    List(DOCS, SUB) -> dirNode,
    List(DOCS, SUB, B) -> fileNode(2),
    List(LOCKED) -> { ...dirNode, locked: true },
    List(LOCKED, C) -> fileNode(3),
  )
  pure val ORIGINAL_CONTENTS = Set(1, 2, 3)

  // ------------------------------------------------------------ path utils
  pure def has(fs: Path -> Node, p: Path): bool = fs.keys().contains(p)
  pure def parent(p: Path): Path = p.slice(0, p.length() - 1)
  pure def last(p: Path): Name = p[p.length() - 1]
  pure def isPrefix(a: Path, b: Path): bool =
    a.length() <= b.length() and b.slice(0, a.length()) == a
  pure def reroot(p: Path, src: Path, dst: Path): Path = dst.concat(p.slice(src.length(), p.length()))
  pure def subtree(fs: Path -> Node, src: Path): Set[Path] = fs.keys().filter(p => isPrefix(src, p))
  pure def isDir(fs: Path -> Node, p: Path): bool = has(fs, p) and fs.get(p).kind == Dir
  pure def validName(n: Name): bool = n != BAD
  // writable folder (root may write anywhere)
  pure def canWrite(fs: Path -> Node, p: Path, asRoot: bool): bool =
    isDir(fs, p) and (asRoot or not(fs.get(p).locked))

  // first free name in dir: n itself, else n + (copy), (copy 2), ...
  pure def withCopy(n: Name, k: int): Name = { ...n, copies: n.copies.append(k) }
  pure def uniq(fs: Path -> Node, dir: Path, n: Name): Name =
    if (not(has(fs, dir.append(n)))) n
    else {
      val free = 1.to(12).filter(k => not(has(fs, dir.append(withCopy(n, k)))))
      withCopy(n, free.fold(99, (m, k) => if (k < m) k else m))
    }

  // ------------------------------------------------- functional core (pure)
  type St = { fs: Path -> Node, trash: Set[TrashEntry], seq: int, code: int, created: Path }

  pure def mkSt(fs: Path -> Node, trash: Set[TrashEntry], seq: int): St =
    { fs: fs, trash: trash, seq: seq, code: OK, created: ROOT }
  pure def withCode(s: St, c: int): St = { ...s, code: c }

  // copy / move of the subtree at src to dst (dst must be fresh)
  pure def copyTree(fs: Path -> Node, src: Path, dst: Path): Path -> Node =
    fs.keys().union(subtree(fs, src).map(p => reroot(p, src, dst)))
      .mapBy(k => if (has(fs, k)) fs.get(k) else fs.get(reroot(k, dst, src)))
  pure def removeTree(fs: Path -> Node, src: Path): Path -> Node =
    fs.keys().filter(p => not(isPrefix(src, p))).mapBy(k => fs.get(k))

  // one item of copy/move, following ops.sh's check order
  pure def xferItem(s: St, move: bool, dest: Path, src: Path, asRoot: bool): St =
    if (s.code != OK) s
    else if (not(has(s.fs, src)) or src == ROOT) withCode(s, FAIL)
    else if (isDir(s.fs, src) and isPrefix(src, dest)) withCode(s, INTO_SELF)
    else if (move and parent(src) == dest) s                                  // already there
    else if (move and not(canWrite(s.fs, parent(src), asRoot))) withCode(s, DENIED)
    else if (move and isDir(s.fs, src) and not(canWrite(s.fs, src, asRoot))) withCode(s, DENIED)
    else if (not(canWrite(s.fs, dest, asRoot))) withCode(s, DENIED)
    else {
      val t = dest.append(uniq(s.fs, dest, last(src)))
      val copied = copyTree(s.fs, src, t)
      { ...s, fs: if (move) removeTree(copied, src) else copied }
    }

  pure def execXfer(s: St, move: bool, dest: Path, srcs: List[Path], asRoot: bool): St =
    if (not(isDir(s.fs, dest))) withCode(s, FAIL)
    else srcs.foldl(s, (acc, src) => xferItem(acc, move, dest, src, asRoot))

  pure def execCreate(s: St, dir: bool, parentDir: Path, n: Name, asRoot: bool): St =
    if (not(validName(n))) withCode(s, INVALID)
    else if (not(isDir(s.fs, parentDir))) withCode(s, FAIL)
    else if (not(canWrite(s.fs, parentDir, asRoot))) withCode(s, DENIED)
    else {
      val t = parentDir.append(uniq(s.fs, parentDir, n))
      { ...s, fs: s.fs.put(t, if (dir) dirNode else fileNode(0)), created: t }
    }

  pure def execRename(s: St, src: Path, n: Name, asRoot: bool): St =
    if (not(validName(n))) withCode(s, INVALID)
    else if (not(has(s.fs, src)) or src == ROOT) withCode(s, FAIL)
    else if (last(src) == n) s
    else if (not(canWrite(s.fs, parent(src), asRoot))) withCode(s, DENIED)
    else if (has(s.fs, parent(src).append(n))) withCode(s, EXISTS)
    else {
      val t = parent(src).append(n)
      { ...s, fs: removeTree(copyTree(s.fs, src, t), src) }
    }

  pure def trashItem(s: St, p: Path, asRoot: bool): St =
    if (s.code != OK) s
    else if (not(has(s.fs, p)) or p == ROOT) withCode(s, FAIL)
    else if (not(canWrite(s.fs, parent(p), asRoot))) withCode(s, DENIED)
    else if (isDir(s.fs, p) and not(canWrite(s.fs, p, asRoot))) withCode(s, DENIED)
    else {
      val entries = subtree(s.fs, p).map(q => { id: s.seq, orig: p, rel: q.slice(p.length(), q.length()), node: s.fs.get(q) })
      { ...s, fs: removeTree(s.fs, p), trash: s.trash.union(entries), seq: s.seq + 1 }
    }

  pure def execTrash(s: St, paths: List[Path], asRoot: bool): St =
    paths.foldl(s, (acc, p) => trashItem(acc, p, asRoot))

  // ------------------------------------------------------------ state machine
  var fs: Path -> Node
  var trash: Set[TrashEntry]
  var trashSeq: int
  var lastCall: Call
  var lastCode: int
  var lastCreated: Path
  // ghost: previous tree, for transition invariants
  var prevFs: Path -> Node

  pure val NO_CALL: Call = { op: "init", dst: ROOT, srcs: List(), name: nm("", ""), asRoot: false }

  action init = all {
    fs' = INIT_FS, trash' = Set(), trashSeq' = 0,
    lastCall' = NO_CALL, lastCode' = OK, lastCreated' = ROOT, prevFs' = INIT_FS,
  }

  action commit(call: Call, r: St): bool = all {
    fs' = r.fs, trash' = r.trash, trashSeq' = r.seq,
    lastCall' = call, lastCode' = r.code,
    lastCreated' = if (r.code == OK) r.created else ROOT,
    prevFs' = fs,
  }

  def cur: St = mkSt(fs, trash, trashSeq)

  action doCopy(dst: Path, srcs: List[Path], asRoot: bool): bool =
    commit({ op: "copy", dst: dst, srcs: srcs, name: nm("", ""), asRoot: asRoot }, execXfer(cur, false, dst, srcs, asRoot))
  action doMove(dst: Path, srcs: List[Path], asRoot: bool): bool =
    commit({ op: "move", dst: dst, srcs: srcs, name: nm("", ""), asRoot: asRoot }, execXfer(cur, true, dst, srcs, asRoot))
  action doMkdir(dir: Path, n: Name, asRoot: bool): bool =
    commit({ op: "mkdir", dst: dir, srcs: List(), name: n, asRoot: asRoot }, execCreate(cur, true, dir, n, asRoot))
  action doNewfile(dir: Path, n: Name, asRoot: bool): bool =
    commit({ op: "newfile", dst: dir, srcs: List(), name: n, asRoot: asRoot }, execCreate(cur, false, dir, n, asRoot))
  action doRename(src: Path, n: Name, asRoot: bool): bool =
    commit({ op: "rename", dst: ROOT, srcs: List(src), name: n, asRoot: asRoot }, execRename(cur, src, n, asRoot))
  action doTrash(paths: List[Path], asRoot: bool): bool =
    commit({ op: "trash", dst: ROOT, srcs: paths, name: nm("", ""), asRoot: asRoot }, execTrash(cur, paths, asRoot))

  action step = {
    // arguments are drawn from what exists, plus a missing path and the root
    val items = fs.keys().exclude(Set(ROOT)).union(Set(MISSING))
    val dirs = fs.keys().filter(p => isDir(fs, p)).union(Set(MISSING, List(DOCS, A)))
    nondet dst = dirs.oneOf()
    nondet s1 = items.oneOf()
    nondet s2 = items.oneOf()
    nondet two = Set(true, false).oneOf()
    nondet n = NEW_NAMES.union(fs.keys().exclude(Set(ROOT)).map(p => last(p))).oneOf()
    nondet asRoot = Set(true, false).oneOf()
    val srcs = if (two) List(s1, s2) else List(s1)   // may repeat: "copy dst a a" is legal
    any {
      doCopy(dst, srcs, asRoot),
      doMove(dst, srcs, asRoot),
      doMkdir(dst, n, asRoot),
      doNewfile(dst, n, asRoot),
      doRename(s1, n, asRoot),
      doTrash(srcs, asRoot),
    }
  }

  // --------------------------------------------------------------- invariants
  // tree stays well formed: root exists, every item's parent is an existing folder
  val wellFormed: bool =
    isDir(fs, ROOT) and fs.keys().forall(p => p == ROOT or isDir(fs, parent(p)))

  // nothing is ever lost: every original file content is still somewhere
  // (in the tree or in the trash)
  val noDataLoss: bool =
    ORIGINAL_CONTENTS.forall(c =>
      fs.keys().exists(p => fs.get(p).kind == File and fs.get(p).content == c)
      or trash.exists(e => e.node.kind == File and e.node.content == c))

  // never overwrite: anything that existed before and still exists is unchanged
  val noOverwrite: bool =
    prevFs.keys().intersect(fs.keys()).forall(p => prevFs.get(p) == fs.get(p))

  // a single-item operation that fails changes nothing
  val failureIsAtomic: bool =
    (lastCode != OK and lastCall.srcs.length() <= 1) implies (fs == prevFs)

  // without root, nothing is added to or removed from a locked folder that stays
  // put. (Renaming a locked folder itself is allowed — its parent is what must be
  // writable — and its contents simply travel with it.)
  pure def lockedIn(t: Path -> Node, p: Path): bool = isDir(t, p) and t.get(p).locked
  val lockedRespected: bool =
    lastCall.asRoot or {
      val removed = prevFs.keys().exclude(fs.keys())
      val added = fs.keys().exclude(prevFs.keys())
      removed.forall(p => not(lockedIn(prevFs, parent(p)) and has(fs, parent(p))))
      and added.forall(p => not(lockedIn(fs, parent(p)) and has(prevFs, parent(p))))
    }

  // created paths are reported and exist
  val createdExists: bool =
    (lastCreated != ROOT) implies has(fs, lastCreated)

  val allInvariants: bool =
    wellFormed and noDataLoss and noOverwrite and failureIsAtomic and lockedRespected and createdExists

  // ---------------------------------------------------------------- witnesses
  val wCopyOk: bool = lastCall.op == "copy" and lastCode == OK and fs != prevFs
  val wCopyCollision: bool = lastCall.op == "copy" and lastCode == OK and fs.keys().exists(p => p.length() > 0 and last(p).copies.length() > 0)
  val wMoveDir: bool = lastCall.op == "move" and lastCode == OK and lastCall.srcs.length() > 0 and isDir(prevFs, lastCall.srcs[0]) and fs != prevFs
  val wIntoSelf: bool = lastCode == INTO_SELF
  val wMkdirOk: bool = lastCall.op == "mkdir" and lastCode == OK
  val wNewfileOk: bool = lastCall.op == "newfile" and lastCode == OK
  val wNewfileCopyName: bool = lastCall.op == "newfile" and lastCode == OK and last(lastCreated).copies.length() > 0
  val wRenameOk: bool = lastCall.op == "rename" and lastCode == OK and fs != prevFs
  val wRenameExists: bool = lastCode == EXISTS
  val wInvalid: bool = lastCode == INVALID
  val wDenied: bool = lastCode == DENIED
  val wRootInLocked: bool = lastCall.asRoot and lastCode == OK and lastCall.dst == List(LOCKED) and fs != prevFs
  val wTrashOk: bool = lastCall.op == "trash" and lastCode == OK
  val wSecondCopy: bool = fs.keys().exists(p => p.length() > 0 and last(p).copies.indices().exists(i => last(p).copies[i] >= 2))
  val wPartial: bool = lastCode != OK and fs != prevFs
}
