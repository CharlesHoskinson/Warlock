#!/usr/bin/env python3
"""Bounded current-process executable FD regression; no compositor, spawn, or input."""
import argparse,hashlib,importlib.util,os,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
parser=argparse.ArgumentParser();parser.add_argument('--module',required=True)
args,rest=parser.parse_known_args()
spec=importlib.util.spec_from_file_location('proc_image_runner',args.module)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
class Controls(unittest.TestCase):
    def test_actual_proc_magic_link_and_fail_closed_guards(self):
        pid=os.getpid();born=m.birth(pid)[0]
        # Independent known current interpreter image, not a fake target process.
        expected=hashlib.sha256(Path(sys.executable).resolve(strict=True).read_bytes()).hexdigest()
        real_open=os.open;opened=[]
        def observe_open(path,flags,*a,**kw):
            opened.append((str(path),flags));return real_open(path,flags,*a,**kw)
        with patch.object(m.os,'open',side_effect=observe_open),patch.object(m.Path,'resolve',side_effect=AssertionError('must not resolve kernel executable link')):
            m.attest_process_image(pid,born,expected)
        self.assertEqual(len(opened),1)
        self.assertEqual(opened[0][0],'/proc/'+str(pid)+'/exe')
        self.assertFalse(opened[0][1]&os.O_NOFOLLOW)
        self.assertTrue(opened[0][1]&os.O_CLOEXEC)
        with self.assertRaisesRegex(ValueError,'image digest'):
            m.attest_process_image(pid,born,'0'*64)
        with self.assertRaisesRegex(ValueError,'birth'):
            m.attest_process_image(pid,str(int(born)+1),expected)
        process_stat=Path('/proc',str(pid),'stat').read_text()
        prefix,tail=process_stat.rsplit(')',1);fields=tail.split()
        def changed_stat(index,value):
            changed=list(fields);changed[index]=value;return prefix+') '+' '.join(changed)
        with patch.object(m.Path,'read_text',side_effect=[process_stat,changed_stat(19,str(int(born)+1))]):
            with self.assertRaisesRegex(ValueError,'birth'):
                m.attest_process_image(pid,born,expected)
        for dead in ('Z','X','x'):
            with patch.object(m.Path,'read_text',return_value=changed_stat(0,dead)):
                with self.assertRaisesRegex(ValueError,'dead or zombie'):
                    m.attest_process_image(pid,born,expected)
        with patch.object(m.Path,'read_text',side_effect=FileNotFoundError('exited')):
            with self.assertRaisesRegex(ValueError,'exited'):
                m.attest_process_image(pid,born,expected)
        actual_stat=os.stat('/proc/'+str(pid)+'/exe')
        replacement=SimpleNamespace(**{k:getattr(actual_stat,k) for k in ('st_dev','st_ino','st_mode','st_size','st_mtime_ns','st_ctime_ns')})
        replacement.st_ino+=1
        with patch.object(m.os,'stat',side_effect=[actual_stat,replacement]):
            with self.assertRaisesRegex(ValueError,'changed'):
                m.attest_process_image(pid,born,expected)
        for bad in (True,0,-1,'self','../self'):
            with self.assertRaises(ValueError):m.attest_process_image(bad,born,expected)
        # Ordinary regular-file custody is deliberately unchanged.
        with tempfile.TemporaryDirectory(prefix='ux024-proc-attestation-') as directory:
            target=Path(directory)/'regular';target.write_bytes(b'ordinary')
            link=Path(directory)/'link';link.symlink_to(target)
            self.assertEqual(m.regular(target),b'ordinary')
            with self.assertRaises(ValueError):m.regular(link)
if __name__=='__main__':unittest.main(argv=[sys.argv[0],*rest])
