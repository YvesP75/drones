# -*- coding: ISO-8859-1 -*-

import numpy as np

# import ad hoc files
from settings import SIZE, SIZE_Y, SIZE_X, SCALE
from settings import TRANSIT_TO_LAG, TRANSIT_TO_IDLE, TRANSIT_TO_LOSS
from util import Util


class Cars:

    def __init__(self, car_init):

        # statut de la voiture
        # probabilité que la voiture soit encore là
        # (tant qu'elle n'est pas née=0)
        self.belief = [0]
        # timer avant la naissance / O = on peut la chasser
        self.alive = [car_init[1]]
        self.caught = [0]   # voiture detectee = succès
        self.loss = [0]     # 0= plus visible (partie, ou non detectable):échec
        self.time_of_birth = car_init[1]

        # positions =
        # liste en fonction du temps de la position des voitures en mouvement
        car_z = car_init[0]
        position = np.zeros((SIZE_Y, SIZE_X))
        # les colonnes = X et ... les lignes Y
        car_X, car_Y = int(np.real(car_z)/SCALE), int(np.imag(car_z)/SCALE)
        # convention X,Y,Z=coordonnee dans la grille (ex. 10m), x,y,z en m
        position[car_Y, car_X] = 1
        self.positions = []
        self.positions.append(position)

        # idle = liste en fonction du temps de la position des voitures idle
        self.idle = np.zeros((SIZE_Y, SIZE_X))

        # matrice de transition vers la perte (ie, on ne catchera plus la voiture)
        transit_to_loss = np.ones((SIZE_Y, SIZE_X))*TRANSIT_TO_LOSS
        transit_to_loss[0, :] = 1
        transit_to_loss[SIZE_Y-1, :] = 1
        transit_to_loss[:, 0] = 1
        transit_to_loss[:, SIZE_X-1] = 1
        self.loss_transit = transit_to_loss

        # matrice de transition de mouvement
        movement = np.abs(Util.arrayspace(car_X, car_Y, SIZE_X, SIZE_Y))

        self.all_movements = np.array(
            [Util.mypos(
                (np.abs(
                    Util.arrayspace(
                            car_X+X,
                            car_Y+Y,
                            SIZE_X,
                            SIZE_Y
                            )
                        )
                 - movement
                 )
                / np.abs(X+1j*Y)
                )
                for X, Y in [(1, 0), (-1, 0), (0, -1), (0, 1),
                             (1, -1), (1, 1), (-1, -1), (-1, 1)]
                # L,R,U,D, LU,LD, RU, RD
             ]
        )
        # i.e. all_movements=
        # [left,right,up,down, upright,dowleft,downright,up,down]
        # hum, attention à ne pas se mélanger les pinceaux entre X et Y
        self.all_movements /= sum(self.all_movements)

    def reset(self):
        # probabilité que la voiture soit encore là
        # (tant qu'elle n'est pas née=0)
        self.belief = [0]
        # timer avant la naissance / O = on peut la chasser
        self.alive = [self.alive[0]]
        self.caught = [0]   # voiture detectee = succes
        # 0 = plus visible (partie, ou non detectable) = echec
        self.loss = [0]
        # self.time_of_birth inchangée
        # self.loss_transit=transit_to_loss
        # self.all_movements/=sum(self.all_movements)
        self.idle = np.zeros((SIZE_Y, SIZE_X))
        self.positions = [self.positions[0]]

    # définit la prochaine position de la croyance
    def next_state(self, visibility):

        alive = self.alive[-1]

        if alive > 0:
            self.alive.append(alive-1)
            self.positions.append(self.positions[-1])
            self.caught.append(0)
            self.loss.append(0)

        else:

            self.alive.append(0)

            visible = self.positions[-1]*visibility
            caught = np.sum(visible)
            self.caught.append(self.caught[-1]+caught)

            # certaines voitures sont détectées = good job
            # dont certaines étaient idle
            # on en perd au passage
            new_position = self.positions[-1]-visible
            self.idle = self.idle*(1-visibility)
            new_position *= (1-self.loss_transit)

            self.idle = self.idle+np.minimum(
                new_position*TRANSIT_TO_IDLE,
                np.ones((SIZE, SIZE))*100/SIZE
            )
            # certaines s'arretent et deviennent idle

            standing_position = (new_position-self.idle)*TRANSIT_TO_LAG
            moving_position = new_position-standing_position
            # certaines s'arretent momentanement

            new_position = sum(
                [Util.shift(movement*moving_position, XY[1], XY[0])
                    for movement, XY in
                    zip(self.all_movements,
                        [[-1, 0], [1, 0], [0, 1], [0, -1],
                         [-1, 1], [-1, -1], [1, 1], [1, -1]
                         ]
                        )
                 ]
            )
            new_position += standing_position
            belief = np.sum(new_position)
            loss = 1-belief-self.caught[-1]

            self.belief.append(belief)
            self.loss.append(loss)
            self.positions.append(new_position)
