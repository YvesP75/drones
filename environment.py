# -*- coding: ISO-8859-1 -*-

import numpy as np
import pandas as pd


# from acme import environment_loop
# from acme import networks
# from acme.adders import reverb as adders
# from acme.agents import actors_tf2 as actors
# from acme.datasets import reverb as datasets
# from acme.wrappers import gym_wrapper
# from acme import specs

# import ad hoc files
from settings import FIRST, MID, LAST, SECOND_EYE
from settings import TIME_LENGTH, SIZE_X, SIZE_Y
from util import Util
from cars import Cars
from drones import Drones


class Environment:

    def __init__(self, drones_positions, cars_inits):
        self.steps_left = TIME_LENGTH
        # création des voitures
        self.cars = [Cars(car_init) for car_init in cars_inits]
        # création des drones
        self.drones = [Drones(drone_z, 0) for drone_z in drones_positions]
        # la visibilité au niveau env est le cumul des visibiités des drones
        self.visibilities = [np.zeros((SIZE_X, SIZE_Y)) < 0]
        # pour se lier avec la librairie Acme
        self.spec = Environment_spec(
            number_of_drones=len(drones_positions),
            number_of_cars=len(cars_inits)
        )

    def reset(self):
        self.steps_left = TIME_LENGTH
        self.cars.reset()
        self.drones.reset()
        self.visibilities = [np.zeros((SIZE_X, SIZE_Y)) < 0]
        self.step([])

    def step(self, actions):

        if self.steps_left == 0:
            self.reset()
        self.steps_left -= 1

        if len(actions) > 0:
            # 1 calcul de la couverture de visibilité des drones
            # suite à leur mouvement
            new_visi = np.zeros((SIZE_X, SIZE_Y))
            for drone, action in zip(self.drones, actions):
                drone.next_state(action)
                new_visi += drone.visibility
            new_visi = new_visi > 0
            # ce qui compte, c'est que la case soit vue au moins une fois
            self.visibilities.append(new_visi)

            # calcul de l'état des voitures : après un intervalle de temps
            # et en fonction de la nouvelle visi des drones
            for car in self.cars:
                car.next_state(new_visi)

        # retour des états pour le cycle de RL
        return (
            self.get_step_type(),
            self.get_reward(),
            self.get_discount(),
            self.get_observation()
        )

    def get_step_type(self):
        if self.steps_left == 0:
            return LAST
        elif self.steps_left == TIME_LENGTH:
            return FIRST
        else:
            return MID

# reward simple :
# plus j'augmente la proba d'attraper une voiture = somme des caughts.
# On aurait pu fire un reward négatif, sommer les pertes. Un mix? à tester

    def get_reward(self):
        reward = 0
        for car in self.cars:
            reward += car.caught[-1]-car.caught[-2]
        return reward

    # à voir si nécessaire : il y a déjà une déperdition naturelle
    def get_discount(self):
        return 0.01

    # L'observation est ce qui est retenu de l'environnement pour être
    # injecté dans l'agent qui fait l'optimisation
    # typiquement, un vecteur de données qui résume au mieux la situation
    # et sa dynamique. C'est un choix impportant.
    # Cette fonction définit l'observation par secteur de pi/4 et par couronne
    # elle donne 3 valeurs :
    #   - la somme de la croyance sur le secteur
    #   - l'indice de la coouronne à partir duquel on a plus de 20% de croyance
    #   - l'indice de la couronne à partir duquel on a plus de 80% de croyance
    # ces 3 valeurs sont calculées pour chacune des voitures
    def get_observation(self):  # attention, checker les nombres de crowns
        obs = []
        for car in self.cars:
            obs.append(car.get_observation())
        return obs

    def get_actions(self):  # pas utilisé par Acme??
        all_drones_possible_actions = np.array(
            [drone.get_actions() for drone in self.drones]
            )
        return all_drones_possible_actions

    def is_done(self):
        return self.steps_left == 0

    '''
        l'observation donne une vue simplifiée de la croyance par voiture
        à partir de sa position initiale
        la croyanve évolue de manière centripète
            - le poids du secteur (integer de 1 à 10)
            - l'indice de la couronne qui permet de dépasser 20% du poids total
                (integer de 1 à 10)
            - l'indice de la couronne qui permet de dépasser 80% du poids total
                (integer de 1 à 10)
    '''

    def observation_spec(self):
        return self.environment_spec.observations

    def reward_spec(self):
        return self.environment_spec.rewards

    def discount_spec(self):
        return self.environment_spec.discounts

    def action_spec(self):
        return self.environment_spec.actions

    # ces fonctions ne devraient pas être ici mais plutôt dans la visu/show
    def get_drones_positions(self, time_index):
        return pd.DataFrame(
            np.array(Util.z_to_latlon(
                [drone.positions[time_index] for drone in self.drones])).T,
            columns=['lat', 'lon']
            )

    def get_second_eyes_positions(self, time_index):
        return pd.DataFrame(
            np.array(Util.z_to_latlon([
                drone.positions[time_index]+drone.caps[time_index]*SECOND_EYE
                for drone in self.drones]
                )).T,
            columns=['lat', 'lon'])

    def get_observations_points(self, time_index):
        obs = []
        for car in self.cars:
            obs = np.concatenate((obs, car.get_observation_points(time_index)))
        df = pd.DataFrame(
                 np.array(Util.z_to_latlon(obs)).T,
                 columns=['lat', 'lon'])
        return df


class Environment_spec:

    def __init__(self, number_of_cars, number_of_drones):
        '''
        self.observations = specs.DiscreteArray(
            shape=(10*number_of_cars,),
            dtype=np.int32,
            name='observation'
        )
        self.rewards = specs.BoundeedArray(
            shape=(),
            dtype=np.dtype('float32'),
            name='reward',
            minimum=0.0,
            maximum=1.0*number_of_cars
        )
        self.discounts = specs.BoundedArray(
            shape=(),
            dtype=np.dtype('float32'),
            name='discount',
            minimum=0.0,
            maximum=1.0
        )
        self.actions = specs.BoundedArray(
            shape=(number_of_drones,),
            dtype=np.dtype('float32'),
            name='action',
            minimum=[-np.pi],
            maximum=[np.pi]
        )
        '''


class TimeStep:

    def __init__(self, step_type):
        self.step_type = step_type

    def last(self):
        return self.step_type == LAST

    def mid(self):
        return self.step_type == MID

    def first(self):
        return self.step_type == FIRST
