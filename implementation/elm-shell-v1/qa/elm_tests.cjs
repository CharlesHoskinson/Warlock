'use strict';
const fs=require('fs'),path=require('path');
const {Elm}=require('../build/tests.js');
const timer=setTimeout(()=>{process.stderr.write('Elm test timeout\n');process.exit(1);},5000);
Elm.Tests.init({flags:null}).ports.results.subscribe(results=>{
 clearTimeout(timer);
 const report={scope:'Real Domain/Protocol pure Elm CPU checks',passed:results.length===14&&results.every(x=>x.passed),results};
 fs.writeFileSync(path.join(__dirname,'elm-test-results.json'),JSON.stringify(report,null,2)+'\n');
 process.stdout.write(JSON.stringify(report,null,2)+'\n');process.exit(report.passed?0:1);
});
