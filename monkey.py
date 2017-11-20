import random
import string
import datetime
import time
import threading

shakespeare = open('src/shakespeare.txt', 'r')
shakespeare_list = shakespeare.readlines()
shakespeare_set = set([line for line in shakespeare_list if not line.isupper()]) #Remove copyright, etc.
shortest_sentence = len(min(shakespeare_set, key=len))
longest_sentence = len(max(shakespeare_set, key=len))
shakespeare.close()

def get_monkey_typed_string():
    alphabet = string.ascii_lowercase + ' '
    monkeytyped = ''
    for x in range ((random.randrange(shortest_sentence,longest_sentence))):
        monkeytyped += random.choice(alphabet)
    return monkeytyped

def is_shakespeare(string):
    return string + '\n' in shakespeare_set

def put_monkey_to_work():
    print('The monkey has begun working.')
    characterstyped = 0
    line = 0
    randomnumber = random.randrange(1000000,1000000000)
    datestarted = datetime.datetime.now()
    founditems = open("src/founditems.txt", "a")
    founditems.write('\nSearch started: ' + str(datestarted))
    founditems.close()
    easteregg = 'It was the best of times, it was the blurst of times.'
    while True:
        line += 1
        monkeytyped = get_monkey_typed_string()
        characterstyped += len(monkeytyped)
        if is_shakespeare(monkeytyped):
            print("Monkey found shakespeare!\n Line: %s, characters typed: %s"  % (line, characterstyped))
            time.sleep(10)
            founditems = open("src/founditems.txt", "a")
            founditems.write(str(line) + '. ' + monkeytyped + ' ' + 'Date found: ' + str(datetime.datetime.now()) + '\n')
            founditems.close()
        if line%100000==0:
            print('Line %s, Characters typed: %s' % (line, characterstyped))
        if line == randomnumber:
            founditems = open("src/founditems.txt", "a")
            founditems.write(easteregg + '. ' + monkeytyped + ' ' + 'Date found: ' + str(datetime.datetime.now()) + '\n')
            founditems.close()

put_monkey_to_work()


