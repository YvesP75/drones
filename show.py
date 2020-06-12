import numpy as np
# import matplotlib.pyplot as plt
# import pandas as pd
import time
import pydeck as pdk
import plotly.graph_objects as go
import streamlit as st

# import ad hoc files
from util import Util
from settings import ZERO_X, ZERO_Y, MAPBOX_KEY, TIME_SLEEP, TIME_LENGTH
from settings import COLOR_BREWER_BLUE_SCALE


class Show:

    def run(env):
        st.title('Où est passée la voiture?')
        deck_map = st.empty()
        counter = st.empty()
        initialViewState = Show.create_map(deck_map)
        Show.run_drones_cars(env, deck_map, initialViewState, counter)

    def create_map(deck_map):
        initialViewState = pdk.ViewState(
            latitude=ZERO_Y,
            longitude=ZERO_X,
            zoom=10,
            pitch=0
        )
        deck_map.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v9',
            initial_view_state=initialViewState,
            mapbox_key=MAPBOX_KEY,
        ))
        return initialViewState

    def run_drones_cars(env, deck_map, initialViewState, counter):
        for i in range(TIME_LENGTH):
            layers = Layers(env, i)
            deck_map.pydeck_chart(pdk.Deck(
                map_style='mapbox://styles/mapbox/light-v9',
                initial_view_state=initialViewState,
                layers=layers.layers
            ))
            if i > 0:
                counter.plotly_chart(
                    Counter(env.cars, i).fig,
                    use_container_width=True
                )
            time.sleep(TIME_SLEEP)


class Layers:

    def __init__(self, env, time_index):
        cars_layer = pdk.Layer(
            'HeatmapLayer',
            data=Util.grid_to_latlon(
                sum(
                    [car.positions[time_index]
                        for car in env.cars if car.alive[-1] == 0]
                    )
            ),
            get_position='[lon, lat]',
            aggregation='"MEAN"',
            opacity=0.7,
            threshold=0.00,
            get_weight="value",
            color_range=COLOR_BREWER_BLUE_SCALE,
            pickable=True,
        )
        visibility_layer = pdk.Layer(
            'ScatterplotLayer',
            data=Util.grid_to_latlon(env.visibilities[time_index]),
            get_position='[lon, lat]',
            get_color='[200, 30, 0, 160]',
            get_radius=8,
            opacity=0.6,
        )
        drones_layer = pdk.Layer(
            'ScatterplotLayer',
            data=env.get_drones_positions(time_index),
            get_position='[lon, lat]',
            get_color='[200, 30, 00, 160]',
            get_radius=50,
        )
        second_eyes_layer = pdk.Layer(
            'ScatterplotLayer',
            data=env.get_second_eyes_positions(time_index),
            get_position='[lon, lat]',
            get_color='[200, 30, 00, 160]',
            get_radius=20,
        )
        self.layers = [
            cars_layer,
            visibility_layer,
            drones_layer,
            second_eyes_layer
            ]


class Counter:

    def __init__(self, cars, time_index):
        time = [*range(time_index)]
        self.fig = go.Figure(data=[
            go.Bar(
                name='caught',
                x=time,
                y=np.sum(
                    [car.caught[0:time_index] for car in cars], axis=0
                    ),
                marker_line_width=0,
                marker_color='rgb(10, 10, 80)',
                width=np.ones(TIME_LENGTH)
            ),
            go.Bar(
                name='loss',
                x=time,
                y=np.sum(
                    [car.loss[0:time_index] for car in cars], axis=0
                ),
                marker_line_width=0,
                marker_color='rgb(100, 100, 100)',
                width=np.ones(TIME_LENGTH)
            ),
            go.Bar(
                name='alive',
                x=time,
                y=np.sum(
                    [car.belief[0:time_index] for car in cars], axis=0
                    ),
                marker_line_width=0,
                marker_color='rgb(200, 200, 200)',
                width=np.ones(TIME_LENGTH)
            ),
        ])
        self.fig.update_layout(
            barmode='stack',
            height=350,
            width=650,
            plot_bgcolor='rgb(255, 255, 255)'
        )
