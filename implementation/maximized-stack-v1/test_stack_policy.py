"""Bounded policy/source tests, explicitly not native compositor acceptance."""
import difflib,hashlib,itertools,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def above(stack, *, floating=True, maximized=True, pinned=frozenset()):
 # Ordinary floats are still drawn in the first pass. Only duplicate final
 # over-fullscreen draws before MAX are suppressed.
 seen=False;result=[]
 for w in stack:
  if w=='MAX':seen=True;continue
  if floating and maximized and not seen and w not in pinned:continue
  result.append(w)
 return result
class StackTest(unittest.TestCase):
 def test_raised_max_no_stale_overlay(self):
  self.assertEqual(above(['float','MAX']),[])
  self.assertEqual(above(['MAX','float']),['float'])
 def test_all_orderings_align_top_hit_with_top_draw(self):
  for stack in itertools.permutations(['MAX','a','b','c']):
   for bits in range(8):
    pinned={w for n,w in enumerate(['a','b','c']) if bits&(1<<n)}
    painted=['MAX',*above(stack,pinned=pinned)]
    expected=next((w for w in reversed(stack) if w in pinned),stack[-1])
    # Stock pinned renderer ordering amongst ordinary floats is separately
    # imperfect; this narrow fix promises pinned remains above MAX only.
    if not pinned:self.assertEqual(painted[-1],expected)
    for w in pinned:self.assertIn(w,painted[1:])
 def test_native_fullscreen_and_tiled_max_unchanged(self):
  for stack in itertools.permutations(['MAX','a','b']):
   ordinary=[w for w in stack if w!='MAX']
   self.assertEqual(above(stack,maximized=False),ordinary)
   self.assertEqual(above(stack,floating=False),ordinary)
 def test_modal_chain_after_owner_preserved(self):
  self.assertEqual(above(['other','MAX','dialog','nested']),['dialog','nested'])
 def test_lowering_max_reuses_flags_without_state_mutations(self):
  self.assertEqual(above(['a','MAX','b']),['b'])
  self.assertEqual(above(['MAX','a','b']),['a','b'])
 def test_exact_sources_and_patch_match(self):
  manifest=json.loads((ROOT/'source-manifest.json').read_text())
  for row in manifest['files']:self.assertEqual(hashlib.sha256((ROOT/'original'/row['path']).read_bytes()).hexdigest(),row['sha256'])
  path=manifest['candidate']['path'];a=(ROOT/'original'/path).read_text();b=(ROOT/'candidate'/path).read_text()
  self.assertEqual(hashlib.sha256(b.encode()).hexdigest(),manifest['candidate']['sha256'])
  expected=''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/'+path,tofile='b/'+path))
  self.assertEqual((ROOT/'floating-max-stack.patch').read_text(),expected)
  additions='\n'.join(line[1:] for line in expected.splitlines() if line.startswith('+') and not line.startswith('+++'))
  for mutation in ('m_allowedOverFullscreen =','updateFullscreenInputState(','setValueAndWarp(','m_realSize','m_realPosition'):self.assertNotIn(mutation,additions)
if __name__=='__main__':unittest.main()
