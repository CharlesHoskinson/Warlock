module data_provenance_proposal {
 type Witness = {ownedConsumer:bool,ownedCompositor:bool,privatePeer:bool,sameLifetime:bool,fdStable:bool,sameInodeDevice:bool,ownedUid:bool,regular:bool,privateMode:bool,unlinked:bool,tmpfs:bool,uuidName:bool,readOnlyVma:bool,noExecutableAlias:bool,boundedSize:bool,sourcePinned:bool,offsetBounds:bool,unambiguousMount:bool,readOnlyProducer:bool}
 var observed: Witness
 var accepted: bool
 pure val blank={ownedConsumer:false,ownedCompositor:false,privatePeer:false,sameLifetime:false,fdStable:false,sameInodeDevice:false,ownedUid:false,regular:false,privateMode:false,unlinked:false,tmpfs:false,uuidName:false,readOnlyVma:false,noExecutableAlias:false,boundedSize:false,sourcePinned:false,offsetBounds:false,unambiguousMount:false,readOnlyProducer:false}
 pure def authority(w:Witness):bool = w.ownedConsumer and w.ownedCompositor and w.privatePeer and w.sameLifetime and w.fdStable and w.sameInodeDevice and w.ownedUid and w.regular and w.privateMode and w.unlinked and w.tmpfs and w.uuidName and w.readOnlyVma and w.noExecutableAlias and w.boundedSize and w.sourcePinned and w.offsetBounds and w.unambiguousMount and w.readOnlyProducer
 action init=all{observed'=blank,accepted'=false}
 action observe(w:Witness):bool=all{observed'=w,accepted'=authority(w)}
 val exactProducer=accepted implies observed.ownedCompositor and observed.privatePeer and observed.sameLifetime and observed.fdStable and observed.sameInodeDevice
 val onlyNonExecutableData=accepted implies observed.readOnlyVma and observed.noExecutableAlias and observed.regular and observed.tmpfs
 val ownedUnlinkedPrivateData=accepted implies observed.ownedUid and observed.privateMode and observed.unlinked and observed.uuidName and observed.ownedConsumer
 val evidenceRequired=accepted implies observed.boundedSize and observed.sourcePinned and observed.offsetBounds and observed.unambiguousMount and observed.readOnlyProducer
 val allProps=exactProducer and onlyNonExecutableData and ownedUnlinkedPrivateData and evidenceRequired
 action step={
  nondet own=Bool.oneOf();nondet comp=Bool.oneOf();nondet peer=Bool.oneOf();nondet life=Bool.oneOf();nondet fd=Bool.oneOf();nondet inode=Bool.oneOf();nondet uid=Bool.oneOf();nondet regular=Bool.oneOf()
  nondet mode=Bool.oneOf();nondet unlink=Bool.oneOf();nondet tmpfs=Bool.oneOf();nondet uuid=Bool.oneOf();nondet readonly=Bool.oneOf();nondet noexec=Bool.oneOf();nondet bound=Bool.oneOf();nondet source=Bool.oneOf();nondet offset=Bool.oneOf();nondet mount=Bool.oneOf();nondet rofd=Bool.oneOf()
  observe({ownedConsumer:own,ownedCompositor:comp,privatePeer:peer,sameLifetime:life,fdStable:fd,sameInodeDevice:inode,ownedUid:uid,regular:regular,privateMode:mode,unlinked:unlink,tmpfs:tmpfs,uuidName:uuid,readOnlyVma:readonly,noExecutableAlias:noexec,boundedSize:bound,sourcePinned:source,offsetBounds:offset,unambiguousMount:mount,readOnlyProducer:rofd})
 }
}
