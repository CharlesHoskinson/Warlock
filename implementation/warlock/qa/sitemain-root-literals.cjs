'use strict';

/*
 * Independent source-bound literal oracle for the ninth Browser.element root:
 * canonical unmodified site/src/SiteMain.elm
 * (SHA-256: f05a3768eb4573161544099917ce009f8df7eb57b8c9408f5266001980cafcfb)
 * and site/elm.json
 * (SHA-256: ffe9bc4f6811166a7bbafca49540bf7b8af214118dd9aff2f4707890eb9824dc).
 *
 * Every expected 9-field Model, Sub.none bag ({ $: 2, m: { $: '[]' } }),
 * closed command-leaf count ({ Task: 0 | 1 }), and pure typed Dom.focus effect
 * description is authored directly from site/src/SiteMain.elm without reading
 * runtime reducer output. This fixture covers the static/one-shot focus
 * homepage boundary only; it never claims desktop recurring-demand or native
 * Omarchy GUI acceptance.
 */

const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const CANONICAL_SITE_MAIN_SHA256 =
  'f05a3768eb4573161544099917ce009f8df7eb57b8c9408f5266001980cafcfb';

const CANONICAL_SITE_ELM_JSON_SHA256 =
  'ffe9bc4f6811166a7bbafca49540bf7b8af214118dd9aff2f4707890eb9824dc';

const NINE_DECLARED_BROWSER_ELEMENT_ROOTS = Object.freeze([
  'implementation/warlock/src/Main.elm',
  'implementation/warlock/src/Bar.elm',
  'implementation/warlock/src/Popup.elm',
  'implementation/warlock/src/HttpMain.elm',
  'implementation/warlock/src/HttpBar.elm',
  'implementation/warlock/src/HttpPopup.elm',
  'implementation/warlock/src/NativePreviewAdmission.elm',
  'implementation/warlock/src/NativePreviewRenderer.elm',
  'site/src/SiteMain.elm',
]);

const digest = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
function insist(ok, message) {
  if (!ok) throw new Error(message);
}

const empty = () => ({ $: '[]' });
const subNone = () => ({ $: 2, m: empty() });
const none = () => ({ $: 'Nothing' });
const just = value => ({ $: 'Just', a: value });
const tag = name => ({ $: name });
const unit = () => ({ $: '#0' });
const okUnit = () => ({ $: 'Ok', a: unit() });
const errDomNotFound = id => ({ $: 'Err', a: { $: 'NotFound', a: id } });

function focusEffect(seq, surfaceName, domId) {
  return {
    domId,
    effect: 'Task.attempt',
    onNotFound: {
      $: 'TabFocusSettled',
      a: seq,
      b: tag(surfaceName),
      c: errDomNotFound(domId),
    },
    onOk: {
      $: 'TabFocusSettled',
      a: seq,
      b: tag(surfaceName),
      c: okUnit(),
    },
    task: 'Browser.Dom.focus',
  };
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function patchModel(baseModel, patch) {
  const next = clone(baseModel);
  for (const [key, value] of Object.entries(patch)) {
    insist(Object.prototype.hasOwnProperty.call(next, key), `unknown SiteMain.Model field: ${key}`);
    next[key] = clone(value);
  }
  return next;
}

function expectedStep(state, effects = []) {
  return {
    state: clone(state),
    subscriptions: subNone(),
    cmdLeaves: { Task: effects.length },
    effects: clone(effects),
  };
}

const SITE_MAIN_INITIAL_MODEL = {
  category: tag('CategoryAll'),
  cues: {
    activeApplication: true,
    switcherCandidate: false,
    windowFocused: true,
  },
  lastTabFocusMiss: none(),
  mobileNavOpen: false,
  motion: tag('MotionStandard'),
  outcomeSample: tag('SampleObserved'),
  spotlight: tag('SurfaceTaskbar'),
  tabFocusSeq: 0,
  theme: tag('ThemeNight'),
};

const M_STEP_1_LAUNCHER = patchModel(SITE_MAIN_INITIAL_MODEL, {
  spotlight: tag('SurfaceLauncher'),
  tabFocusSeq: 1,
  lastTabFocusMiss: none(),
});

const M_JUMP_2_FILES = patchModel(M_STEP_1_LAUNCHER, {
  spotlight: tag('SurfaceFiles'),
  tabFocusSeq: 2,
  lastTabFocusMiss: none(),
});

const M_FILES_FOCUS_MISS = patchModel(M_JUMP_2_FILES, {
  lastTabFocusMiss: just('wl-tab-files'),
});

const M_FILES_FOCUS_OK = patchModel(M_FILES_FOCUS_MISS, {
  lastTabFocusMiss: none(),
});

const M_JUMP_1_FILES = patchModel(SITE_MAIN_INITIAL_MODEL, {
  spotlight: tag('SurfaceFiles'),
  tabFocusSeq: 1,
  lastTabFocusMiss: none(),
});

const M_JUMP_1_FILES_MISS = patchModel(M_JUMP_1_FILES, {
  lastTabFocusMiss: just('wl-tab-files'),
});

const M_POINTER_1_TASKBAR = patchModel(M_JUMP_1_FILES_MISS, {
  spotlight: tag('SurfaceTaskbar'),
  lastTabFocusMiss: none(),
});

const M_POINTER_1_SETTINGS = patchModel(M_POINTER_1_TASKBAR, {
  spotlight: tag('SurfaceSettings'),
  lastTabFocusMiss: none(),
});

const M_LOCAL_1_NAV_OPEN = patchModel(SITE_MAIN_INITIAL_MODEL, {
  mobileNavOpen: true,
});

const M_LOCAL_2_NAV_CLOSED = patchModel(M_LOCAL_1_NAV_OPEN, {
  mobileNavOpen: false,
});

const M_LOCAL_3_THEME_DAWN = patchModel(M_LOCAL_2_NAV_CLOSED, {
  theme: tag('ThemeDawn'),
});

const M_LOCAL_4_MOTION_REDUCED = patchModel(M_LOCAL_3_THEME_DAWN, {
  motion: tag('MotionReduced'),
});

const M_LOCAL_5_CATEGORY_WINDOWS = patchModel(M_LOCAL_4_MOTION_REDUCED, {
  category: tag('CategoryWindows'),
});

const M_LOCAL_6_UNFOCUSED = patchModel(M_LOCAL_5_CATEGORY_WINDOWS, {
  cues: {
    activeApplication: true,
    switcherCandidate: false,
    windowFocused: false,
  },
});

const M_LOCAL_7_INACTIVE_APP = patchModel(M_LOCAL_6_UNFOCUSED, {
  cues: {
    activeApplication: false,
    switcherCandidate: false,
    windowFocused: false,
  },
});

const M_LOCAL_8_SWITCHER_CANDIDATE = patchModel(M_LOCAL_7_INACTIVE_APP, {
  cues: {
    activeApplication: false,
    switcherCandidate: true,
    windowFocused: false,
  },
});

const M_LOCAL_9_OUTCOME_REFUSED = patchModel(M_LOCAL_8_SWITCHER_CANDIDATE, {
  outcomeSample: tag('SampleRefused'),
});

const M_DOM_SEQ2_SWITCHER = patchModel(M_STEP_1_LAUNCHER, {
  spotlight: tag('SurfaceSwitcher'),
  tabFocusSeq: 2,
  lastTabFocusMiss: none(),
});

const M_DOM_SEQ3_FILES = patchModel(M_DOM_SEQ2_SWITCHER, {
  spotlight: tag('SurfaceFiles'),
  tabFocusSeq: 3,
  lastTabFocusMiss: none(),
});

const M_DOM_SEQ4_TASKBAR = patchModel(M_DOM_SEQ3_FILES, {
  spotlight: tag('SurfaceTaskbar'),
  tabFocusSeq: 4,
  lastTabFocusMiss: none(),
});

const M_DOM_SEQ4_TASKBAR_MISS = patchModel(M_DOM_SEQ4_TASKBAR, {
  lastTabFocusMiss: just('wl-tab-taskbar'),
});

const M_DOM_SEQ4_POINTER_LAUNCHER = patchModel(M_DOM_SEQ4_TASKBAR_MISS, {
  spotlight: tag('SurfaceLauncher'),
  lastTabFocusMiss: none(),
});

const coverage = Object.freeze({
  complete: false,
  originalAcceptanceClaim: false,
  requirement: 'ELM-TEA-004',
  scenario: 'tea-subscriptions',
  rootsInventoried: NINE_DECLARED_BROWSER_ELEMENT_ROOTS,
  ninthRoot: 'site/src/SiteMain.elm',
  ninthRootSha256: CANONICAL_SITE_MAIN_SHA256,
  siteElmJsonSha256: CANONICAL_SITE_ELM_JSON_SHA256,
  recurringDemand: 'none',
});

function build(repository) {
  insist(typeof repository === 'string' && repository.length > 0, 'repository root path required');
  const siteMainPath = path.join(repository, 'site/src/SiteMain.elm');
  const siteElmJsonPath = path.join(repository, 'site/elm.json');
  insist(fs.existsSync(siteMainPath), 'siteMain: missing or empty');
  const siteMainBytes = fs.readFileSync(siteMainPath);
  insist(siteMainBytes.length > 0, 'siteMain: missing or empty');
  insist(digest(siteMainBytes) === CANONICAL_SITE_MAIN_SHA256, 'siteMain: source digest mismatch');
  insist(fs.existsSync(siteElmJsonPath), 'siteElmJson: missing or empty');
  const siteElmJsonBytes = fs.readFileSync(siteElmJsonPath);
  insist(siteElmJsonBytes.length > 0, 'siteElmJson: missing or empty');
  insist(digest(siteElmJsonBytes) === CANONICAL_SITE_ELM_JSON_SHA256, 'siteElmJson: manifest digest mismatch');

  const cases = [
    {
      name: 'SiteMain-init-and-sub-none-no-recurring-demand',
      root: 'SiteMain',
      steps: [
        {
          input: { kind: 'init' },
          expected: expectedStep(SITE_MAIN_INITIAL_MODEL, []),
        },
      ],
    },
    {
      name: 'SiteMain-keyboard-step-jump-stale-and-settled-focus',
      root: 'SiteMain',
      steps: [
        {
          input: { kind: 'init' },
          expected: expectedStep(SITE_MAIN_INITIAL_MODEL, []),
        },
        {
          input: { kind: 'KeyboardStepSpotlight', delta: 1 },
          expected: expectedStep(M_STEP_1_LAUNCHER, [focusEffect(1, 'SurfaceLauncher', 'wl-tab-launcher')]),
        },
        {
          input: { kind: 'KeyboardJumpSpotlight', surface: 'SurfaceFiles' },
          expected: expectedStep(M_JUMP_2_FILES, [focusEffect(2, 'SurfaceFiles', 'wl-tab-files')]),
        },
        {
          input: { kind: 'TabFocusSettledNotFound', seq: 1, surface: 'SurfaceLauncher', domId: 'wl-tab-launcher' },
          expected: expectedStep(M_JUMP_2_FILES, []),
        },
        {
          input: { kind: 'TabFocusSettledNotFound', seq: 2, surface: 'SurfaceTaskbar', domId: 'wl-tab-taskbar' },
          expected: expectedStep(M_JUMP_2_FILES, []),
        },
        {
          input: { kind: 'TabFocusSettledNotFound', seq: 2, surface: 'SurfaceFiles', domId: 'wl-tab-files' },
          expected: expectedStep(M_FILES_FOCUS_MISS, []),
        },
        {
          input: { kind: 'TabFocusSettledOk', seq: 2, surface: 'SurfaceFiles' },
          expected: expectedStep(M_FILES_FOCUS_OK, []),
        },
      ],
    },
    {
      name: 'SiteMain-pointer-spotlight-clears-focus-miss-without-cmd',
      root: 'SiteMain',
      steps: [
        {
          input: { kind: 'init' },
          expected: expectedStep(SITE_MAIN_INITIAL_MODEL, []),
        },
        {
          input: { kind: 'KeyboardJumpSpotlight', surface: 'SurfaceFiles' },
          expected: expectedStep(M_JUMP_1_FILES, [focusEffect(1, 'SurfaceFiles', 'wl-tab-files')]),
        },
        {
          input: { kind: 'TabFocusSettledNotFound', seq: 1, surface: 'SurfaceFiles', domId: 'wl-tab-files' },
          expected: expectedStep(M_JUMP_1_FILES_MISS, []),
        },
        {
          input: { kind: 'StepSpotlight', delta: 1 },
          expected: expectedStep(M_POINTER_1_TASKBAR, []),
        },
        {
          input: { kind: 'SelectSpotlight', surface: 'SurfaceSettings' },
          expected: expectedStep(M_POINTER_1_SETTINGS, []),
        },
      ],
    },
    {
      name: 'SiteMain-pure-local-controls-no-effects-or-subscriptions',
      root: 'SiteMain',
      steps: [
        {
          input: { kind: 'init' },
          expected: expectedStep(SITE_MAIN_INITIAL_MODEL, []),
        },
        {
          input: { kind: 'ToggleMobileNav' },
          expected: expectedStep(M_LOCAL_1_NAV_OPEN, []),
        },
        {
          input: { kind: 'CloseMobileNav' },
          expected: expectedStep(M_LOCAL_2_NAV_CLOSED, []),
        },
        {
          input: { kind: 'SelectTheme', theme: 'ThemeDawn' },
          expected: expectedStep(M_LOCAL_3_THEME_DAWN, []),
        },
        {
          input: { kind: 'ToggleMotion' },
          expected: expectedStep(M_LOCAL_4_MOTION_REDUCED, []),
        },
        {
          input: { kind: 'SelectCategory', category: 'CategoryWindows' },
          expected: expectedStep(M_LOCAL_5_CATEGORY_WINDOWS, []),
        },
        {
          input: { kind: 'ToggleWindowFocused' },
          expected: expectedStep(M_LOCAL_6_UNFOCUSED, []),
        },
        {
          input: { kind: 'ToggleActiveApplication' },
          expected: expectedStep(M_LOCAL_7_INACTIVE_APP, []),
        },
        {
          input: { kind: 'ToggleSwitcherCandidate' },
          expected: expectedStep(M_LOCAL_8_SWITCHER_CANDIDATE, []),
        },
        {
          input: { kind: 'SelectOutcomeSample', sample: 'SampleRefused' },
          expected: expectedStep(M_LOCAL_9_OUTCOME_REFUSED, []),
        },
      ],
    },
  ];

  const fakeDomExpectedTrace = [
    expectedStep(SITE_MAIN_INITIAL_MODEL, []),
    expectedStep(M_STEP_1_LAUNCHER, [focusEffect(1, 'SurfaceLauncher', 'wl-tab-launcher')]),
    expectedStep(M_STEP_1_LAUNCHER, []),
    expectedStep(M_DOM_SEQ2_SWITCHER, [focusEffect(2, 'SurfaceSwitcher', 'wl-tab-switcher')]),
    expectedStep(M_DOM_SEQ3_FILES, [focusEffect(3, 'SurfaceFiles', 'wl-tab-files')]),
    expectedStep(M_DOM_SEQ3_FILES, []),
    expectedStep(M_DOM_SEQ3_FILES, []),
    expectedStep(M_DOM_SEQ4_TASKBAR, [focusEffect(4, 'SurfaceTaskbar', 'wl-tab-taskbar')]),
    expectedStep(M_DOM_SEQ4_TASKBAR_MISS, []),
    expectedStep(M_DOM_SEQ4_POINTER_LAUNCHER, []),
  ];

  return {
    coverage,
    cases,
    fakeDomExpectedTrace,
    sourcePins: {
      siteMain: { path: 'site/src/SiteMain.elm', sha256: CANONICAL_SITE_MAIN_SHA256 },
      siteElmJson: { path: 'site/elm.json', sha256: CANONICAL_SITE_ELM_JSON_SHA256 },
    },
  };
}

module.exports = {
  CANONICAL_SITE_MAIN_SHA256,
  CANONICAL_SITE_ELM_JSON_SHA256,
  NINE_DECLARED_BROWSER_ELEMENT_ROOTS,
  coverage,
  build,
};
