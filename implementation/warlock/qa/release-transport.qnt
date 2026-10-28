module release_transport {
  type State = { canonical: int, link: int, escaped: bool, content: int, kind: int, members: List[int], manifestVersion: int, archiveVersion: int, decision: int, expectedLink: int, snapCanonical: int, snapLink: int, snapExpectedLink: int, snapEscaped: bool, snapContent: int, snapKind: int, snapMembers: List[int], snapVersionsMatch: bool, last: int }
  var s: State
  action init = s' = { canonical: 1, link: 1, escaped: false, content: 1, kind: 1, members: List(1, 2), manifestVersion: 1, archiveVersion: 1, decision: 0, expectedLink: 1, snapCanonical: 1, snapLink: 1, snapExpectedLink: 1, snapEscaped: false, snapContent: 1, snapKind: 1, snapMembers: List(1, 2), snapVersionsMatch: true, last: 0 }
  val eligible = s.canonical == 1 and s.link == s.expectedLink and not(s.escaped) and s.content == 1 and s.kind == 1 and s.members == List(1, 2) and s.manifestVersion == s.archiveVersion
  val acceptedSnapshot = s.decision == 1 implies (s.snapCanonical == 1 and s.snapLink == s.snapExpectedLink and not(s.snapEscaped) and s.snapContent == 1 and s.snapKind == 1 and s.snapMembers == List(1, 2) and s.snapVersionsMatch)
  action alias = s' = { ...s, link: 2, last: 1 }
  action retarget = s' = { ...s, canonical: 2, link: 3, last: 2 }
  action escape = s' = { ...s, escaped: true, last: 3 }
  action duplicate = s' = { ...s, members: List(1, 2, 2), archiveVersion: 2, last: 4 }
  action missing = s' = { ...s, members: List(1), archiveVersion: 2, last: 5 }
  action unexpected = s' = { ...s, members: List(1, 2, 3), archiveVersion: 2, last: 6 }
  action mismatchType = s' = { ...s, kind: 2, archiveVersion: 2, last: 7 }
  action mismatchContent = s' = { ...s, content: 2, archiveVersion: 2, last: 8 }
  action restore = s' = { ...s, canonical: 1, link: 1, escaped: false, content: 1, kind: 1, members: List(1, 2), archiveVersion: 1, expectedLink: 1, last: 9 }
  action refreshAlias = all { s.link == 2, s.canonical == 1, not(s.escaped), s' = { ...s, expectedLink: 2, last: 11 } }
  action audit = s' = { ...s, decision: if (eligible) 1 else 2, snapCanonical: s.canonical, snapLink: s.link, snapExpectedLink: s.expectedLink, snapEscaped: s.escaped, snapContent: s.content, snapKind: s.kind, snapMembers: s.members, snapVersionsMatch: s.manifestVersion == s.archiveVersion, last: 10 }
  action step = any { alias, retarget, escape, duplicate, missing, unexpected, mismatchType, mismatchContent, restore, refreshAlias, audit }
}
