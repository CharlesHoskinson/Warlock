from pathlib import Path
import json
root=Path(__file__).resolve().parent;identity=root/'identity'
facets=[('parchment','12,24 44,24 44,76'),('gold','44,24 91,108 44,76'),('lilac','44,76 91,108 78,164'),('parchment','78,164 101,88 101,145'),('slateFacet','101,88 120,128 101,145'),('parchment','149,108 196,24 196,76'),('lilac','196,24 228,24 196,76'),('slateFacet','149,108 196,76 162,164'),('gold','162,164 139,88 139,145'),('slateFacet','139,88 120,128 139,145'),('paleGold','121,57 121,99 108,78'),('gold','121,57 134,78 121,99')]
colors={'ink':'#10111A','surface':'#1B1E2B','parchment':'#F5F0E8','lilac':'#B7A2FF','mint':'#7DE2C1','gold':'#F0BE75','muted':'#ABB1C4','slateFacet':'#79758F','paleGold':'#F6DEA9','danger':'#FF9B9B','border':'#68718C'}
polygons='\n'.join(f'<polygon points="{points}" fill="{colors[c]}"/>' for c,points in facets)
mono='\n'.join(f'<polygon points="{points}" fill="currentColor"/>' for c,points in facets)
for name,body in [('warlock-mark.svg',polygons),('warlock-mark-mono.svg',mono)]:
 (identity/name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 188" role="img" aria-labelledby="title" color="#F5F0E8"><title id="title">Warlock flow sigil</title>{body}</svg>\n')
(identity/'warlock-app-icon.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" role="img" aria-labelledby="title"><title id="title">Warlock</title><rect width="256" height="256" rx="52" fill="{colors["ink"]}"/><g transform="translate(18 38) scale(.9167)">{polygons}</g></svg>\n')
(root/'tokens.json').write_text(json.dumps({'schema':1,'brand':'Warlock','tagline':'Crafted for flow.','colors':colors,'light':{'background':'#F5F0E8','surface':'#FFFFFF','text':'#10111A','muted':'#53596C','accent':'#583DA4','mint':'#12644F','gold':'#805010','danger':'#A12A37','border':'#838A9A'},'typography':{'display':'Space Grotesk','body':'Inter','code':'JetBrains Mono'},'logo':{'clearSpace':'One central-diamond width on all sides','minimumDetailedSizePx':32,'minimumSimpleSizePx':24,'smallSizeRule':'Use monochrome; omit facet color changes below32px'},'motion':{'demoDefault':'paused','honorReducedMotion':True,'pauseWhenHidden':True,'productTiming':'Freeze and qualify under S02; brand art does not establish latency or presentation evidence'},'semantics':{'colorNeverSoleSignal':True,'decorativeDiagramNotProtocolEvidence':True}},indent=2)+'\n')
(root/'tokens.css').write_text('''@font-face{font-family:Space Grotesk;src:url(fonts/space-grotesk-bold.woff2) format("woff2");font-weight:700;font-display:swap}
@font-face{font-family:Inter;src:url(fonts/inter-variable.woff2) format("woff2");font-weight:100 900;font-display:swap}
@font-face{font-family:JetBrains Mono;src:url(fonts/jetbrains-mono-regular.woff2) format("woff2");font-weight:400;font-display:swap}
:root{--w-ink:#10111a;--w-surface:#1b1e2b;--w-text:#f5f0e8;--w-muted:#abb1c4;--w-accent:#b7a2ff;--w-stream:#7de2c1;--w-gold:#f0be75;--w-danger:#ff9b9b;--w-border:#68718c;--w-display:"Space Grotesk",sans-serif;--w-body:Inter,sans-serif;--w-code:"JetBrains Mono",monospace;--w-radius:14px}
:root[data-theme=light]{--w-ink:#f5f0e8;--w-surface:#fff;--w-text:#10111a;--w-muted:#53596c;--w-accent:#583da4;--w-stream:#12644f;--w-gold:#805010;--w-danger:#a12a37;--w-border:#838a9a}
''')
print('tokens and vector companion marks written')
