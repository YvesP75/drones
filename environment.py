# -*- coding: ISO-8859-1 -*-

import numpy as np
import pandas as pd


import numpy as np

import copy
import imageio
import base64
import IPython


from acme import environment_loop
from acme import networks
from acme.adders import reverb as adders
from acme.agents import actors_tf2 as actors
from acme.datasets import reverb as datasets
from acme.wrappers import gym_wrapper
from acme import specs

#import ad hoc files
from settings import *
from util import Util
from cars import Cars
from drones import Drones


class Environment:

    def __init__(self,drones_positions,cars_inits):
        self.steps_left=TIME_LENGTH
        self.cars=[Cars(car_init) for car_init in cars_inits] #Cars(car_z) #
        self.drones=[Drones(drone_z,0) for drone_z in drones_positions]
        self.visibilities=[np.zeros((SIZE_X,SIZE_Y))<0]      #la visibilité au niveau env est le cumul des visibiités des drones
        self.spec=Environment_spec(number_of_drones=len(drones_positions),number_of_cars=len(car_inits))

    def reset():
        self.steps_left=TIME_LENGTH
        self.cars.reset()
        self.drones.reset()
        self.visibilities=[np.zeros((SIZE_X,SIZE_Y))<0]
        self.step([])


    def step(self,actions):

        if self.steps_left == 0: self.reset()
        self.steps_left-=1

        if len(actions)>0 :

            #1 czlcul de la couverture de visibilité des drones suite à leur mouvement
            new_visi=np.zeros((SIZE_X,SIZE_Y))
            for drone,action in zip(self.drones,actions):
                drone.next_state(action)
                new_visi+=drone.visibility
            new_visi=new_visi>0  #ce qui compte, c'est que la case soit vue au moins une fois
            self.visibilities.append(new_visi)

            #calcul de l'état des voitures : après un intervalle de temps et en fonction de la nouvelle visi des drones
            for car in self.cars : car.next_state(new_visi)

        #retour des états pour le cycle de RL
        return self.get_step_type(), self.get_reward(), self.get_discount(), self.get_observation()


    def get_step_type(self):
        FIRST, MID, LAST = -1, 0, 1 #à chnager pour s'aligner sur l'API Acme
        if self.steps_left==0:
            return LAST
        elif self.steps_left==TIME_LENGTH :
            return FIRST
        else :
            return MID


    def get_reward(self): #reward simple : plus j'augmente la proba d'attraper une voiture = somme des caughts. On aurait pu fire un reward négatif, sommer les pertes. Un mix? à tester
        reward=0
        for car in self.cars :
            reward+=car.caught[-1]-car.caught[-2]
        return reward

    def get_discount(self): #à voir si nécessaire : il y a déjà une déperdition naturelle
        return 0.01

    def get_observation(self): #attanion, checker les nombres de crowns
        crown_size=min(SIZE_X,SIZE_Y)/NUMBER_OF_CROWNS*2/3
        sector_size=2*np.pi/NUMBER_OF_SECTORS
        obs=[]
        for car in self.cars :
            if car.alive[-1]==0 :  # si la voiture est vivante
                filter=Util.array_space(car.positions[0][1], car.positions[0][0],SIZE_Y, SIZE_X)
                for sector in range(0,NUMBER_OF_SECTORS*sector_size,sector_size):
                    car_sector=max(Util.mysector(filter,sector, sector_size)*car.positions[-1],1)
                    car_sector_presence=np.sum(car_sector)
                    distri=[np.sum(Util.mycrown(car_sector, crown, crown_size))
                        for crown in range(0,NUMBER_OF_CROWNS*crown_size,crown_size)]
                    np.concatenate(obs, int(car_sector_presence * NUMBER_OF_SECTORS), Util.get_interval(distri,low*car_sector_presence, high*car_sector_presence))
            else :
                for _ in range(number_of_sectors): np.concatenate(obs, [0,0,NUMBER_OF_SECTORS-1])
        return obs

    def get_actions(self) : #pas utilisé par Acme??
        all_drones_possible_actions=np.array([drone.get_actions() for drone in self.drones])
        return all_drones_possible_actions

    def is_done(self):
        return self.steps_left==0


    '''
            l'observation donne une vue simplifiée de la croyance par voiture à partir de sa position initiale
            la croyanve évolue de manière centripète
                - le poids du secteur (integer de 1 à 10)
                - l'indice de la couronne qui permet de dépasser 20% du poids total (integer de 1 à 10)
                - l'indice de la couronne qui permet de dépasser 80% du poids total (integer de 1 à 10)
    '''
    def observation_spec(self):
        return  self.environment_spec.observations


    def reward_spec(self):
        return  self.environment_spec.rewards

    def discount_spec(self):
        return  self.environment_spec.discounts

    def action_spec():
        return self.environment_spec.actions


    # ces fonctions ne devraient pas être ici mais plutôt dans la visu/show
    def get_drones_positions(self,time_index):
        return pd.DataFrame(
            np.array(Util.z_to_latlon([drone.positions[time_index] for drone in self.drones])).T,
            columns=['lat','lon'])


    def get_second_eyes_positions(self,time_index):
        return pd.DataFrame(
            np.array(Util.z_to_latlon([
                drone.positions[time_index]+drone.caps[time_index]*SECOND_EYE for drone in self.drones]
                )).T,
            columns=['lat','lon'])


class Environment_spec(number_of_cars,number_of_drones):

    self.observations=specs.DiscreteArray(shape=(10*number_of_cars,),dtype=np.int32, name='observation')
    self.rewards=specs.BoundeedArray(shape=(), dtype=dtype('float32'), name='reward', minimum=0.0, maximum=1.0*number_of_cars)
    self.discounts=BoundedArray(shape=(), dtype=dtype('float32'), name='discount', minimum=0.0, maximum=1.0)
    self.actions=BoundedArray(shape=(number_of_drones,), dtype=dtype('float32'), name='action', minimum=[-np.pi], maximum=[np.pi])


class TimeStep:

    def __init__(self, step_type):
        self.step_type=step_type

    def last(self):
        return self.step_type==LAST

    def mid(self):
        return self.step_type==MID

    def first(self):
        return self.step_type==FIRST
