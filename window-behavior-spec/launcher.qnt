/** App taskbar indicators: incremental fields, independent publishers, and
 * cleanup on sender disconnect. Progress is discretized into 0, 1/2, 1. */
module launcher {
  type Entry = { count: int, countVisible: bool, progress: int, progressVisible: bool,
                 urgent: bool, updating: bool, quicklist: int, serial: int }
  type Event = Count((int,int,int)) | CountVisible((int,int,bool))
    | Progress((int,int,int)) | ProgressVisible((int,int,bool))
    | Urgent((int,int,bool)) | Updating((int,int,bool)) | Quicklist((int,int,int)) | Disconnect(int) | Connect(int)
  pure val SENDERS = Set(1,2)
  pure val APPS = Set(1,2)
  pure val EMPTY = {count:0, countVisible:false, progress:0, progressVisible:false,
                    urgent:false, updating:false, quicklist:0, serial:0}
  var connected: Set[int]
  var entries: (int,int) -> Entry
  var serial: int
  var lastEvent: Event
  pure def key(e: Event): (int,int) = match e {
    | Count(t) => (t._1,t._2) | CountVisible(t) => (t._1,t._2)
    | Progress(t) => (t._1,t._2) | ProgressVisible(t) => (t._1,t._2)
    | Urgent(t) => (t._1,t._2) | Updating(t) => (t._1,t._2)
    | Quicklist(t) => (t._1,t._2)
    | Disconnect(s) => (s,0) | Connect(s) => (s,0)
  }
  def previous(e: Event): Entry = if (entries.keys().contains(key(e))) entries.get(key(e)) else EMPTY
  def changed(e: Event): Entry = match e {
    | Count(t) => {...previous(e),count:t._3}
    | CountVisible(t) => {...previous(e),countVisible:t._3}
    | Progress(t) => {...previous(e),progress:t._3}
    | ProgressVisible(t) => {...previous(e),progressVisible:t._3}
    | Urgent(t) => {...previous(e),urgent:t._3}
    | Updating(t) => {...previous(e),updating:t._3}
    | Quicklist(t) => {...previous(e),quicklist:t._3}
    | _ => previous(e)
  }
  def canFire(e: Event): bool = match e {
    | Connect(s) => not(connected.contains(s))
    | Disconnect(s) => connected.contains(s)
    | _ => connected.contains(key(e)._1)
  }
  def updates(e: Event): bool = match e {
    | Connect(_) => false | Disconnect(_) => false
    | _ => not(entries.keys().contains(key(e))) or changed(e) != previous(e)
  }
  def selected(app: int): Entry = entries.keys().filter(k => k._2 == app)
    .fold(EMPTY, (best,k) => if(entries.get(k).serial > best.serial) entries.get(k) else best)
  def badge(app: int): int = if (selected(app).countVisible) selected(app).count else 0
  def progress(app: int): int = if (selected(app).progressVisible) selected(app).progress else -1
  action init = all { connected'=SENDERS, entries'=Map(), serial'=0, lastEvent'=Connect(1) }
  action fire(e: Event): bool = all {
    canFire(e),
    connected' = match e { | Connect(s) => connected.union(Set(s))
      | Disconnect(s) => connected.exclude(Set(s)) | _ => connected },
    entries' = match e {
      | Disconnect(s) => entries.keys().filter(k => k._1 != s).mapBy(k => entries.get(k))
      | _ => if (updates(e)) entries.put(key(e),{...changed(e),serial:serial+1}) else entries
    },
    serial' = if (updates(e)) serial+1 else serial,
    lastEvent'=e,
  }
  pure val EVENTS = tuples(SENDERS,APPS,Set(0,1,2)).map(t => Count(t))
    .union(tuples(SENDERS,APPS,Set(0,1,2)).map(t => Progress(t)))
    .union(tuples(SENDERS,APPS,Set(true,false)).map(t => CountVisible(t)))
    .union(tuples(SENDERS,APPS,Set(true,false)).map(t => ProgressVisible(t)))
    .union(tuples(SENDERS,APPS,Set(true,false)).map(t => Urgent(t)))
    .union(tuples(SENDERS,APPS,Set(true,false)).map(t => Updating(t)))
    .union(tuples(SENDERS,APPS,Set(0,1,2)).map(t => Quicklist(t)))
    .union(SENDERS.map(s => Connect(s))).union(SENDERS.map(s => Disconnect(s)))
  action step = { nondet e=EVENTS.filter(e => canFire(e)).oneOf(); fire(e) }
  val allProps = entries.keys().forall(k => connected.contains(k._1) and APPS.contains(k._2)
      and entries.get(k).serial > 0 and entries.get(k).serial <= serial)
    and APPS.forall(app => badge(app) >= 0 and badge(app) <= 2
      and progress(app) >= -1 and progress(app) <= 2)
}
