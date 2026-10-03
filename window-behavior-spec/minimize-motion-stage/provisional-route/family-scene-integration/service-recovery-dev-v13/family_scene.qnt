/** Fresh family authority is independent of retained provisional pixels.
 * Each composite scene and metadata reply carries epoch + exact member IDs.
 */
module family_scene {
 type Proof={epoch:int,ids:List[int],scope:Set[int],complete:bool,edges:bool,detached:bool}
 type Image={epoch:int,member:int,id:int,version:int}
 type Frame={epoch:int,output:int,generation:int,scope:Set[int],ids:List[int],versions:List[int]}
 type Event=Reserve|Validate(Proof)|Capture(Image)|Present(Frame)|Commit|Replace(int)|OutputChange|Reduce|Cancel
 type State={epoch:int,ids:List[int],captured:List[int],versions:List[int],scope:Set[int],validated:bool,detachedProof:bool,completeProof:bool,edgeProof:bool,presented:Set[int],generation:int,active:bool,nativeEpoch:int,nativeIds:List[int],nativeScope:Set[int],committed:bool}
 var s:State
 action init=s'={epoch:1,ids:List(1,2),captured:List(1,2),versions:List(11,22),scope:Set(0,1),validated:true,detachedProof:false,completeProof:true,edgeProof:true,presented:Set(),generation:1,active:true,nativeEpoch:0,nativeIds:List(),nativeScope:Set(),committed:false}
 def pixelsCurrent(b:State):bool=b.scope.forall(i=>b.captured.nth(i)==b.ids.nth(i) and b.versions.nth(i)>0)
 def eligible(b:State):bool=b.active and b.validated and b.completeProof and b.edgeProof and pixelsCurrent(b) and b.presented==Set(0,1)
 def retire(b:State):State={...b,active:false,validated:false,presented:Set()}
 action fire(e:Event):bool={
  val b={...s,committed:false}
  s'=match e {
   | Reserve=>if(s.active){...b,epoch:s.epoch+1,validated:false,completeProof:false,edgeProof:false,detachedProof:false,presented:Set()} else b
   | Validate(p)=>if(s.active and p.epoch==s.epoch and p.ids==s.ids and p.complete and p.edges and (p.scope==Set(0,1) or (p.scope==Set(0) and p.detached))) {...b,scope:p.scope,validated:true,completeProof:true,edgeProof:true,detachedProof:p.detached,presented:if(p.scope==s.scope)s.presented else Set()} else b
   | Capture(i)=>if(s.active and i.epoch==s.epoch and i.member>=0 and i.member<2 and i.id==s.ids.nth(i.member) and i.version>0){...b,captured:s.captured.replaceAt(i.member,i.id),versions:s.versions.replaceAt(i.member,i.version),presented:Set()} else b
   | Present(f)=>if(s.active and f.epoch==s.epoch and f.output>=0 and f.output<2 and f.generation==s.generation and f.scope==s.scope and f.ids==s.captured and f.versions==s.versions and pixelsCurrent(s)){...b,presented:s.presented.union(Set(f.output))} else b
   | Commit=>if(eligible(s)){...b,nativeEpoch:s.epoch,nativeIds:s.ids,nativeScope:s.scope,committed:true} else b
   | Replace(i)=>if(i>=0 and i<2){...retire(b),ids:s.ids.replaceAt(i,s.ids.nth(i)+10),captured:s.captured.replaceAt(i,0),versions:s.versions.replaceAt(i,0)} else b
   | OutputChange=>{...retire(b),generation:s.generation+1}
   | Reduce=>retire(b)
   | Cancel=>retire(b)
  }
 }
 val committedHasFreshCompleteAuthority=s.committed implies (eligible(s) and s.nativeEpoch==s.epoch and s.nativeIds==s.ids and s.nativeScope==s.scope)
 val singletonRequiresExplicitFreshDetachment=(s.validated and s.scope==Set(0)) implies (s.detachedProof and s.completeProof and s.edgeProof)
 val replacementNeverInheritsCapturedPixels=s.scope.forall(i=>s.captured.nth(i)==s.ids.nth(i) or (s.captured.nth(i)==0 and s.versions.nth(i)==0))
 val unvalidatedCannotCommit=(not(s.validated)) implies not(s.committed)
 val allProps=committedHasFreshCompleteAuthority and singletonRequiresExplicitFreshDetachment and replacementNeverInheritsCapturedPixels and unvalidatedCannotCommit
 action step={
  val proof={epoch:s.epoch,ids:s.ids,scope:Set(0,1),complete:true,edges:true,detached:false}
  val frame={epoch:s.epoch,output:0,generation:s.generation,scope:s.scope,ids:s.captured,versions:s.versions}
  val image={epoch:s.epoch,member:0,id:s.ids.nth(0),version:s.epoch+100}
  nondet e=Set(Reserve,Validate(proof),Validate({...proof,epoch:s.epoch-1}),Validate({...proof,complete:false,scope:Set(0)}),Validate({...proof,scope:Set(0)}),Validate({...proof,scope:Set(0),detached:true}),Validate({...proof,edges:false}),Capture(image),Capture({...image,id:s.ids.nth(0)-10}),Present(frame),Present({...frame,output:1}),Present({...frame,epoch:s.epoch-1}),Present({...frame,ids:List(99,99)}),Commit,Replace(0),Replace(1),OutputChange,Reduce,Cancel).oneOf();fire(e)
 }
}
