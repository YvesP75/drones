
# -*- coding: ISO-8859-1 -*-
import sys
import getopt

# import ad hoc files
from environment import Environment
from agent import Agent
from show import Show


def run_episode(drones, cars, go='False'):
    print(drones, cars, go)
    agent = Agent()
    env = Environment(drones, cars)
    while not env.is_done():
        agent.step(env)

    if go:
        Show.run(env)


def main(argv):
    drones = [8500+5500j, 8000+5300j, 4000+2000j]
    cars = [[8200+4500j, 0]]
    long_drones = [8500+5500j, 8000+5300j, 4000+2000j, 5000+5000j, 2000+6000j,
                   8000+5000j, 7000+5000j, 3000+3000j]
    long_cars = [[8200+4500j, 0], [4000+4400j, 35],
                 [3500+4400j, 34], [2800+3400j, 23]]
    global _time_length
    _time_length = 30

    try:
        opts, args = getopt.getopt(
            argv, 'c:d:hLt:CD', ['cars=', 'drones=', 'help', 'long', 'time=']
            )
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
        elif opt in ('-c', '--cars'):
            cars = arg
        elif opt in ('-d', '--drones'):
            drones = args
        elif opt in ('-C', '--longcars'):
            cars = long_cars
        elif opt in ('-D', '--longdrones'):
            drones = long_drones
        elif opt in ('-L', '--long'):
            _time_length = 200
        elif opt in ('-t', '--time'):
            _time_length = arg

    if argv == [] or argv[0] == 'False':
        print('arg = False')
        run_episode(drones, cars, False)
    elif arg[0] == 'True':
        print('arg = [True]')
        run_episode(drones, cars, True)
    else:
        print(arg)
        print('default')
        usage()


def usage():
    print('usage: python carhunter.py [-h --help] [-C] [-D]')
    print('                           [-c | --cars = <[[car_z,time]]>]')
    print('                           [-d | --drones = <[drone_z]]>')
    print('                           [-L | --long] [-t | --time = <value>]')


if __name__ == "__main__":
    main(sys.argv[1:])
