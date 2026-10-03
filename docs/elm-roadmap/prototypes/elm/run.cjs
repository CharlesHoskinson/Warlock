const fs = require('fs');
const {Elm} = require('./main.js');
const app = Elm.Main.init({flags:null});
const timeout = setTimeout(() => { process.stderr.write('Elm receipt timeout\n'); process.exit(1); }, 5000);
app.ports.results.subscribe(results => {
  clearTimeout(timeout);
  const report = {scope:'Headless pure reducer; not native host/effect acceptance', results};
  fs.writeFileSync('results.json', JSON.stringify(report,null,2)+'\n');
  process.stdout.write(JSON.stringify(report,null,2)+'\n');
  process.exit(results.every(x=>x.passed) ? 0 : 1);
});
