"""Observe real preview custody alongside main-window recovery; issue no facts."""
import json
from pathlib import Path


class BarCollector:
    """Exact-publication bar observation, independent of the pure popup DOM.

    The pure preview intentionally has no window policy or window-selection
    buttons. Main policy inspection still supplies transaction/picker state;
    only actual matching bar DOM supplies the commands and their positions.
    """
    def __init__(self):
        self.last = None

    def read(self, text):
        inspections, bars = [], {}
        for line in text.splitlines():
            if line.startswith('surface-inspection: '):
                inspections.append(json.loads(line.split(': ', 1)[1]))
            prefix = 'surface-report: origin=bar '
            if line.startswith(prefix):
                row = json.loads(line[len(prefix):])
                body = row['body']
                bars[(body['publication'], body['lease'])] = body
        for inspection in inspections:
            bar = bars.get((inspection['publication'], inspection['lease']))
            if bar is None:
                continue
            groups = []
            for group in inspection['body']['groups']:
                buttons = [b for b in bar['buttons'] if b['id'] == group['domId']]
                if len(buttons) != 1:
                    break
                b = buttons[0]
                x, y, width, height = [b[k] for k in ['x', 'y', 'width', 'height']]
                groups.append(dict(group, disabled=b['disabled'], label=b['accessibleName'],
                    point=[x + width / 2, y + height / 2],
                    visible=0 <= x and 0 <= y and width > 0 and height > 0 and x + width <= 800 and y + height <= 48))
            if len(groups) == len(inspection['body']['groups']):
                self.last = dict(inspection['body'], groups=groups, publication=inspection['publication'], lease=inspection['lease'])
        return self.last


class PreviewObserver:
    def __init__(self, output, pre, log, projection, click, helper, check, wait):
        self.output = Path(output)
        self.pre = pre
        self.log = log
        self.projection = projection
        self.click = click
        self.helper = helper
        self.check = check
        self.wait = wait
        self.captures = {}

    def text(self):
        text = self.log().read_text(errors='replace')
        return text if text.endswith('\n') else text[:text.rfind('\n') + 1]

    def states(self):
        prefix = 'controlled-native-private-status: '
        return [json.loads(line[len(prefix):]) for line in self.text().splitlines() if line.startswith(prefix)]

    def reader_stimulus(self, generation, value):
        path = self.output / ('controlled-reader-generation-' + str(generation))
        temporary = path.with_suffix('.tmp')
        temporary.write_text(value + '\n')
        temporary.chmod(0o600)
        temporary.replace(path)

    def group(self):
        p = self.projection()
        return next((g for g in p['groups'] if g['title'] == 'WARLOCK-CHILD-PROBE' and not g['disabled']), None) if p and p['phase'] == 'Coherent' else None

    def capture(self, generation):
        self.check('combinedPreviewAbsentBeforeRealPickerAdmission-' + str(generation), 'controlled-native-start:' not in self.text())
        self.click(self.wait(self.group))
        self.wait(lambda: 'controlled-native-start:' in self.text() and 'controlled-renderer-initialized:' in self.text() and 'controlled-renderer-applied:' in self.text())
        self.check('combinedPreviewOriginalGTKThenPureRenderer-' + str(generation), self.text().index('surface-presentation-applied:') < self.text().index('controlled-native-start:') and 'windowPolicies=0 physicalReveal=0' in self.text() and 'originalContext=1 currentProjection=1 physicalReveal=0' in self.text())
        def current():
            states = self.states()
            if not states:
                return None
            s = states[-1]
            models = s['privatePolicy']['models']
            return s if len(models) == 1 and models[0]['model'].get('image') and models[0]['model'].get('accepted') and int(s['transport']['nativeIssuedThrough']) > 0 and int(s['transport']['deliveredThrough']) > 0 else None
        state = self.wait(current)
        model = state['privatePolicy']['models'][0]['model']
        self.check('combinedPreviewKnownActualNativeCustody-' + str(generation), model['accepted']['owned'] and model['accepted']['signaled'] and state['nativeEffectError'] == '' and state['privatePolicy']['realm']['controlled'] and not state['privatePolicy']['realm']['closed'], state=state)
        def snapshot():
            rows = [line for line in self.text().splitlines() if line.startswith('native-client-webkit-snapshot-job: ')]
            if not rows:
                return None
            path = Path(rows[-1].split(' path=', 1)[1])
            assert path.parent == self.output and path.name.startswith('controlled-webkit-generation-' + str(generation) + '.png')
            return path if path.is_file() else None
        image = self.wait(snapshot)
        result = self.helper([self.pre['pixelOracle'], str(image)], check=True, timeout=5)
        pixels = json.loads(result.stdout)
        self.check('combinedPreviewIndependentActualSourcePixels-' + str(generation), pixels['red'] == 19200 and pixels['green'] == 0 and pixels['blue'] == 0, pixels=pixels, image=str(image))
        self.wait(lambda: 'controlled-native-reader-held: epoch=1 actualGIO=1 firstByte=137 ' in self.text())
        paint = self.wait(lambda: next((r for r in reversed([json.loads(line.split(': ', 1)[1]) for line in self.text().splitlines() if line.startswith('controlled-native-paint-observation: ')]) if r['nativeEpoch'] == '1' and r['opacity'] == 0), None))
        self.check('combinedPreviewOriginalCurtainAndGTKPaint-' + str(generation), paint['gtkAfterPaint'] and not paint['physicalFrameQualified'] and paint['width'] == 700 and paint['height'] == 420 and paint['opacity'] == 0, paint=paint)
        captured = dict(state=state, model=model, pixels=pixels, image=str(image), paint=paint)
        self.captures[generation] = captured
        return captured

    def begin_close(self, generation):
        result = self.helper([self.pre['pointer'], '800', '600'], input='move 400 500\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n', timeout=5)
        self.check('combinedOutsidePopupPointerNormalExit-' + str(generation), result.returncode == 0)
        closing = self.wait(lambda: next((s for s in reversed(self.states()) if s['privatePolicy']['realm']['closing'] and not s['privatePolicy']['realm']['closed']), None))
        self.check('combinedActualReaderBlocksRetirementBeforeCommand-' + str(generation), 'controlled-native-realm-retired:' not in self.text() and 'controlled-native-reader-released:' not in self.text() and self.text().count('controlled-native-start:') == 1, state=closing)
        self.reader_stimulus(generation, 'probe')
        self.wait(lambda: 'controlled-native-reader-probed: epoch=1 ' in self.text())
        self.check('combinedActualHeldAndFreshURIRevocation-' + str(generation), 'controlled-native-reader-probed: epoch=1 heldRead=-1 heldDenied=1 freshDenied=1 actualGIO=1 physicalSettlement=0' in self.text())
        return closing

    def strictly_closed(self):
        states = self.states()
        if not states:
            return None
        s = states[-1]
        p = s['privatePolicy']
        return s if p['realm']['closed'] and not p['models'] and not p['realm']['ingress']['pending'] and not p['realm']['deferred'] and not s['retainedInputs'] and not s['postedTickets'] and not s['confirmations'] and not s['returnedEventBatches'] and s['transport']['pending'] == 0 else None

    def release(self, generation):
        self.reader_stimulus(generation, 'release')
        self.wait(lambda: 'controlled-native-reader-released: epoch=1 originalCloseCalls=1 nativeGrantReset=0' in self.text())
        closed = self.wait(self.strictly_closed)
        self.check('combinedOriginalStrictNativeAndHostCustodyClose-' + str(generation), closed['nativeEffectError'] == '' and 'controlled-native-realm-retired: epoch=1 ' in self.text(), state=closed)
        return closed

    def release_after_renderer_fault(self, generation):
        self.wait(lambda: 'Web process terminated:' in self.text() and 'controlled-native-renderer-failure-drain: epoch=1 ' in self.text())
        self.check('combinedRendererDeathCannotSettleHeldNativeReader', 'native-recovery-ready:' not in self.text() and 'controlled-native-realm-retired:' not in self.text() and 'controlled-native-reader-released:' not in self.text(), states=self.states()[-2:])
        closed = self.release(generation)
        self.wait(lambda: 'native-recovery-ready:' in self.text())
        markers = ['Web process terminated:', 'controlled-native-reader-released:', 'controlled-native-realm-retired:', 'native-recovery-ready:']
        positions = [self.text().index(m) for m in markers]
        self.check('combinedNativeReaderAndStrictClosePrecedeGTKRecovery', positions == sorted(positions), markers=markers, positions=positions, state=closed)
        return closed
