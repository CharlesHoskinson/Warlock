const fs = require('node:fs');
const compiled = require(process.argv[2]);
const manifest = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const expected = [...manifest.fixture.checks].sort();
const timer = setTimeout(() => { throw new Error('No replay result within ten seconds'); }, 10000);
compiled.Elm.NotificationCapabilityReplay.init({ flags: null }).ports.outgoing.subscribe(result => {
  clearTimeout(timer);
  const checks = result.checks;
  if (!checks || JSON.stringify(Object.keys(checks).sort()) !== JSON.stringify(expected)
      || Object.values(checks).some(value => typeof value !== 'boolean')) {
    throw new Error('Exact literal replay inventory differs');
  }
  fs.writeFileSync(process.argv[4], JSON.stringify(result, null, 2) + '\n');
  const failed = Object.keys(checks).filter(key => !checks[key]);
  process.stdout.write(JSON.stringify({ checks: expected.length, failed }) + '\n');
  process.exit(failed.length ? 1 : 0);
});
