
import numpy as np
import pandas as pd

from util import Util
from settings import *

class Drones:

    def __init__(self,drone_z,target_z):
        #attention, tout exprimer en m
        self.positions=[drone_z]
        self.caps=[(target_z-drone_z)/np.abs(target_z-drone_z)]
        self.visibility=np.zeros((SIZE_X,SIZE_Y))<0
        self.actions=[FULL_STEAM]

    def reset():
        self.positions=[self.positions[0]]
        self.caps=[self.caps[0]]
        self.visibility=np.zeros((SIZE_X,SIZE_Y))<0
        self.actions=[FULL_STEAM]


    def next_state(self,action):

        #updates position (of a single drone)
        new_pos_cap=self.next_possible_positions_and_caps()
        self.positions.append(new_pos_cap[0][action])
        self.caps.append(new_pos_cap[1][action])
        self.actions.append(action)

        #updates visibility
        if action!=STOP: self.sees()

    def next_possible_positions_and_caps(self):
        next_pos=self.positions[-1]
        cap=self.caps[-1]
        left=np.exp(1j*np.pi/4)*cap
        right=np.exp(-1j*np.pi/4)*cap
        next_pos+=np.array([cap*FORWARD_STEP,right*SIDE_STEP,left*SIDE_STEP,0])
        next_cap=np.array([cap,right,left,cap])
        return next_pos, next_cap

    def get_actions(self):  #si on sort du cadre, les actions qui conduisent à dégrader la situation sont exclues
        actions=[FULL_STEAM,RIGHT,LEFT,STOP]
        position=self.positions[-1]
        if np.abs(Util.complex_outofbound(position,0,THEATER_LENGTH))>0 : #i.e. le drone sort du cadre
            actions=[]
            distances=np.abs(Util.complex_outofbound(self.next_possible_positions_and_caps()[0],0,THEATER_LENGTH))
            min=np.amin(distances[:-1])
            for action in [FULL_STEAM,RIGHT,LEFT]:
                if distances[action]==min : actions.append(action)
        return actions

    # le domaine de visibilité des drones est une ellipse dont l'équation est donnée par !z-a!+!z-b!<c
    def sees(self):
        position_a=self.positions[-1]/SCALE
        z_moins_a=Util.arrayspace(np.real(position_a),np.imag(position_a),SIZE_Y,SIZE_X)
        position_b=position_a+self.caps[-1]*SECOND_EYE/SCALE
        z_moins_b=Util.arrayspace(np.real(position_b),np.imag(position_b),SIZE_X,SIZE_Y)
        self.visibility=(np.abs(z_moins_a)+np.abs(z_moins_b))<(VIEW_LENGTH/SCALE+1)
