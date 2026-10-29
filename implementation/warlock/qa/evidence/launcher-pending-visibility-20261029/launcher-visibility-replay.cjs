'use strict';
const fs = require('node:fs');
const vm = require('node:vm');
const sandbox = {console, setTimeout, clearTimeout};
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(process.argv[2], 'utf8'), sandbox);
const app = sandbox.Elm.LauncherVisibilityReplay.init();
const timer = setTimeout(() => { console.error('Elm replay watchdog'); process.exit(2); }, 3000);
app.ports.outgoing.subscribe(result => {
  clearTimeout(timer);
  process.stdout.write(JSON.stringify(result) + '\n');
});
