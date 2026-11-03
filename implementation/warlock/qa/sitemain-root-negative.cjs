'use strict';
// Root-only ninth-root negative controls; fixtures remain independent source literals.
const fs = require('node:fs');
const path = require('node:path');
const { validateFiles, validateCases, instrument } = require('./sitemain-root-observer.cjs');

const dir = __dirname;
const repo = path.resolve(process.argv[2] || '.');
const bundlePath = process.argv[3] ? path.resolve(process.argv[3]) : null;
const manifest = JSON.parse(fs.readFileSync(path.join(dir, 'sitemain-root-manifest.json'), 'utf8'));
const files = {
  siteMain: fs.readFileSync(path.join(repo, manifest.fixtures.siteMain.file)),
  siteElmJson: fs.readFileSync(path.join(repo, manifest.fixtures.siteElmJson.file)),
  literals: fs.readFileSync(path.join(dir, manifest.fixtures.literals.file)),
};

function mustFail(name, fn, expected) {
  let error;
  try {
    fn();
  } catch (e) {
    error = e;
  }
  if (!error || !String(error.message).includes(expected)) {
    throw new Error(`${name}: expected rejection ${expected}, got ${error ? error.message : 'no error'}`);
  }
}

validateFiles(manifest, files);
const literals = require('./sitemain-root-literals.cjs');
const packet = literals.build(repo);
validateCases(manifest, packet.cases, packet.fakeDomExpectedTrace);

mustFail(
  'missing-sitemain-source',
  () => validateFiles(manifest, { ...files, siteMain: undefined }),
  'siteMain: missing or empty'
);
mustFail(
  'empty-sitemain-source',
  () => validateFiles(manifest, { ...files, siteMain: Buffer.alloc(0) }),
  'siteMain: missing or empty'
);
mustFail(
  'altered-sitemain-source',
  () => validateFiles(manifest, { ...files, siteMain: Buffer.concat([files.siteMain, Buffer.from('x')]) }),
  'siteMain: fixture digest mismatch'
);
mustFail(
  'missing-site-elm-json',
  () => validateFiles(manifest, { ...files, siteElmJson: undefined }),
  'siteElmJson: missing or empty'
);
mustFail(
  'altered-site-elm-json',
  () => validateFiles(manifest, { ...files, siteElmJson: Buffer.concat([files.siteElmJson, Buffer.from('x')]) }),
  'siteElmJson: fixture digest mismatch'
);
mustFail(
  'altered-literals',
  () => validateFiles(manifest, { ...files, literals: Buffer.concat([files.literals, Buffer.from('x')]) }),
  'literals: fixture digest mismatch'
);
mustFail(
  'removed-case',
  () => validateCases(manifest, packet.cases.slice(0, -1), packet.fakeDomExpectedTrace),
  'ordered case inventory differs'
);
mustFail(
  'duplicate-case',
  () => validateCases(manifest, packet.cases.concat(packet.cases[0]), packet.fakeDomExpectedTrace),
  'duplicate case name'
);

const syntheticBundle = bundlePath
  ? fs.readFileSync(bundlePath, 'utf8')
  : "var _List_Nil = { $: '[]' };\n";
mustFail(
  'injected-animated-subscription-bundle',
  () => instrument(syntheticBundle + '\n// $elm$browser$Browser$Events$onAnimationFrame\n'),
  'rejected animated or mutated SiteMain bundle'
);

console.log(
  JSON.stringify({
    ok: true,
    controls: [
      'missing-sitemain-source',
      'empty-sitemain-source',
      'altered-sitemain-source',
      'missing-site-elm-json',
      'altered-site-elm-json',
      'altered-literals',
      'removed-case',
      'duplicate-case',
      'injected-animated-subscription-bundle',
    ],
    lexicalOnlyControls: ['injected-animated-subscription-bundle'],
    limits: ['The animation comment checks a lexical guard; a behavioral nonempty-subscription negative remains unverified.'],
    originalAcceptanceClaim: false,
  })
);
