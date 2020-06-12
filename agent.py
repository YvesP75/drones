# -*- coding: ISO-8859-1 -*-


import numpy as np


# import ad hoc files

class Agent:

    def __init__(self):
        self.total_reward = 0.

    def step(self, env):
        all_drones_possible_actions = env.get_actions() #= liste de liste : la liste des actions possibles à un instant donné pour la totalité des drones
        all_drones_action = [] # la liste,  pour chaque drone à l'instant considéré, de l'action choisie
        for drone_possible_actions in all_drones_possible_actions: #pour chaque drone
            all_drones_action.append(np.random.choice(drone_possible_actions))
        next_state, reward, is_done, obs = env.step(all_drones_action)
