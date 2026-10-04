'use strict';
const app = Elm.Bar.init({node:document.getElementById('app')});
const post = value => window.webkit.messageHandlers.native.postMessage(JSON.stringify(value));
window.receivePresentation = value => {
  app.ports.presentation.send(value);
  requestAnimationFrame(() => requestAnimationFrame(() => {
    const node=document.querySelector('.surface-bar');
    if (node?.dataset.publication===value.publication && node.dataset.lease===value.lease) {
      post({surfaceProtocol:2,kind:'presentation-applied',publication:value.publication,lease:value.lease});
    }
  }));
};
window.receiveFocus = value => requestAnimationFrame(() => {
  const node=document.querySelector('.surface-bar');
  if(value.surfaceProtocol!==2 || value.kind!=='surface-focus' || !node || node.dataset.publication!==value.publication || node.dataset.lease!==value.lease) return;
  const focused=[];
  for (const target of value.targets) {
    const control=document.getElementById(target);
    if(control && node.contains(control) && !control.disabled){control.focus();if(document.activeElement===control) focused.push(target);}
  }
  post({surfaceProtocol:2,kind:'focus-applied',publication:value.publication,lease:value.lease,targets:focused});
});
app.ports.actions.subscribe(post);
post({surfaceProtocol:2,kind:'presentation-ready'});

if (window.elmHostQA) {
  let last='';
  const observe=()=>requestAnimationFrame(()=>{
    const buttons=[...document.querySelectorAll('button')].map(button=>{
      const r=button.getBoundingClientRect();return {id:button.id,label:button.textContent,accessibleName:button.getAttribute('aria-label'),disabled:button.disabled,x:r.x,y:r.y,width:r.width,height:r.height};
    });
    const node=document.querySelector('.surface-bar,.surface-bar');
    const body={publication:node?.dataset.publication||null,lease:node?.dataset.lease||null,buttons,focus:document.activeElement?.id||'',text:document.body.innerText};
    const current=JSON.stringify(body);if(current!==last){last=current;post({kind:'surface-report',body});}
  });
  document.addEventListener('scroll',observe,true);
  new MutationObserver(observe).observe(document.body,{subtree:true,childList:true,attributes:true});
  document.addEventListener('focusin',observe);observe();
}

// Qualification instrumentation is confined to the trusted QA launch mode.
if (window.elmHostQA) (async () => {
  const body={secureContext:window.isSecureContext,webgpu:{exposed:Boolean(navigator.gpu)},webgl:{},resourcesRetired:false};
  const canvas=document.createElement('canvas');canvas.width=32;canvas.height=32;
  canvas.style.cssText='position:fixed;right:4px;top:8px;width:32px;height:32px;pointer-events:none;z-index:9999';
  canvas.setAttribute('aria-hidden','true');document.body.appendChild(canvas);
  const gl=canvas.getContext('webgl',{preserveDrawingBuffer:true,antialias:false,alpha:false});
  try {
    if (!gl) throw Error('No WebGL context');
    const debug=gl.getExtension('WEBGL_debug_renderer_info');
    body.webgl={version:gl.getParameter(gl.VERSION),vendor:gl.getParameter(gl.VENDOR),renderer:gl.getParameter(gl.RENDERER),unmaskedVendor:debug?gl.getParameter(debug.UNMASKED_VENDOR_WEBGL):null,unmaskedRenderer:debug?gl.getParameter(debug.UNMASKED_RENDERER_WEBGL):null};
    const shader=(kind,source)=>{const s=gl.createShader(kind);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s;};
    const vertex=shader(gl.VERTEX_SHADER,'attribute vec2 p;void main(){gl_Position=vec4(p,0.0,1.0);}');
    const fragment=shader(gl.FRAGMENT_SHADER,'precision mediump float;void main(){gl_FragColor=vec4(17.0/255.0,193.0/255.0,71.0/255.0,1.0);}');
    const program=gl.createProgram();gl.attachShader(program,vertex);gl.attachShader(program,fragment);gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(program));
    const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,3,-1,-1,3]),gl.STATIC_DRAW);gl.useProgram(program);
    const attribute=gl.getAttribLocation(program,'p');gl.enableVertexAttribArray(attribute);gl.vertexAttribPointer(attribute,2,gl.FLOAT,false,0,0);gl.viewport(0,0,32,32);gl.drawArrays(gl.TRIANGLES,0,3);gl.finish();
    const pixel=new Uint8Array(4);gl.readPixels(16,16,1,1,gl.RGBA,gl.UNSIGNED_BYTE,pixel);
    body.webgl.pixel=Array.from(pixel);body.webgl.error=gl.getError();
    gl.deleteBuffer(buffer);gl.deleteProgram(program);gl.deleteShader(vertex);gl.deleteShader(fragment);body.resourcesRetired=true;
  } catch(error) {body.webgl.failure=String(error);}
  if(navigator.gpu) {
    let device;const allocated=[];
    try {
      const timeout=new Promise((_,reject)=>setTimeout(()=>reject(Error('WebGPU probe deadline')),1500));
      await Promise.race([(async()=>{
        const adapter=await navigator.gpu.requestAdapter();if(!adapter){body.webgpu.status='no-adapter';return;}
        const info=adapter.info||{};body.webgpu.adapter={vendor:info.vendor||'',architecture:info.architecture||'',device:info.device||'',description:info.description||'',fallback:adapter.isFallbackAdapter??null};
        device=await adapter.requestDevice();device.pushErrorScope('validation');
        const result=device.createBuffer({size:4,usage:GPUBufferUsage.STORAGE|GPUBufferUsage.COPY_SRC});const read=device.createBuffer({size:4,usage:GPUBufferUsage.COPY_DST|GPUBufferUsage.MAP_READ});allocated.push(result,read);
        const module=device.createShaderModule({code:'@group(0) @binding(0) var<storage,read_write> value: array<u32>; @compute @workgroup_size(1) fn main(){value[0]=42u;}'});
        const pipeline=device.createComputePipeline({layout:'auto',compute:{module,entryPoint:'main'}});const group=device.createBindGroup({layout:pipeline.getBindGroupLayout(0),entries:[{binding:0,resource:{buffer:result}}]});
        const encoder=device.createCommandEncoder();const pass=encoder.beginComputePass();pass.setPipeline(pipeline);pass.setBindGroup(0,group);pass.dispatchWorkgroups(1);pass.end();encoder.copyBufferToBuffer(result,0,read,0,4);device.queue.submit([encoder.finish()]);await read.mapAsync(GPUMapMode.READ);body.webgpu.value=new Uint32Array(read.getMappedRange())[0];read.unmap();
        const validation=await device.popErrorScope();body.webgpu.validation=validation?String(validation):null;body.webgpu.status='executed';
      })(),timeout]);
    } catch(error){body.webgpu.status='failed';body.webgpu.failure=String(error);}
    finally {for(const resource of allocated)resource.destroy();device?.destroy();}
  } else body.webgpu.status='unavailable';
  await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
  const rect=canvas.getBoundingClientRect();body.canvas={x:rect.x,y:rect.y,width:rect.width,height:rect.height};
  post({kind:'gpu-probe',body});
})();
