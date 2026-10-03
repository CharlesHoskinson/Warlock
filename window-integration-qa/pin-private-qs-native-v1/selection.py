"""Exact selected production components, independently preserved ancestors."""
from pathlib import Path
QA=Path('/home/hoskinson/window-integration-qa');B=Path(__file__).resolve().parent
COMPOSITION=QA/'pin-frontend-composition-v2'
CORE_STAGE=Path('/home/hoskinson/window-behavior-spec/pin-maximized-core-v3-hit-fallback')
CORE=CORE_STAGE/'build-core-make/Hyprland'
PLUGIN=CORE_STAGE/'plugin/hyprbars-native-max-core-v2-candidate.so'
CORE_SHA='8b18c39ec980a5d9e8fa27018a70fc104617562e008d75113f2c7c1c50a3bbbc'
PLUGIN_SHA='0c9084e237194faf91e61fc7a8bba9fc17e6862dc3dd0082a9af1d8fbaeecbc9'
POLICY='59a1485d5f900db177414814bae9577898d687d17f2dc6a533ecec40a21590d3'
PROVIDER_STAGE=Path('/home/hoskinson/window-behavior-spec/qml-process-provider-v8-terminal-retire')
PROVIDER=PROVIDER_STAGE/'libobjectlifetime-process-terminal.so'
HELPER_STAGE=Path('/home/hoskinson/window-behavior-spec/pin-lifetime-v3/frontend')
HELPER_SHA='30cf295bbc3032b10996e9b6db7c602f6044d38cf73d4eb6ef917e72dd80f0f2'
CAPTURE_SHA='31bcc600f7d9d51a365ca50639445696b6f2db9fc5487a011fe70b4f5287f84a'
QS=Path('/usr/bin/quickshell');QS_SHA='2dc99382c032710fe495ed115cdee9dc9c69bdb3a21af4d86a9a8ea16733069b'
LAYER_PROBE=B/'native-probe/libpin-layer-episode-probe.so'
WINDOW_PROBE=QA/'pin-maximized-native-v2/readonly-probe/libqt-modal-probe.so'
KEYBOARD=QA/'pin-frontend-qa-v1/keyboard/physical-keyboard'
FIXTURE=QA/'qt-modal-private-v9/build-v7/qt-window-modal-fixture'
POINTER=Path('/home/hoskinson/.local/share/hypr-window-controls/qa/virtual-pointer')
LIFE_SCHEDULE=(
 ('A',1,'owner','right','pointer'),('A',2,'owner','keyboard','return'),('A',3,'peer','right','pointer'),
 ('B',1,'peer','keyboard','return'),('B',2,'owner','right','pointer'),('B',3,'owner','keyboard','return'))
def verify_selection():
 from io_guard import sha
 for p,h in [(CORE,CORE_SHA),(PLUGIN,PLUGIN_SHA),(QS,QS_SHA),(HELPER_STAGE/'pin_helper.py',HELPER_SHA),(HELPER_STAGE/'pin_capture.py',CAPTURE_SHA)]:
  if p.is_symlink()or not p.is_file()or sha(p)!=h:raise ValueError('Exact selected component changed: '+str(p))
 return dict(core=str(CORE),plugin=str(PLUGIN),provider=str(PROVIDER),ordinaryHelper=str(HELPER_STAGE/'pin_helper.py'),maxSpecificHelperSelected=False,requiredWindowsFloating=True,GUI=False)
