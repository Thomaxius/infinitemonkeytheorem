import multiprocessing
import os
import queue
import unittest
from unittest import mock

os.chdir(os.path.dirname(os.path.abspath(__file__)))  # monkey.py reads src/shakespeare.txt relative to cwd
import monkey


def make_shared(egg_line=10**9, next_report=100000):
    return {
        'lock': multiprocessing.Lock(),
        'lines': multiprocessing.Value('q', 0, lock=False),
        'chars': multiprocessing.Value('q', 0, lock=False),
        'next_report': multiprocessing.Value('q', next_report, lock=False),
        'egg_line': egg_line,
    }


class TestTyping(unittest.TestCase):
    def test_length_within_line_bounds(self):
        for _ in range(200):
            text = monkey.get_monkey_typed_string()
            self.assertGreaterEqual(len(text), monkey.shortest_sentence)
            self.assertLessEqual(len(text), monkey.longest_sentence)

    def test_only_uses_alphabet(self):
        for _ in range(200):
            self.assertTrue(set(monkey.get_monkey_typed_string()) <= set(monkey.alphabet))


class TestMatching(unittest.TestCase):
    def test_real_line_matches(self):
        line = next(l for l in monkey.shakespeare_set if l.strip())
        self.assertTrue(monkey.is_shakespeare(line.rstrip('\n')))

    def test_gibberish_does_not_match(self):
        self.assertFalse(monkey.is_shakespeare('zzqx not a line zzqx'))

    def test_needs_exact_match(self):
        line = next(l for l in monkey.shakespeare_set if len(l.strip()) > 5)
        self.assertFalse(monkey.is_shakespeare(line.rstrip('\n')[:-1]))


class TestFlush(unittest.TestCase):
    def test_accumulates_totals(self):
        shared = make_shared()
        monkey.flush(shared, 10, 100)
        monkey.flush(shared, 5, 50)
        self.assertEqual(shared['lines'].value, 15)
        self.assertEqual(shared['chars'].value, 150)

    def test_easter_egg_triggers_once_when_crossed(self):
        shared = make_shared(egg_line=15)
        self.assertFalse(monkey.flush(shared, 10, 0))
        self.assertTrue(monkey.flush(shared, 10, 0))
        self.assertFalse(monkey.flush(shared, 10, 0))

    def test_progress_report_advances(self):
        shared = make_shared(next_report=100)
        with mock.patch('builtins.print') as fake_print:
            monkey.flush(shared, 150, 0)
        fake_print.assert_called_once()
        self.assertEqual(shared['next_report'].value, 100100)


class TestClosestMatch(unittest.TestCase):
    def test_exact_line_scores_100(self):
        line = next(l for l in monkey.shakespeare_lines if len(l) > 5)
        self.assertEqual(monkey.closest_match(line, 0.0), (line, 100.0))

    def test_near_miss_scores_below_100(self):
        line = next(l for l in monkey.shakespeare_lines if len(l) > 10)
        matched, score = monkey.closest_match(line[:-1] + '#', 0.0)
        self.assertLess(score, 100.0)
        self.assertGreater(score, 80.0)

    def test_returns_none_when_cutoff_not_beaten(self):
        line = next(l for l in monkey.shakespeare_lines if len(l) > 5)
        self.assertIsNone(monkey.closest_match(line, 100.0))


class TestSampleQueue(unittest.TestCase):
    def test_offer_sample_drops_when_full(self):
        samples = multiprocessing.Queue(maxsize=1)
        monkey.offer_sample(samples, 'first')
        monkey.offer_sample(samples, 'second')  # must not block or raise
        self.assertEqual(samples.get(timeout=1), 'first')
        with self.assertRaises(queue.Empty):
            samples.get(timeout=0.2)


class TestLogging(unittest.TestCase):
    def test_log_found_writes_monkey_and_text(self):
        shared = make_shared()
        opener = mock.mock_open()
        with mock.patch('builtins.open', opener), mock.patch('builtins.print'):
            monkey.log_found(shared, 7, 'to be or not to be', 1, 18)
        opener.assert_called_once_with('src/founditems.txt', 'a')
        written = opener().write.call_args[0][0]
        self.assertIn('Monkey 7', written)
        self.assertIn('to be or not to be', written)

    def test_log_easter_egg_writes_quote(self):
        shared = make_shared()
        opener = mock.mock_open()
        with mock.patch('builtins.open', opener):
            monkey.log_easter_egg(shared, 'abc')
        written = opener().write.call_args[0][0]
        self.assertIn(monkey.EASTER_EGG, written)
        self.assertIn('abc', written)


if __name__ == '__main__':
    unittest.main()
