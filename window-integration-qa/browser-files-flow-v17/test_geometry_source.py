"""Preserve all predecessor input/data/lifecycle oracles outside exact geometry work."""
import ast
from pathlib import Path
import unittest
B=Path(__file__).resolve().parent;OLD=B.with_name('browser-files-flow-v13')

class Preservation(unittest.TestCase):
 def test_private_session_reconstructs_original_except_reviewed_geometry(self):
  old=(OLD/'private_session.py').read_text();new=(B/'private_session.py').read_text()
  new=new.replace('from focus_setup import command as focus_command,validate_ack as validate_focus_ack,observed as observed_focus,ordered_points,require_displacement\n','',1)
  new=new.replace('from viewport_witness import key as viewport_key,sample as viewport_sample,pair as viewport_pair,unchanged as viewport_unchanged,move_command,integer_interior\n','',1)
  start=new.index(' def browser_rect():');end=new.index(' def files_point():',start)
  oldpart=old[old.index(' def browser_rect():'):old.index(' def files_point():')]
  new=new[:start]+oldpart+new[end:]
  new=new.replace('pointer.stdin.write(move_command(point));pointer.stdin.flush()',"pointer.stdin.write(f'move {point[0]} {point[1]}\\n');pointer.stdin.flush()",1)
  new=new.replace("r=peers[0]['rect'];point=integer_interior([s[0]+r[0],s[1]+r[1],r[2],r[3]],1);b=surface('browser')['surfaceBox']", "r=peers[0]['rect'];point=[s[0]+r[0]+r[2]/2,s[1]+r[1]+r[3]/2];b=surface('browser')['surfaceBox']",1)
  new=new.replace("caption=integer_interior([bw['at'][0]+89,bw['at'][1]-13,2,2],0)","caption=[bw['at'][0]+90,bw['at'][1]-12]",1)
  self.assertEqual(new,old)
 def test_original15_check_calls_identical(self):
  def calls(path):return [ast.dump(n,include_attributes=False)for n in ast.walk(ast.parse(path.read_text()))if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='check']
  self.assertEqual(calls(B/'private_session.py'),calls(OLD/'private_session.py'))
 def test_readonly_protocol_allowlist_and_original_query_exact(self):
  old=(OLD/'cdp_readonly.py').read_text();new=(B/'cdp_readonly.py').read_text()
  addition=',pointerMoves:window.qaPointerMoves,pointerSequence:window.qaPointerSequence,timeOrigin:performance.timeOrigin,now:performance.now(),scroll:[scrollX,scrollY],viewport:visualViewport?[visualViewport.width,visualViewport.height,visualViewport.scale,visualViewport.offsetLeft,visualViewport.offsetTop]:null'
  self.assertEqual(new.replace(addition,'',1),old)
 def test_original_local_fixture_events_and_no_submission_exact(self):
  old=(OLD/'compose.html').read_text();new=(B/'compose.html').read_text();start=new.index('window.qaPointerMoves=[];')
  self.assertEqual(new[:start]+new[new.index('</script>',start):],old)
 def test_all_other_original_runtime_python_bytefiles_unchanged(self):
  exceptions={'private_session.py','cdp_readonly.py','freeze_packet.py','metrics_offline.py'}
  for path in OLD.glob('*.py'):
   if path.name not in exceptions:self.assertEqual((B/path.name).read_bytes(),path.read_bytes(),path.name)
 def test_all_eight_inherited_models_and_tests_unchanged(self):
  for path in OLD.glob('*.qnt'):self.assertEqual((B/path.name).read_bytes(),path.read_bytes(),path.name)
 def test_no_unchecked_direct_move_writes(self):
  source=(B/'private_session.py').read_text();self.assertEqual(source.count('pointer.stdin.write(move_command(point))'),2)
  self.assertNotIn("pointer.stdin.write(f'move",source)
 def test_helper_contains_no_input_or_process_access(self):
  tree=ast.parse((B/'viewport_witness.py').read_text());imports={n.names[0].name for n in ast.walk(tree)if isinstance(n,ast.Import)}
  self.assertFalse(imports&{'os','subprocess','socket'});self.assertNotIn('Path(',ast.unparse(tree))

if __name__=='__main__':unittest.main()
