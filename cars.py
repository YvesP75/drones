# -*- coding: ISO-8859-1 -*-

import numpy as np

# import ad hoc files
from settings import SIZE, SIZE_Y, SIZE_X, SCALE, NUMBER_OF_CROWNS
from settings import NUMBER_OF_SECTORS, LOW, HIGH
from settings import TRANSIT_TO_LAG, TRANSIT_TO_IDLE, TRANSIT_TO_LOSS
from util import Util


class Cars:

    def __init__(self, car_init):

        # probabilité que la voiture soit encore là
        # (tant qu'elle n'est pas née=0)
        self.belief = [0]
        # timer avant la naissance / O = on peut la chasser
        self.alive = [car_init[1]]
        self.caught = [0]   # voiture detectee = succès
        self.loss = [0]     # 0= plus visible (partie ou non detectable)
        self.time_of_birth = car_init[1]

        self.car_z = car_init[0]
        # positions =
        # liste en fonction du temps de la position des voitures en mouvement
        position = np.zeros((SIZE_Y, SIZE_X))
        # les colonnes = X et ... les lignes Y
        car_X = int(np.real(self.car_z)/SCALE)
        car_Y = int(np.imag(self.car_z)/SCALE)
        # convention X,Y,Z=coordonnee dans la grille (ex. 10m), x,y,z en m
        position[car_Y, car_X] = 1
        self.crowns, self.sectors, self.points = (
            self.create_radar(car_X, car_Y)
            )
        self.observations = []
        self.positions = []
        self.positions.append(position)

        # idle = liste en fonction du temps de la position des voitures idle
        self.idle = np.zeros((SIZE_Y, SIZE_X))

        # matrice de transition vers la perte
        # (ie, on ne catchera plus la voiture)
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

            # certaines s'arretent et deviennent idle
            self.idle = self.idle+np.minimum(
                new_position*TRANSIT_TO_IDLE,
                np.ones((SIZE, SIZE))*10/SIZE
            )


            standing_position = (
                (new_position-self.idle)*TRANSIT_TO_LAG
                + self.idle
                )
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

    # crée le "radar" autour de la voiture pour exprimer une vision
    # simplifiée de la croyance en observation pour le renforcement
    def create_radar(self, car_X, car_Y):
        crown_size = min(SIZE_X, SIZE_Y)/(NUMBER_OF_CROWNS*1)
        sector_angle = 2*np.pi/NUMBER_OF_SECTORS

        # carspace = complex matrix giving relative positions
        # against initial car position
        car_space = Util.arrayspace(
            car_Y,
            car_X,
            SIZE_Y,
            SIZE_X
        )
        crowns = []
        for crown_index in range(NUMBER_OF_CROWNS):
            crowns.append(Util.mycrown(
                car_space,
                crown_index,
                crown_size
                )
            )
        sectors = []
        for sector_index in range(NUMBER_OF_SECTORS):
            sectors.append(Util.mysector(
                car_space,
                sector_index,
                sector_angle
                )
            )
        points = [
            [
            self.car_z
            +crown_index*crown_size*SCALE *
                np.exp(1j* (sector_index + 0.5) *sector_angle)
            for crown_index in  range(NUMBER_OF_CROWNS)
            ] for sector_index in range(NUMBER_OF_SECTORS)

        ]

        return crowns, sectors, points


    def get_observation(self):
        obs=[]
        if self.alive[-1] == 0:  # si la voiture est vivante
            for sector in self.sectors:
                sector_belief = sector*self.positions[-1]
                sector_belief_sum = np.sum(sector_belief)
                distri = [np.sum(sector_belief*crown) for crown in self.crowns]
                obs=np.concatenate((
                obs,
                [int(sector_belief_sum*NUMBER_OF_SECTORS)],
                Util.get_interval(
                    distri,
                    LOW*sector_belief_sum,
                    HIGH*sector_belief_sum
                    )
                ))
        else:
            for _ in range(NUMBER_OF_SECTORS):
                np.concatenate((obs, [0, 0, NUMBER_OF_SECTORS-1]))
        obs = np.cast[int](obs)

        self.observations.append(obs)
        return obs

    def get_observation_points(self, time_index):
        obs_points = []
        for sector_index in range(NUMBER_OF_SECTORS):
            obs_points.append(
                self.points
                    [sector_index]
                    [self.observations[time_index][sector_index*3 +1]]
            )
            obs_points.append(
                self.points
                    [sector_index]
                    [self.observations[time_index][sector_index*3 +2]]
            )
        return obs_points
