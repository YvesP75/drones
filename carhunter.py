
# -*- coding: ISO-8859-1 -*-
import sys

#import ad hoc files
from environment import Environment
from agent import Agent
from show import Show


def run_episode():
    agent=Agent()
    env=Environment(
        [8500+5500j,8000+5300j,4000+2000j,5000+5000j,2000+6000j,8000+5000j,7000+5000j,3000+3000j], #les drones
        [[8200+4500j,0],[4000+4400j,35],[3500+4400j,34],[2800+3400j,23]
        ])  #les cars

        while not env.is_done():
            agent.step(env)
    return env

Show.run(env)


if __name__ == "__main__":
    env=run_episode()
    if argv[1] == "go":
        Show.run(env)
