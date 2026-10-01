import unittest
from pathlib import Path
from app import analyze

class LogTests(unittest.TestCase):
    def test_demo(self):
        d=analyze(Path(__file__).with_name('sample.log').read_text())
        self.assertEqual(d['counts'],{'ERROR':5,'WARNING':3,'INFO':5,'DEBUG':2,'OTHER':1})
        self.assertEqual(d['error_groups'][0],{'message':'Database connection failed','count':3})
    def test_formats_and_message_keywords(self):
        d=analyze('[2026-10-01T12:00:00.123Z] [error] failed\nINFO The word ERROR is in the message\nFATAL: failed\nplain error sentence')
        self.assertEqual(d['counts']['ERROR'],2)
        self.assertEqual(d['counts']['INFO'],1)
        self.assertEqual(d['counts']['OTHER'],1)
        self.assertEqual(d['error_groups'][0]['count'],2)
    def test_blank(self):
        with self.assertRaises(ValueError):analyze(' \n')
    def test_limit(self):
        with self.assertRaises(ValueError):analyze('INFO x\n'*50001)

if __name__=='__main__':unittest.main()
