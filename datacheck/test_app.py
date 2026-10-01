import unittest
from app import analyze

class QualityTests(unittest.TestCase):
    def test_sample(self):
        from pathlib import Path
        result = analyze(Path('sample.csv').read_text())
        self.assertEqual((result['rows'],result['missing_cells'],result['duplicates'],result['cleaned_rows']), (6,3,1,5))
        self.assertEqual(result['completeness'],87.5)
    def test_quoted_multiline_and_empty(self):
        result = analyze('name,note\n"A,B","line1\nline2"\nC,\n')
        self.assertEqual(result['missing_cells'],1)
        self.assertIn('line1\nline2',result['cleaned_csv'])
    def test_invalid_structure(self):
        for text in ['', 'a,b\n', 'a,a\n1,2\n', 'a,b\n1\n', 'a,b\n"unclosed,2']:
            with self.assertRaises((ValueError, __import__('csv').Error)):
                analyze(text)

if __name__ == '__main__':
    unittest.main()
