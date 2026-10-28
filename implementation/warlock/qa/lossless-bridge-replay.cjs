'use strict';
// Exercise compiled Elm ports with JSON received from the Python driver.
const fs = require('node:fs');
const vm = require('node:vm');
const [compiled, input] = process.argv.slice(2);
const cases = JSON.parse(fs.readFileSync(input, 'utf8'));
const sandbox = { console, setTimeout, clearTimeout };
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(compiled, 'utf8'), sandbox);
const app = sandbox.Elm.LosslessBridgeReplay.init();
let index = 0;
const rows = [];
const timer = setTimeout(() => { console.error('Elm port response deadline'); process.exit(2); }, 3000);
app.ports.outgoing.subscribe(value => {
  rows.push(JSON.parse(JSON.stringify(value)));
  index += 1;
  if (index === cases.length) {
    clearTimeout(timer);
    process.stdout.write(JSON.stringify(rows) + '\n');
  } else {
    app.ports.incoming.send(cases[index]);
  }
});
app.ports.incoming.send(cases[0]);
