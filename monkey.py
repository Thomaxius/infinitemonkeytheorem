import random
import string
import datetime
import time
import threading
import multiprocessing
import queue

from rapidfuzz import fuzz, process

NUM_MONKEYS = 1000
NUM_PROCESSES = max(1, multiprocessing.cpu_count() - 1)  # one core is left for the checker
BATCH = 1000  # lines a monkey types before flushing its counts to the shared totals
SAMPLE_EVERY = 10000  # each monkey offers one of its strings to the checker this often
QUEUE_SIZE = 100
EASTER_EGG = 'It was the best of times, it was the blurst of times.'

with open('src/shakespeare.txt', 'r') as shakespeare:
    shakespeare_set = set(line for line in shakespeare if not line.isupper())  # Remove copyright, etc.
shortest_sentence = len(min(shakespeare_set, key=len))
longest_sentence = len(max(shakespeare_set, key=len))
shakespeare_lines = [line.rstrip('\n') for line in shakespeare_set if line.strip()]

alphabet = string.ascii_lowercase + ' '


def get_monkey_typed_string():
    length = random.randrange(shortest_sentence, longest_sentence + 1)
    return ''.join(random.choices(alphabet, k=length))


def is_shakespeare(text):
    return text + '\n' in shakespeare_set


def log_found(shared, monkey_id, text, lines, chars):
    print("Monkey %s found shakespeare!\n Line: %s, characters typed: %s" % (monkey_id, lines, chars))
    with shared['lock']:
        with open("src/founditems.txt", "a") as founditems:
            founditems.write('Monkey %s: %s Date found: %s\n' % (monkey_id, text, datetime.datetime.now()))


def log_easter_egg(shared, text):
    with shared['lock']:
        with open("src/founditems.txt", "a") as founditems:
            founditems.write(EASTER_EGG + '. ' + text + ' Date found: ' + str(datetime.datetime.now()) + '\n')


def flush(shared, lines, chars):
    """Adds a monkey's counts to the totals; returns True if the easter egg line was crossed."""
    with shared['lock']:
        start = shared['lines'].value
        shared['lines'].value += lines
        shared['chars'].value += chars
        if shared['lines'].value >= shared['next_report'].value:
            print('Line %s, Characters typed: %s' % (shared['lines'].value, shared['chars'].value))
            shared['next_report'].value += 100000
        return start < shared['egg_line'] <= shared['lines'].value


def offer_sample(samples, text):
    """Hands a string to the checker, dropping it if the checker is behind."""
    try:
        samples.put_nowait(text)
    except queue.Full:
        pass


def closest_match(text, cutoff):
    """Returns (line, score) for the best match scoring above cutoff, else None."""
    result = process.extractOne(text, shakespeare_lines, scorer=fuzz.ratio, score_cutoff=cutoff)
    if result is None or result[1] <= cutoff:
        return None
    return result[0], result[1]


def log_closest(shared, text, line, score):
    print('New closest (%.1f%%): "%s" ~ "%s"' % (score, text, line))
    with shared['lock']:
        with open("src/founditems.txt", "a") as founditems:
            founditems.write('Closest %.1f%%: "%s" ~ "%s" Date found: %s\n' % (score, text, line, datetime.datetime.now()))


def checker(shared):
    best = 0.0
    try:
        while True:
            text = shared['samples'].get()
            match = closest_match(text, best)
            if match:
                line, best = match
                log_closest(shared, text, line, best)
    except KeyboardInterrupt:
        pass


def monkey(shared, monkey_id):
    lines = 0
    chars = 0
    typed = 0
    while True:
        text = get_monkey_typed_string()
        lines += 1
        typed += 1
        chars += len(text)
        if typed % SAMPLE_EVERY == 0:
            offer_sample(shared['samples'], text)
        if is_shakespeare(text):
            log_found(shared, monkey_id, text, lines, chars)
        if lines == BATCH:
            if flush(shared, lines, chars):
                log_easter_egg(shared, text)
            lines = 0
            chars = 0


def worker(shared, first_id, count):
    for i in range(first_id, first_id + count):
        threading.Thread(target=monkey, args=(shared, i), daemon=True).start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass


def put_monkeys_to_work():
    print('%s monkeys have begun working across %s processes.' % (NUM_MONKEYS, NUM_PROCESSES))
    shared = {
        'lock': multiprocessing.Lock(),
        'lines': multiprocessing.Value('q', 0, lock=False),
        'chars': multiprocessing.Value('q', 0, lock=False),
        'next_report': multiprocessing.Value('q', 100000, lock=False),
        'egg_line': random.randrange(1000000, 1000000000),
        'samples': multiprocessing.Queue(maxsize=QUEUE_SIZE),
    }
    with open("src/founditems.txt", "a") as founditems:
        founditems.write('\nSearch started: ' + str(datetime.datetime.now()) + '\n')

    per_process = -(-NUM_MONKEYS // NUM_PROCESSES)  # ceiling division
    processes = [
        multiprocessing.Process(target=worker, args=(shared, p * per_process, per_process), daemon=True)
        for p in range(NUM_PROCESSES)
    ]
    checker_process = multiprocessing.Process(target=checker, args=(shared,), daemon=True)
    for p in processes + [checker_process]:
        p.start()
    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print('Monkeys stopped.')
        for p in processes + [checker_process]:
            p.terminate()


if __name__ == '__main__':
    put_monkeys_to_work()
