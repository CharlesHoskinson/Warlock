import { readFileSync } from 'node:fs';
const pages = ['popup', 'bar'];
let failed = false;
for (const page of pages) {
  const html = readFileSync(new URL(`../runtime/${page}.html`, import.meta.url), 'utf8');
  if (/href="theme\/(?:foundations|launcher|window-switcher|task-view|previews-snap|notifications|settings|files|system-menus|taskbar|compatibility)\.css"/.test(html)) {
    console.error(`${page}: stale component copy in runtime`); failed = true;
  }
  for (const href of html.matchAll(/href="(\.\.\/\.\.\/design\/[^\"]+\.css)"/g)) {
    try { readFileSync(new URL(`../runtime/${href[1]}`, import.meta.url)); }
    catch { console.error(`${page}: missing ${href[1]}`); failed = true; }
  }
}
if (failed) process.exitCode = 1; else console.log('Runtime component links resolve to canonical design styles.');
