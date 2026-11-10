'use strict';
// Controlled DOM patterned after qa/ui-http.cjs; no browser, native input or AT evidence.
const fs = require('node:fs'), vm = require('node:vm');
const path = require('node:path');
const compiled = path.join(__dirname, '../assets/workspace-unsupported-dom.js');
if (process.argv.length !== 2) throw Error('Fixed fixture takes no arguments');
class Node {
  constructor(type,name,text='') { this.nodeType=type; this.tagName=name; this.nodeName=name; this.data=text; this.nodeValue=text; this.parentNode=null; this.childNodes=[]; this.attributes={}; this.listeners={}; this.style={setProperty(k,v){this[k]=v;},removeProperty(k){delete this[k];}}; }
  get textContent(){return this.nodeType===3?this.data:this.childNodes.map(x=>x.textContent).join('');}
  set textContent(value){if(this.nodeType===3){this.data=String(value);this.nodeValue=this.data;}else{this.childNodes=[];if(value)this.appendChild(new Node(3,'#text',String(value)));}}
  appendChild(child){return this.insertBefore(child,null);}
  insertBefore(child,before){if(child.nodeType===11){for(const item of [...child.childNodes])this.insertBefore(item,before);return child;}if(child.parentNode)child.parentNode.removeChild(child);let i=before?this.childNodes.indexOf(before):-1;if(i<0)i=this.childNodes.length;this.childNodes.splice(i,0,child);child.parentNode=this;return child;}
  removeChild(child){const i=this.childNodes.indexOf(child);if(i<0)throw Error('Missing DOM child');this.childNodes.splice(i,1);child.parentNode=null;return child;}
  replaceChild(child,old){this.insertBefore(child,old);this.removeChild(old);return old;}
  replaceData(_offset,_count,value){this.data=String(value);this.nodeValue=this.data;}
  setAttribute(k,v){this.attributes[k]=String(v);}
  setAttributeNS(_ns,k,v){this.setAttribute(k,v);}
  getAttribute(k){return this.attributes[k]??null;}
  removeAttribute(k){delete this.attributes[k];}
  removeAttributeNS(_ns,k){this.removeAttribute(k);}
  addEventListener(k,fn){this.listeners[k]=fn;}
  removeEventListener(k,fn){if(this.listeners[k]===fn)delete this.listeners[k];}
  focus(){this.focused=true;}
}
function collect(node,predicate){return (predicate(node)?[node]:[]).concat(node.childNodes.flatMap(child=>collect(child,predicate)));}
const timers=new Map();let serial=0;
const later=(fn,delay=0)=>{const id=++serial;timers.set(id,{fn,delay});return id;};
const cancel=id=>timers.delete(id);
const container=new Node(1,'DIV'),mount=new Node(3,'#text','');container.appendChild(mount);
const document={body:container,documentElement:container,createTextNode:t=>new Node(3,'#text',String(t)),createElement:t=>new Node(1,t.toUpperCase()),createElementNS:(_ns,t)=>new Node(1,t.toUpperCase()),createDocumentFragment:()=>new Node(11,'#document-fragment'),addEventListener(){},removeEventListener(){}};
const window={document,addEventListener(){},removeEventListener(){},requestAnimationFrame:fn=>later(fn,0),cancelAnimationFrame:cancel};
const sandbox={console,document,window,setTimeout:later,clearTimeout:cancel,requestAnimationFrame:window.requestAnimationFrame,cancelAnimationFrame:cancel};
const checks={};
function check(name,value){checks[name]=value===true;}
async function flush(){for(let round=0;round<12;round++){for(const [id,row] of [...timers])if(row.delay<=0){timers.delete(id);row.fn();}await new Promise(resolve=>setImmediate(resolve));}}
async function main(){
  vm.createContext(sandbox);vm.runInContext(fs.readFileSync(compiled,'utf8'),sandbox,{timeout:2000});
  const app=sandbox.Elm.WorkspaceUnsupportedDomReplay.init({node:mount,flags:null}),messages=[];
  app.ports.outgoing.subscribe(value=>messages.push(JSON.parse(JSON.stringify(value))));
  await flush();
  const rows=collect(container,n=>n.attributes && n.attributes['data-surface-control']);
  const cases=[['overview:workspace-create','Create workspace'],['overview:workspace-delete','Delete workspace'],['overview:workspace-rename','Rename workspace']];
  const find=id=>rows.filter(n=>n.attributes['data-surface-control']===id);
  const wanted=['control:close','overview:all',...cases.map(x=>x[0])];
  check('literalOrder',JSON.stringify(rows.map(n=>n.attributes['data-surface-control']).filter(id=>wanted.includes(id)))===JSON.stringify(wanted));
  for(const [id,label] of cases){
    const matches=find(id),node=matches[0];
    const parts=node?collect(node,n=>n.className==='control-label'||n.attributes?.class==='control-label'):[];
    const detail=node?collect(node,n=>n.className==='control-detail'||n.attributes?.class==='control-detail'):[];
    check(id+'/identity',matches.length===1 && node.tagName==='BUTTON');
    check(id+'/label',parts.length===1 && parts[0].textContent===label && node.attributes['aria-label']===label+'; unavailable');
    check(id+'/detail',detail.length===1 && detail[0].textContent==='Not supported');
    check(id+'/disabledRole',node.disabled===true && node.attributes['aria-disabled']==='true' && node.attributes.role==='button' && node.attributes['data-focus-only']==='false');
    check(id+'/noClickHandler',!Object.hasOwn(node.listeners,'click'));
  }
  const close=find('control:close'),button=close[0];
  check('closeContrast',close.length===1 && button.tagName==='BUTTON' && button.disabled===false && button.attributes['aria-disabled']==='false' && button.attributes['aria-label']==='Close Task View and return to windows' && typeof button.listeners.click==='function');
  app.ports.probe.send(null);await flush();
  check('packetAndStale',messages.length===1 && JSON.stringify(messages[0])===JSON.stringify({kind:'probe',snapshotChecks:true,sourceChecks:true,rowChecks:true,staleChecks:true}));
  if(button && typeof button.listeners.click==='function')button.listeners.click({});
  await flush();
  const expected={kind:'tap',action:{surface:'popup',surfaceProtocol:2,kind:'surface-action',publication:'1',lease:'1',id:'control:close'}};
  check('oneCloseAfterRefusal',messages.length===2 && JSON.stringify(messages[1])===JSON.stringify(expected));
  const names=['literalOrder',...cases.flatMap(([id])=>['identity','label','detail','disabledRole','noClickHandler'].map(k=>id+'/'+k)),'closeContrast','packetAndStale','oneCloseAfterRefusal'];
  if(JSON.stringify(Object.keys(checks))!==JSON.stringify(names)||names.some(name=>checks[name]!==true))throw Error('DOM checks differ: '+JSON.stringify(checks));
  process.stdout.write(JSON.stringify({classification:'CONTROLLED_DOM_GREEN',checks,names,nativeAcceptance:false,originalAcceptance:false})+'\n');
}
main().catch(error=>{console.error(String(error.stack||error));process.exitCode=1;});
