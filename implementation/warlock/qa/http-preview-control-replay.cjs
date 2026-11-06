'use strict';
// QA-only first-increment compiled-root checks. Root uses protected execution.
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const {isDeepStrictEqual}=require('node:util');
const {run}=require('./sol-http-root-observer-0535.cjs');
const {build}=require('./http-preview-control-literals.cjs');
const hash=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
try {
  const args=process.argv.slice(2);
  if(args.length!==2 || !args.every(path.isAbsolute)) throw new Error('expected ABS_REPOSITORY ABS_PLAIN_HTTPPOPUP_JS');
  const [repository,image]=args;
  const original=fs.readFileSync(image,'utf8');
  const fixture=build(repository);
  const results=[];
  for(const spec of fixture.cases) {
    const first=run(original,spec),second=run(original,spec);
    if(!isDeepStrictEqual(first.trace,second.trace)) throw new Error('nondeterministic complete control trace');
    const negative=JSON.parse(JSON.stringify(spec));
    negative.steps[1].expected.state.popup.previews.b={$:'Nothing'};
    let refused=false;
    try {run(original,negative);} catch(error) {
      if(error.message!==`${spec.name} step 1: COMPLETE owning model/subscription/typed descriptions differ` || error.counterexample?.step!==1) throw error;
      refused=true;
    }
    if(!refused) throw new Error('missing full-model mutation rejection');
    results.push({name:spec.name,steps:spec.steps.length,freshRuns:2,negative:'grant-retention-model-altered',instrumentation:first.instrumentation});
  }
  console.log(JSON.stringify({ok:true,results,imageSha256:hash(original),fixtureSha256:hash(fs.readFileSync(path.join(__dirname,'http-preview-control-literals.cjs'))),
    observerSha256:hash(fs.readFileSync(path.join(__dirname,'sol-http-root-observer-0535.cjs'))),tool:{node:process.version},fuzz:fixture.fuzz,coverage:fixture.coverage,originalAcceptanceClaim:false}));
} catch(error) {console.error(JSON.stringify({ok:false,error:error.message,counterexample:error.counterexample||null,originalAcceptanceClaim:false}));process.exitCode=1;}
