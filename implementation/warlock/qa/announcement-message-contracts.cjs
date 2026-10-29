// Root-only protected execution; pass the compiled Elm JS as argv[2].
const { Elm } = require(process.argv[2]);
const seed = 0x0a110c10; let state = seed >>> 0;
function random() { state ^= state << 13; state ^= state >>> 17; state ^= state << 5; return state >>> 0; }
const counters = ['0','1','9007199254740992','9007199254740993','18446744073709551615'];
const texts = ['', 'ordinary', 'Ω 東京 🪟', 'quote " slash \\', 'line\ncontrol\u0001', 'x'.repeat(4097)];
const correlations = ['', 'request:1', 'α\n\u0000"\\', 'c'.repeat(4097)];
const cases = [];
for (const sequence of counters) for (const interrupt of [false,true])
  cases.push({sequence,interrupt,correlation:correlations[cases.length%correlations.length],text:texts[cases.length%texts.length],counterValid:true});
for (let i=0;i<200;i++) cases.push({sequence:counters[random()%counters.length],interrupt:!!(random()%2),correlation:correlations[random()%correlations.length]+'#'+i,text:texts[random()%texts.length]+'#'+(random()%1000),counterValid:true});
for (const sequence of ['', '01', '-1', '18446744073709551616', '1.0', '9'.repeat(21)])
  cases.push({sequence,interrupt:false,correlation:'invalid-counter',text:'not an encoder input',counterValid:false});
const worker = Elm.AnnouncementMessageContracts.init({flags:{cases}});
worker.ports.outgoing.subscribe(output => {
  const failures = [];
  if (output.cases.length !== cases.length) failures.push({name:'case-count',expected:cases.length,actual:output.cases.length});
  output.cases.forEach((actual,i) => {
    const input=cases[i];
    if (!actual.inputDecoded || actual.counterAccepted !== input.counterValid) {
      failures.push({name:'counter-admission',index:i,input,actual}); return;
    }
    if (!input.counterValid) return;
    const expected=JSON.stringify({interrupt:input.interrupt,sequence:input.sequence,correlation:input.correlation,text:input.text});
    if (actual.old!==expected || actual.pure!==expected || actual.facade!==expected || !actual.aliases)
      failures.push({name:'encoder',index:i,input,expected,actual});
  });
  process.stdout.write(JSON.stringify({seed:'0x0a110c10',generated:200,caseCount:cases.length,positiveCounters:counters,failures},null,2)+'\n');
  process.exitCode=failures.length ? 1 : 0;
});
