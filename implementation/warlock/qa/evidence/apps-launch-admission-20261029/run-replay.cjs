'use strict';
const fs=require('node:fs'),vm=require('node:vm');
const sandbox={console,setTimeout,clearTimeout};vm.createContext(sandbox);vm.runInContext(fs.readFileSync(process.argv[2],'utf8'),sandbox);
const app=sandbox.Elm.LaunchAdmissionReplay.init();const timer=setTimeout(()=>process.exit(2),3000);
app.ports.outgoing.subscribe(x=>{clearTimeout(timer);process.stdout.write(JSON.stringify(x)+'\n')});
