import random
import string
import datetime
import time

shakespeare = open('src/shakespeare.txt', 'r')
shakespeare_lines = ''.join(shakespeare.readlines())
shakespeare.close()

founddict = {}

def get_monkey_typed_string():
    alphabet = string.ascii_lowercase + ' '
    monkeytyped = ''
    for x in range ((random.randrange(8,77))): # 8 and 77 are the shortest and longest lines in the file
        monkeytyped += random.choice(alphabet)
    return monkeytyped

def is_shakespeare(string):
    return string in shakespeare_lines

def start_shit():
    print('The monkey has begun working.')
    characterstyped = 0
    line = 0
    randomnumber = random.randrange(1000000,1000000000)
    datestarted = datetime.datetime.now()
    founditems = open("src/founditems.txt", "a")
    founditems.write('\nSearch started: ' + str(datestarted))
    while True:
        line += 1
        monkeytyped = get_monkey_typed_string()
        print(line, monkeytyped)
        characterstyped += len(monkeytyped)
        if is_shakespeare(monkeytyped):
            print("Monkey found shakespeare!\n Line: %s, characters typed: %s"  % (line, characterstyped))
            time.sleep(10)
            founditems.write(str(line) + '.' + monkeytyped + ' ' + 'Date found: ' + str(datetime.datetime.now()) + '\n')
        if line%100000==0:
            print('Line %s, Characters typed: %s' % (line, characterstyped))
        if line == randomnumber:
            founditems.write('It was the best of times, it was the blurst of times.' + '.' + monkeytyped + ' ' + 'Date found: ' + str(datetime.datetime.now()) + '\n')

start_shit()


