# temps de simulation
TIME_LENGTH = 5

# taille du quadrillage
SIZE = SIZE_X = SIZE_Y = 20

###
TIME_SLEEP = 0.01

ZERO_X = 2.25125
ZERO_Y = 48.8130

# taille de la zone en m
THEATER_LENGTH = 10000

# typiquemeent 1 carreau=10m
SCALE = THEATER_LENGTH/SIZE

# propabilite de transition de statut
TRANSIT_TO_IDLE = 0.01         # proba que la voiture s'arrête sans disparaître
TRANSIT_TO_LOSS = 0.000        # proba de perte définiive
TRANSIT_TO_LAG = 0.2
# proba que la voiture reste en mouvement mais n'a pas le temps de changer
# de case, indicateur de dispersion

THRESHOLD = 10                # décalage pour éviter les problèmes d'arrondis

FULL_STEAM = 0
RIGHT = 1
LEFT = 2
STOP = 3
FORWARD_STEP = 50  # en m/s 1m/s=3,6 km/h
SIDE_STEP = 20
SECOND_EYE = 300
VIEW_LENGTH = 500

# Indicateur de la position du step
# à changer pour s'aligner sur l'API Acme
_FIRST = -1
MID = 0
LAST = 1

# Interface HM
MAPBOX_KEY =    'pk.eyJ1IjoieXZlc3A3NSIsImEiOiJja2EzcGE3cGowMGpwM2ZvMmc2bGpsZjVpIn0.H0xY3gvvr4Ajtj6hKgMEhA'

COLOR_BREWER_BLUE_SCALE = [
    [240, 249, 232],
    [204, 235, 197],
    [168, 221, 181],
    [123, 204, 196],
    [67, 162, 202],
    [8, 104, 172],
]

NUMBER_OF_SECTORS = 8
NUMBER_OF_CROWNS = 10
HIGH = 0.8
LOW = 0.2
